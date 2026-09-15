"""
Camada de NEGÓCIO (Business Layer)
Contém as regras da aplicação. A camada de apresentação (front-end/rotas)
nunca fala direto com o banco — sempre passa por aqui.
"""
from database import db


def _formatar_preco(preco):
    return f"R$ {preco:.2f}".replace(".", ",")


def obter_catalogo():
    """Retorna a lista de produtos, cada um com as imagens das suas variantes
    (usadas no slideshow do catálogo)."""
    produtos = db.listar_produtos()
    catalogo = []
    for p in produtos:
        variantes = db.listar_variantes_por_produto(p["id"])
        imagens = [v["imagem_url"] for v in variantes] or [p["imagem_url"]]
        catalogo.append({
            "id": p["id"],
            "nome": p["nome"],
            "descricao": p["descricao"],
            "preco": p["preco"],
            "preco_formatado": _formatar_preco(p["preco"]),
            "imagens": imagens,
            "disponivel": p["estoque"] > 0,
        })
    return catalogo


def obter_produto(produto_id):
    """Retorna o produto junto com suas opções (variantes) disponíveis,
    todas pelo mesmo preço do produto."""
    p = db.buscar_produto_por_id(produto_id)
    if p is None:
        return None

    variantes_db = db.listar_variantes_por_produto(produto_id)
    opcoes = [
        {
            "id": v["id"],
            "nome": v["nome"],
            "imagem_url": v["imagem_url"],
            "disponivel": v["estoque"] > 0,
        }
        for v in variantes_db
    ]

    return {
        "id": p["id"],
        "nome": p["nome"],
        "descricao": p["descricao"],
        "preco": p["preco"],
        "preco_formatado": _formatar_preco(p["preco"]),
        "estoque": p["estoque"],
        "opcoes": opcoes,
    }
