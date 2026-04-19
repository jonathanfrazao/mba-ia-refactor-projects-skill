import logging
from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY, DEBUG
from database import get_db
from routes.main_routes import main_bp
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from routes.pedido_routes import pedido_bp
from routes.admin_routes import admin_bp
from middlewares.error_handler import register_error_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG

CORS(app)

app.register_blueprint(main_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(pedido_bp)
app.register_blueprint(admin_bp)

register_error_handlers(app)

if __name__ == "__main__":
    get_db()
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
