"""
Camada de NEGÓCIO — Finalização do pedido / checkout (AC3)

Recebe o carrinho da sessão e os dados de endereço, valida tudo e
delega a gravação para a camada de dados.
"""
from decimal import Decimal, ROUND_HALF_UP

from database import db
from services.carrinho_service import _dinheiro, formatar_preco

_ESTADOS_BR = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def validar_endereco(nome, endereco, cidade, estado, cep):
    """Valida os campos de endereço. Devolve lista de erros (vazia = ok)."""
    erros = []
    if not nome or not nome.strip():
        erros.append("Informe seu nome completo.")
    if not endereco or not endereco.strip():
        erros.append("Informe o endereço de entrega.")
    if not cidade or not cidade.strip():
        erros.append("Informe a cidade.")
    if not estado or estado.strip().upper() not in _ESTADOS_BR:
        erros.append("Informe uma UF válida (ex.: SP, RJ).")
    cep_limpo = (cep or "").replace("-", "").replace(".", "").strip()
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        erros.append("Informe um CEP válido (8 dígitos).")
    return erros


def finalizar_pedido(carrinho, nome, endereco, cidade, estado, cep):
    """Processa o checkout completo.

    Devolve (pedido_id, erro). Se deu certo, erro é None.
    """
    if not carrinho:
        return None, "Seu carrinho está vazio."

    erros_endereco = validar_endereco(nome, endereco, cidade, estado, cep)
    if erros_endereco:
        return None, " ".join(erros_endereco)

    itens_para_gravar = []
    total = Decimal("0.00")

    for variante_id_str, quantidade in carrinho.items():
        dados = db.buscar_variante_com_produto(int(variante_id_str))
        if dados is None:
            return None, f"A opção #{variante_id_str} não existe mais no catálogo."
        if dados["estoque"] < quantidade:
            return None, (
                f"Estoque insuficiente para {dados['produto_nome']} - "
                f"{dados['variante_nome']}. Restam {dados['estoque']} unidade(s)."
            )
        preco = _dinheiro(dados["preco"])
        total += preco * quantidade
        itens_para_gravar.append({
            "variante_id": int(variante_id_str),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })

    cep_limpo = (cep or "").replace("-", "").replace(".", "").strip()
    pedido_id = db.criar_pedido(
        total=total,
        nome_cliente=nome.strip(),
        endereco=endereco.strip(),
        cidade=cidade.strip(),
        estado=estado.strip().upper(),
        cep=cep_limpo,
        itens=itens_para_gravar,
    )
    return pedido_id, None


def obter_confirmacao(pedido_id):
    """Monta os dados para a tela de confirmação do pedido."""
    pedido = db.buscar_pedido_por_id(pedido_id)
    if pedido is None:
        return None

    itens_formatados = []
    for item in pedido["itens"]:
        subtotal = _dinheiro(item["preco_unitario"]) * item["quantidade"]
        itens_formatados.append({
            "produto_nome": item["produto_nome"],
            "variante_nome": item["variante_nome"],
            "imagem_url": item["imagem_url"],
            "quantidade": item["quantidade"],
            "preco_formatado": formatar_preco(item["preco_unitario"]),
            "subtotal_formatado": formatar_preco(subtotal),
        })

    return {
        "id": pedido["id"],
        "data": pedido["data_criacao"],
        "total_formatado": formatar_preco(pedido["total"]),
        "nome_cliente": pedido["nome_cliente"],
        "endereco": pedido["endereco"],
        "cidade": pedido["cidade"],
        "estado": pedido["estado"],
        "cep": pedido["cep"],
        "itens": itens_formatados,
    }
