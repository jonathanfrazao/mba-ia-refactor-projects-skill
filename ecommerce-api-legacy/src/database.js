const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const settings = require('./config/settings');

const dbAbsPath = path.resolve(settings.dbPath);
const dbDir = path.dirname(dbAbsPath);
if (!fs.existsSync(dbDir)) fs.mkdirSync(dbDir, { recursive: true });

const db = new sqlite3.Database(dbAbsPath);

const run = (sql, params = []) => new Promise((resolve, reject) => {
    db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
    });
});

const get = (sql, params = []) => new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
    });
});

const all = (sql, params = []) => new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
    });
});

async function initDb() {
    await run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
    await run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
    await run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
    await run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
    await run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

    const existing = await get('SELECT id FROM courses WHERE id = 1');
    if (!existing) {
        const hash = await bcrypt.hash('123', 12);
        await run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", ['Leonan', 'leonan@fullcycle.com.br', hash]);
        await run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1)");
        await run("INSERT INTO courses (title, price, active) VALUES ('Docker', 497.00, 1)");
        await run("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)");
        await run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
    }
}

module.exports = { db, run, get, all, initDb };
