# Refactoring Playbook

Reference for Phase 3. Each pattern maps an anti-pattern from the catalog to a concrete transformation with before/after code examples in both Python and Node.js.

Apply transformations in this order: Config → Models → Services → Controllers → Routes → Middlewares → Entry Point.

---

## PT-01 — SQL Injection via Concatenation → Parameterized Queries

**Addresses:** AP-01

### Python (sqlite3 raw)

**Before:**
```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "' AND password = '" + password + "'")

cursor.execute("SELECT * FROM products WHERE id = " + str(id))

query = "SELECT * FROM products WHERE 1=1"
query += " AND name LIKE '%" + term + "%'"
cursor.execute(query)
```

**After:**
```python
cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))

cursor.execute("SELECT * FROM products WHERE id = ?", (id,))

query = "SELECT * FROM products WHERE 1=1"
params = []
if term:
    query += " AND name LIKE ?"
    params.append(f"%{term}%")
cursor.execute(query, params)
```

### Node.js (sqlite3)

**Before:**
```javascript
db.get(`SELECT * FROM users WHERE email = '${email}'`, (err, row) => { ... });
db.run("INSERT INTO users (name, email) VALUES ('" + name + "', '" + email + "')", ...);
```

**After:**
```javascript
db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) => { ... });
db.run("INSERT INTO users (name, email) VALUES (?, ?)", [name, email], ...);
```

**Rule:** Every value from the outside world — URL params, query strings, request body, headers — must go through a placeholder (`?` in sqlite3, `$1` in pg). Never use `+`, f-strings or template literals to build SQL.

---

## PT-02 — Hardcoded Credentials → Environment Variables

**Addresses:** AP-02

### Python

**Before:**
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

# services/notification_service.py
self.email_user = 'taskmanager@gmail.com'
self.email_password = 'senha123'
```

**After:**
```python
# config.py (new file)
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# app.py — import from config, not hardcoded
from config import SECRET_KEY, DATABASE_URL
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

### Node.js

**Before:**
```javascript
// utils.js
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    port: 3000
};
```

**After:**
```javascript
// config/settings.js
require('dotenv').config();

module.exports = {
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    port: parseInt(process.env.PORT) || 3000,
};
```

Also create a `.env.example` file (safe to commit) and add `.env` to `.gitignore`.

---

## PT-03 — Plaintext / Broken Password Storage → Secure Hash

**Addresses:** AP-03

### Python (Flask — werkzeug already available)

**Before:**
```python
# Using MD5 — cryptographically broken
import hashlib
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()

# Or plaintext
cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, senha))
```

**After:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, raw_password):
    self.password = generate_password_hash(raw_password)

def check_password(self, raw_password):
    return check_password_hash(self.password, raw_password)
```

### Node.js

**Before:**
```javascript
// Custom base64 "hash" — not a hash
function badCrypto(pwd) {
    return Buffer.from(pwd).toString('base64').substring(0, 10);
}
```

**After:**
```javascript
// npm install bcrypt
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;

async function hashPassword(pwd) {
    return bcrypt.hash(pwd, SALT_ROUNDS);
}

async function verifyPassword(pwd, hash) {
    return bcrypt.compare(pwd, hash);
}
```

---

## PT-04 — God Object → Layered MVC Structure

**Addresses:** AP-04

This is a structural transformation. When a single class/file contains routes + DB + business logic, split it as follows:

**Before (Node.js — AppManager pattern):**
```javascript
class AppManager {
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            // 50+ lines: DB query + user creation + payment logic + enrollment + audit
            this.db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
                this.db.run("INSERT INTO enrollments ...", [...], function(err) {
                    // ... 3 more levels of nesting
                });
            });
        });
    }
}
```

**After:**
```javascript
// models/courseModel.js
const getCourseById = (db, id) => new Promise((resolve, reject) => {
    db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id], (err, row) => {
        if (err) reject(err); else resolve(row);
    });
});

// services/enrollmentService.js
async function processCheckout(db, { userName, email, password, courseId, cardNumber }) {
    const course = await getCourseById(db, courseId);
    if (!course) throw new Error('Curso não encontrado');
    const status = await paymentService.charge(cardNumber, course.price);
    if (status === 'DENIED') throw new Error('Pagamento recusado');
    return enrollmentRepository.create(db, { userId, courseId, amount: course.price });
}

// controllers/checkoutController.js
async function checkout(req, res) {
    try {
        const result = await processCheckout(db, req.body);
        res.status(200).json({ success: true, enrollment_id: result.id });
    } catch (e) {
        res.status(400).json({ error: e.message });
    }
}

// routes/checkoutRoutes.js
router.post('/api/checkout', checkout);
```

**Before (Python — models.py with business logic):**
```python
# models.py
def criar_pedido(usuario_id, itens):
    # stock check, total calc, insert order, insert items, decrement stock — all here
    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente"}
    # ...
```

**After:**
```python
# services/order_service.py
def criar_pedido(usuario_id, itens):
    total = 0
    for item in itens:
        product = db.session.get(Product, item['product_id'])
        if not product:
            raise ValueError(f"Produto {item['product_id']} não encontrado")
        if product.stock < item['quantity']:
            raise ValueError(f"Estoque insuficiente para {product.name}")
        total += product.price * item['quantity']
    order = Order(user_id=usuario_id, total=total, status='pending')
    db.session.add(order)
    db.session.commit()
    return order

# controllers/order_controller.py
def criar_pedido():
    data = request.get_json()
    try:
        order = order_service.criar_pedido(data['user_id'], data['items'])
        return jsonify({'data': order.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

---

## PT-05 — Sensitive Fields in Response → Public Serialization

**Addresses:** AP-07

**Before:**
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'password': self.password,  # hash exposed in every response
        'role': self.role,
    }
```

**After:**
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'role': self.role,
        # password intentionally excluded
    }
```

Apply the same pattern to health check endpoints: remove `secret_key`, `db_path`, `debug` from any public response.

---

## PT-06 — N+1 Queries → JOIN or Eager Loading

**Addresses:** AP-09

### Python (raw sqlite3 → JOIN)

**Before:**
```python
cursor.execute("SELECT * FROM orders")
for row in rows:
    cursor2.execute("SELECT * FROM order_items WHERE order_id = " + str(row["id"]))
    for item in items:
        cursor3.execute("SELECT name FROM products WHERE id = " + str(item["product_id"]))
```

**After:**
```python
cursor.execute("""
    SELECT o.*, oi.product_id, oi.quantity, oi.unit_price, p.name as product_name
    FROM orders o
    LEFT JOIN order_items oi ON oi.order_id = o.id
    LEFT JOIN products p ON p.id = oi.product_id
""")
rows = cursor.fetchall()
# Group in Python
orders = {}
for row in rows:
    oid = row['id']
    if oid not in orders:
        orders[oid] = {...}  # order fields
    if row['product_id']:
        orders[oid]['items'].append({...})  # item fields
```

### Python (SQLAlchemy → joinedload)

**Before:**
```python
users = User.query.all()
for u in users:
    tasks = Task.query.filter_by(user_id=u.id).all()  # N extra queries
```

**After:**
```python
from sqlalchemy.orm import joinedload
users = User.query.options(joinedload(User.tasks)).all()
# tasks already loaded — no extra queries
```

### Node.js (sqlite3 → aggregate query)

**Before:**
```javascript
db.all("SELECT * FROM courses", [], (err, courses) => {
    courses.forEach(c => {
        db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], ...); // N queries
    });
});
```

**After:**
```javascript
db.all(`
    SELECT c.id, c.title, COUNT(e.id) as enrollment_count, SUM(p.amount) as revenue
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN payments p ON p.enrollment_id = e.id AND p.status = 'PAID'
    GROUP BY c.id
`, [], (err, rows) => { ... });
```

---

## PT-07 — Duplicated Validation → Centralized Validator

**Addresses:** AP-10

**Before:**
```python
# In create_task handler
if status not in ['pending', 'in_progress', 'done', 'cancelled']:
    return jsonify({'error': 'Status inválido'}), 400

# In update_task handler (copy-pasted)
if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
    return jsonify({'error': 'Status inválido'}), 400
```

**After:**
```python
# config.py or validators.py
VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200

def validate_task(data):
    errors = []
    if 'title' in data:
        if len(data['title']) < MIN_TITLE_LENGTH:
            errors.append('Título muito curto')
        if len(data['title']) > MAX_TITLE_LENGTH:
            errors.append('Título muito longo')
    if 'status' in data and data['status'] not in VALID_STATUSES:
        errors.append('Status inválido')
    return errors

# In both create and update handlers
errors = validate_task(data)
if errors:
    return jsonify({'error': errors[0]}), 400
```

---

## PT-08 — Deprecated `Query.get()` → `db.session.get()`

**Addresses:** AP-13 (Deprecated API)

This is a mechanical find-and-replace applicable to any Flask-SQLAlchemy ≥ 3.0 project.

**Before:**
```python
task = Task.query.get(task_id)
user = User.query.get(user_id)
category = Category.query.get(cat_id)
```

**After:**
```python
task = db.session.get(Task, task_id)
user = db.session.get(User, user_id)
category = db.session.get(Category, cat_id)
```

The behavior is identical for simple primary-key lookups. Returns `None` if not found (same as before). Import `db` from the database module wherever the replacement is made.

---

## PT-09 — print/console.log → Structured Logging

**Addresses:** AP-14

### Python

**Before:**
```python
print("Produto criado com ID: " + str(id))
print("ERRO ao criar produto: " + str(e))
print("ENVIANDO EMAIL: Pedido criado")  # fake side-effect
```

**After:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Produto criado: id={id}")
logger.error(f"Erro ao criar produto: {e}", exc_info=True)
# Fake side-effects replaced with real service calls or explicit TODOs:
# notification_service.send_order_confirmation(order_id, user_id)
```

Configure logging in the entry point:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
```

### Node.js

**Before:**
```javascript
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

**After:**
```javascript
// npm install pino
const logger = require('pino')();
logger.info({ courseId }, 'Processing checkout');
// Never log card numbers or secrets
```

---

## PT-10 — Callback Hell → async/await

**Addresses:** AP-06 (deeply nested callbacks in Node.js)

**Before:**
```javascript
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    db.get("SELECT id FROM users WHERE email = ?", [email], (err, user) => {
        db.run("INSERT INTO enrollments ...", [...], function(err) {
            db.run("INSERT INTO payments ...", [...], function(err) {
                res.json({ success: true });
            });
        });
    });
});
```

**After:**
```javascript
// Promisify sqlite3 (or use better-sqlite3 which is synchronous)
const { promisify } = require('util');
const dbGet = promisify(db.get.bind(db));
const dbRun = promisify(db.run.bind(db));

async function processCheckout(courseId, email) {
    const course = await dbGet("SELECT * FROM courses WHERE id = ?", [courseId]);
    if (!course) throw new Error('Course not found');

    const user = await dbGet("SELECT id FROM users WHERE email = ?", [email]);
    const userId = user ? user.id : await createUser(email);

    await dbRun("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, courseId]);
    await dbRun("INSERT INTO payments (amount, status) VALUES (?, ?)", [course.price, 'PAID']);
    return { success: true };
}
```

---

## PT-11 — In-Memory Database → Persistent Storage

**Addresses:** AP-12

**Before:**
```javascript
this.db = new sqlite3.Database(':memory:');
```

**After:**
```javascript
const path = require('path');
const dbPath = process.env.DATABASE_PATH || path.join(__dirname, '../data/app.db');
const db = new sqlite3.Database(dbPath);
```

Also create the `data/` directory and add it to `.gitignore` (the `.db` file) while committing the directory itself.

---

## Application Order for Phase 3

When refactoring a project, apply transformations in this sequence to avoid broken intermediate states:

1. **PT-02** — Extract config (secrets must be moved before anything else references them)
2. **PT-03** — Fix password hashing in the model
3. **PT-05** — Remove sensitive fields from serialization
4. **PT-08** — Replace deprecated API calls (mechanical, low risk)
5. **PT-01** — Fix SQL Injection (parameterize all queries)
6. **PT-04** — Split God Object into layers (biggest structural change)
7. **PT-06** — Fix N+1 queries (requires layers to be in place)
8. **PT-07** — Centralize validation (requires controllers to exist)
9. **PT-09** — Replace print/console.log with structured logging
10. **PT-10** — Convert callbacks to async/await (Node.js only, after restructuring)
11. **PT-11** — Replace in-memory DB (if detected)
