# Requisitos não funcionais — Fase 1

Escopo: caminho crítico de leitura. Ver [docs/phase-1-plan.md](../phase-1-plan.md)
e a seção 14 de [docs/initial-architecture.md](../initial-architecture.md)
para os requisitos de segurança do projeto como um todo.

## Segurança

- **RNF-01** — Nenhuma credencial privilegiada (chave privada da GitHub
  App, client secret, installation access token) deve chegar ao frontend,
  em bundle, `localStorage`, cookie legível por JavaScript ou parâmetro de
  URL.
- **RNF-02** — A sessão do portal deve usar cookie `HttpOnly`, `Secure` e
  `SameSite` apropriado; nenhuma lógica de autorização deve depender de
  dado controlável pelo cliente.
- **RNF-03** — O backend deve validar CORS restringindo a origem à do
  frontend configurado, não a qualquer origem (`*`).
- **RNF-04** — O backend deve validar o parâmetro `state` do OAuth para
  mitigar CSRF no fluxo de login.
- **RNF-05** — `owner`, `repo` e `branch` do repositório de conteúdo devem
  ser fixos no backend, nunca aceitos como entrada do cliente.
- **RNF-06** — Segredos não devem ser versionados no repositório do portal
  em nenhuma hipótese (ver checklist de CI em
  [docs/definition-of-done.md](../definition-of-done.md)).

## Disponibilidade esperada

- **RNF-07** — Nesta fase (spike, sem produção real), disponibilidade é
  medida apenas em ambiente de desenvolvimento local; não há SLA formal.
  `GET /health` deve responder em menos de 1 segundo em ambiente local.

## Desempenho aceitável

- **RNF-08** — A leitura do documento de exemplo (`GET /api/documents/sample`)
  deve responder em tempo aceitável para uso interativo (referência: menos
  de 3 segundos em ambiente de desenvolvimento local, dominado pela latência
  da API do GitHub).
- **RNF-09** — O backend não deve fazer chamadas redundantes à API do
  GitHub para a mesma requisição (por exemplo, buscar o token de instalação
  mais de uma vez por chamada).

## Acessibilidade

- **RNF-10** — As telas do frontend (login, carregando, autorizado, não
  autorizado, erro) devem ser navegáveis por teclado e usar HTML semântico
  (landmarks, `button`/`a` apropriados, texto alternativo quando houver
  imagem).
- **RNF-11** — Mensagens de erro e estado devem ser anunciáveis por leitor
  de tela (uso de `role="alert"` ou equivalente quando aplicável).

## Observabilidade

- **RNF-12** — Cada requisição relevante (login iniciado, callback,
  verificação de autorização, leitura de documento, erro) deve gerar um log
  estruturado com um `correlation_id`.
- **RNF-13** — Logs não devem conter chave privada, tokens, cookies ou
  conteúdo completo de documentos.

## LGPD

- **RNF-14** — Os únicos dados pessoais tratados nesta fase são os
  necessários para autenticação e autorização (identificador GitHub, nome
  de usuário, nome público, avatar). Nenhum dado pessoal adicional deve ser
  coletado nesta fase.
- **RNF-15** — Ver [docs/initial-architecture.md, seção 15](../initial-architecture.md#15-lgpd-e-privacidade)
  para as diretrizes gerais do projeto; a análise jurídica institucional
  continua pendente e fora do escopo desta fase.

## Manutenção

- **RNF-16** — O código do backend e do frontend deve seguir lint e
  formatação automatizados, verificados no CI.
- **RNF-17** — A configuração (URLs, IDs de aplicação, flags) deve vir de
  variáveis de ambiente, nunca hardcoded no código-fonte, exceto os valores
  fixos de repositório/branch citados em RNF-05 (que são constantes
  intencionais, não segredos).

## Testabilidade

- **RNF-18** — Toda integração com a API do GitHub deve ser isolável por
  mock/fixture em testes automatizados, sem depender de rede ou de
  credenciais reais.
- **RNF-19** — Os fluxos de autenticação, autorização e leitura de
  documento devem ter testes automatizados cobrindo os casos de sucesso e
  de erro descritos em `docs/requirements/functional-requirements.md`.

## Restrições de custo

- **RNF-20** — Esta fase não deve provisionar recursos AWS reais; a
  infraestrutura entregue é composta por templates e documentação para
  execução local, evitando custo de nuvem antes de uma decisão explícita de
  implantação.

## Ausência de segredos no frontend

- **RNF-21** — O bundle de produção do frontend não deve conter nenhuma
  variável de ambiente que represente segredo; apenas configuração pública
  (por exemplo, a URL base da API) pode ser embutida no build.
