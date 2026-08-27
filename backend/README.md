# Backend — `ifrn-editorial-portal` (Fase 1 / Fase 2.1 / Fase 3.1 / Fase 3.2 / Fase 4.1 / Fase 4.2 / Fase 4.3 / Fase 4.4 / Fase 4.5)

Backend em Python (FastAPI), pensado para rodar em AWS Lambda por trás de
um API Gateway HTTP API (ver
[ADR-0005](../docs/decisions/0005-backend-lambda-api-gateway.md)), mas
executável localmente com `uvicorn` sem qualquer dependência de AWS.

Escopo: [docs/phase-1-plan.md](../docs/phase-1-plan.md),
[docs/phase-2.1-plan.md](../docs/phase-2.1-plan.md),
[docs/phase-3.1-plan.md](../docs/phase-3.1-plan.md),
[docs/phase-3.2-plan.md](../docs/phase-3.2-plan.md),
[docs/phase-4.1-plan.md](../docs/phase-4.1-plan.md),
[docs/phase-4.2-plan.md](../docs/phase-4.2-plan.md),
[docs/phase-4.3-plan.md](../docs/phase-4.3-plan.md),
[docs/phase-4.4-plan.md](../docs/phase-4.4-plan.md) e
[docs/phase-4.5-plan.md](../docs/phase-4.5-plan.md). Contrato completo da
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
pip-audit -r requirements-dev.txt  # Fase 4.5, ADR-0015
```

Toda chamada à API do GitHub é isolada com `respx` (mock de `httpx`) — os
testes não fazem chamadas de rede nem exigem credenciais reais (RNF-18).
Sessões são criadas diretamente com `create_session_cookie_value` nos
testes que não precisam validar o fluxo OAuth completo.

`pip-audit` também roda no CI (`.github/workflows/ci.yml`), complementando
o Dependabot já configurado — captura vulnerabilidades conhecidas no
momento do PR, não só na próxima execução agendada do Dependabot.

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

## Observabilidade (Fase 4.2)

- Um middleware (`access_log_middleware`, `src/app.py`) registra, ao
  final de toda requisição — inclusive em caso de exceção não tratada
  — uma linha `request.completed` com método, rota, status HTTP,
  duração em milissegundos e `correlation_id`. Só esses quatro campos
  são logados: nenhum dado da requisição em si (corpo, cookies,
  cabeçalhos) é incluído.
- O mesmo middleware emite duas métricas em Embedded Metric Format
  (EMF) via `log_metric` (`src/logging.py`): `RequestCount` (toda
  requisição, dimensionada por rota) e `ErrorCount` (só quando
  `status_code >= 400`, dimensionada por rota e status). O handler de
  submissões (`src/handlers/submissions.py`) emite `SubmissionCompleted`
  após uma submissão bem-sucedida. EMF é escrito direto em `stdout`
  (fora do `logging` padrão) — é assim que o CloudWatch extrai métricas
  de uma linha de log sem uma chamada `PutMetricData` separada.
- `infra/sam/template.yaml` define dois alarmes do CloudWatch (taxa de
  erro e latência da função Lambda, usando as métricas nativas
  `AWS/Lambda`) — sem canal de notificação real conectado nesta fase.

## Rate limiting e proteção contra abuso (Fase 4.3)

- O rate limiting em si é feito pelo throttling nativo do API Gateway
  HTTP API (`ThrottleSettings` em `infra/sam/template.yaml`, ver
  [ADR-0013](../docs/decisions/0013-rate-limiting-api-gateway.md)), não
  por código de aplicação — só tem efeito depois de uma implantação
  real; sem uma, o backend não impõe nenhum limite de taxa por si só.
- `request_size_limit_middleware` (`src/app.py`) rejeita, com `413`
  (`payload_too_large`) e antes de qualquer parsing, uma requisição
  `POST /api/submissions` cujo `Content-Length` excede
  `max_submission_body_bytes` (`src/config.py`, padrão 8 MB) — um teto
  sobre o payload inteiro, separado dos limites por asset individual já
  existentes (`max_image_size_bytes`/`max_file_size_bytes`).

## Segurança da aplicação (Fase 4.4)

- **Cabeçalhos de segurança**: `security_headers_middleware`
  (`src/app.py`) adiciona `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY` e `Referrer-Policy: no-referrer` a toda
  resposta, e `Content-Security-Policy: default-src 'none'` em toda
  resposta exceto `/docs`/`/redoc` (a UI interativa do FastAPI carrega
  script/estilo de um CDN externo, incompatível com esse CSP). Este CSP
  só afeta as respostas deste backend — a UI do Tiptap roda inteiramente
  no frontend, em outra origem, e não é afetada por ele.
- **CSRF em requisições autenticadas por cookie** (ver
  [ADR-0014](../docs/decisions/0014-csrf-cookies-cross-origin.md)):
  `csrf_header_middleware` rejeita com `403` (`missing_csrf_header`)
  toda requisição `POST`/`PUT`/`PATCH`/`DELETE` sem o cabeçalho
  `X-Portal-Client`, mesmo com um cookie de sessão válido. O frontend
  (`apiClient.ts`) já envia esse cabeçalho em toda chamada.
- **Erros nunca vazam detalhe interno**: além dos erros de domínio já
  mapeados (`{error, message, correlation_id}`), um
  `unhandled_exception_handler` genérico garante a mesma garantia
  mesmo para uma exceção não antecipada — sem ele, um bug real
  escaparia para o texto plano padrão do Starlette (`Internal Server
  Error`), inconsistente com o resto da API (ainda que sem vazar
  detalhe, já que `debug=False`).
- **Auditoria de permissões** (verificada via `gh api
  orgs/cte-zl-ifrn/installations`, 2026-08-27): a GitHub App em uso para
  escrita (`cte-zl-ifrn-editorial-portal-dev`) tem exatamente
  `contents: write`, `pull_requests: write`, `metadata: read` — bate
  com o teto da [ADR-0004](../docs/decisions/0004-integracao-github-app.md),
  nada a mais (nenhuma permissão de `actions`, `administration`,
  `secrets`, `workflows` etc.), `repository_selection: selected` (não
  `all`). A OAuth App não solicita nenhum `scope` no fluxo de
  autorização (`build_authorize_url`, `src/services/auth_service.py`) —
  o token do usuário é usado só para identificá-lo (`GET /user`); toda
  verificação de permissão no repositório e toda escrita usam o token
  de instalação da GitHub App, nunca o token OAuth do usuário.
  **Achado, não corrigido nesta fase**: a instalação antiga
  `ifrn-editorial-portal-dev` (somente leitura, usada até a Fase 3.1,
  substituída pela acima) continua instalada — superfície residual
  pequena (só leitura), mas recomendo desinstalá-la se não for mais
  necessária; decisão institucional, não uma ação de código.

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
