import logging
from werkzeug.security import generate_password_hash, check_password_hash
import models.usuario_model as usuario_model

logger = logging.getLogger(__name__)


def listar():
    return usuario_model.get_todos_usuarios()


def buscar_por_id(usuario_id):
    usuario = usuario_model.get_usuario_por_id(usuario_id)
    if not usuario:
        raise LookupError("Usuário não encontrado")
    return usuario


def criar(nome, email, senha):
    if not nome or not email or not senha:
        raise ValueError("Nome, email e senha são obrigatórios")
    senha_hash = generate_password_hash(senha)
    usuario_id = usuario_model.criar_usuario(nome, email, senha_hash)
    logger.info(f"Usuário criado: email={email}")
    return usuario_id


def autenticar(email, senha):
    if not email or not senha:
        raise ValueError("Email e senha são obrigatórios")
    usuario = usuario_model.get_usuario_por_email(email)
    if usuario and check_password_hash(usuario["senha"], senha):
        logger.info(f"Login bem-sucedido: email={email}")
        return {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "tipo": usuario["tipo"],
        }
    logger.warning(f"Login falhou: email={email}")
    return None
