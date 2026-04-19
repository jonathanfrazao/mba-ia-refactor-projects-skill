import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
DATABASE_URL = os.environ.get('DATABASE_URL', 'loja.db')
FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

CATEGORIAS_VALIDAS = ['informatica', 'moveis', 'vestuario', 'geral', 'eletronicos', 'livros']
STATUS_PEDIDO_VALIDOS = ['pendente', 'aprovado', 'enviado', 'entregue', 'cancelado']
