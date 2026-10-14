# 🍺 Canecas Shop

Sistema de vendas de canecas online, desenvolvido para a disciplina de Software Product.

## Integrante(s) do grupo

- Alex Wagner Olímpio Pires — RA: 2403006

## Arquitetura (3 camadas)

- **Apresentação**: rotas Flask + templates HTML (`app.py`, `templates/`)
- **Negócio**: regras da aplicação (`services/`)
- **Dados**: acesso ao banco PostgreSQL, hospedado no Aiven (`database/`)

### Estrutura do projeto

```
canecas-shop/
├── app.py                        # rotas Flask (apresentação)
├── database/
│   └── db.py                     # acesso ao PostgreSQL (dados)
├── services/
│   ├── produto_service.py        # catálogo (negócio)
│   └── carrinho_service.py       # carrinho de compras (negócio)
├── templates/                    # base, catálogo, produto e carrinho
├── static/                       # imagens e estilos
├── tests/                        # testes automatizados (pytest)
├── Dockerfile
└── requirements.txt
```

## Funcionalidades por entrega

- **AC1** (14/09): Catálogo de produtos — listagem e detalhe de canecas, banco migrado para PostgreSQL (Aiven), containerização com Docker
- **AC2** (13/10): Carrinho de compras — sessão, controle de estoque e testes automatizados
- **AC3** (08/11): Finalização do pedido (checkout)
- **Entrega final** (22/11): Painel administrativo + integração completa + pipeline CI/CD

## AC2 — Carrinho de compras

O cliente escolhe uma opção de caneca na página do produto e a adiciona ao carrinho. O carrinho fica guardado na **sessão do navegador** (cookie assinado do Flask), sem exigir login.

### Funcionalidades

- Adicionar uma opção (variante) de caneca ao carrinho
- Alterar a quantidade de um item e remover itens
- Esvaziar o carrinho
- Subtotal por item, total geral e contador de canecas no cabeçalho
- Mensagens de confirmação e de erro após cada ação

### Regras de negócio

- Só é possível adicionar uma opção que existe e tem estoque
- A quantidade no carrinho nunca ultrapassa o estoque da opção
- Quantidade 0 na atualização remove o item
- Valores em reais são calculados com `Decimal`, sem erro de ponto flutuante
- Se o estoque cair depois que o item foi ao carrinho, a tela avisa e pede ajuste (o AC3 usará isso para bloquear o pedido)

### Rotas

| Método | Rota | Função |
|---|---|---|
| GET | `/carrinho` | Mostra o carrinho |
| POST | `/carrinho/adicionar/<variante_id>` | Adiciona uma caneca |
| POST | `/carrinho/atualizar/<variante_id>` | Altera a quantidade |
| POST | `/carrinho/remover/<variante_id>` | Remove um item |
| POST | `/carrinho/limpar` | Esvazia o carrinho |

As rotas que alteram o carrinho aceitam apenas `POST`, e após cada uma o usuário é redirecionado para `/carrinho`.

### Decisões de projeto

- O carrinho é um dicionário `{id_da_variante: quantidade}` guardado na sessão do Flask
- As funções de `services/carrinho_service.py` recebem o carrinho atual e devolvem um **novo** carrinho, sem acessar a sessão. Isso separa a regra de negócio da apresentação e permite testar sem o Flask
- O carrinho guarda **variantes** (as opções de cada caneca), pois é a variante que tem o estoque

## Como rodar

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ele não vai para o repositório):

```
DATABASE_URL=postgresql://usuario:senha@host:porta/defaultdb?sslmode=require
SECRET_KEY=uma_chave_aleatoria_longa
```

- `DATABASE_URL`: conexão com o PostgreSQL
- `SECRET_KEY`: assina o cookie da sessão (usada pelo carrinho). Para gerar uma: `python -c "import secrets; print(secrets.token_hex(32))"`

### Localmente (Python)

```bash
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

### Com Docker

```bash
docker build -t canecas-shop .
docker run --rm -p 5000:5000 --env-file .env canecas-shop
```

Acesse: http://localhost:5000

## Rodar os testes

Há 31 testes automatizados: 19 do service do carrinho, 7 das rotas do carrinho e 5 do catálogo (AC1). Os testes do carrinho não acessam o banco real.

### Com Docker

A imagem não inclui o pytest (ferramenta de desenvolvimento), então ele é instalado no container descartável:

```bash
docker run --rm --env-file .env -v ${PWD}:/app canecas-shop sh -c "pip install -q pytest && python -m pytest -q"
```

### Localmente

```bash
pip install pytest
pytest tests/ -v
```

## Links

- Link do GitHub: https://github.com/AlexOlimpio/canecas-shop
- Board do projeto: [github.com/users/AlexOlimpio/projects/2](https://github.com/users/AlexOlimpio/projects/2)
- Vídeo de apresentação AC1: [adicionar link]
- Vídeo de apresentação AC2: [adicionar link]
- Vídeo de apresentação AC3: [adicionar link]
