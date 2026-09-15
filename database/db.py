"""
Camada de DADOS (Data Layer)
Responsável por toda a comunicação com o banco de dados (SQLite).
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "canecas.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas do banco, caso não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            imagem_url TEXT,
            estoque INTEGER DEFAULT 0,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    # AC2/AC3 (carrinho e pedidos) — tabelas já preparadas para os próximos sprints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            total REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    conn.commit()

    # Seed inicial — só insere se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
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
            "INSERT INTO produtos (nome, descricao, preco, imagem_url, estoque) VALUES (?, ?, ?, ?, ?)",
            produtos_exemplo
        )
        conn.commit()

        # Duas opções (variantes) por produto, mesmo preço do produto principal
        variantes_seeds = {
            "Caneca Geek Python": [("Fundo branco", "python-a"), ("Fundo preto", "python-b")],
            "Caneca Café da Manhã": [("Bege", "coffee-a"), ("Listrada", "coffee-b")],
            "Caneca Personalizada": [("Azul mágica", "magic-a"), ("Vermelha mágica", "magic-b")],
            "Caneca Universitária": [("Com alça", "uni-a"), ("Térmica lisa", "uni-b")],
        }
        # Fotos reais já disponíveis localmente (static/img/); as demais seguem
        # com placeholder até as fotos correspondentes serem enviadas.
        fotos_locais = {"python-a", "python-b"}

        produtos_ids = {row["nome"]: row["id"] for row in cursor.execute("SELECT id, nome FROM produtos")}
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
            "INSERT INTO variantes (produto_id, nome, imagem_url, estoque) VALUES (?, ?, ?, ?)",
            variantes_exemplo
        )
        conn.commit()

    conn.close()


def listar_produtos():
    conn = get_connection()
    produtos = conn.execute("SELECT * FROM produtos ORDER BY id").fetchall()
    conn.close()
    return produtos


def buscar_produto_por_id(produto_id):
    conn = get_connection()
    produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    conn.close()
    return produto


def listar_variantes_por_produto(produto_id):
    conn = get_connection()
    variantes = conn.execute(
        "SELECT * FROM variantes WHERE produto_id = ? ORDER BY id", (produto_id,)
    ).fetchall()
    conn.close()
    return variantes
