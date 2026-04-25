import logging
from flask import request, jsonify
from services import task_service

logger = logging.getLogger(__name__)


def get_tasks():
    try:
        return jsonify(task_service.get_all_tasks()), 200
    except Exception:
        logger.exception("Erro em get_tasks")
        return jsonify({'error': 'Erro interno'}), 500


def get_task(task_id):
    data = task_service.get_task(task_id)
    if data is None:
        return jsonify({'error': 'Task não encontrada'}), 404
    return jsonify(data), 200


def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        task = task_service.create_task(data)
        return jsonify(task), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        logger.exception("Erro em create_task")
        return jsonify({'error': 'Erro ao criar task'}), 500


def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        task = task_service.update_task(task_id, data)
        if task is None:
            return jsonify({'error': 'Task não encontrada'}), 404
        return jsonify(task), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        logger.exception("Erro em update_task")
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_task(task_id):
    if not task_service.delete_task(task_id):
        return jsonify({'error': 'Task não encontrada'}), 404
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    result = task_service.search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', '')
    )
    return jsonify(result), 200


def task_stats():
    return jsonify(task_service.get_task_stats()), 200
