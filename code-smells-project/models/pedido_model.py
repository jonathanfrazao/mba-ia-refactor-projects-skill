import logging
from database import get_db

logger = logging.getLogger(__name__)


def criar_pedido_completo(usuario_id, itens_validados, total):
    """All order inserts and stock decrements in a single transaction.

    itens_validados: list of dicts with keys produto_id, quantidade, preco_unitario.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total)
    )
    pedido_id = cursor.lastrowid
    for item in itens_validados:
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"])
        )
    db.commit()
    return pedido_id


def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.id
    """, (usuario_id,))
    return _agrupar_pedidos(cursor.fetchall())


def get_todos_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        ORDER BY p.id
    """)
    return _agrupar_pedidos(cursor.fetchall())


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id)
    )
    db.commit()


def get_estatisticas_vendas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS faturamento,
            SUM(CASE WHEN status = 'pendente'  THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'aprovado'  THEN 1 ELSE 0 END) AS aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
    """)
    row = cursor.fetchone()
    return {
        "total_pedidos": row["total_pedidos"] or 0,
        "faturamento": row["faturamento"] or 0.0,
        "pendentes": row["pendentes"] or 0,
        "aprovados": row["aprovados"] or 0,
        "cancelados": row["cancelados"] or 0,
    }


def _agrupar_pedidos(rows):
    pedidos = {}
    for row in rows:
        oid = row["id"]
        if oid not in pedidos:
            pedidos[oid] = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            pedidos[oid]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())
