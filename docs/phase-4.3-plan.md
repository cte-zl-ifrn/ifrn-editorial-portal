# Plano da Fase 4.3 — Rate limiting e proteção contra abuso

Sub-fase de [docs/phase-4-plan.md](phase-4-plan.md). Desdobramento da
[issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Aplicar limitação de requisições nas rotas do backend, priorizando
`POST /api/submissions` (escrita), sem introduzir estado compartilhado
nem banco de dados — ver [ADR-0013](decisions/0013-rate-limiting-api-gateway.md).

## Escopo

### Dentro

- Infra: `infra/sam/template.yaml` — `ThrottleSettings`
  (`RateLimit`/`BurstLimit`) por rota do API Gateway HTTP API: um
  limite mais restritivo em `POST /api/submissions`, um mais
  permissivo nas rotas de leitura.
- Backend: validar que o tamanho do corpo da requisição de submissão
  (documento + assets em base64) tem um teto explícito antes mesmo da
  validação de asset já existente (`backend/src/assets/validation.py`)
  — hoje o limite de tamanho é por asset individual
  (`max_image_size_bytes`/`max_file_size_bytes`), mas não há um teto
  para o payload inteiro da requisição.
- Documentação do comportamento esperado quando o limite é excedido
  (API Gateway responde `429` nativamente).

### Fora

- Limitação por usuário ou por IP individual — ver ADR-0013
  (exigiria estado compartilhado, adiado).
- Qualquer implantação real do throttling (só tem efeito depois de uma
  implantação real, fora do escopo desta fase).
- WAF — listado como "futuro, somente se necessário"
  (`docs/initial-architecture.md`, seção 17).

## Entregáveis

1. `infra/sam/template.yaml`: `ThrottleSettings` por rota.
2. Backend: teto de tamanho do corpo da requisição de submissão
   (middleware ou validação explícita antes do parsing).
3. Testes: requisição de submissão acima do teto de tamanho é
   rejeitada antes de qualquer processamento.
4. `infra/sam/README.md` e `docs/api/openapi.yaml` atualizados
   (documentar o `429` como resposta possível).

**Entregue** (nomes reais): `infra/sam/template.yaml` —
`PortalApi.DefaultRouteSettings` (20 req/s, burst 40) e
`RouteSettings["POST /api/submissions"]` (2 req/s, burst 5); nova rota
explícita `SubmissionsApi` em `PortalFunction.Events` (necessária para
o `RouteSettings` ter uma rota real para sobrescrever, além do
`ANY /{proxy+}` já existente). `backend/src/app.py` —
`request_size_limit_middleware`, rejeitando `POST /api/submissions`
acima de `max_submission_body_bytes` com `413`.
`backend/src/config.py:max_submission_body_bytes` (padrão 8 MB).
`backend/tests/test_submissions.py` — 1 teste novo.
`docs/api/openapi.yaml` — `413`/`429` documentados em
`POST /api/submissions`.

## Critérios de aceite / definição de pronto

- [x] `infra/sam/template.yaml` define `ThrottleSettings` distintos
      para `POST /api/submissions` e para as rotas de leitura;
      validado estruturalmente (mesma ressalva das Fases 4.1/4.2 — AWS
      SAM CLI não disponível neste ambiente de desenvolvimento).
- [x] Uma requisição de submissão cujo corpo excede o teto configurado
      é rejeitada, com erro claro, antes de qualquer chamada ao
      GitHub (`test_submission_rejects_oversized_body_before_touching_github`
      — confirma zero chamadas às rotas de instalação/conteúdo do
      GitHub).
- [x] `docs/api/openapi.yaml` documenta `429` (e também `413`, que não
      estava no escopo original mas é a resposta real do novo
      middleware) como respostas possíveis em `POST /api/submissions`.
- [x] `ruff check` e `pytest` passam; nenhuma regressão — 74 testes no
      total no backend (73 + 1 novo).

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0013](decisions/0013-rate-limiting-api-gateway.md) para a
decisão completa e seus limites conhecidos (throttling por estágio, não
por usuário/IP).

- **Falso positivo em pico de uso legítimo**: os limites devem ser
  calibrados generosamente para o volume esperado do MVP (poucos
  usuários simultâneos) — valores exatos ficam documentados no
  template, revisáveis sem exigir nova ADR.

## Decisões tomadas durante a implementação

- **`ThrottleSettings` por rota exige uma rota real, não só uma
  referência em `RouteSettings`**: a API tinha só um catch-all
  (`ANY /{proxy+}`), então o `RouteSettings["POST /api/submissions"]`
  não teria nada a que se aplicar. Solução: adicionar
  `POST /api/submissions` como uma rota explícita, além do catch-all —
  API Gateway prioriza a rota mais específica, então isso não muda o
  comportamento de nenhuma outra rota.
- **`413` documentado além do `429` original**: o plano só previa
  documentar `429` (do API Gateway); o teto de tamanho do corpo
  (`request_size_limit_middleware`) é uma resposta do próprio backend,
  então `413` também precisou entrar na definição de pronto e no
  OpenAPI.
- **`max_submission_body_bytes` (8 MB) escolhido por um motivo
  concreto, não arbitrário**: é o maior valor que ainda fica abaixo do
  limite real de payload do próprio API Gateway HTTP API (10 MB fixo,
  não configurável). Ao verificar isso, ficou claro que
  `max_file_size_bytes` (20 MB, Fase 3.2) já permite configurar um
  asset individual maior do que o API Gateway jamais entregaria ao
  Lambda em produção — um risco pré-existente, não introduzido nem
  corrigido nesta fase (corrigir exigiria revisitar os limites da Fase
  3.2, fora de escopo aqui).
- **Verificação por `Content-Length`, não por leitura do corpo**: mais
  barato (não exige buffer o corpo inteiro só para rejeitá-lo) e
  suficiente para o cenário real (um cliente HTTP normal sempre envia
  esse cabeçalho para um corpo JSON não streamado). Uma requisição
  sem `Content-Length` (ex.: `Transfer-Encoding: chunked`) não é
  bloqueada por este middleware — cenário não utilizado pelo frontend
  hoje.

## Roteiro de validação manual (Fase 4.3.5)

- [x] Enviar uma submissão com payload acima do teto configurado →
      rejeitada antes de qualquer chamada ao GitHub. Confirmado via
      teste automatizado
      (`test_submission_rejects_oversized_body_before_touching_github`,
      com o teto reduzido para tornar o teste rápido — o comportamento
      é idêntico ao do valor real de produção).
- [x] `sam validate --template infra/sam/template.yaml` com os novos
      `ThrottleSettings` — mesma ressalva das Fases 4.1/4.2: AWS SAM
      CLI não disponível neste ambiente; validado estruturalmente com
      um parser YAML que reconhece as tags curtas do CloudFormation.
      Recomendo `sam validate` de verdade antes de qualquer implantação
      real.

## Dependências

- Nenhuma dependência de código de outras sub-fases — pode ser
  implementada isoladamente.
