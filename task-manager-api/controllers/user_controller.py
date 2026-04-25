import logging
from flask import request, jsonify
from services import user_service

logger = logging.getLogger(__name__)


def get_users():
    return jsonify(user_service.get_all_users()), 200


def get_user(user_id):
    data = user_service.get_user(user_id)
    if data is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(data), 200


def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        user = user_service.create_user(data)
        return jsonify(user), 201
    except ValueError as e:
        status_code = 409 if 'cadastrado' in str(e) else 400
        return jsonify({'error': str(e)}), status_code
    except Exception:
        logger.exception("Erro em create_user")
        return jsonify({'error': 'Erro ao criar usuário'}), 500


def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        user = user_service.update_user(user_id, data)
        if user is None:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify(user), 200
    except ValueError as e:
        status_code = 409 if 'cadastrado' in str(e) else 400
        return jsonify({'error': str(e)}), status_code
    except Exception:
        logger.exception("Erro em update_user")
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_user(user_id):
    if not user_service.delete_user(user_id):
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    result = user_service.get_user_tasks(user_id)
    if result is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(result), 200


def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    try:
        user = user_service.login(email, password)
        return jsonify({'message': 'Login realizado com sucesso', 'user': user}), 200
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
