# Backend — `ifrn-editorial-portal` (Fase 1 / Fase 2.1 / Fase 3.1 / Fase 3.2 / Fase 4.1)

Backend em Python (FastAPI), pensado para rodar em AWS Lambda por trás de
um API Gateway HTTP API (ver
[ADR-0005](../docs/decisions/0005-backend-lambda-api-gateway.md)), mas
executável localmente com `uvicorn` sem qualquer dependência de AWS.

Escopo: [docs/phase-1-plan.md](../docs/phase-1-plan.md),
[docs/phase-2.1-plan.md](../docs/phase-2.1-plan.md),
[docs/phase-3.1-plan.md](../docs/phase-3.1-plan.md),
[docs/phase-3.2-plan.md](../docs/phase-3.2-plan.md) e
[docs/phase-4.1-plan.md](../docs/phase-4.1-plan.md). Contrato completo da
API: [docs/api/openapi.yaml](../docs/api/openapi.yaml).

## Por que FastAPI

`docs/initial-architecture.md` (seção 6.2) já previa "Python com FastAPI
adaptado para Lambda" como uma opção válida. Foi a escolhida por oferecer,
sem introduzir Django: tipagem com Pydantic, testes diretos via
`TestClient`, documentação automática e um adaptador maduro para Lambda
(`mangum`).

## Estrutura

```text
backend/
├── src/
│   ├── handlers/    # rotas FastAPI (health, auth, me, documents, submissions)
│   ├── services/    # orquestração (login, autorização, leitura, submissão)
│   ├── github/      # cliente da API do GitHub e autenticação da GitHub App
│   ├── auth/         # sessão e state OAuth (cookies assinados)
│   ├── markdown/      # separação front matter/corpo (Fase 2.1, ADR-0009)
│   ├── assets/         # validação de imagens/arquivos (Fase 3.2, ADR-0007)
│   ├── models/       # esquemas de requisição/resposta (Pydantic)
│   ├── config.py     # configuração via variáveis de ambiente
│   ├── logging.py    # logging estruturado com correlation_id
│   ├── errors.py      # erros de domínio → status HTTP
│   ├── dependencies.py # dependências do FastAPI (sessão, cliente HTTP)
│   ├── app.py         # criação da aplicação FastAPI
│   └── lambda_handler.py # adaptador Mangum para AWS Lambda
└── tests/
```

## Configuração

Copie `.env.example` para `.env` e preencha os valores (nunca versione
`.env`):

```bash
cp .env.example .env
```

`GITHUB_OWNER`, `GITHUB_REPOSITORY` e `GITHUB_BASE_BRANCH` são constantes
do projeto — o backend rejeita qualquer tentativa de sobrescrevê-los via
parâmetro de requisição (RF-21). Não altere esses valores para apontar a
outro repositório sem uma nova ADR.

Para testar o fluxo real de ponta a ponta (fora dos testes automatizados),
você precisa de:

1. Uma **OAuth App** do GitHub (não confundir com a GitHub App) com
   callback `http://localhost:8000/auth/callback`, para autenticação da
   pessoa usuária.
2. Uma **GitHub App** instalada em `cte-zl-ifrn/central-ajuda`, com
   permissões `Contents: Read and write`, `Pull requests: Read and write`
   e `Metadata: Read-only` (ver
   [ADR-0004](../docs/decisions/0004-integracao-github-app.md) — a partir
   da Fase 3.1 as permissões de escrita, já previstas na ADR-0004, são
   efetivamente usadas), com sua chave privada em
   `GITHUB_APP_PRIVATE_KEY`.

Sem essas credenciais reais, os testes automatizados continuam funcionando
normalmente (ver seção "Testes").

## Executando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn src.app:app --reload --port 8000
```

`GET http://localhost:8000/health` deve responder `{"status": "ok"}` sem
qualquer configuração adicional.

## Testes

```bash
source .venv/bin/activate
pytest
ruff check src tests
```

Toda chamada à API do GitHub é isolada com `respx` (mock de `httpx`) — os
testes não fazem chamadas de rede nem exigem credenciais reais (RNF-18).
Sessões são criadas diretamente com `create_session_cookie_value` nos
testes que não precisam validar o fluxo OAuth completo.

## Sessão e segredos

- A sessão do portal é um cookie assinado (`itsdangerous`), sem
  armazenamento em banco — coerente com a decisão de MVP sem banco de
  dados (ADR-0005). O cookie contém a identidade e o resultado da
  verificação de autorização, nunca um token do GitHub.
- O `state` do OAuth usa o mesmo mecanismo, com expiração curta, para
  proteção contra CSRF sem exigir armazenamento server-side.
- `SESSION_SECRET`, `GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_APP_ID` e
  `GITHUB_APP_PRIVATE_KEY` são segredos: em desenvolvimento, variáveis
  de ambiente (`.env`); em produção, um único segredo JSON no AWS
  Secrets Manager (Fase 4.1, ver
  [ADR-0012](../docs/decisions/0012-segredos-secrets-manager.md)) —
  `get_settings()` (`src/config.py`) busca esse segredo uma única vez
  por cold start quando a variável de ambiente
  `SECRETS_MANAGER_SECRET_ARN` está presente (injetada pelo template
  SAM); sem essa variável, o comportamento continua sendo `.env`, sem
  qualquer mudança. Uma falha ao buscar o segredo, quando a variável
  está presente, interrompe a inicialização — nunca cai silenciosamente
  nos valores padrão inseguros. Nenhum segredo aparece em logs (ver
  `src/logging.py`, que filtra campos sensíveis por nome).

## Escrita no central-ajuda (Fase 3.1 / Fase 3.2)

`POST /api/submissions` cria uma branch, grava o documento (e assets) e
abre um Pull Request — ver
[ADR-0011](../docs/decisions/0011-escrita-branch-commit-pull-request.md),
[docs/phase-3.1-plan.md](../docs/phase-3.1-plan.md) e
[docs/phase-3.2-plan.md](../docs/phase-3.2-plan.md). Pontos importantes:

- O backend **relê** o documento (`get_repository_content`) no momento da
  gravação para obter o `sha` e o `front_matter_raw` atuais — nunca
  confia no que o cliente enviou. Se o `sha` divergir do `base_sha`
  enviado na requisição, a submissão falha com `409` antes de qualquer
  gravação.
- A gravação usa chamadas sequenciais à Contents API (uma por arquivo),
  não a Git Data API de blobs/trees.
- Idempotência é *best-effort*: não há armazenamento de deduplicação
  nesta fase — uma requisição repetida pode gerar branch/PR duplicados.
- **Assets** (`request.assets`, ver ADR-0007): validados integralmente
  (`src/assets/validation.py` — extensão permitida, assinatura/magic
  bytes, tamanho máximo, nome seguro) antes de qualquer chamada ao
  GitHub. O diretório final (`assets/images/{categoria}/`) é sempre
  calculado a partir do documento fixo — o `filename` no payload é só
  uma sugestão do frontend, nunca aceito sem validar. SVG não é
  suportado nesta fase (exigiria sanitização de script, desnecessária
  para o MVP).

## Lambda

`src/lambda_handler.py` expõe `handler`, compatível com o handler de uma
função Lambda atrás de um API Gateway HTTP API. Ver
[infra/README.md](../infra/README.md) para o template SAM correspondente.
Esta fase não implanta nenhum recurso AWS real.
