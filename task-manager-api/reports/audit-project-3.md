================================
ARCHITECTURE AUDIT REPORT
================================
Project:   task-manager-api
Stack:     Python + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1
Files:     11 analyzed | ~1160 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 3
Total findings: 12

## Findings

### [CRITICAL] Broken password hashing with MD5 — no salt
File:           models/user.py:27-32
Category:       Security
Description:    User passwords are hashed with MD5, a cryptographically broken
                algorithm that produces unsalted, reversible digests trivially
                crackable by rainbow-table lookup.
Evidence:
```python
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```
Impact:         A single DB dump exposes every user's password as a
                pre-image-reversible MD5 hash; rainbow tables crack common
                passwords in milliseconds.
Recommendation: Replace with werkzeug.security.generate_password_hash /
                check_password_hash (PT-03). Remove hashlib import from the model.

---

### [CRITICAL] Hardcoded credentials — SECRET_KEY and SMTP password in source
File:           app.py:13 · services/notification_service.py:9-10
Category:       Security
Description:    The Flask SECRET_KEY is a hardcoded literal in the entry point
                and the SMTP password is hardcoded in the notification service;
                python-dotenv is installed but load_dotenv() is never called.
Evidence:
```python
# app.py
app.config['SECRET_KEY'] = 'super-secret-key-123'

# services/notification_service.py
self.email_user    = 'taskmanager@gmail.com'
self.email_password = 'senha123'
```
Impact:         Any repository exposure (accidental public push, stolen laptop,
                CI log leak) instantly compromises session signing and the SMTP
                account. Secret rotation requires a code change and redeploy.
Recommendation: Create config.py with load_dotenv() and os.environ.get() for
                every secret (PT-02). Add .env to .gitignore. Provide .env.example.

---

### [CRITICAL] All destructive endpoints publicly accessible — no authentication
File:           routes/task_routes.py:225-238 · routes/user_routes.py:134-151
                routes/report_routes.py:211-223
Category:       Security
Description:    Every DELETE endpoint — including one that cascades deletion
                of a user plus all their tasks — is reachable without any
                authentication token, session check or middleware guard.
Evidence:
```python
# routes/user_routes.py:134-151
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    ...
    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)
    db.session.delete(user)
    db.session.commit()
```
Impact:         Any anonymous HTTP client can delete any user (and all their
                tasks) or any category by knowing only the integer ID. Data loss
                is irreversible.
Recommendation: Implement JWT authentication middleware (flask-jwt-extended) and
                protect all state-changing routes (POST/PUT/DELETE) with a
                @jwt_required() decorator before Phase 3 validation.

---

### [HIGH] Password hash exposed in every user API response
File:           models/user.py:16-25 · routes/user_routes.py:207-211
Category:       Security
Description:    User.to_dict() includes the password field, and that method is
                called in GET /users/<id> and the /login response — returning
                the raw password hash to every caller.
Evidence:
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'password': self.password,   # hash sent to client
        'role': self.role,
        ...
    }
```
Impact:         Any authenticated list call leaks every user's password hash,
                enabling offline cracking. The login response returns the hash
                of the just-authenticated user to the client unnecessarily.
Recommendation: Remove 'password' from to_dict(). Create a safe serialization
                method that excludes all secret fields (PT-05).

---

### [HIGH] Login returns a predictable, unsigned fake token
File:           routes/user_routes.py:207-211
Category:       Security
Description:    The /login endpoint generates a token by concatenating a static
                prefix with the user's integer ID; there is no signing, no
                expiry, and no verification anywhere in the codebase.
Evidence:
```python
return jsonify({
    'message': 'Login realizado com sucesso',
    'user': user.to_dict(),
    'token': 'fake-jwt-token-' + str(user.id)
}), 200
```
Impact:         Any attacker who knows a valid user ID (obtainable from GET
                /users) can forge a valid token for any account. The
                authentication system provides zero security.
Recommendation: Integrate flask-jwt-extended; generate signed tokens with
                expiry in /login and verify them in all protected routes (AP-08).

---

### [HIGH] Business logic (overdue calculation) duplicated across five handlers
File:           routes/task_routes.py:30-39,71-80,282-287
                routes/user_routes.py:171-180 · routes/report_routes.py:34-38
Category:       Architecture
Description:    The same overdue-detection block (compare due_date to utcnow,
                skip done/cancelled) is copy-pasted verbatim in five separate
                route handlers instead of being extracted to a service or model
                method.
Evidence:
```python
# routes/task_routes.py:30-39 — identical logic in 4 other files
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
        else:
            task_data['overdue'] = False
    else:
        task_data['overdue'] = False
else:
    task_data['overdue'] = False
```
Impact:         A rule change (e.g. treating 'cancelled' differently) requires
                editing five files; any missed copy causes silent inconsistency
                between endpoints.
Recommendation: Extract to Task.is_overdue() (already defined in the model but
                not used by routes) and call it from a service layer (PT-04/PT-07).

---

### [MEDIUM] N+1 query problem in GET /tasks and GET /reports/summary
File:           routes/task_routes.py:41-57 · routes/report_routes.py:54-68
Category:       Performance
Description:    For every task returned by Task.query.all(), two additional
                primary-key lookups are executed (User and Category); and for
                every user in the report, all their tasks are fetched individually.
Evidence:
```python
# routes/task_routes.py:41-57
for t in tasks:          # outer: 1 query for N tasks
    if t.user_id:
        user = User.query.get(t.user_id)         # +1 per task
    if t.category_id:
        cat = Category.query.get(t.category_id)  # +1 per task

# routes/report_routes.py:56
for u in users:
    user_tasks = Task.query.filter_by(user_id=u.id).all()  # +1 per user
```
Impact:         With 100 tasks each with a user and category, GET /tasks
                executes 201 queries. Under load this causes multi-second
                response times and connection pool exhaustion.
Recommendation: Use SQLAlchemy joinedload on the relationships already defined
                on Task, or add GROUP BY aggregate queries for counts (PT-06).

---

### [MEDIUM] Validation constants duplicated inline — never imported from utils
File:           routes/task_routes.py:110,177 · routes/user_routes.py:71,120
                utils/helpers.py:110-116
Category:       Quality
Description:    VALID_STATUSES, VALID_ROLES, MAX_TITLE_LENGTH constants are
                defined in utils/helpers.py but the route files redefine the same
                lists inline instead of importing from helpers.
Evidence:
```python
# utils/helpers.py:110 — authoritative definition (never imported by routes)
VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']

# routes/task_routes.py:110 — redefined inline in create_task
if status not in ['pending', 'in_progress', 'done', 'cancelled']:

# routes/task_routes.py:177 — redefined again in update_task
if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
```
Impact:         Adding a new status value requires editing at least 4 locations;
                create and update handlers can diverge, accepting different values.
Recommendation: Import VALID_STATUSES from utils.helpers (or a new validators
                module) and use it in both handlers (PT-07).

---

### [MEDIUM] Global mutable in-memory notification list in NotificationService
File:           services/notification_service.py:5-6
Category:       Architecture
Description:    NotificationService stores all notifications in a plain instance
                list (self.notifications = []) that grows unbounded and is never
                persisted; if the service is instantiated once at module level
                it behaves as shared global state across requests.
Evidence:
```python
class NotificationService:
    def __init__(self):
        self.notifications = []   # grows forever, lost on restart
        self.email_host    = 'smtp.gmail.com'
```
Impact:         Memory grows linearly with every task assignment. All notification
                history is lost on process restart; under concurrent requests
                the list is written without synchronization.
Recommendation: Replace the in-memory list with a DB-backed Notification model,
                or use Flask's application context (flask.g) for per-request
                state (AP-11).

---

### [LOW] Deprecated SQLAlchemy Query.get() used throughout codebase
File:           routes/task_routes.py:67,117,158,188,195
                routes/user_routes.py:29,94,155 · routes/report_routes.py:105
Category:       Deprecated API
Description:    Model.query.get(id) is deprecated since SQLAlchemy 2.0
                (used via Flask-SQLAlchemy 3.1.1) and scheduled for removal.
Evidence:
```python
task  = Task.query.get(task_id)        # task_routes.py:67
user  = User.query.get(user_id)        # user_routes.py:29
cat   = Category.query.get(cat_id)     # report_routes.py:192
```
Impact:         Deprecation warnings flood logs now; when the method is removed
                in a future SQLAlchemy release, all lookups silently break.
Recommendation: Replace every occurrence with db.session.get(Model, id) — a
                mechanical find-and-replace (PT-08).

---

### [LOW] Unstructured print() logging across route handlers and services
File:           routes/task_routes.py:149,153,219,234
                routes/user_routes.py:83,89,147 · services/notification_service.py:21,24
Category:       Quality
Description:    Operational events (entity created/deleted, errors) and fake
                email-send confirmations are written with print() — no log
                level, no timestamp, no structured fields.
Evidence:
```python
print(f"Task criada: {task.id} - {task.title}")   # task_routes.py:149
print(f"Erro ao criar task: {str(e)}")             # task_routes.py:153
print(f"Email enviado para {to}")                  # notification_service.py:21
```
Impact:         No filtering by severity in production. Log aggregation tools
                cannot parse unstructured output. Fake email prints mask
                unimplemented integrations from monitoring.
Recommendation: Replace all print() with logging.getLogger(__name__) calls;
                configure basicConfig in the entry point (PT-09).

---

### [LOW] Unused imports in route files and utils
File:           routes/task_routes.py:7 · routes/user_routes.py:6
                utils/helpers.py:3-7
Category:       Quality
Description:    Multiple modules are imported at the top of source files but
                never referenced in the file body.
Evidence:
```python
# routes/task_routes.py:7
import json, os, sys, time   # none used in any handler

# routes/user_routes.py:6
import hashlib, json, re     # hashlib and json unused in this file

# utils/helpers.py:3-7
import os, json, sys, math   # math unused; os/json/sys not used in helpers
```
Impact:         Misleads readers about file dependencies; may trigger ImportError
                in minimal deployment environments where optional packages are absent.
Recommendation: Remove all unused imports; enforce with ruff or flake8 (AP-15).

================================
Total: 12 findings
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 3
================================
