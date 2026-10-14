# Canecas Shop

Sistema web de e-commerce de canecas personalizadas, desenvolvido para a disciplina **Software Product**. O projeto conta com arquitetura em camadas (Apresentação / Negócio / Dados), com back-end em Flask (Python), banco de dados PostgreSQL e execução via Docker.

**Autor:** Alex Wagner Olímpio Pires — RA 2403006 (projeto individual)

## 🛠 Tecnologias Utilizadas

* **Front-end:** HTML5, CSS3 e templates Jinja2 (renderizados pelo Flask).
* **Back-end:** Python 3, Flask 3.0.3, Gunicorn.
* **Banco de Dados:** PostgreSQL (Aiven), acesso via psycopg2 com consultas parametrizadas.
* **Testes:** pytest (testes unitários de regra de negócio e testes de rotas com `test_client`).
* **Infraestrutura:** Docker, GitHub Actions (CI) e Render (deploy).

## 🏗 Arquitetura

O código é dividido em três camadas, e cada uma só conversa com a camada vizinha:

```
app.py + templates/     -> Apresentação (rotas Flask e páginas HTML)
services/               -> Negócio (regras do carrinho, preços, estoque)
database/               -> Dados (conexão e consultas SQL)
tests/                  -> Testes automatizados
```

As regras de negócio ficam em funções puras dentro de `services/`: elas recebem o carrinho atual e devolvem um novo carrinho, sem depender do Flask nem da sessão. Por isso podem ser testadas isoladamente.

## 📋 Funcionalidades do Sistema (ACs)

O sistema é entregue em etapas, uma para cada avaliação:

### 1. Catálogo de Produtos (AC1) — concluída

* Listagem dos produtos (canecas) em uma vitrine com imagem e preço.
* Página de detalhes do produto, com as opções (variantes) disponíveis e o estoque de cada uma.
* Conexão com o banco PostgreSQL e criação da estrutura de tabelas na inicialização.

### 2. Carrinho de Compras (AC2) — concluída

* Adicionar uma opção de caneca ao carrinho direto da página do produto (botão "Esgotado" quando não há estoque).
* Página do carrinho (`/carrinho`) com imagem, preço unitário, quantidade, subtotal de cada item e **total do pedido**.
* Alterar a quantidade, remover um item ou esvaziar o carrinho.
* Contador de itens no cabeçalho, visível em todas as páginas: `Carrinho (3)`.
* Mensagens de feedback ao usuário (item adicionado, estoque insuficiente, carrinho esvaziado).

**Regras de negócio implementadas:**

* Só é possível adicionar uma opção que existe e tem estoque.
* A quantidade no carrinho nunca ultrapassa o estoque da opção.
* Atualizar a quantidade para 0 (ou menos) remove o item.
* Valores em reais são calculados com `Decimal`, sem erros de ponto flutuante.
* O carrinho fica guardado na sessão do navegador (cookie assinado), sem exigir login.

**Rotas do carrinho:**

| Método | Rota | Ação |
|--------|------|------|
| GET | `/carrinho` | Exibe o carrinho e o total |
| POST | `/carrinho/adicionar/<id>` | Adiciona uma opção ao carrinho |
| POST | `/carrinho/atualizar/<id>` | Altera a quantidade de um item |
| POST | `/carrinho/remover/<id>` | Remove um item |
| POST | `/carrinho/limpar` | Esvazia o carrinho |

### 3. Finalização do Pedido (AC3) — em desenvolvimento

* Fluxo de checkout que grava o pedido no banco (tabelas de pedidos e itens do pedido).
* Cálculo do total final e tela de confirmação do pedido.
* Baixa automática do estoque ao concluir a compra.

### 4. Integração Completa (Entrega Final) — planejada

* Integração de todos os módulos, ajustes finais e apresentação do sistema completo.

## 🚀 Como Executar o Projeto

O projeto roda em um container Docker e se conecta a um banco PostgreSQL hospedado na nuvem.

### Pré-requisitos

* [Docker](https://www.docker.com/) instalado e em execução.
* [Git](https://git-scm.com/) para clonar o repositório.
* As credenciais do banco de dados (`DATABASE_URL`). Por segurança elas **não** ficam no repositório; solicite ao autor.

### Passo a Passo

**1. Clone o repositório:**

```bash
git clone https://github.com/AlexOlimpio/canecas-shop.git
cd canecas-shop
```

**2. Crie o arquivo `.env` na raiz do projeto** com o conteúdo abaixo (substitua pelos valores reais):

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/banco?sslmode=require
SECRET_KEY=uma-chave-secreta-qualquer
```

**3. Construa a imagem Docker:**

```bash
docker build -t canecas-shop .
```

**4. Inicie a aplicação:**

```bash
docker run --rm -p 5000:5000 --env-file .env -v ${PWD}:/app canecas-shop gunicorn --reload --bind 0.0.0.0:5000 app:app
```

**5. Acesse no navegador:** http://localhost:5000

> No Linux/macOS use `$(pwd)` no lugar de `${PWD}`.

### Sem Docker (opcional)

Com Python 3 instalado e o `.env` configurado:

```bash
pip install -r requirements.txt
flask --app app run --port 5000
```

## 🧪 Testes Automatizados

O projeto tem 31 testes: regras do carrinho (service), rotas HTTP do carrinho e o catálogo da AC1. Para executar com Docker:

```bash
docker run --rm --env-file .env -v ${PWD}:/app canecas-shop sh -c "pip install -q pytest && python -m pytest -q"
```

Ou localmente: `pip install pytest && python -m pytest -q`.

A cada `push`, o GitHub Actions ("CI - Testes Automatizados") roda a suíte completa.

## 🔗 Links do Projeto

* **Repositório:** https://github.com/AlexOlimpio/canecas-shop
* **Quadro de tarefas (GitHub Projects):** https://github.com/users/AlexOlimpio/projects/2
* **Aplicação online (Render):** https://canecas-shop.onrender.com
  *(plano gratuito: o primeiro acesso pode levar cerca de 1 minuto para "acordar" o servidor)*
* **Vídeo de apresentação da AC2:** [adicionar link]
