# Security Policy

## Escopo

O `ifrn-editorial-portal` está na Fase 1: um spike do caminho crítico de
leitura (autenticação → sessão → autorização → GitHub App → leitura de um
documento), sem escrita no repositório de conteúdo. Ver
[docs/phase-1-plan.md](docs/phase-1-plan.md).

Não há release estável nem versionamento semântico do produto ainda — não
se aplica uma tabela de "versões suportadas" tradicional. O que existe hoje
é o branch `main`, que deve ser tratado como a única linha ativa.

## Superfície de segurança relevante nesta fase

- Fluxo OAuth do GitHub e sessão do portal (cookie assinado) — ver
  [docs/architecture/authentication-flow.md](docs/architecture/authentication-flow.md).
- Credenciais da GitHub App (JWT da aplicação, installation access token)
  — nunca devem chegar ao frontend nem aparecer em logs (ver
  [docs/requirements/non-functional-requirements.md](docs/requirements/non-functional-requirements.md),
  RNF-01 a RNF-06, RNF-13).
- Segredos de configuração (`SESSION_SECRET`, `GITHUB_OAUTH_CLIENT_SECRET`,
  `GITHUB_APP_PRIVATE_KEY`): apenas em variável de ambiente local ou AWS
  Secrets Manager em produção (ver
  [ADR-0005](docs/decisions/0005-backend-lambda-api-gateway.md)) — nunca
  versionados no repositório.

## Reportando uma vulnerabilidade

Preferencialmente, use o recurso de **Report a vulnerability** do GitHub
(aba "Security" deste repositório → "Report a vulnerability"), que abre um
canal privado de comunicação com os mantenedores antes de qualquer
divulgação pública.

Caso esse recurso não esteja habilitado no momento do reporte, abra uma
issue **sem detalhes sensíveis** pedindo contato privado, ou entre em
contato diretamente com os mantenedores listados no repositório. Não abra
uma issue pública detalhando uma vulnerabilidade ainda não corrigida.

Ao reportar, inclua:

- descrição do problema e impacto potencial;
- passos para reproduzir, se possível;
- se envolve exposição de segredo (token, chave privada, cookie de
  sessão) — nesse caso, trate como crítico.

## O que esperar

- Confirmação de recebimento em até 5 dias úteis.
- Uma avaliação inicial de severidade e próximos passos em até 10 dias
  úteis.
- Nenhuma vulnerabilidade real de segurança será fechada apenas com
  documentação — exige correção de código e, quando aplicável, rotação de
  segredos.

## Antes de qualquer implantação real

Antes de configurar uma GitHub App real ou implantar o backend em um
ambiente acessível externamente, revise:

- as permissões da GitHub App (ver
  [ADR-0004](docs/decisions/0004-integracao-github-app.md) e a nota de
  escopo somente leitura da Fase 1 em
  [docs/phase-1-plan.md](docs/phase-1-plan.md));
- a configuração de `.github/dependabot.yml`;
- a lista de segredos e onde estão armazenados (ver
  `backend/README.md`).
