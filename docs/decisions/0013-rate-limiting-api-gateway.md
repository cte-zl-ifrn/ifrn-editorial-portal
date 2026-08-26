# ADR-0013: Rate limiting via throttling nativo do API Gateway

## Status

Aceita

## Contexto

`docs/initial-architecture.md` (seção 14) exige "aplicar limitação de
requisições"; nenhuma proteção contra abuso existe hoje em nenhuma
camada. O backend é uma função Lambda sem estado compartilhado entre
invocações e, deliberadamente, sem banco de dados (ADR-0005,
ADR-0011) — um limitador de taxa por usuário/IP (token bucket, janela
deslizante) exigiria um armazenamento compartilhado (ex.: DynamoDB,
ElastiCache), contrariando essa decisão já tomada.

## Decisão

Usar o throttling nativo do API Gateway HTTP API (`ThrottleSettings` —
`RateLimit`/`BurstLimit`), configurado por rota no template SAM
(`infra/sam/template.yaml`), não implementado como código de
aplicação. Duas faixas: um limite mais restritivo em
`POST /api/submissions` (escrita — mais custosa e mais sujeita a
abuso) e um limite mais permissivo nas rotas de leitura
(`GET /api/documents/*`, `GET /api/me`, etc.).

## Consequências

- Nenhum serviço novo, nenhum estado compartilhado, nenhum banco de
  dados — coerente com a postura de MVP já estabelecida.
- O throttling é por estágio do API Gateway (granularidade grosseira:
  não é por usuário nem por IP individual) — protege contra abuso ou
  estouro de custo geral, não contra um único usuário insistente vindo
  de múltiplos IPs. Aceitável para o modelo de ameaça do MVP (base de
  usuários pequena e conhecida, todos com permissão de escrita no
  `central-ajuda`).
- Só tem efeito real depois de uma implantação de verdade — como todo
  o restante de `infra/` até aqui, esta fase documenta/templatiza a
  configuração; não fica ativa sem uma implantação real.
- Limitação por usuário ou mais granular, se algum dia necessária,
  exigiria um componente com estado (ex.: DynamoDB) — explicitamente
  adiado, coerente com "Serviços futuros, somente se necessários"
  (`docs/initial-architecture.md`, seção 17).

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seções
  14 e 17.
- [ADR-0005](0005-backend-lambda-api-gateway.md),
  [ADR-0011](0011-escrita-branch-commit-pull-request.md) — postura
  sem banco de dados.
- [docs/phase-4.3-plan.md](../phase-4.3-plan.md).
