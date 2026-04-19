================================
ARCHITECTURE AUDIT REPORT
================================
Project:   ecommerce-api-legacy
Stack:     Node.js + Express 4.18.2
Files:     3 analyzed | ~181 lines of code

## Summary
CRITICAL: 4 | HIGH: 2 | MEDIUM: 3 | LOW: 2
Total findings: 11

## Findings

### [CRITICAL] Hardcoded Production Credentials in Source File
File:           src/utils.js:1-7
Category:       Security
Description:    Database password, live payment gateway key, and SMTP credentials are
                assigned as string literals directly in source code instead of being
                loaded from environment variables.
Evidence:
```js
const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br",
    port: 3000
};
```
Impact:         Any repository access (including accidental public exposure) immediately
                compromises the payment gateway account, SMTP service, and database.
                The live key prefix `pk_live_` confirms these are production credentials.
Recommendation: Move all secrets to a `.env` file loaded via `dotenv`. Reference via
                `process.env.PAYMENT_GATEWAY_KEY` etc. Add `.env` to `.gitignore`.
                Create `.env.example` with placeholder values. Apply PT-02.

### [CRITICAL] Broken Password Storage via Custom Base64 "Hash"
File:           src/utils.js:17-23
Category:       Security
Description:    Passwords are processed by `badCrypto()`, a custom function that encodes
                the input with base64 and truncates to 10 characters — base64 is fully
                reversible and provides no cryptographic protection whatsoever.
Evidence:
```js
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```
Impact:         Any database dump immediately exposes all user passwords. The 10-character
                output space is tiny, making brute-force trivial. Seed data stores the
                literal password '123' in the users table.
Recommendation: Replace `badCrypto()` with `bcrypt.hash(password, 12)` and
                `bcrypt.compare(password, hash)`. Update `package.json` to add `bcrypt`.
                Apply PT-03.

### [CRITICAL] God Object — AppManager Concentrates All Application Concerns
File:           src/AppManager.js:1-141
Category:       Architecture
Description:    The `AppManager` class combines HTTP route definitions, raw SQLite queries,
                payment processing business logic, user creation, audit logging, and
                database initialization in a single file with no layer separation.
Evidence:
```js
class AppManager {
    constructor() { this.db = new sqlite3.Database(':memory:'); }
    initDb() { /* CREATE TABLE + INSERT seed data */ }
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            // DB queries, payment logic, enrollment, audit — all here
            console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
            let status = cc.startsWith("4") ? "PAID" : "DENIED";
            this.db.run("INSERT INTO enrollments ...");
            self.db.run("INSERT INTO payments ...");
            self.db.run("INSERT INTO audit_logs ...");
        });
    }
}
```
Impact:         No component can be tested in isolation. Any change to payment logic
                requires modifying the same file that defines HTTP routes and DB schema.
                Violates SRP, OCP and all MVC principles.
Recommendation: Split into: `config/settings.js`, `models/` (schema), `services/`
                (checkout, payment, enrollment logic), `controllers/` (HTTP parsing),
                `routes/` (route registration). Apply PT-04.

### [CRITICAL] Unauthenticated Destructive Endpoint — DELETE /api/users/:id
File:           src/AppManager.js:131-137
Category:       Security
Description:    The user deletion endpoint performs an irreversible DELETE FROM operation
                with no authentication check, authorization guard, or middleware — any
                HTTP client can delete any user by guessing their numeric ID.
Evidence:
```js
app.delete('/api/users/:id', (req, res) => {
    let id = req.params.id;
    this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
        res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
    });
});
```
Impact:         Any unauthenticated caller can permanently delete users. The response
                message acknowledges orphaned enrollments and payments, indicating this
                endpoint is known to corrupt data integrity.
Recommendation: Add authentication middleware before the handler. Add cascade deletion
                or a transaction that removes related enrollments and payments. In
                development, gate behind `process.env.NODE_ENV !== 'production'`.
                Apply PT-04.

### [HIGH] Payment Approval Business Logic Inside Route Handler
File:           src/AppManager.js:43-64
Category:       Architecture
Description:    Payment approval is determined by inspecting the card number prefix
                inside a nested callback within the checkout route handler — business
                logic that belongs in a dedicated payment service.
Evidence:
```js
let processPaymentAndEnroll = (userId) => {
    console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
    let status = cc.startsWith("4") ? "PAID" : "DENIED";

    if (status === "DENIED") return res.status(400).send("Pagamento recusado");

    this.db.run("INSERT INTO enrollments ...", [userId, cid], function(err) {
        self.db.run("INSERT INTO payments ...", [enrId, course.price, status], ...);
    });
};
```
Impact:         Payment logic cannot be tested without an HTTP request. The card number
                is logged to the console exposing PCI-sensitive data. The approval rule
                is a stub that would silently fail in production.
Recommendation: Extract to `services/payment_service.js` with a `processPayment(cardNumber,
                amount)` function. Route handler should only call the service and map
                the result to an HTTP response. Apply PT-04.

### [HIGH] No Authentication System — Admin Endpoint Publicly Accessible
File:           src/AppManager.js:80-129
Category:       Security
Description:    The `/api/admin/financial-report` endpoint returns revenue totals and
                student enrollment data with no authentication, authorization, or token
                verification of any kind — no JWT library is imported anywhere in the
                codebase.
Evidence:
```js
app.get('/api/admin/financial-report', (req, res) => {
    let report = [];
    this.db.all("SELECT * FROM courses", [], (err, courses) => {
        // Returns course revenue and student names with no auth check
        courses.forEach(c => {
            this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], ...);
        });
    });
});
```
Impact:         Any unauthenticated caller can retrieve the full financial report including
                student names, payment amounts and course revenue. Violates basic
                access control and data privacy requirements.
Recommendation: Implement JWT authentication via `jsonwebtoken`. Add a `verifyToken`
                middleware and apply it to all `/api/admin/*` routes. Apply PT-04.

### [MEDIUM] N+1 Query Problem in Financial Report
File:           src/AppManager.js:83-128
Category:       Performance
Description:    For each course the handler executes an enrollments query; for each
                enrollment it executes two more queries (user + payment lookup) inside
                nested callbacks, yielding 1 + N + 2*sum(enrollments) total queries.
Evidence:
```js
this.db.all("SELECT * FROM courses", [], (err, courses) => {
    courses.forEach(c => {
        this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
            enrollments.forEach(enr => {
                this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], ...);
                this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", [enr.id], ...);
            });
        });
    });
});
```
Impact:         With 2 courses and 10 enrollments each, this executes 43 queries per
                request. Under load, this causes database saturation and request timeouts.
Recommendation: Replace with a single JOIN query fetching courses, enrollments, users,
                and payments in one round-trip. Apply PT-06.

### [MEDIUM] Global Mutable State Without Isolation or TTL
File:           src/utils.js:9-10
Category:       Architecture
Description:    `globalCache` and `totalRevenue` are module-level mutable variables shared
                across all concurrent requests with no synchronization, eviction policy,
                or isolation boundary.
Evidence:
```js
let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    console.log(`[LOG] Salvando no cache: ${key}`);
    globalCache[key] = data;
}
```
Impact:         Under concurrent requests, cache writes interleave without ordering
                guarantees. `globalCache` grows unbounded (no eviction). `totalRevenue`
                is exported but never incremented, masking a missing feature.
Recommendation: Use a per-request context object instead of module globals. For shared
                caching, use a dedicated store with TTL. Remove or implement
                `totalRevenue` as a proper DB aggregate query.

### [MEDIUM] In-Memory SQLite Database — Zero Data Durability
File:           src/AppManager.js:7
Category:       Architecture
Description:    The database is instantiated with `:memory:`, meaning all tables, users,
                courses, enrollments, and payments are destroyed every time the process
                restarts.
Evidence:
```js
constructor() {
    this.db = new sqlite3.Database(':memory:');
}
```
Impact:         Any crash, restart, or deployment wipes all application data permanently.
                The system has zero data durability and cannot be used in production.
Recommendation: Replace `:memory:` with a file path configured via environment variable:
                `new sqlite3.Database(process.env.DB_PATH || './data/app.db')`.
                Apply PT-11.

### [LOW] Unstructured Logging via console.log
File:           src/app.js:13, src/AppManager.js:45, src/utils.js:13
Category:       Quality
Description:    Application events including PCI-sensitive card processing details are
                emitted via `console.log` with no log level, structured format, or
                configurable output destination.
Evidence:
```js
// src/app.js:13
console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
// src/AppManager.js:45
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
// src/utils.js:13
console.log(`[LOG] Salvando no cache: ${key}`);
```
Impact:         Card numbers and gateway keys are written to unguarded stdout. No log
                level filtering is possible in production. No timestamps or structured
                fields for log aggregation tools.
Recommendation: Replace with a structured logger such as `pino`. Use `logger.info()`,
                `logger.warn()`, `logger.error()`. Never log card numbers or secret keys.
                Apply PT-09.

### [LOW] Unused Import — totalRevenue Never Referenced
File:           src/AppManager.js:2
Category:       Quality
Description:    `totalRevenue` is destructured from `utils.js` in the import statement
                but is never read or written anywhere in `AppManager.js`.
Evidence:
```js
const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');
// totalRevenue never appears again in AppManager.js
```
Impact:         Misleads readers into believing revenue is being tracked in this module.
                The variable in `utils.js` also goes unincremented, masking a missing
                feature rather than exposing a bug.
Recommendation: Remove `totalRevenue` from the destructured import. If revenue tracking
                is required, implement it as a DB aggregate query. Apply PT-15.

================================
Total: 11 findings
CRITICAL: 4 | HIGH: 2 | MEDIUM: 3 | LOW: 2
================================
