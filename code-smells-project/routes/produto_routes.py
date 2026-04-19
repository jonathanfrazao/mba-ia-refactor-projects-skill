from flask import Blueprint
from controllers.produto_controller import (
    listar_produtos,
    buscar_produtos,
    buscar_produto,
    criar_produto,
    atualizar_produto,
    deletar_produto,
)

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

produto_bp.add_url_rule("", "listar_produtos", listar_produtos, methods=["GET"])
produto_bp.add_url_rule("/busca", "buscar_produtos", buscar_produtos, methods=["GET"])
produto_bp.add_url_rule("/<int:id>", "buscar_produto", buscar_produto, methods=["GET"])
produto_bp.add_url_rule("", "criar_produto", criar_produto, methods=["POST"])
produto_bp.add_url_rule("/<int:id>", "atualizar_produto", atualizar_produto, methods=["PUT"])
produto_bp.add_url_rule("/<int:id>", "deletar_produto", deletar_produto, methods=["DELETE"])
