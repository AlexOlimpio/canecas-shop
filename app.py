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
from services import produto_service, carrinho_service, pedido_service

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


# --------------- AC3: Checkout ---------------

@app.route("/checkout")
def checkout():
    """AC3 - Formulário de endereço + resumo do pedido."""
    resumo = carrinho_service.resumo(_carrinho_atual())
    if resumo["vazio"]:
        flash("Adicione itens ao carrinho antes de finalizar.", "erro")
        return redirect(url_for("ver_carrinho"))
    if resumo["tem_item_indisponivel"]:
        flash("Ajuste os itens com estoque insuficiente antes de continuar.", "erro")
        return redirect(url_for("ver_carrinho"))
    return render_template("checkout.html", carrinho=resumo)


@app.route("/checkout", methods=["POST"])
def processar_checkout():
    """AC3 - Grava o pedido, baixa estoque e redireciona à confirmação."""
    nome = request.form.get("nome", "").strip()
    endereco = request.form.get("endereco", "").strip()
    cidade = request.form.get("cidade", "").strip()
    estado = request.form.get("estado", "").strip()
    cep = request.form.get("cep", "").strip()

    pedido_id, erro = pedido_service.finalizar_pedido(
        _carrinho_atual(), nome, endereco, cidade, estado, cep,
    )

    if erro:
        flash(erro, "erro")
        return redirect(url_for("checkout"))

    session["carrinho"] = carrinho_service.limpar()
    session["ultimo_pedido"] = pedido_id
    return redirect(url_for("confirmacao_pedido", pedido_id=pedido_id))


@app.route("/pedido/<int:pedido_id>/confirmacao")
def confirmacao_pedido(pedido_id):
    """AC3 - Tela de confirmação do pedido finalizado."""
    if session.get("ultimo_pedido") != pedido_id:
        abort(403)
    confirmacao = pedido_service.obter_confirmacao(pedido_id)
    if confirmacao is None:
        abort(404)
    return render_template("confirmacao.html", pedido=confirmacao)


init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)