import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import init_db
from services import produto_service


def test_catalogo_retorna_produtos():
    init_db()
    catalogo = produto_service.obter_catalogo()
    assert len(catalogo) > 0
    assert "nome" in catalogo[0]
    assert "preco_formatado" in catalogo[0]


def test_produto_formata_preco_em_reais():
    init_db()
    catalogo = produto_service.obter_catalogo()
    assert catalogo[0]["preco_formatado"].startswith("R$")


def test_buscar_produto_inexistente_retorna_none():
    init_db()
    produto = produto_service.obter_produto(9999)
    assert produto is None


def test_produto_tem_duas_opcoes_com_mesmo_preco():
    init_db()
    catalogo = produto_service.obter_catalogo()
    produto = produto_service.obter_produto(catalogo[0]["id"])
    assert len(produto["opcoes"]) == 2


def test_catalogo_traz_imagens_para_slideshow():
    init_db()
    catalogo = produto_service.obter_catalogo()
    assert len(catalogo[0]["imagens"]) == 2
