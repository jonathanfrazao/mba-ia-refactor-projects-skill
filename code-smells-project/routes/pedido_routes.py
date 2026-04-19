from flask import Blueprint
from controllers.pedido_controller import (
    criar_pedido,
    listar_todos_pedidos,
    listar_pedidos_usuario,
    atualizar_status_pedido,
    relatorio_vendas,
    health_check,
)

pedido_bp = Blueprint("pedidos", __name__)

pedido_bp.add_url_rule("/pedidos", "criar_pedido", criar_pedido, methods=["POST"])
pedido_bp.add_url_rule("/pedidos", "listar_todos_pedidos", listar_todos_pedidos, methods=["GET"])
pedido_bp.add_url_rule(
    "/pedidos/usuario/<int:usuario_id>",
    "listar_pedidos_usuario",
    listar_pedidos_usuario,
    methods=["GET"],
)
pedido_bp.add_url_rule(
    "/pedidos/<int:pedido_id>/status",
    "atualizar_status_pedido",
    atualizar_status_pedido,
    methods=["PUT"],
)
pedido_bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", relatorio_vendas, methods=["GET"])
pedido_bp.add_url_rule("/health", "health_check", health_check, methods=["GET"])
