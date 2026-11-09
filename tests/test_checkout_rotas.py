import importlib
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from services import carrinho_service, pedido_service

VARIANTES = {
    1: {"id": 1, "variante_nome": "Marrom", "imagem_url": "/img/a.jpg",
        "estoque": 5, "produto_id": 2, "produto_nome": "Caneca Café", "preco": 29.9},
}

_pedido_counter = 0
_pedidos_store = {}

FORM_OK = {
    "nome": "João da Silva",
    "endereco": "Rua das Flores, 123",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01234567",
}


def _fake_buscar(variante_id):
    return VARIANTES.get(int(variante_id))


def _fake_criar_pedido(total, nome_cliente, endereco, cidade, estado, cep, itens):
    global _pedido_counter
    _pedido_counter += 1
    _pedidos_store[_pedido_counter] = {
        "id": _pedido_counter, "total": float(total),
        "data_criacao": "2026-11-08 12:00:00",
        "nome_cliente": nome_cliente, "endereco": endereco,
        "cidade": cidade, "estado": estado, "cep": cep,
        "itens": [
            {**i, "produto_nome": "Caneca Café", "variante_nome": "Marrom",
             "imagem_url": "/img/a.jpg"}
            for i in itens
        ],
    }
    return _pedido_counter


def _fake_buscar_pedido(pedido_id):
    return _pedidos_store.get(pedido_id)


@pytest.fixture
def client(monkeypatch):
    global _pedido_counter
    _pedido_counter = 0
    _pedidos_store.clear()

    import database.db as dbm
    monkeypatch.setattr(dbm, "init_db", lambda: None)
    monkeypatch.setattr(carrinho_service.db, "buscar_variante_com_produto", _fake_buscar)
    monkeypatch.setattr(pedido_service.db, "buscar_variante_com_produto", _fake_buscar)
    monkeypatch.setattr(pedido_service.db, "criar_pedido", _fake_criar_pedido)
    monkeypatch.setattr(pedido_service.db, "buscar_pedido_por_id", _fake_buscar_pedido)

    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_checkout_redireciona_se_carrinho_vazio(client):
    resp = client.get("/checkout", follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "Adicione itens" in html


def test_checkout_exibe_formulario_com_itens(client):
    client.post("/carrinho/adicionar/1")
    resp = client.get("/checkout")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "Endereço de entrega" in html
    assert "Caneca Café" in html


def test_checkout_post_cria_pedido_e_redireciona(client):
    client.post("/carrinho/adicionar/1", data={"quantidade": 2})
    resp = client.post("/checkout", data=FORM_OK)
    assert resp.status_code == 302
    assert "/pedido/1/confirmacao" in resp.headers["Location"]


def test_confirmacao_mostra_dados_do_pedido(client):
    client.post("/carrinho/adicionar/1", data={"quantidade": 2})
    client.post("/checkout", data=FORM_OK)
    resp = client.get("/pedido/1/confirmacao")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "Pedido confirmado" in html
    assert "João da Silva" in html
    assert "R$ 59,80" in html


def test_checkout_com_endereco_invalido_mostra_erro(client):
    client.post("/carrinho/adicionar/1")
    resp = client.post("/checkout", data={"nome": "", "endereco": "", "cidade": "", "estado": "", "cep": ""}, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "nome" in html.lower() or "CEP" in html


def test_carrinho_esvaziado_apos_pedido(client):
    client.post("/carrinho/adicionar/1")
    client.post("/checkout", data=FORM_OK)
    resp = client.get("/carrinho")
    html = resp.get_data(as_text=True)
    assert "Seu carrinho está vazio" in html


def test_confirmacao_sem_sessao_retorna_403(client):
    resp = client.get("/pedido/999/confirmacao")
    assert resp.status_code == 403
