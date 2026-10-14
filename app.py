"""
Camada de APRESENTAÇÃO (Presentation Layer)
Rotas Flask — recebem as requisições e devolvem HTML, sempre delegando
as regras de negócio para a camada de services.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from database.db import init_db
from services import produto_service, carrinho_service

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret-change-me")
def _carrinho_atual():
    """Carrinho guardado na sessão deste navegador (vazio se ainda não há)."""
    return session.get("carrinho", {})


@app.context_processor
def injetar_carrinho():
    """Deixa `cart_count` disponível em TODOS os templates (contador do header)."""
    return {"cart_count": carrinho_service.contar_itens(_carrinho_atual())}


@app.route("/")
def index():
    """AC1 - Página inicial com o catálogo de canecas."""
    produtos = produto_service.obter_catalogo()
    return render_template("index.html", produtos=produtos)


@app.route("/produto/<int:produto_id>")
def detalhe_produto(produto_id):
    produto = produto_service.obter_produto(produto_id)
    return render_template("produto.html", produto=produto)

@app.route("/carrinho")
def ver_carrinho():
    """AC2 - Tela do carrinho: itens, subtotais e total."""
    resumo = carrinho_service.resumo(_carrinho_atual())
    return render_template("carrinho.html", carrinho=resumo)


@app.route("/carrinho/adicionar/<int:variante_id>", methods=["POST"])
def adicionar_ao_carrinho(variante_id):
    quantidade = request.form.get("quantidade", 1, type=int)
    novo, erro = carrinho_service.adicionar_item(_carrinho_atual(), variante_id, quantidade)
    session["carrinho"] = novo
    if erro:
        flash(erro, "erro")
    else:
        flash("Caneca adicionada ao carrinho.", "ok")
    return redirect(url_for("ver_carrinho"))


@app.route("/carrinho/atualizar/<int:variante_id>", methods=["POST"])
def atualizar_carrinho(variante_id):
    quantidade = request.form.get("quantidade", type=int)
    novo, erro = carrinho_service.atualizar_quantidade(_carrinho_atual(), variante_id, quantidade)
    session["carrinho"] = novo
    if erro:
        flash(erro, "erro")
    return redirect(url_for("ver_carrinho"))


@app.route("/carrinho/remover/<int:variante_id>", methods=["POST"])
def remover_do_carrinho(variante_id):
    session["carrinho"] = carrinho_service.remover_item(_carrinho_atual(), variante_id)
    flash("Item removido do carrinho.", "ok")
    return redirect(url_for("ver_carrinho"))


@app.route("/carrinho/limpar", methods=["POST"])
def limpar_carrinho():
    session["carrinho"] = carrinho_service.limpar()
    flash("Carrinho esvaziado.", "ok")
    return redirect(url_for("ver_carrinho"))


init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)