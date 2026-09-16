# 🍺 Canecas Shop

Sistema de vendas de canecas online, desenvolvido para a disciplina de Software Product.

## Integrante(s) do grupo

- Alex Wagner Olímpio Pires — RA: 2403006

## Arquitetura (3 camadas)

- **Apresentação**: rotas Flask + templates HTML (`app.py`, `templates/`)
- **Negócio**: regras da aplicação (`services/`)
- **Dados**: acesso ao banco PostgreSQL, hospedado no Aiven (`database/`)

## Funcionalidades por entrega

- **AC1** (14/09): Catálogo de produtos — listagem e detalhe de canecas, banco migrado para PostgreSQL (Aiven), containerização com Docker
- **AC2** (13/10): Carrinho de compras
- **AC3** (08/11): Finalização do pedido (checkout)
- **Entrega final** (22/11): Painel administrativo + integração completa + pipeline CI/CD

## Como rodar

### Localmente (Python)

1. Crie um arquivo `.env` na raiz do projeto com a variável:

DATABASE_URL=postgresql://usuario:senha@host:porta/defaultdb?sslmode=require

pip install -r requirements.txt
python app.py

3. Acesse: http://localhost:5000

### Com Docker

docker build -t canecas-shop .
docker run --rm -p 5000:5000 --env-file .env canecas-shop


Acesse: http://localhost:5000

## Rodar os testes

pytest tests/ -v


## Links

- Link do GitHub: https://github.com/AlexOlimpio/canecas-shop
- Board do projeto: [github.com/users/AlexOlimpio/projects/2](https://github.com/users/AlexOlimpio/projects/2)
- Vídeo de apresentação: [adicionar link]