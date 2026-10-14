import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from services import carrinho_service

# Banco "de mentira": os testes do carrinho não dependem do Postgres.
VARIANTES = {
    1: {"id": 1, "variante_nome": "Marrom", "imagem_url": "/static/img/marrom-a.jpg",
        "estoque": 5, "produto_id": 2, "produto_nome": "Caneca Café da Manhã", "preco": 29.9},
    2: {"id": 2, "variante_nome": "Verde Musgo", "imagem_url": "/static/img/verdemusgo-b.jpg",
        "estoque": 0, "produto_id": 2, "produto_nome": "Caneca Café da Manhã", "preco": 29.9},
    3: {"id": 3, "variante_nome": "Branca", "imagem_url": "/static/img/brancoperson-a.jpg",
        "estoque": 2, "produto_id": 3, "produto_nome": "Caneca Personalizada", "preco": 49.9},
}


@pytest.fixture(autouse=True)
def banco_falso(monkeypatch):
    monkeypatch.setattr(
        carrinho_service.db, "buscar_variante_com_produto",
        lambda variante_id: VARIANTES.get(int(variante_id)),
    )


def test_adicionar_item_novo():
    carrinho, erro = carrinho_service.adicionar_item({}, 1)
    assert erro is None
    assert carrinho == {"1": 1}


def test_adicionar_mesmo_item_soma_quantidade():
    carrinho, _ = carrinho_service.adicionar_item({}, 1, 2)
    carrinho, erro = carrinho_service.adicionar_item(carrinho, 1, 1)
    assert erro is None
    assert carrinho["1"] == 3


def test_nao_altera_o_carrinho_original():
    original = {"1": 1}
    novo, _ = carrinho_service.adicionar_item(original, 3)
    assert original == {"1": 1}
    assert novo == {"1": 1, "3": 1}


def test_nao_adiciona_alem_do_estoque():
    carrinho, erro = carrinho_service.adicionar_item({"3": 2}, 3)
    assert erro is not None
    assert "estoque" in erro
    assert carrinho == {"3": 2}


def test_nao_adiciona_item_esgotado():
    carrinho, erro = carrinho_service.adicionar_item({}, 2)
    assert "esgotada" in erro
    assert carrinho == {}


def test_nao_adiciona_variante_inexistente():
    carrinho, erro = carrinho_service.adicionar_item({}, 999)
    assert erro is not None
    assert carrinho == {}


def test_quantidade_invalida():
    _, erro = carrinho_service.adicionar_item({}, 1, 0)
    assert erro == "Quantidade inválida."

def test_atualizar_quantidade():
    carrinho, erro = carrinho_service.atualizar_quantidade({"1": 1}, 1, 4)
    assert erro is None
    assert carrinho == {"1": 4}


def test_atualizar_para_zero_remove_o_item():
    carrinho, erro = carrinho_service.atualizar_quantidade({"1": 2, "3": 1}, 1, 0)
    assert erro is None
    assert carrinho == {"3": 1}


def test_atualizar_alem_do_estoque_mantem_quantidade():
    carrinho, erro = carrinho_service.atualizar_quantidade({"3": 1}, 3, 5)
    assert erro is not None
    assert carrinho == {"3": 1}


def test_atualizar_item_que_nao_esta_no_carrinho():
    _, erro = carrinho_service.atualizar_quantidade({}, 1, 2)
    assert erro == "Este item não está no carrinho."


def test_remover_item():
    assert carrinho_service.remover_item({"1": 2, "3": 1}, 1) == {"3": 1}


def test_remover_item_ausente_nao_da_erro():
    assert carrinho_service.remover_item({"3": 1}, 1) == {"3": 1}


def test_limpar():
    assert carrinho_service.limpar() == {}


def test_contar_itens_soma_quantidades():
    assert carrinho_service.contar_itens({"1": 2, "3": 1}) == 3
    assert carrinho_service.contar_itens({}) == 0


def test_resumo_calcula_subtotais_e_total_sem_erro_de_float():
    r = carrinho_service.resumo({"1": 2, "3": 1})  # 2 x 29,90 + 1 x 49,90
    assert r["quantidade_total"] == 3
    assert r["total_formatado"] == "R$ 109,70"
    assert [i["subtotal_formatado"] for i in r["itens"]] == ["R$ 59,80", "R$ 49,90"]
    assert r["vazio"] is False
    assert r["tem_item_indisponivel"] is False


def test_resumo_carrinho_vazio():
    r = carrinho_service.resumo({})
    assert r["vazio"] is True
    assert r["total_formatado"] == "R$ 0,00"


def test_resumo_marca_item_quando_estoque_caiu():
    r = carrinho_service.resumo({"3": 5})  # estoque atual é 2
    assert r["itens"][0]["disponivel"] is False
    assert r["tem_item_indisponivel"] is True


def test_resumo_ignora_variante_que_nao_existe_mais():
    r = carrinho_service.resumo({"1": 1, "999": 3})
    assert [i["variante_id"] for i in r["itens"]] == [1]