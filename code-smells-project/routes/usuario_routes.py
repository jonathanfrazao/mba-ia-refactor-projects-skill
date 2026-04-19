from flask import Blueprint
from controllers.usuario_controller import (
    listar_usuarios,
    buscar_usuario,
    criar_usuario,
    login,
)

usuario_bp = Blueprint("usuarios", __name__)

usuario_bp.add_url_rule("/usuarios", "listar_usuarios", listar_usuarios, methods=["GET"])
usuario_bp.add_url_rule("/usuarios/<int:id>", "buscar_usuario", buscar_usuario, methods=["GET"])
usuario_bp.add_url_rule("/usuarios", "criar_usuario", criar_usuario, methods=["POST"])
usuario_bp.add_url_rule("/login", "login", login, methods=["POST"])
