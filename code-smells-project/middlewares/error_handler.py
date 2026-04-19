import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": "Requisição inválida", "detalhes": str(e)}), 400

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"erro": "Acesso negado"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}", exc_info=True)
        return jsonify({"erro": "Erro interno do servidor"}), 500
