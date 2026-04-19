================================
ARCHITECTURE AUDIT REPORT
================================
Project:   code-smells-project
Stack:     Python + Flask 3.1.1 (raw sqlite3, no ORM)
Files:     4 analyzed | ~530 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2
Total findings: 12

## Findings

### [CRITICAL] SQL Injection via String Concatenation — Multiple Vectors
File:           models.py:28, 47-50, 57-62, 68, 92, 109-111, 127-131, 140, 149-151, 155, 163-165, 174, 188-189, 192-193, 280-282, 289-296
Category:       Security
Description:    Every SQL query in models.py is constructed by string concatenation of
                user-supplied values directly into the query string — no parameterized
                placeholders are used anywhere.
Evidence:
```python
# models.py:28 — product lookup
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

# models.py:109–111 — authentication
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)

# models.py:289–296 — dynamic search (all filters injected)
query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
if categoria:
    query += " AND categoria = '" + categoria + "'"
```
Impact:         Full authentication bypass (login with `' OR '1'='1`), complete database
                exfiltration, arbitrary data modification, and table dropping — all
                exploitable without credentials via public endpoints.
Recommendation: Replace every concatenated SQL string with parameterized queries using `?`
                placeholders (PT-01). E.g.:
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

---

### [CRITICAL] Hardcoded Secrets and Plaintext Seed Credentials
File:           app.py:7 | database.py:5, 76-83
Category:       Security
Description:    The Flask SECRET_KEY is hardcoded as a string literal in the entry point,
                the SQLite file path is a hardcoded module-level string, and seed user
                records are inserted with plaintext passwords directly in source code.
Evidence:
```python
# app.py:7
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"

# database.py:5
db_path = "loja.db"

# database.py:76-79
usuarios = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]
```
Impact:         Any repository access (including accidental public exposure) immediately
                reveals the signing key for all sessions. Seed credentials are a
                pre-known backdoor in every deployed instance.
Recommendation: Move all secrets to a `.env` file loaded via `python-dotenv`. Reference via
                `os.environ.get('SECRET_KEY')` (PT-02). Add `.env` to `.gitignore`. Replace
                seed passwords with hashed values (PT-03).

---

### [CRITICAL] Plaintext Password Storage and Comparison
File:           models.py:105-131 | database.py:76-83
Category:       Security
Description:    User passwords are stored as plaintext strings with no hashing — the
                `criar_usuario` function inserts the raw `senha` value into the database,
                and `login_usuario` compares it in plaintext via SQL.
Evidence:
```python
# models.py:126-131 — stores raw password
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" +
    nome + "', '" + email + "', '" + senha + "', '" + tipo + "')"
)

# models.py:83-86 — returns password in user dict
return {
    "id": row["id"], "nome": row["nome"],
    "email": row["email"], "senha": row["senha"], ...
}
```
Impact:         Any database dump immediately exposes every user's password in cleartext.
                There is no import of bcrypt, werkzeug.security, or any hashing library
                in the entire codebase.
Recommendation: Use `werkzeug.security.generate_password_hash` on registration and
                `check_password_hash` on login (PT-03). Update requirements.txt to
                include `werkzeug`.

---

### [CRITICAL] Unauthenticated Destructive Admin Endpoints
File:           app.py:47-78
Category:       Security
Description:    Two endpoints — `/admin/reset-db` (bulk-deletes all tables) and
                `/admin/query` (executes arbitrary user-supplied SQL) — are publicly
                accessible with no authentication or authorization check.
Evidence:
```python
# app.py:47-57 — no auth, deletes entire database
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")

# app.py:59-69 — executes raw SQL from request body, no auth
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = dados.get("sql", "")
    cursor.execute(query)
```
Impact:         Any HTTP client can wipe the entire database or execute arbitrary SQL
                (DROP TABLE, INSERT of admin accounts, SELECT of all passwords) with a
                single unauthenticated POST request.
Recommendation: Protect both endpoints with an authentication middleware/decorator that
                validates a token or session. For reset-db, add an environment gate:
                `if os.getenv('FLASK_ENV') != 'development': abort(403)` (PT-04/AP-05).

---

### [HIGH] Business Logic Embedded in the Data-Access Layer
File:           models.py:133-169, 235-273
Category:       Architecture
Description:    `criar_pedido` performs inventory validation, total calculation, stock
                reservation, and multi-table inserts all within a single model function;
                `relatorio_vendas` hardcodes discount tier business rules inside a raw
                SQL data-access function.
Evidence:
```python
# models.py:139-146 — stock validation inside model
for item in itens:
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
    produto = cursor.fetchone()
    if produto is None:
        return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
    if produto["estoque"] < item["quantidade"]:
        return {"erro": "Estoque insuficiente para " + produto["nome"]}

# models.py:256-260 — discount tiers in data layer
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
```
Impact:         Business rules cannot be unit-tested without a database connection. Any
                change to discount tiers or order validation requires editing the same
                file that owns raw SQL. Model functions returning error dicts mix
                presentation concerns into the data layer.
Recommendation: Extract `criar_pedido` and `relatorio_vendas` logic into a
                `services/order_service.py` module (PT-04). Models should only perform
                database reads/writes; services own business rules.

---

### [HIGH] Sensitive Fields Exposed in API Responses
File:           models.py:79-87, 93-103 | controllers.py:276-290
Category:       Security
Description:    `get_todos_usuarios` and `get_usuario_por_id` include the `senha` field in
                their returned dicts; the `/health` endpoint returns `secret_key`,
                `db_path`, and `debug` in its JSON response body.
Evidence:
```python
# models.py:79-87 — password in user list response
result.append({
    "id": row["id"], "nome": row["nome"],
    "email": row["email"], "senha": row["senha"],
    "tipo": row["tipo"], "criado_em": row["criado_em"]
})

# controllers.py:284-289 — secrets in health check
"ambiente": "producao",
"db_path": "loja.db",
"debug": True,
"secret_key": "minha-chave-super-secreta-123"
```
Impact:         Password hashes (or plaintext passwords, given AP-03) are returned via
                `GET /usuarios`. The health endpoint broadcasts the Flask signing key to
                any client that calls it, enabling session forgery.
Recommendation: Remove `senha` from all serialization methods. Create explicit allowlists
                for public fields (PT-05). Remove all config fields from health-check
                responses.

---

### [HIGH] Login Returns User Data with No Authentication Token
File:           controllers.py:167-186
Category:       Security
Description:    The login endpoint authenticates the user but returns only the user object
                with no signed token, leaving the client with no verifiable credential.
                No JWT or session library is present in requirements.txt.
Evidence:
```python
# controllers.py:176-183
usuario = models.login_usuario(email, senha)
if usuario:
    print("Login bem-sucedido: " + email)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
else:
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
```
Impact:         There is no token to verify on subsequent requests, making it impossible
                to enforce authorization anywhere in the API. Any client can call any
                endpoint freely since no endpoint checks identity after login.
Recommendation: Integrate `flask-jwt-extended`. Generate a signed JWT on login and add
                a `@jwt_required()` decorator to all protected endpoints (PT-04/AP-08).

---

### [MEDIUM] N+1 Query Problem in Order Listing Functions
File:           models.py:171-233
Category:       Performance
Description:    Both `get_pedidos_usuario` and `get_todos_pedidos` execute nested queries
                inside loops: one SELECT per order to fetch its items, then one SELECT per
                item to resolve the product name — three cursor levels deep.
Evidence:
```python
# models.py:186-198 — three nested query levels
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
    prod = cursor3.fetchone()
    pedido["itens"].append({...})
```
Impact:         With N orders each having M items, the endpoint executes 1 + N + N*M
                queries. 50 orders × 3 items = 151 queries per request. Response time
                degrades linearly and causes timeouts under load.
Recommendation: Replace with a JOIN query that fetches orders, items, and product names
                in a single roundtrip (PT-06):
                SELECT p.*, ip.*, prod.nome FROM pedidos p
                JOIN itens_pedido ip ON ip.pedido_id = p.id
                JOIN produtos prod ON prod.id = ip.produto_id

---

### [MEDIUM] Duplicated Validation Constants Across Handlers
File:           controllers.py:52-54, 242-243
Category:       Quality
Description:    The `categorias_validas` list is defined only inside `criar_produto` and
                never reused in `atualizar_produto`; the valid-status list is defined only
                inside `atualizar_status_pedido` with no shared constant.
Evidence:
```python
# controllers.py:52-54 — inline in criar_produto only
categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
if categoria not in categorias_validas:
    return jsonify({"erro": "Categoria inválida..."}), 400

# controllers.py:242-243 — inline in atualizar_status_pedido
if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
    return jsonify({"erro": "Status inválido"}), 400
```
Impact:         Updating a category or status value requires finding and editing multiple
                locations. `atualizar_produto` currently performs no category validation,
                silently accepting invalid categories on update.
Recommendation: Extract constants to a `config.py` or `validators.py` module (PT-07).
                Import `CATEGORIAS_VALIDAS` and `STATUS_VALIDOS` in all handlers that
                need them.

---

### [MEDIUM] Global Mutable Database Connection
File:           database.py:4-10
Category:       Architecture
Description:    The database connection is stored in a module-level mutable variable
                `db_connection` and shared across all requests via `global db_connection`,
                with no thread-safety mechanism.
Evidence:
```python
# database.py:4-10
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
```
Impact:         Under concurrent requests, multiple threads share one connection object.
                `check_same_thread=False` suppresses the error but does not add locking —
                concurrent writes can corrupt transactions or return stale data.
Recommendation: Use Flask's `g` object for per-request connection management, or use
                SQLAlchemy's connection pool (PT-04). At minimum, add thread locking
                around connection creation.

---

### [LOW] Unstructured Logging via print() Throughout Codebase
File:           controllers.py:8, 11, 57, 106, 161, 179, 182, 208-210, 219, 248-250 | app.py:56, 83-86
Category:       Quality
Description:    All application events, errors and simulated side-effects are written via
                `print()` with no log levels, timestamps, or structured format. Three
                `print()` calls simulate email/SMS/push notifications as if they were
                real integrations.
Evidence:
```python
# controllers.py:208-210 — fake integrations masquerading as log lines
print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))
print("ENVIANDO SMS: Seu pedido foi recebido!")
print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")

# controllers.py:11
print("ERRO: " + str(e))
```
Impact:         Cannot filter by severity in production. No timestamps or structured
                fields. Fake notification stubs are invisible to monitoring systems and
                mislead maintainers into thinking integrations are implemented.
Recommendation: Replace all `print()` with `logging.getLogger(__name__)` calls using
                `logger.info()` / `logger.error()` (PT-09). Mark notification stubs as
                explicit TODOs or extract to a stub service module.

---

### [LOW] Unused Import in models.py
File:           models.py:2
Category:       Quality
Description:    `import sqlite3` is declared at the top of models.py but the module never
                calls any `sqlite3` symbol directly — all database access goes through
                `get_db()` imported from database.py.
Evidence:
```python
# models.py:1-2
from database import get_db
import sqlite3
```
Impact:         Misleads readers into thinking models.py manages its own connections.
                Increases coupling surface and will cause an ImportError if sqlite3 is
                ever not available in the environment.
Recommendation: Remove the `import sqlite3` line from models.py (PT-N/A — linter fix).
                Use `ruff` or `flake8` to catch unused imports automatically.

================================
Total: 12 findings
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2
================================
