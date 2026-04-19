import logging
from flask import Blueprint, jsonify, request, abort
from config import FLASK_ENV
from database import get_db

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_dev_env():
    if FLASK_ENV != "development":
        abort(403)


@admin_bp.route("/reset-db", methods=["POST"])
def reset_database():
    _require_dev_env()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    logger.warning("Database reset performed (development only)")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
