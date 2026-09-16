"""
Camada de DADOS (Data Layer)
Responsável por toda a comunicação com o banco de dados (PostgreSQL / Aiven).
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não configurada. Defina a variável de ambiente "
            "(arquivo .env local ou Environment do Render) com a connection "
            "string do Postgres."
        )
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Cria as tabelas do banco, caso não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            imagem_url TEXT,
            estoque INTEGER DEFAULT 0
        )
    """)

    # Cada produto (categoria de caneca) pode ter mais de uma opção/variante,
    # todas pelo mesmo preço do produto — usado no slideshow e na página de detalhe.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS variantes (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER NOT NULL REFERENCES produtos (id),
            nome TEXT NOT NULL,
            imagem_url TEXT,
            estoque INTEGER DEFAULT 0
        )
    """)

    # AC2/AC3 (carrinho e pedidos) — tabelas já preparadas para os próximos sprints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos (id),
            produto_id INTEGER REFERENCES produtos (id),
            quantidade INTEGER,
            preco_unitario REAL
        )
    """)

    conn.commit()

    # Seed inicial — só insere se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()["count"] == 0:
        produtos_exemplo = [
            ("Caneca Geek Python", "Caneca de porcelana 300ml com estampa da logo Python", 39.90,
             "/static/img/python-a.jpg", 15),
            ("Caneca Café da Manhã", "Caneca branca 350ml, ideal para o café do dia a dia", 29.90,
             "https://picsum.photos/seed/coffee-a/300/300", 20),
            ("Caneca Personalizada", "Caneca mágica que muda de cor com líquidos quentes", 49.90,
             "https://picsum.photos/seed/magic-a/300/300", 10),
            ("Caneca Universitária", "Caneca térmica 400ml com tampa, ideal para levar na mochila", 59.90,
             "https://picsum.photos/seed/uni-a/300/300", 8),
        ]
        cursor.executemany(
            "INSERT INTO produtos (nome, descricao, preco, imagem_url, estoque) VALUES (%s, %s, %s, %s, %s)",
            produtos_exemplo
        )
        conn.commit()

        # Duas opções (variantes) por produto, mesmo preço do produto principal
        variantes_seeds = {
            "Caneca Geek Python": [("Fundo branco", "python-b"), ("Fundo preto", "python-a")],
            "Caneca Café da Manhã": [("Bege", "coffee-a"), ("Listrada", "coffee-b")],
            "Caneca Personalizada": [("Azul mágica", "magic-a"), ("Vermelha mágica", "magic-b")],
            "Caneca Universitária": [("Com alça", "uni-a"), ("Térmica lisa", "uni-b")],
        }
        # Fotos reais já disponíveis localmente (static/img/); as demais seguem
        # com placeholder até as fotos correspondentes serem enviadas.
        fotos_locais = {"python-a", "python-b"}

        cursor.execute("SELECT id, nome FROM produtos")
        produtos_ids = {row["nome"]: row["id"] for row in cursor.fetchall()}

        variantes_exemplo = []
        for nome_produto, opcoes in variantes_seeds.items():
            produto_id = produtos_ids[nome_produto]
            estoque_base = next(p[4] for p in produtos_exemplo if p[0] == nome_produto)
            for nome_variante, seed in opcoes:
                if seed in fotos_locais:
                    imagem_url = f"/static/img/{seed}.jpg"
                else:
                    imagem_url = f"https://picsum.photos/seed/{seed}/300/300"
                variantes_exemplo.append(
                    (produto_id, nome_variante, imagem_url, estoque_base)
                )
        cursor.executemany(
            "INSERT INTO variantes (produto_id, nome, imagem_url, estoque) VALUES (%s, %s, %s, %s)",
            variantes_exemplo
        )
        conn.commit()

    cursor.close()
    conn.close()


def listar_produtos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY id")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return produtos


def buscar_produto_por_id(produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()
    cursor.close()
    conn.close()
    return produto


def listar_variantes_por_produto(produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM variantes WHERE produto_id = %s ORDER BY id", (produto_id,)
    )
    variantes = cursor.fetchall()
    cursor.close()
    conn.close()
    return variantes