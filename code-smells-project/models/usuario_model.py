import logging
from database import get_db

logger = logging.getLogger(__name__)


def get_todos_usuarios():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
    return [dict(row) for row in cursor.fetchall()]


def get_usuario_por_id(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def get_usuario_por_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, nome, email, senha, tipo, criado_em FROM usuarios WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def criar_usuario(nome, email, senha_hash, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo)
    )
    db.commit()
    return cursor.lastrowid
