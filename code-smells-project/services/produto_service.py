import logging
from config import CATEGORIAS_VALIDAS
import models.produto_model as produto_model

logger = logging.getLogger(__name__)


def listar():
    return produto_model.get_todos_produtos()


def buscar_por_id(produto_id):
    produto = produto_model.get_produto_por_id(produto_id)
    if not produto:
        raise LookupError("Produto não encontrado")
    return produto


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    return produto_model.buscar_produtos(termo, categoria, preco_min, preco_max)


def criar(dados):
    nome = dados.get("nome", "")
    descricao = dados.get("descricao", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")
    categoria = dados.get("categoria", "geral")

    if not nome:
        raise ValueError("Nome é obrigatório")
    if preco is None:
        raise ValueError("Preço é obrigatório")
    if estoque is None:
        raise ValueError("Estoque é obrigatório")
    if preco < 0:
        raise ValueError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValueError("Estoque não pode ser negativo")
    if len(nome) < 2:
        raise ValueError("Nome muito curto")
    if len(nome) > 200:
        raise ValueError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")

    produto_id = produto_model.criar_produto(nome, descricao, preco, estoque, categoria)
    logger.info(f"Produto criado: id={produto_id}")
    return produto_id


def atualizar(produto_id, dados):
    if not produto_model.get_produto_por_id(produto_id):
        raise LookupError("Produto não encontrado")

    nome = dados.get("nome", "")
    descricao = dados.get("descricao", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")
    categoria = dados.get("categoria", "geral")

    if not nome:
        raise ValueError("Nome é obrigatório")
    if preco is None:
        raise ValueError("Preço é obrigatório")
    if estoque is None:
        raise ValueError("Estoque é obrigatório")
    if preco < 0:
        raise ValueError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValueError("Estoque não pode ser negativo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")

    produto_model.atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria)
    logger.info(f"Produto atualizado: id={produto_id}")


def deletar(produto_id):
    if not produto_model.get_produto_por_id(produto_id):
        raise LookupError("Produto não encontrado")
    produto_model.deletar_produto(produto_id)
    logger.info(f"Produto deletado: id={produto_id}")
