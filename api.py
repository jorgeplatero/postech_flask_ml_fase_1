import logging
import joblib
import numpy as np
from flask import Flask, request, jsonify
from config import Config
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from models import db, User, Prediction


CLASS_NAMES = {
    0: 'setosa',
    1: 'versicolor',
    2: 'virginica'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api')

try:
    model = joblib.load('model.pkl')
    logger.info('Modelo carregado com sucesso')
except FileNotFoundError:
    logger.error('Arquivo "model.pkl" não encontrado. Certifique-se de ter um modelo treinado.')
    model = None

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
swagger = Swagger(app)
bcrypt = Bcrypt(app)

with app.app_context():
    try:
        db.create_all() 
        logger.info('Tabelas do banco de dados criadas/verificadas.')
    except Exception as e:
        logger.error('Erro crítico ao criar as tabelas do BD: %s', e)

prediction_cache = {}

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    '''Retorna quando o token está ausente na requisição protegida.'''
    if 'Missing' in str(callback) or 'Authorization header' in str(callback):
        return jsonify({'msg': 'Token não informado'}), 401
    return jsonify({
        'error': 'Erro de autenticação'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(err):
    '''Retorna quando o token é malformado (ex: erro de padding, assinatura inválida).'''
    logger.error(f'Erro de token inválido: {err}')
    return jsonify({
        'error': 'Token inválido'
    }), 401

@jwt.expired_token_loader
def expired_token_callback(header, payload):
    '''Retorna quando o token é válido, mas o tempo de expiração já passou.'''
    return jsonify({
        'error': 'Token expirado'
    }), 401

@app.route('/')
def home():
    '''
    Endpoint raiz da API.
    ---
    responses:
        200:
            description: Mensagem de boas-vindas e status da API.
    '''
    return jsonify({
        'status': 'online',
        'msg': 'Bem-vindo à API de predição Iris. Acesse /apidocs para documentação.' 
    })


def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user

@app.route('/register', methods=['POST'])
def register_user():
    '''
    Registra um novo usuário.
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
                password:
                    type: string
    responses:
        201:
            description: Usuário criado com sucesso
        400:
            description: Usuário já existe
    '''
    data = request.get_json(force=True)
    if get_user_by_username(data['username']):
        return jsonify({'error': 'Usuário já existe'}), 400
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error('Erro ao registrar usuário: %s', e)
        return jsonify({'error': 'Erro interno ao registrar usuário'}), 500
    return jsonify({'msg': 'Usuário criado com sucesso'}), 201

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
                  password:
                      type: string
    responses:
        200:
            description: Login bem sucedido, retorna o token JWT
            schema:
                type: object
                properties:
                    access_token:
                        type: string
                        description: O token de acesso JWT
        401:
            description: Credenciais inválidas
    '''
    data = request.get_json(force=True)
    user = get_user_by_username(data['username'])
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200
    return jsonify({'error': 'Credenciais inválidas'}), 401
    
@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    '''
    Realiza uma predição com o modelo Iris e armazena o resultado.
    ---
    security:
        - BearerAuth: []
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
                    predicted_specie:
                        type: string
                        description: "Classe prevista (ex: setosa, versicolor ou virginica)"
        400:
            description: Dados inválidos, verifique parâmetros
        401:
            description: Token não informado/Token inválido/Token expirado/Erro de autenticação
    '''
    data = request.get_json(force=True)
    try:
        sepal_length = float(data['sepal_length'])
        sepal_width = float(data['sepal_width'])
        petal_length = float(data['petal_length'])
        petal_width = float(data['petal_width'])
    except (ValueError, KeyError) as e:
        logger.error('Dados de entrada inválidos')
        return jsonify({'error': 'Dados inválidos, verifique parâmetros'}), 400
    features = (sepal_length, sepal_width, petal_length, petal_width)
    if features in prediction_cache:
        logger.info('Cache hit para %s', features)
        predicted_class = prediction_cache[features]
    else:
        input_data = np.array([features])
        prediction = model.predict(input_data)
        predicted_class = int(prediction[0])
        prediction_cache[features] = predicted_class
        logger.info('Cache updated para %s', features)
    predicted_specie_name = CLASS_NAMES.get(predicted_class)
    try:
        new_pred = Prediction(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width,
            predicted_class=predicted_class,
            predicted_specie=predicted_specie_name
        )
        db.session.add(new_pred)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error('Erro ao salvar predição: %s', e)
    return jsonify({'predicted_specie': predicted_specie_name})

@app.route('/predictions', methods=['GET'])
@jwt_required()
def list_predictions():
    '''
    Lista as predições armazenadas no banco, com paginação.
    ---
    security:
        - BearerAuth: []
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
                        predicted_specie:
                            type: string
                        created_at:
                            type: string
                            format: date-time
        401:
            description: Token não informado/Token inválido/Token expirado/Erro de autenticação
    '''
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    preds = Prediction.query.order_by(Prediction.id.desc()).limit(limit).offset(offset).all()
    
    results = []
    for p in preds:
        results.append({
            'id': p.id,
            'sepal_length': p.sepal_length,
            'sepal_width': p.sepal_width,
            'petal_length': p.petal_length,
            'petal_width': p.petal_width,
            'predicted_class': p.predicted_class,
            'predicted_specie': p.predicted_specie,
            'created_at': p.created_at.isoformat()
        })

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info('Tabelas do banco de dados criadas/verificadas.')
    app.run(debug=True)