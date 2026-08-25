# Histórias de usuário — Fase 1

Escopo: caminho crítico de leitura. Ver
[docs/phase-1-plan.md](../phase-1-plan.md).

## Usuário autorizado

- Como **usuário autorizado** (com permissão `write`, `maintain` ou `admin`
  no repositório `cte-zl-ifrn/central-ajuda`),
  quero **autenticar-me com minha conta GitHub e visualizar um documento
  Markdown do repositório**,
  para **confirmar que o portal reconhece minha permissão sem que eu
  precise usar a interface do GitHub diretamente**.

- Como **usuário autorizado**,
  quero **ver claramente meu nome/usuário e o status de autorização após o
  login**,
  para **ter certeza de que estou operando com a identidade correta**.

## Usuário não autorizado

- Como **usuário autenticado, mas sem permissão suficiente** no repositório
  `cte-zl-ifrn/central-ajuda`,
  quero **receber uma mensagem clara de acesso não autorizado**,
  para **entender que preciso solicitar permissão antes de usar o portal,
  sem ver conteúdo que não deveria acessar**.

## Usuário não autenticado

- Como **usuário não autenticado**,
  quero **ser direcionado a uma tela de login ao acessar o portal**,
  para **iniciar o processo de autenticação com o GitHub de forma óbvia**.

- Como **usuário não autenticado**,
  quero **que qualquer tentativa de acessar dados protegidos via API falhe
  de forma clara**,
  para **ter certeza de que não há vazamento de conteúdo sem login**.

## Mantenedor do sistema

- Como **mantenedor do sistema**,
  quero **um endpoint de health check que não dependa do GitHub**,
  para **monitorar a disponibilidade do backend de forma simples e
  rápida**.

- Como **mantenedor do sistema**,
  quero **logs estruturados com identificador de correlação para cada
  requisição**,
  para **investigar falhas de autenticação, autorização ou leitura sem
  precisar reproduzir o problema manualmente**.

- Como **mantenedor do sistema**,
  quero **que o backend rejeite qualquer tentativa de alterar o
  repositório, dono ou branch configurados**,
  para **ter certeza de que o portal nunca vai operar, mesmo por engano,
  contra um repositório diferente do autorizado**.

## Operador responsável pelos segredos

- Como **operador responsável pelos segredos** (chave privada da GitHub
  App, client secret, segredos de sessão),
  quero **configurar esses valores apenas por variável de ambiente ou
  Secrets Manager, nunca no código-fonte**,
  para **reduzir o risco de vazamento de credenciais no repositório do
  portal**.

- Como **operador responsável pelos segredos**,
  quero **ter certeza de que nenhum log ou resposta de erro do backend
  expõe tokens, chaves ou cookies**,
  para **evitar que um incidente de log se torne um incidente de
  segurança**.
