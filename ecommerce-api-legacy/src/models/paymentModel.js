const { run } = require('../database');

async function create(enrollmentId, amount, status) {
    return run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status]
    );
}

module.exports = { create };
