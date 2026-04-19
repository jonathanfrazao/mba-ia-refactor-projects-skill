# MVC Architecture — Target Standard

This document defines the target architecture for Phase 3. Every refactoring decision must converge toward this structure, regardless of the original project's language or framework.

---

## 1. Core Principle

Each layer has exactly one reason to change:

| Layer | Reason to change |
|-------|-----------------|
| Config | Environment or infrastructure changes |
| Model | Data schema or persistence strategy changes |
| Service/Controller | Business rules change |
| Routes/Views | HTTP contract or API shape changes |
| Middleware | Cross-cutting concerns (auth, logging, error handling) change |

No layer should reach into the responsibilities of another.

---

## 2. Target Directory Structure

### Python / Flask

```
project/
├── app.py                    # Composition root — wires everything together
├── config.py                 # All configuration, loaded from env vars
├── database.py               # DB initialization (SQLAlchemy instance or connection factory)
├── models/
│   ├── __init__.py
│   ├── user_model.py         # ORM class + relationships only
│   ├── product_model.py
│   └── ...
├── services/
│   ├── __init__.py
│   ├── user_service.py       # Business logic for user domain
│   ├── order_service.py
│   └── ...
├── controllers/
│   ├── __init__.py
│   ├── user_controller.py    # HTTP handlers — parse input, call service, return response
│   ├── product_controller.py
│   └── ...
├── routes/
│   ├── __init__.py
│   ├── user_routes.py        # Blueprint with route declarations only
│   ├── product_routes.py
│   └── ...
└── middlewares/
    ├── __init__.py
    ├── auth.py               # Token verification decorator
    └── error_handler.py      # Centralized error responses
```

### Node.js / Express

```
src/
├── app.js                    # Composition root — wires everything together
├── config/
│   └── settings.js           # All configuration from process.env
├── models/
│   ├── userModel.js          # Schema + DB access only
│   ├── courseModel.js
│   └── ...
├── services/
│   ├── userService.js        # Business logic
│   ├── paymentService.js
│   └── ...
├── controllers/
│   ├── userController.js     # req/res handling — delegates to service
│   ├── courseController.js
│   └── ...
├── routes/
│   ├── userRoutes.js         # express.Router() with route declarations
│   ├── courseRoutes.js
│   └── ...
└── middlewares/
    ├── authMiddleware.js     # Token verification
    └── errorHandler.js       # Centralized error responses
```

---

## 3. Layer Responsibilities

### 3.1 Config

**What belongs here:** All values that differ between environments (development, staging, production).

**Rules:**
- Never hardcode secrets, ports, DSNs or API keys as string literals in any other file
- All values read from environment variables with a sensible default only for non-sensitive ones
- Single source of truth — all other files import config, never access `os.environ` directly

```python
# Python example — config.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

```javascript
// Node.js example — config/settings.js
require('dotenv').config();

module.exports = {
    secretKey: process.env.SECRET_KEY,
    databaseUrl: process.env.DATABASE_URL || './data/app.db',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    port: parseInt(process.env.PORT) || 3000,
};
```

---

### 3.2 Model

**What belongs here:** Data schema definition, relationships, field validation at the persistence level, and a `to_dict()` / serialization method that excludes sensitive fields.

**Rules:**
- No business logic (no multi-step operations, no conditional workflows)
- No HTTP-specific code (`request`, `jsonify`, `res`, `req`)
- No direct business error returns (`return {"erro": "..."}`)
- The `to_dict()` method must **never** include `password`, `secret`, `token`, or internal keys

```python
# Python example — models/user_model.py
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}
        # password is intentionally excluded
```

---

### 3.3 Service / Use-Case Layer

**What belongs here:** All business rules, domain validations, multi-step operations, and orchestration of model calls.

**Rules:**
- No HTTP-specific code — services receive plain Python/JS values and return plain values or raise exceptions
- Services call models/repositories; they do not call other services unless composing use-cases
- All complex conditionals (stock checks, discount tiers, payment approval logic) live here
- External service calls (email, SMS, push) are invoked from here via injected or imported adapters

```python
# Python example — services/order_service.py
from models.product_model import Product
from models.order_model import Order, OrderItem
from database import db

def create_order(user_id, items):
    total = 0
    for item in items:
        product = db.session.get(Product, item['product_id'])
        if not product:
            raise ValueError(f"Produto {item['product_id']} não encontrado")
        if product.stock < item['quantity']:
            raise ValueError(f"Estoque insuficiente para {product.name}")
        total += product.price * item['quantity']

    order = Order(user_id=user_id, total=total, status='pending')
    db.session.add(order)
    # ... rest of the logic
    db.session.commit()
    return order
```

---

### 3.4 Controller

**What belongs here:** Parsing HTTP input, calling the service, and returning the HTTP response.

**Rules:**
- Controller functions should be short (≤ 20 lines in most cases)
- Validate that required fields exist in the request body — delegate deeper validation to the service
- Catch service exceptions and map them to appropriate HTTP status codes
- No direct database access (`db.session`, `cursor.execute`)

```python
# Python example — controllers/order_controller.py
from flask import request, jsonify
from services.order_service import create_order

def criar_pedido():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    try:
        order = create_order(data.get('user_id'), data.get('items', []))
        return jsonify({'data': order.to_dict(), 'success': True}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Erro interno'}), 500
```

---

### 3.5 Routes / Views

**What belongs here:** URL path declarations, HTTP method bindings, and grouping by domain (Blueprint / Router).

**Rules:**
- Route files contain **only** `Blueprint`/`Router` declarations and `add_url_rule`/`.get()`/`.post()` calls
- No business logic, no database access, no `request.get_json()` processing
- Each domain (users, products, orders) has its own route file

```python
# Python example — routes/order_routes.py
from flask import Blueprint
from controllers.order_controller import criar_pedido, listar_pedidos

order_bp = Blueprint('orders', __name__, url_prefix='/orders')

order_bp.add_url_rule('', 'criar_pedido', criar_pedido, methods=['POST'])
order_bp.add_url_rule('', 'listar_pedidos', listar_pedidos, methods=['GET'])
```

```javascript
// Node.js example — routes/orderRoutes.js
const express = require('express');
const { criarPedido, listarPedidos } = require('../controllers/orderController');
const router = express.Router();

router.post('/', criarPedido);
router.get('/', listarPedidos);

module.exports = router;
```

---

### 3.6 Middleware

**What belongs here:** Cross-cutting concerns that apply to multiple routes — authentication, request logging, centralized error handling, CORS.

**Rules:**
- Middleware must not contain business logic
- Authentication middleware: verify token and attach user context to the request; reject with 401 if invalid
- Error handler middleware: catch all unhandled exceptions and return a consistent JSON error format
- Logging middleware: log method, path, status code and duration

```python
# Python example — middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
```

---

## 4. Composition Root (Entry Point)

The entry point (`app.py` / `app.js`) is the **only** place that wires all layers together. It should contain:
- Application factory or instance creation
- Configuration loading
- Database initialization
- Middleware registration
- Blueprint / Router registration
- Server startup

It must **not** contain route handlers, business logic or database queries.

```python
# Python example — app.py
from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY, DATABASE_URL
from database import db
from routes.user_routes import user_bp
from routes.order_routes import order_bp
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    CORS(app)
    db.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    register_error_handlers(app)
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run()
```

---

## 5. What is NOT MVC (Anti-checklist)

Reject any structure where:
- [ ] A route handler calls `cursor.execute(` or `db.session.query(` directly
- [ ] A model method returns `{"erro": "..."}` or `{"error": "..."}`
- [ ] Business logic (loops, conditionals, calculations) lives inside the entry point
- [ ] A service imports `request` or `jsonify`
- [ ] A single file registers routes AND contains model definitions AND has business logic
- [ ] `password`, `secret_key` or `token` appear in any `to_dict()` output
- [ ] Any `SECRET_KEY`, `DATABASE_URL`, API key is a string literal outside `config.py`
