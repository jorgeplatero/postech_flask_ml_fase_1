import os


class Config(object):
    '''Configuração da API para Predição de Espécies Iris'''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///predictions.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'MEUSEGREDOAQUI')
    JWT_ALGORITHM = 'HS256'
    SWAGGER = {
        'title': 'API Flask para Predição de Espécies Iris',
        'uiversion': 3,
        'description': 'API Flask para predição de espécies Iris.'
    }