import logging
from flask import request, jsonify
import services.pedido_service as pedido_service

logger = logging.getLogger(__name__)


def criar_pedido():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    try:
        resultado = pedido_service.criar(
            dados.get("usuario_id"),
            dados.get("itens", []),
        )
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
    except ValueError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 400


def listar_todos_pedidos():
    pedidos = pedido_service.listar_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_service.listar_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    try:
        pedido_service.atualizar_status(pedido_id, dados.get("status", ""))
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


def relatorio_vendas():
    relatorio = pedido_service.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200


def health_check():
    from database import get_db, ping
    if not ping():
        return jsonify({"status": "erro", "database": "disconnected"}), 500
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    pedidos = cursor.fetchone()[0]
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
        "versao": "1.0.0",
    }), 200
