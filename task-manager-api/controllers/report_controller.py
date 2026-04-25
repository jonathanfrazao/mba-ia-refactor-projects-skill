import logging
from flask import request, jsonify
from services import report_service

logger = logging.getLogger(__name__)


def summary_report():
    return jsonify(report_service.get_summary_report()), 200


def user_report(user_id):
    data = report_service.get_user_report(user_id)
    if data is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(data), 200


def get_categories():
    return jsonify(report_service.get_categories()), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        cat = report_service.create_category(data)
        return jsonify(cat), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        logger.exception("Erro em create_category")
        return jsonify({'error': 'Erro ao criar categoria'}), 500


def update_category(cat_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    cat = report_service.update_category(cat_id, data)
    if cat is None:
        return jsonify({'error': 'Categoria não encontrada'}), 404
    return jsonify(cat), 200


def delete_category(cat_id):
    if not report_service.delete_category(cat_id):
        return jsonify({'error': 'Categoria não encontrada'}), 404
    return jsonify({'message': 'Categoria deletada'}), 200
