# Analysis Heuristics — Stack, Architecture & Domain Detection

Use this document in Phase 1 to detect the project's stack, architecture and domain before any audit or refactoring.

---

## 1. Language Detection

| Signal | Language |
|--------|----------|
| File `requirements.txt` exists at root | Python |
| File `package.json` exists at root | Node.js |
| Files with extension `.py` | Python |
| Files with extension `.js` or `.ts` | JavaScript / TypeScript |
| File `Pipfile` or `pyproject.toml` | Python |
| File `yarn.lock` or `pnpm-lock.yaml` | Node.js |

**Action:** Run `Glob` for `requirements.txt`, `package.json`, `*.py`, `*.js` at project root to confirm.

---

## 2. Framework Detection

### Python
| Signal | Framework |
|--------|-----------|
| `from flask import` or `import flask` in any `.py` file | Flask |
| `from fastapi import` | FastAPI |
| `from django` | Django |
| `flask==` in `requirements.txt` | Flask (version confirmed) |
| `fastapi==` in `requirements.txt` | FastAPI |

### Node.js
| Signal | Framework |
|--------|-----------|
| `require('express')` or `import express` | Express |
| `"express":` in `package.json` dependencies | Express |
| `require('fastify')` | Fastify |
| `require('koa')` | Koa |

**Action:** `Grep` for `from flask import`, `require('express')`, `import express` across source files.

---

## 3. Database Detection

| Signal | Database / Access Pattern |
|--------|--------------------------|
| `import sqlite3` | Raw SQLite (Python) |
| `sqlite3.connect(` | Raw SQLite connection (Python) |
| `from flask_sqlalchemy import` or `from database import db` | SQLAlchemy ORM (Python) |
| `require('sqlite3')` | Raw SQLite (Node.js) |
| `new Database(':memory:')` | In-memory SQLite — data lost on restart |
| `require('pg')` or `require('mysql2')` | PostgreSQL / MySQL (Node.js) |
| `SQLALCHEMY_DATABASE_URI` in config | SQLAlchemy with configured DB |
| `.db` files at project root | SQLite file-based database |
| `CREATE TABLE` statements in source code | Schema defined in application code (no migrations) |

---

## 4. Architecture Pattern Detection

Inspect the directory structure and file contents to classify the current architecture:

### 4.1 Flat Monolith (no separation)
**Signals:**
- All source files at root level (no subdirectories for routes, models, controllers)
- Single file contains route definitions AND database queries AND business logic
- `Glob` returns only 3–6 files with no nested structure

### 4.2 Pseudo-MVC (named layers, not enforced)
**Signals:**
- Files named `models.py`, `controllers.py`, `routes.py` exist but in the same directory
- Models contain business logic (multi-step operations, validation rules)
- Controllers contain direct database access (`cursor.execute`, `db.session.query`)

### 4.3 God Object
**Signals:**
- A single class (e.g., `AppManager`, `Server`, `App`) contains methods for routing (`setupRoutes`), database operations, and business logic
- `Grep` for `class \w+` in a single file that also contains `app.get(`, `app.post(`, `db.run(`, `db.get(`

### 4.4 Partial MVC (organized but incomplete)
**Signals:**
- Separate directories exist: `routes/`, `models/`, `services/`, `utils/`
- Blueprints or Router objects registered in entry point
- Models use ORM (SQLAlchemy, Sequelize) but still contain validation logic
- Utility functions defined but not used by routes (duplicated inline instead)

---

## 5. Entry Point Detection

| Signal | Entry Point |
|--------|-------------|
| `app.run(` in a `.py` file | That file is the Flask entry point |
| `"main": "src/app.js"` in `package.json` | `src/app.js` |
| `app.listen(` in a `.js` file | That file is the Express entry point |
| `if __name__ == '__main__':` in a `.py` file | That file is the Python entry point |
| `app = Flask(__name__)` | Flask application factory |

**Action:** `Grep` for `app.run(`, `app.listen(`, `if __name__ == '__main__':` to locate the entry point.

---

## 6. Domain Inference

Infer the business domain from table names, route paths, and model/class names:

| Observed names | Inferred domain |
|----------------|-----------------|
| `produtos`, `pedidos`, `itens_pedido`, `usuarios` | E-commerce |
| `courses`, `enrollments`, `payments`, `users` | LMS / EdTech |
| `tasks`, `categories`, `users`, `reports` | Task management / Productivity |
| `posts`, `comments`, `tags` | Blog / CMS |
| `orders`, `customers`, `invoices` | ERP / Finance |
| `appointments`, `patients`, `doctors` | Healthcare |

**How to detect:** `Grep` for `CREATE TABLE`, `__tablename__`, `db.Model` to extract table names. `Grep` for `@app.route`, `app.get(`, `app.post(` to extract route paths.

---

## 7. Dependency & Configuration Analysis

### Check for security-relevant dependencies
| Dependency present | Implication |
|-------------------|-------------|
| `bcrypt`, `argon2-cffi`, `passlib` in `requirements.txt` | Secure password hashing available |
| `flask-jwt-extended`, `PyJWT` | JWT authentication available |
| `python-dotenv` in `requirements.txt` but no `load_dotenv()` in entry point | Env config installed but not wired |
| No `bcrypt`-equivalent in deps | Passwords likely stored insecurely |
| No auth library in deps | Authentication likely absent or fake |

### Check for hardcoded configuration
`Grep` for these patterns to find hardcoded secrets:
- Python: `SECRET_KEY\s*=\s*['"]`, `password\s*=\s*['"]`, `= "pk_live_`, `= "sk_live_`
- Node.js: `dbPass:`, `paymentGatewayKey:`, `smtpPassword:` as string literals in source files

---

## 8. Phase 1 Output Format

After completing detection, print the following summary before proceeding to Phase 2:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:       <Python | Node.js>
Framework:      <Flask x.x | Express x.x>
Dependencies:   <comma-separated key libs>
Domain:         <inferred domain description>
Architecture:   <Flat Monolith | God Object | Pseudo-MVC | Partial MVC>
Entry point:    <path/to/entrypoint>
Source files:   <N files analyzed>
DB tables:      <comma-separated table names>
================================
```
