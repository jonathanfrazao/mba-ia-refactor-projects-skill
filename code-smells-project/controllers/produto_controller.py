import logging
from flask import request, jsonify
import services.produto_service as produto_service

logger = logging.getLogger(__name__)


def listar_produtos():
    produtos = produto_service.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)
    resultados = produto_service.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def buscar_produto(id):
    try:
        produto = produto_service.buscar_por_id(id)
        return jsonify({"dados": produto, "sucesso": True}), 200
    except LookupError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 404


def criar_produto():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    try:
        produto_id = produto_service.criar(dados)
        return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


def atualizar_produto(id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    try:
        produto_service.atualizar(id, dados)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


def deletar_produto(id):
    try:
        produto_service.deletar(id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
