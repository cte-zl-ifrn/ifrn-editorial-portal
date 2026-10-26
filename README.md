# ifrn-editorial-portal
Portal editorial para criação, edição e submissão de conteúdo da Central de Ajuda, com autenticação via GitHub App e publicação controlada por Pull Requests.

## Documentação

Comece por [docs/project-context.md](docs/project-context.md). Escopo e status da fase atual: [docs/phase-1-plan.md](docs/phase-1-plan.md). Decisões de arquitetura: [docs/decisions/](docs/decisions/README.md).

## Desenvolvimento local

- Backend: [backend/README.md](backend/README.md)
- Frontend: [frontend/README.md](frontend/README.md)
- Infraestrutura: [infra/README.md](infra/README.md)

### Verificações locais (pre-commit)

Este repositório usa [pre-commit](https://pre-commit.com/) para rodar lint, testes e verificações de segurança básicas antes de cada commit. Instale as dependências de `backend/` e `frontend/` primeiro (ver os READMEs acima), depois:

```bash
pip install pre-commit   # ou: uv tool install pre-commit / pipx install pre-commit
pre-commit install
```

Para rodar manualmente em todo o repositório: `pre-commit run --all-files`.
