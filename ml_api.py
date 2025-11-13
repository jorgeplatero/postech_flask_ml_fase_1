import os
import logging
import datetime
import jwt
from functools import wraps
from flask import Flask, request, jsonify
import joblib
import numpy as np
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from flasgger import Swagger


#mapeamento da target para o nome da espécie
CLASS_NAMES = {
    0: 'setosa',
    1: 'versicolor',
    2: 'virginica'
}

#configurações de JWT e logs
JWT_SECRET = 'MEUSEGREDOAQUI'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('model_api')

#configuração do sqlalchemy
DB_URL = 'sqlite:///predictions.db'
engine = create_engine(DB_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Prediction(Base):
    __tablename__ = 'prediction'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    predicted_species = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)

model = joblib.load('model_iris.pkl')
logger.info('Modelo carregado com sucesso')

app = Flask(__name__)
swagger = Swagger(app)

prediction_cache = {}

TEST_USERNAME = 'admin'
TEST_PASSWORD = 'secret'

def create_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        #pegar o token do eader authorization: bearer <token>
        #decodificar e checar expiração
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    '''
    Endpoint raiz da API.
    ---
    responses:
        200:
            description: Mensagem de boas-vindas e status da API.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        example: online
                    message:
                        type: string
                        example: Bem-vindo à API de predição Iris. Acesse /apidocs para documentação..
    '''
    return jsonify({
        'status': 'online',
        'message': 'Bem-vindo à API de predição Iris. Acesse /apidocs para documentação.'
    })

@app.route('/login', methods=['POST'])
def login():
    '''
    Gera um token JWT para autenticação.
    ---
    parameters:
        - in: body
          name: body
          required: true
          schema:
              type: object
              properties:
                  username:
                      type: string
                      example: admin
                  password:
                      type: string
                      example: secret
    responses:
        200:
            description: Login bem sucedido, retorna o token JWT
            schema:
                type: object
                properties:
                    token:
                        type: string
                        description: O token de acesso JWT
        401:
            description: Credenciais inválidas
    '''
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    if username == TEST_USERNAME and password == TEST_PASSWORD:
        token = create_token(username)
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401
    
@app.route('/predict', methods=['POST'])
@token_required
def predict():
    '''
    Realiza uma predição com o modelo Iris e armazena o resultado.
    ---
    security:
        - Bearer: []
    parameters:
        - in: body
          name: body
          required: true
          schema:
              type: object
              properties:
                  sepal_length:
                      type: number
                      format: float
                      description: Comprimento da sépala (cm).
                      example: 5.1
                  sepal_width:
                      type: number
                      format: float
                      description: Largura da sépala (cm).
                      example: 3.5
                  petal_length:
                      type: number
                      format: float
                      description: Comprimento da pétala (cm).
                      example: 1.4
                  petal_width:
                      type: number
                      format: float
                      description: Largura da pétala (cm).
                      example: 0.2
    responses:
        200:
            description: Predição realizada com sucesso
            schema:
                type: object
                properties:
                    predicted_species:
                        type: string
                        description: "Classe prevista (ex: setosa, versicolor ou virginica)"
        400:
            description: Dados de entrada inválidos
        401:
            description: Token não fornecido ou inválido/expirado
    '''
    data = request.get_json(force=True)
    try:
        sepal_length = float(data['sepal_length'])
        sepal_width = float(data['sepal_width'])
        petal_length = float(data['petal_length'])
        petal_width = float(data['petal_width'])
    except (ValueError, KeyError) as e:
        logger.error('Dados de entreda inválidos')
        return jsonify({'error': 'Dados inválidos, verifique parâmetros'}), 400
    
    #verificar se já está no cache
    features = (sepal_length, sepal_width, petal_length, petal_width)
    if features in prediction_cache:
        logger.info('Cache hit para %s', features)
        predicted_class = prediction_cache[features]
    else:
        #rodar o modelo
        input_data = np.array([features])
        prediction = model.predict(input_data)
        predicted_class = int(prediction[0])
        #armazenar no cache
        prediction_cache[features] = predicted_class
        logger.info('Cache updated para %s', features)

    predicted_species_name = CLASS_NAMES.get(predicted_class)
    #armazenar em db
    db = SessionLocal()
    new_pred = Prediction(
        sepal_length=sepal_length,
        sepal_width=sepal_width,
        petal_length=petal_length,
        petal_width=petal_width,
        predicted_class=predicted_class,
        predicted_species=predicted_species_name
    )
    db.add(new_pred)
    db.commit()
    db.close()

    return jsonify({'predicted_species': predicted_species_name})

@app.route('/predictions', methods=['GET'])
@token_required
def list_predictions():
    '''
    Lista as predições armazenadas no banco, com paginação.
    ---
    security:
        - Bearer: []
    parameters:
        - in: query
          name: limit
          type: integer
          required: false
          default: 10
          description: Número máximo de registros para retornar.
        - in: query
          name: offset
          type: integer
          required: false
          default: 0
          description: Número de registros a ignorar (para paginação).
    responses:
        200:
            description: Lista de predições.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        sepal_length:
                            type: number
                        sepal_width:
                            type: number
                        petal_length:
                            type: number
                        petal_width:
                            type: number
                        predicted_class:
                            type: integer
                        predicted_species:
                            type: string
                        created_at:
                            type: string
                            format: date-time
        401:
            description: Token não fornecido ou inválido/expirado
    '''
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    db = SessionLocal()
    preds = db.query(Prediction).order_by(Prediction.id.desc()).limit(limit).offset(offset).all() 
    db.query(Prediction).order_by(Prediction.id.desc()).limit(limit).offset(offset).all()
    db.close()
    results = []
    for p in preds:
        results.append({
            'id': p.id,
            'sepal_length': p.sepal_length,
            'sepal_width': p.sepal_width,
            'petal_length': p.petal_length,
            'petal_width': p.petal_width,
            'predicted_class': p.predicted_class,
            'predicted_species': p.predicted_species,
            'created_at': p.created_at.isoformat()
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
