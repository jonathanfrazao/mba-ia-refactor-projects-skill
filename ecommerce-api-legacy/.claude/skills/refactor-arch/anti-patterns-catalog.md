# Anti-Patterns Catalog

Reference for Phase 2. For each finding, record: name, severity, file, exact lines, description, evidence, impact and recommendation.

Severities: **CRITICAL** · **HIGH** · **MEDIUM** · **LOW**

---

## AP-01 · [CRITICAL] SQL Injection via String Concatenation

**Description:** SQL queries are built by concatenating or interpolating user-supplied values directly into the query string instead of using parameterized placeholders.

**Detectable signals:**
- Python: `cursor.execute("... " + variable)`, `cursor.execute(f"... {variable}")`, `cursor.execute("... '%s'" % value)`
- Node.js: `` db.run(`SELECT ... WHERE id = ${req.params.id}`) `` (template literal inside SQL)
- Dynamic query construction: `query = "SELECT ... WHERE 1=1"` followed by `query += " AND col = '" + value + "'"`
- Any `cursor.execute(` or `db.run(` / `db.get(` / `db.all(` where the first argument is not a pure string literal with `?` or `$1` placeholders

**Impact:** Complete database compromise. An attacker can bypass authentication (login bypass), extract all data, modify records, or drop tables. OWASP Top 1 since 2010.

**Recommendation:** Replace all string concatenation with parameterized queries. Pass values as a tuple/array in the second argument of the execute call.

---

## AP-02 · [CRITICAL] Hardcoded Credentials / Secrets

**Description:** Sensitive values (passwords, API keys, secret keys, SMTP credentials, payment gateway keys) are written as string literals directly in source files instead of being loaded from environment variables.

**Detectable signals:**
- Python: `SECRET_KEY = "..."`, `password = "literal"`, `api_key = "sk_live_..."` assigned to a variable outside `os.environ.get()`
- Node.js: object literals with keys `dbPass`, `dbUser`, `paymentGatewayKey`, `smtpPassword`, `apiSecret` assigned to string values
- Any `pk_live_`, `sk_live_`, `Bearer ` prefix as a hardcoded string
- Seed/fixture data with plaintext passwords like `"admin123"`, `"senha123"`, `"123456"`
- `python-dotenv` present in `requirements.txt` but `load_dotenv()` absent from the entry point

**Impact:** Any repository access (including accidental public exposure) compromises production systems, payment processors and user accounts.

**Recommendation:** Move all secrets to a `.env` file loaded at startup. Reference via `os.environ.get('KEY')` (Python) or `process.env.KEY` (Node.js). Add `.env` to `.gitignore`.

---

## AP-03 · [CRITICAL] Plaintext or Broken Password Storage

**Description:** User passwords are stored without a proper cryptographic hash, or with a broken algorithm that provides no real protection.

**Detectable signals:**
- Plaintext: password field inserted directly from user input (`VALUES (... '" + senha + "' ...)` or `user.password = data['password']` without calling a hash function)
- Broken hash: `hashlib.md5(pwd.encode()).hexdigest()` — MD5 is cryptographically broken and has no salt
- Broken hash: `hashlib.sha1(pwd.encode()).hexdigest()` — SHA-1 is similarly broken for password storage
- Custom encoding: base64 encoding presented as a hash (base64 is reversible, not a hash)
- No import of `bcrypt`, `argon2`, `passlib`, or `werkzeug.security` anywhere in the codebase
- Seed data with readable passwords (`"admin123"`, `"password"`, `"123456"`) stored directly in the DB

**Impact:** Any database dump immediately exposes all user passwords. With MD5/SHA-1, rainbow table attacks crack most passwords in seconds.

**Recommendation:** Use `werkzeug.security.generate_password_hash` (Flask) or `bcrypt` with cost factor ≥ 12. Never store plaintext or reversible encodings.

---

## AP-04 · [CRITICAL] God Object — Absent Separation of Concerns

**Description:** A single class or file is responsible for HTTP routing, database access, business logic, authentication, external service calls and configuration — all at once.

**Detectable signals:**
- A class with a method named `setupRoutes` (or similar) that also contains `db.run(`, `db.get(`, `db.all(` calls
- A single file where `Grep` finds: route definitions (`app.get(`, `app.post(`, `@app.route`) AND raw SQL (`cursor.execute(`, `db.run(`) AND business logic conditionals (`if payment.status === 'PAID'`, `if stock < quantity`)
- No `routes/`, `controllers/`, `services/` directories — all logic in 1–3 files
- A model function that returns `{"erro": "..."}` dictionaries (business error handling leaking into the data layer)

**Impact:** Impossible to test any component in isolation. Any change to business logic requires modifying the same file that handles HTTP concerns. Violates SRP, OCP and all MVC principles.

**Recommendation:** Split into dedicated layers: routes (HTTP only), controllers/services (business logic), repositories/models (data access), config (environment).

---

## AP-05 · [CRITICAL] Unauthenticated Destructive Endpoint

**Description:** An endpoint that performs irreversible destructive operations (bulk delete, arbitrary SQL execution, database reset) is publicly accessible with no authentication or authorization check.

**Detectable signals:**
- Route path contains `admin`, `reset`, `query`, `exec`, `drop`, `truncate` but has no auth decorator or middleware before the handler
- Handler body contains `DELETE FROM` applied to multiple tables, or `cursor.execute(query)` where `query` comes from `request.get_json()`
- No import of any auth library (`flask_jwt_extended`, `functools` wraps, middleware functions) in the file defining the route

**Impact:** Any HTTP client can wipe the entire database or execute arbitrary SQL, causing irreversible data loss and full system compromise.

**Recommendation:** Protect with authentication middleware/decorator. For development-only utilities, add an environment flag check (`if os.getenv('ENV') != 'development': abort(403)`) and remove entirely in production builds.

---

## AP-06 · [HIGH] Business Logic Outside the Service Layer

**Description:** Complex business rules, multi-step operations, and domain validations are implemented inside route handlers or model/data-access functions instead of a dedicated service or use-case layer.

**Detectable signals:**
- A model function (in `models.py` or a class method) that: loops over items, checks inventory, calculates totals, inserts into multiple tables and returns a business error dict — all in one function
- A route handler with more than ~15 lines of non-HTTP logic (no `request.`, no `jsonify(`, no `return`) inside a `try` block
- Business rules hardcoded inside route handlers: discount tiers, approval conditions, stock reservation logic
- Payment approval decided by a data property: `if card_number.startswith("4")` inside a route handler

**Impact:** Business rules cannot be tested without an HTTP request. Rules are scattered and duplicated. Changes require touching presentation and data layers simultaneously.

**Recommendation:** Extract complex operations into a service module (e.g., `services/order_service.py`, `services/payment_service.js`). Route handlers should only parse input, call the service and return the response.

---

## AP-07 · [HIGH] Sensitive Data Exposed in API Response

**Description:** A serialization method or response builder includes fields that should never leave the server, such as password hashes, internal tokens, database paths, or runtime configuration.

**Detectable signals:**
- `to_dict()` or equivalent method that includes `'password'`, `'secret_key'`, `'api_key'`, `'db_path'` as keys
- A health-check or status endpoint that returns `{"secret_key": ..., "debug": true, "db_path": ...}` in its JSON response
- Response object built from `dict(row)` on a table row without field filtering (exposes all columns including `password`)

**Impact:** Password hashes returned in API responses can be attacked offline. Secret keys exposed in health checks compromise the entire session/signature mechanism.

**Recommendation:** Create a `to_public_dict()` method that explicitly lists allowed fields. Never include `password`, `secret`, `key`, or internal config in responses.

---

## AP-08 · [HIGH] Fake or Predictable Authentication Token

**Description:** The login endpoint generates a token by string concatenation or a trivially predictable formula instead of using a cryptographically signed JWT or session mechanism.

**Detectable signals:**
- `token = 'fake-jwt-token-' + str(user.id)` or any token built with `+` operator
- No import of `jwt`, `flask_jwt_extended`, `PyJWT`, `jsonwebtoken`, or similar in the auth route file
- The generated token is never verified in any other endpoint (no `Grep` match for a token validation call)

**Impact:** Any attacker who knows a valid user ID can forge a token for that user. The authentication system provides no actual security.

**Recommendation:** Use `flask-jwt-extended` (Python) or `jsonwebtoken` (Node.js) to generate signed tokens with expiry. Protect all state-changing endpoints with a token verification decorator/middleware.

---

## AP-09 · [MEDIUM] N+1 Query Problem

**Description:** For each record returned by an initial query, one or more additional queries are executed inside a loop, causing the total number of database roundtrips to grow linearly with the result set size.

**Detectable signals:**
- Python: `cursor.execute(...)` or `Model.query.filter_by(...).all()` inside a `for row in rows:` loop
- Node.js: `db.get(` or `db.all(` call inside a `.forEach(` or nested callback that fires once per item from an outer query
- Three or more nested cursor objects (`cursor`, `cursor2`, `cursor3`) within the same function
- `SELECT ... FROM related_table WHERE foreign_key = ` constructed inside a loop

**Impact:** With N records and M related items each, the endpoint executes `1 + N + N*M` queries. A list of 100 orders with 3 items each = 401 queries. Performance degrades linearly and causes timeouts under load.

**Recommendation:** Use SQL JOINs to fetch related data in a single query, or use ORM eager loading (`joinedload`, `subqueryload` in SQLAlchemy). For aggregations, use `GROUP BY` + `COUNT` instead of Python/JS loops.

---

## AP-10 · [MEDIUM] Duplicated Validation / Business Rules

**Description:** The same validation constraints (allowed status values, length limits, regex patterns, allowed roles) are copied verbatim across multiple route handlers instead of being centralized in a single function or constant.

**Detectable signals:**
- The same list literal appears in multiple functions: `['pending', 'in_progress', 'done', 'cancelled']` defined inline in both `create_task` and `update_task`
- The same regex pattern (e.g., email validation) copy-pasted in two or more route handlers
- Identical `if len(field) < N or len(field) > M` checks in multiple functions
- Constants defined in a utility module (`VALID_STATUSES`, `MAX_TITLE_LENGTH`) but redefined inline in route files instead of imported

**Impact:** When a rule changes (e.g., adding a new status value), it must be updated in multiple locations. Divergence between handlers causes inconsistent behavior on create vs. update.

**Recommendation:** Extract all validation constants to a shared config or schema file. Create a single `validate_<entity>(data)` function used by all handlers for that entity.

---

## AP-11 · [MEDIUM] Global Mutable State

**Description:** Application state (cache, counters, DB connection) is stored in a module-level mutable variable shared across all requests, with no synchronization, TTL, or isolation.

**Detectable signals:**
- Python: `db_connection = None` at module level, modified via `global db_connection`
- Node.js: `let globalCache = {}` at module level, written to directly in request handlers
- A variable named `cache`, `store`, `state`, `session_store` that is a plain dict/object updated without locks
- `totalRevenue = 0` declared at module level but incremented inside request handlers

**Impact:** Under concurrent requests, writes from different requests interleave without ordering guarantees. In-process cache grows unbounded (no eviction). Module-level DB connections can corrupt transactions.

**Recommendation:** Use `flask.g` for per-request state (Python), or a dedicated cache store (Redis) with TTL for shared caching. Database connections should use a connection pool (SQLAlchemy, `pg.Pool`).

---

## AP-12 · [MEDIUM] In-Memory Database in Production Context

**Description:** The database is created entirely in memory, meaning all data is destroyed when the process restarts.

**Detectable signals:**
- Node.js: `new sqlite3.Database(':memory:')`
- Python: `sqlite3.connect(':memory:')`
- No persistent `.db` file path configured or referenced

**Impact:** Any deployment, crash or restart wipes all users, orders, payments and sessions. The system has zero data durability and cannot be used in production.

**Recommendation:** Replace `:memory:` with a file path (`./data/app.db`) or migrate to a persistent database (PostgreSQL, MySQL). Use environment variable to configure the path.

---

## AP-13 · [LOW] Deprecated API Usage (SQLAlchemy `Query.get()`)

**Description:** The `Model.query.get(id)` pattern is deprecated since SQLAlchemy 2.0 and will be removed in a future version. It was replaced by `db.session.get(Model, id)`.

**Detectable signals:**
- `Task.query.get(task_id)` — any `<Model>.query.get(` call pattern in a Flask-SQLAlchemy project
- `User.query.get(user_id)`, `Category.query.get(cat_id)` — any variant with different model names
- Flask-SQLAlchemy version `>= 3.0` in `requirements.txt` (uses SQLAlchemy 2.x underneath)

**Impact:** Deprecation warnings in logs. When SQLAlchemy removes the method, the application crashes silently on record lookup. Silent breakage risk during dependency upgrades.

**Recommendation:** Replace `Model.query.get(id)` with `db.session.get(Model, id)` throughout the codebase.

---

## AP-14 · [LOW] Unstructured Logging via print/console.log

**Description:** Application events, errors and debug information are written via `print()` (Python) or `console.log()` (Node.js) without log levels, structured format or configurable output.

**Detectable signals:**
- Python: `print("ERRO: " + str(e))`, `print("Produto criado: " + str(id))` inside route handlers or model functions
- Node.js: `console.log(` inside request handlers for operational events (not just development traces)
- Log messages that simulate integrations: `print("ENVIANDO EMAIL: ...")`, `print("ENVIANDO SMS: ...")` — these are fake side-effects hidden as log lines

**Impact:** Cannot filter by log level in production. No timestamps or structured fields. Fake integration calls (email, SMS, push) hidden as print statements are invisible to monitoring systems.

**Recommendation:** Python: use `import logging; logger = logging.getLogger(__name__)` with `logger.info()`, `logger.error()`. Node.js: use `pino` or `winston`. Fake integration stubs should be replaced with real service calls or clearly marked as TODOs in a stub module.

---

## AP-15 · [LOW] Unused Imports

**Description:** Modules are imported at the top of a file but never referenced in the file's body.

**Detectable signals:**
- Python: `import json, os, sys, time` at top of a route file where none of these names appear in the function bodies
- Python: `import math` imported but no `math.` call found
- Node.js: `const { unused } = require('./module')` where `unused` is never referenced

**Impact:** Increases startup time, misleads readers about the file's dependencies, and may cause import errors in environments where the unused package is not installed.

**Recommendation:** Remove all unused imports. Use a linter (`flake8`, `ruff` for Python; `eslint` for Node.js) to detect them automatically.
