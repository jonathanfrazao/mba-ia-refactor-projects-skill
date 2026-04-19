const bcrypt = require('bcrypt');
const { run, get } = require('../database');

const SALT_ROUNDS = 12;

async function findByEmail(email) {
    return get('SELECT id, name, email FROM users WHERE email = ?', [email]);
}

async function findById(id) {
    return get('SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create(name, email, password) {
    const hash = await bcrypt.hash(password, SALT_ROUNDS);
    const result = await run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, hash]
    );
    return result.lastID;
}

async function remove(id) {
    return run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, remove };
