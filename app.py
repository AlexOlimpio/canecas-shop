"""
Camada de APRESENTAÇÃO (Presentation Layer)
Rotas Flask — recebem as requisições e devolvem HTML, sempre delegando
as regras de negócio para a camada de services.
"""
from flask import Flask, render_template
from database.db import init_db
from services import produto_service

app = Flask(__name__)


@app.route("/")
def index():
    """AC1 - Página inicial com o catálogo de canecas."""
    produtos = produto_service.obter_catalogo()
    return render_template("index.html", produtos=produtos)


@app.route("/produto/<int:produto_id>")
def detalhe_produto(produto_id):
    produto = produto_service.obter_produto(produto_id)
    return render_template("produto.html", produto=produto)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
