# ☕ Canecas Shop

Sistema de vendas de canecas online, desenvolvido para a disciplina de Software Product.

## Integrante(s) do grupo
- [Seu nome] — RA: [seu RA]

## Arquitetura (3 camadas)
- **Apresentação**: rotas Flask + templates HTML (`app.py`, `templates/`)
- **Negócio**: regras da aplicação (`services/`)
- **Dados**: acesso ao banco SQLite (`database/`)

## Funcionalidades por entrega
- **AC1** (14/09): Catálogo de produtos — listagem e detalhe de canecas
- **AC2** (13/10): Carrinho de compras
- **AC3** (08/11): Finalização do pedido (checkout)
- **Entrega final** (22/11): Integração completa + pipeline CI/CD

## Como rodar
```bash
pip install -r requirements.txt
python app.py
```
Acesse: http://localhost:5000

## Rodar os testes
```bash
pytest tests/ -v
```

## Links
- Board do projeto: [adicionar link]
- Vídeo de apresentação: [adicionar link]
