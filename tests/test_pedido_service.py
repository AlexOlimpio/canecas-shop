import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from services import pedido_service

VARIANTES = {
    1: {"id": 1, "variante_nome": "Marrom", "imagem_url": "/img/a.jpg",
        "estoque": 5, "produto_id": 2, "produto_nome": "Caneca Café", "preco": 29.9},
    3: {"id": 3, "variante_nome": "Branca", "imagem_url": "/img/b.jpg",
        "estoque": 2, "produto_id": 3, "produto_nome": "Caneca Personalizada", "preco": 49.9},
}

_pedidos_criados = []


def _fake_buscar(variante_id):
    return VARIANTES.get(int(variante_id))


def _fake_criar_pedido(total, nome_cliente, endereco, cidade, estado, cep, itens):
    pid = len(_pedidos_criados) + 100
    _pedidos_criados.append({
        "id": pid, "total": float(total),
        "nome_cliente": nome_cliente, "endereco": endereco,
        "cidade": cidade, "estado": estado, "cep": cep,
        "itens": itens,
    })
    return pid


@pytest.fixture(autouse=True)
def banco_falso(monkeypatch):
    _pedidos_criados.clear()
    monkeypatch.setattr(pedido_service.db, "buscar_variante_com_produto", _fake_buscar)
    monkeypatch.setattr(pedido_service.db, "criar_pedido", _fake_criar_pedido)


ENDERECO_OK = {
    "nome": "João da Silva",
    "endereco": "Rua das Flores, 123",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01234-567",
}


# ---- Validação de endereço ----

def test_endereco_valido():
    erros = pedido_service.validar_endereco(**ENDERECO_OK)
    assert erros == []


def test_endereco_nome_vazio():
    erros = pedido_service.validar_endereco("", "Rua X", "Cidade", "SP", "01234567")
    assert any("nome" in e.lower() for e in erros)


def test_endereco_estado_invalido():
    erros = pedido_service.validar_endereco("Ana", "Rua X", "Cidade", "XX", "01234567")
    assert any("UF" in e for e in erros)


def test_endereco_cep_curto():
    erros = pedido_service.validar_endereco("Ana", "Rua X", "Cidade", "SP", "123")
    assert any("CEP" in e for e in erros)


def test_endereco_cep_com_letras():
    erros = pedido_service.validar_endereco("Ana", "Rua X", "Cidade", "SP", "0123ABCD")
    assert any("CEP" in e for e in erros)


# ---- Finalizar pedido ----

def test_finalizar_pedido_com_sucesso():
    carrinho = {"1": 2, "3": 1}
    pid, erro = pedido_service.finalizar_pedido(carrinho, **ENDERECO_OK)
    assert erro is None
    assert pid == 100
    assert len(_pedidos_criados) == 1
    assert _pedidos_criados[0]["total"] == pytest.approx(109.70, abs=0.01)


def test_finalizar_pedido_carrinho_vazio():
    pid, erro = pedido_service.finalizar_pedido({}, **ENDERECO_OK)
    assert pid is None
    assert "vazio" in erro


def test_finalizar_pedido_endereco_invalido():
    pid, erro = pedido_service.finalizar_pedido({"1": 1}, nome="", endereco="", cidade="", estado="", cep="")
    assert pid is None
    assert erro is not None


def test_finalizar_pedido_estoque_insuficiente():
    carrinho = {"3": 5}  # estoque da variante 3 é 2
    pid, erro = pedido_service.finalizar_pedido(carrinho, **ENDERECO_OK)
    assert pid is None
    assert "insuficiente" in erro.lower()


def test_finalizar_pedido_variante_inexistente():
    carrinho = {"999": 1}
    pid, erro = pedido_service.finalizar_pedido(carrinho, **ENDERECO_OK)
    assert pid is None
    assert "não existe" in erro


def test_cep_com_traco_e_normalizado():
    carrinho = {"1": 1}
    pid, _ = pedido_service.finalizar_pedido(carrinho, **ENDERECO_OK)
    assert _pedidos_criados[0]["cep"] == "01234567"


def test_estado_e_normalizado_para_maiusculo():
    carrinho = {"1": 1}
    dados = dict(ENDERECO_OK, estado="sp")
    pid, _ = pedido_service.finalizar_pedido(carrinho, **dados)
    assert _pedidos_criados[0]["estado"] == "SP"
