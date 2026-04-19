const { run } = require('../database');

async function log(action) {
    return run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action]
    );
}

module.exports = { log };
