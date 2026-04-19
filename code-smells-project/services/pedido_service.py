import logging
import models.produto_model as produto_model
import models.pedido_model as pedido_model
from config import STATUS_PEDIDO_VALIDOS

logger = logging.getLogger(__name__)


def criar(usuario_id, itens):
    if not usuario_id:
        raise ValueError("Usuario ID é obrigatório")
    if not itens:
        raise ValueError("Pedido deve ter pelo menos 1 item")

    total = 0
    itens_validados = []
    for item in itens:
        produto = produto_model.get_produto_por_id(item["produto_id"])
        if not produto:
            raise ValueError(f"Produto {item['produto_id']} não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise ValueError(f"Estoque insuficiente para {produto['nome']}")
        total += produto["preco"] * item["quantidade"]
        itens_validados.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": produto["preco"],
        })

    pedido_id = pedido_model.criar_pedido_completo(usuario_id, itens_validados, total)
    logger.info(f"Pedido criado: id={pedido_id}, usuario_id={usuario_id}, total={total}")
    # TODO: notify user via email/SMS/push — integrate notification service
    return {"pedido_id": pedido_id, "total": total}


def listar_todos():
    return pedido_model.get_todos_pedidos()


def listar_usuario(usuario_id):
    return pedido_model.get_pedidos_usuario(usuario_id)


def atualizar_status(pedido_id, novo_status):
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValueError(f"Status inválido. Válidos: {STATUS_PEDIDO_VALIDOS}")
    pedido_model.atualizar_status_pedido(pedido_id, novo_status)
    logger.info(f"Pedido {pedido_id}: status atualizado para '{novo_status}'")


def relatorio_vendas():
    stats = pedido_model.get_estatisticas_vendas()
    faturamento = stats["faturamento"]
    total_pedidos = stats["total_pedidos"]

    desconto = 0.0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
