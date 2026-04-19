const { get } = require('../database');

async function findActiveById(id) {
    return get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

module.exports = { findActiveById };
