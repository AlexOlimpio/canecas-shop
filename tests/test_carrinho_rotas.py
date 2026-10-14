import importlib
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from services import carrinho_service

VARIANTES = {
    1: {"id": 1, "variante_nome": "Marrom", "imagem_url": "/static/img/marrom-a.jpg",
        "estoque": 5, "produto_id": 2, "produto_nome": "Caneca Café da Manhã", "preco": 29.9},
    2: {"id": 2, "variante_nome": "Verde Musgo", "imagem_url": "/static/img/verdemusgo-b.jpg",
        "estoque": 0, "produto_id": 2, "produto_nome": "Caneca Café da Manhã", "preco": 29.9},
}


@pytest.fixture
def client(monkeypatch):
    """Cliente de teste do Flask sem tocar no banco real (init_db e consultas são trocados)."""
    import database.db as dbm
    monkeypatch.setattr(dbm, "init_db", lambda: None)
    monkeypatch.setattr(
        carrinho_service.db, "buscar_variante_com_produto",
        lambda variante_id: VARIANTES.get(int(variante_id)),
    )

    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_carrinho_comeca_vazio(client):
    resposta = client.get("/carrinho")
    assert resposta.status_code == 200
    assert "Seu carrinho está vazio" in resposta.get_data(as_text=True)


def test_adicionar_mostra_item_e_total(client):
    resposta = client.post("/carrinho/adicionar/1", data={"quantidade": 2}, follow_redirects=True)
    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert "Marrom" in html
    assert "R$ 59,80" in html


def test_adicionar_item_esgotado_mostra_erro(client):
    resposta = client.post("/carrinho/adicionar/2", follow_redirects=True)
    html = resposta.get_data(as_text=True)
    assert "esgotada" in html
    assert "Seu carrinho está vazio" in html


def test_atualizar_quantidade_pela_rota(client):
    client.post("/carrinho/adicionar/1")
    html = client.post("/carrinho/atualizar/1", data={"quantidade": 3}, follow_redirects=True).get_data(as_text=True)
    assert "R$ 89,70" in html


def test_remover_item_pela_rota(client):
    client.post("/carrinho/adicionar/1")
    html = client.post("/carrinho/remover/1", follow_redirects=True).get_data(as_text=True)
    assert "Seu carrinho está vazio" in html


def test_limpar_carrinho_pela_rota(client):
    client.post("/carrinho/adicionar/1")
    html = client.post("/carrinho/limpar", follow_redirects=True).get_data(as_text=True)
    assert "Seu carrinho está vazio" in html


def test_rotas_do_carrinho_so_aceitam_post_para_alterar(client):
    assert client.get("/carrinho/adicionar/1").status_code == 405
    assert client.get("/carrinho/limpar").status_code == 405