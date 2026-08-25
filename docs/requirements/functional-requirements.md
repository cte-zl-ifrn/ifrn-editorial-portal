# Requisitos funcionais — Fase 1

Escopo: caminho crítico de leitura (autenticação → sessão → autorização →
GitHub App → leitura de documento). Ver [docs/phase-1-plan.md](../phase-1-plan.md).

Cada requisito tem um identificador (`RF-NN`) para referência em testes e
Pull Requests.

## Login

- **RF-01** — O sistema deve oferecer um endpoint (`GET /auth/login`) que
  inicia o fluxo de autenticação OAuth do GitHub, gerando um estado
  (`state`) único e de curta duração para proteção contra CSRF.
- **RF-02** — O sistema deve redirecionar o usuário para a página de
  autorização do GitHub com os escopos mínimos necessários para identificar
  o usuário.

## Callback

- **RF-03** — O sistema deve oferecer um endpoint (`GET /auth/callback`)
  que recebe o código de autorização e o `state` devolvidos pelo GitHub.
- **RF-04** — O sistema deve validar o `state` recebido contra o valor
  gerado no login; um `state` ausente, expirado ou divergente deve resultar
  em erro de autenticação, sem criar sessão.
- **RF-05** — O sistema deve trocar o código de autorização por um token de
  acesso do GitHub e identificar o usuário autenticado (login, id, nome,
  avatar).
- **RF-06** — Falhas na comunicação com o GitHub durante o callback devem
  resultar em erro tratado, sem expor detalhes internos ao usuário.

## Sessão

- **RF-07** — Após um callback válido, o sistema deve criar uma sessão
  própria do portal, independente do token do GitHub, identificando o
  usuário autenticado.
- **RF-08** — A sessão deve ser transportada por cookie `HttpOnly`,
  `Secure` e com política `SameSite` adequada à separação entre o frontend
  (GitHub Pages) e a API.
- **RF-09** — A sessão deve ter tempo de expiração curto e verificável.
- **RF-10** — Uma sessão expirada, ausente ou inválida deve ser tratada de
  forma equivalente a "usuário não autenticado" em qualquer endpoint
  protegido.

## Consulta do usuário atual

- **RF-11** — O sistema deve oferecer um endpoint (`GET /api/me`) que
  retorna a identidade do usuário autenticado e o resultado da verificação
  de autorização no repositório `cte-zl-ifrn/central-ajuda`.
- **RF-12** — Sem sessão válida, `GET /api/me` deve responder com erro de
  não autenticado (HTTP 401), sem revelar se o usuário existe ou não no
  GitHub.

## Autorização

- **RF-13** — O sistema deve verificar a permissão efetiva do usuário
  autenticado no repositório `cte-zl-ifrn/central-ajuda` usando a API do
  GitHub.
- **RF-14** — Usuários com permissão `write`, `maintain` ou `admin` devem
  ser considerados autorizados para as operações de leitura desta fase.
- **RF-15** — Usuários com permissão inferior (`read`/`triage`) ou sem
  acesso ao repositório devem ser considerados não autorizados.
- **RF-16** — Um usuário autenticado, porém não autorizado, deve receber
  uma resposta controlada (HTTP 403) ao tentar acessar endpoints que exigem
  autorização, sem acesso ao conteúdo do documento.

## Leitura de conteúdo

- **RF-17** — O sistema deve oferecer um endpoint (`GET /api/documents/sample`)
  que lê, via GitHub App, o conteúdo do arquivo
  `_docs/ambiente-virtual/acesso-moodle.md` no repositório
  `cte-zl-ifrn/central-ajuda`, branch `main`.
- **RF-18** — O endpoint de leitura deve exigir sessão válida e usuário
  autorizado (RF-13 a RF-16).
- **RF-19** — A resposta deve incluir `path`, `name`, `content` (decodificado
  para UTF-8), `sha` e `encoding`.
- **RF-20** — O sistema não deve aceitar caminho de arquivo arbitrário via
  parâmetro de requisição nesta fase; o caminho é fixo no backend.
- **RF-21** — `owner`, `repo` e `branch` usados nas chamadas ao GitHub
  devem ser fixos no backend (`cte-zl-ifrn`, `central-ajuda`, `main`) e
  qualquer tentativa de sobrescrevê-los via parâmetro de requisição deve
  ser rejeitada.

## Tratamento de erros

- **RF-22** — Arquivo inexistente no repositório deve resultar em erro
  tratado (HTTP 404), sem expor stack trace ou detalhes internos.
- **RF-23** — Conteúdo com codificação inesperada (diferente de UTF-8 via
  Base64) deve resultar em erro tratado, não em falha não tratada.
- **RF-24** — Erros de comunicação com a API do GitHub (rate limit,
  indisponibilidade, permissão insuficiente da GitHub App) devem ser
  tratados e traduzidos em uma resposta de erro consistente, sem vazar
  tokens ou chaves.
- **RF-25** — Ausência de configuração ou segredo obrigatório (chave
  privada da GitHub App, client secret) deve impedir a inicialização do
  fluxo correspondente com um erro claro nos logs, sem expor o valor
  ausente.

## Logout

- **RF-26** — O sistema deve oferecer um endpoint (`POST /auth/logout`) que
  encerra a sessão do portal (invalida/expira o cookie de sessão).
- **RF-27** — Logout deve ser idempotente: chamar logout sem sessão ativa
  não deve resultar em erro.

## Health check

- **RF-28** — O sistema deve oferecer um endpoint (`GET /health`) que
  responde com sucesso quando o backend está no ar, sem exigir
  autenticação e sem acessar o GitHub ou qualquer dependência externa.
