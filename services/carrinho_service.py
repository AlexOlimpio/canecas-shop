"""
Camada de NEGÓCIO — Carrinho de compras (AC2)

O carrinho é um dicionário {id_da_variante: quantidade}, guardado na sessão.
Ex.: {"3": 2, "7": 1} = 2 canecas da variante 3 e 1 da variante 7.
As funções recebem o carrinho atual e devolvem um NOVO carrinho.
"""
from decimal import Decimal, ROUND_HALF_UP
from database import db

def _dinheiro(valor):
    """Converte para Decimal com 2 casas (centavos), sem erro de float."""
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def formatar_preco(valor):
    """Ex.: 59.8 -> 'R$ 59,80' (formato brasileiro)."""
    return f"R$ {_dinheiro(valor):.2f}".replace(".", ",")

def contar_itens(carrinho):
    """Total de canecas no carrinho (soma das quantidades)."""
    return sum(carrinho.values())


def remover_item(carrinho, variante_id):
    """Devolve um novo carrinho sem a variante informada.

    Não altera o carrinho original e não dá erro se a variante
    não estiver no carrinho.
    """
    novo = dict(carrinho)
    novo.pop(str(variante_id), None)
    return novo


def limpar():
    """Devolve um carrinho vazio."""
    return {}

def adicionar_item(carrinho, variante_id, quantidade=1):
    """Adiciona caneca(s) ao carrinho, respeitando o estoque.

    Devolve (novo_carrinho, erro). Se deu certo, erro é None.
    Se deu errado, o carrinho devolvido é uma cópia sem alterações.
    """
    novo = dict(carrinho)

    if quantidade is None or quantidade < 1:
        return novo, "Quantidade inválida."

    item = db.buscar_variante_com_produto(variante_id)
    if item is None:
        return novo, "Esta opção de caneca não existe."
    if item["estoque"] <= 0:
        return novo, "Esta opção está esgotada."

    quantidade_atual = novo.get(str(variante_id), 0)
    nova_quantidade = quantidade_atual + quantidade
    if nova_quantidade > item["estoque"]:
        return novo, f"Só temos {item['estoque']} unidade(s) em estoque."

    novo[str(variante_id)] = nova_quantidade
    return novo, None

def atualizar_quantidade(carrinho, variante_id, quantidade):
    """Define a quantidade de um item que já está no carrinho.

    quantidade <= 0 remove o item. Devolve (novo_carrinho, erro).
    """
    novo = dict(carrinho)

    if str(variante_id) not in novo:
        return novo, "Este item não está no carrinho."

    if quantidade is None:
        return novo, "Quantidade inválida."

    if quantidade <= 0:
        return remover_item(carrinho, variante_id), None

    item = db.buscar_variante_com_produto(variante_id)
    if item is None:
        return remover_item(carrinho, variante_id), "Esta opção de caneca não existe mais."

    if quantidade > item["estoque"]:
        return novo, f"Só temos {item['estoque']} unidade(s) em estoque."

    novo[str(variante_id)] = quantidade
    return novo, None

def resumo(carrinho):
    """Monta os dados que a tela do carrinho precisa: itens, subtotais e total.

    Itens cuja variante deixou de existir no banco são ignorados. Se o estoque
    caiu abaixo da quantidade escolhida, o item vem com disponivel=False.
    """
    itens = []
    total = Decimal("0.00")

    for variante_id, quantidade in carrinho.items():
        dados = db.buscar_variante_com_produto(int(variante_id))
        if dados is None:
            continue

        subtotal = _dinheiro(dados["preco"]) * quantidade
        total += subtotal
        itens.append({
            "variante_id": int(variante_id),
            "produto_id": dados["produto_id"],
            "produto_nome": dados["produto_nome"],
            "variante_nome": dados["variante_nome"],
            "imagem_url": dados["imagem_url"],
            "preco_formatado": formatar_preco(dados["preco"]),
            "quantidade": quantidade,
            "estoque": dados["estoque"],
            "subtotal": subtotal,
            "subtotal_formatado": formatar_preco(subtotal),
            "disponivel": dados["estoque"] >= quantidade,
        })

    return {
        "itens": itens,
        "quantidade_total": sum(i["quantidade"] for i in itens),
        "total": total,
        "total_formatado": formatar_preco(total),
        "tem_item_indisponivel": any(not i["disponivel"] for i in itens),
        "vazio": len(itens) == 0,
    }