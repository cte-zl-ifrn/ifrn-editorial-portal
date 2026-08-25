# Fluxo de autenticação — Fase 1

Este documento detalha o fluxo de autenticação implementado na Fase 1 e
esclarece a diferença entre quatro conceitos frequentemente confundidos.

## Quatro identidades distintas

| Conceito | O que é | Onde vive |
|---|---|---|
| **Autenticação da pessoa usuária** | Prova de que a pessoa é quem alega ser, feita via OAuth do GitHub. | Fluxo `GET /auth/login` → GitHub → `GET /auth/callback`. |
| **Sessão do portal** | Estado próprio do `ifrn-editorial-portal`, criado após a autenticação, que representa "este usuário está logado no portal agora". | Cookie de sessão `HttpOnly`/`Secure`, validado pelo backend. |
| **Identidade técnica da GitHub App** | Identidade da aplicação GitHub instalada em `cte-zl-ifrn/central-ajuda`, usada pelo backend para ler conteúdo do repositório. Não representa nenhum usuário específico. | JWT da aplicação + installation access token, ambos gerados e usados só no backend. |
| **Autorização para uso do portal** vs. **autorização da GitHub App para ler o repositório** | A primeira é "este usuário pode usar o portal?" (calculada a partir da permissão do usuário no repositório). A segunda é "a aplicação instalada pode ler este repositório?" (calculada a partir das permissões concedidas à instalação da GitHub App). São verificações independentes — ver [docs/architecture/authorization-model.md](authorization-model.md). | Backend, em pontos diferentes do fluxo. |

Um erro comum a evitar: tratar o token de acesso do usuário (obtido no
OAuth) como se fosse a mesma coisa que o installation access token da
GitHub App. Nesta fase, o backend usa o token do usuário apenas para
identificá-lo e consultar sua permissão no repositório (via API do GitHub
em nome do usuário ou, alternativamente, via API de colaboradores usando a
própria GitHub App — ver nota abaixo); a leitura do conteúdo do documento
usa exclusivamente o installation access token da GitHub App.

> Nota de implementação: como a permissão de um usuário em um repositório
> também pode ser consultada pela GitHub App (endpoint de
> "Get repository permissions for a user"), o backend pode optar por usar
> apenas o installation access token para essa verificação, evitando
> depender de escopos adicionais no token OAuth do usuário. Essa escolha é
> um detalhe de implementação do backend, documentado em
> `backend/README.md`, e não altera o modelo conceitual acima.

## Passo a passo

```text
1.  Usuário acessa o frontend (não autenticado).
2.  Frontend chama GET /auth/login (redirecionamento de navegador).
3.  Backend gera um `state` aleatório de curta duração e o associa a uma
    sessão temporária (ex.: cookie assinado de curta duração).
4.  Backend redireciona o navegador para a página de autorização OAuth do
    GitHub, incluindo o `state`.
5.  Usuário autoriza o acesso no GitHub.
6.  GitHub redireciona o navegador para GET /auth/callback com `code` e
    `state`.
7.  Backend valida o `state` recebido contra o valor gerado no passo 3.
    Se inválido/ausente/expirado: erro de autenticação, nenhuma sessão é
    criada.
8.  Backend troca o `code` por um token de acesso do usuário junto ao
    GitHub.
9.  Backend identifica o usuário (login, id, nome, avatar) usando esse
    token.
10. Backend verifica a permissão do usuário no repositório
    `cte-zl-ifrn/central-ajuda` (ver
    docs/architecture/authorization-model.md).
11. Backend cria a sessão do portal (cookie HttpOnly/Secure/SameSite),
    contendo o identificador do usuário e o resultado da verificação de
    autorização (ou recalculando-a a cada requisição sensível — decisão de
    implementação registrada em `backend/README.md`).
12. Backend redireciona o navegador de volta ao frontend.
13. Frontend chama GET /api/me (com o cookie de sessão) para exibir a
    identidade do usuário e o status de autorização.
14. Se autorizado, frontend pode chamar GET /api/documents/sample.
```

## Cookies e CORS entre GitHub Pages e a API

- Em produção, o frontend (GitHub Pages) e o backend (API Gateway) ficam em
  origens diferentes. O cookie de sessão deve usar `SameSite=None` e
  `Secure` para ser enviado em requisições cross-site, o que exige HTTPS em
  ambos os lados.
- O backend deve validar CORS restringindo `Access-Control-Allow-Origin`
  à origem exata do frontend configurado (não `*`), com
  `Access-Control-Allow-Credentials: true`.
- Em desenvolvimento local, frontend e backend também rodam em origens
  diferentes (portas diferentes do Vite e do backend local); a mesma
  configuração de CORS/cookie deve ser usada, para validar o comportamento
  real de produção desde já (ver `backend/README.md` e
  `frontend/README.md` para os valores usados em desenvolvimento).
- Esta é uma das questões em aberto do projeto quanto à estratégia
  definitiva de produção (ver
  `docs/project-context.md#questões-em-aberto`); a Fase 1 valida a
  configuração necessária, sem fechar a decisão final de domínio/hospedagem.

## Logout

```text
1. Frontend chama POST /auth/logout (com o cookie de sessão).
2. Backend invalida/expira a sessão correspondente.
3. Backend responde com sucesso mesmo se não havia sessão ativa
   (idempotente).
```

## O que este fluxo não faz nesta fase

- Não emite nem armazena tokens de longa duração do usuário além do
  necessário para o callback.
- Não persiste sessões em banco de dados (ver limites em
  `docs/architecture/system-context.md`).
- Não implementa refresh de sessão além de reautenticação simples via novo
  login.
