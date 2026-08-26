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

## Critérios de aceite / definição de pronto

- [ ] `infra/sam/template.yaml` define `ThrottleSettings` distintos
      para `POST /api/submissions` e para as rotas de leitura;
      `sam validate` continua válido.
- [ ] Uma requisição de submissão cujo corpo excede o teto configurado
      é rejeitada, com erro claro, antes de qualquer chamada ao
      GitHub.
- [ ] `docs/api/openapi.yaml` documenta `429` como resposta possível
      em `POST /api/submissions`.
- [ ] `ruff check` e `pytest` passam; nenhuma regressão.

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0013](decisions/0013-rate-limiting-api-gateway.md) para a
decisão completa e seus limites conhecidos (throttling por estágio, não
por usuário/IP).

- **Falso positivo em pico de uso legítimo**: os limites devem ser
  calibrados generosamente para o volume esperado do MVP (poucos
  usuários simultâneos) — valores exatos ficam documentados no
  template, revisáveis sem exigir nova ADR.

## Roteiro de validação manual (Fase 4.3.5)

A ser executado e registrado quando a implementação estiver concluída:

- [ ] Enviar uma submissão com payload acima do teto configurado →
      rejeitada antes de qualquer chamada ao GitHub.
- [ ] `sam validate --template infra/sam/template.yaml` com os novos
      `ThrottleSettings`.

## Dependências

- Nenhuma dependência de código de outras sub-fases — pode ser
  implementada isoladamente.
