import logging
from flask import request, jsonify
import services.usuario_service as usuario_service

logger = logging.getLogger(__name__)


def listar_usuarios():
    usuarios = usuario_service.listar()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    try:
        usuario = usuario_service.buscar_por_id(id)
        return jsonify({"dados": usuario, "sucesso": True}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404


def criar_usuario():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    try:
        usuario_id = usuario_service.criar(
            dados.get("nome", ""),
            dados.get("email", ""),
            dados.get("senha", ""),
        )
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    try:
        usuario = usuario_service.autenticar(
            dados.get("email", ""),
            dados.get("senha", ""),
        )
        if usuario:
            # TODO: generate a signed JWT via flask-jwt-extended and return it here
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
