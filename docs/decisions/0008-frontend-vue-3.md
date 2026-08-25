# ADR-0008: Frontend em Vue 3, TypeScript e Vite

## Status

Aceita

## Contexto

O documento de arquitetura inicial ([docs/initial-architecture.md](../initial-architecture.md),
seção 6.1) já definia que o frontend seria uma aplicação estática publicada
no GitHub Pages, hospedando o editor Tiptap, mas não fixava um framework de
componente. A escolha do framework ficou registrada como questão em aberto
em [docs/project-context.md](../project-context.md) ("framework do
frontend") e na seção 24 de `docs/initial-architecture.md`.

Antes de criar o esqueleto do frontend na Fase 1, essa decisão precisava ser
tomada e registrada.

## Decisão

O frontend do `ifrn-editorial-portal` será construído com:

- **Vue 3** (Composition API) como framework de componentes;
- **TypeScript** como linguagem;
- **Vite** como build tool e servidor de desenvolvimento;
- **Vue Router** para as rotas que a experiência exigir (login, painel,
  edição, acesso negado);
- **Vitest** para testes unitários;
- **Playwright** (ou ferramenta equivalente) para testes end-to-end
  futuros, quando o fluxo de edição completo existir;
- **Tiptap para Vue** (`@tiptap/vue-3`) como integração do editor com a
  camada de componentes, quando a edição for implementada em fase futura.

Não será usado React, Next.js ou qualquer outro framework de componentes
como padrão do projeto.

### Preferência e experiência da equipe

A equipe responsável pelo portal tem preferência declarada e experiência
prática com Vue.js. Priorizar uma tecnologia em que a equipe já é produtiva
reduz o tempo de rampa da Fase 1 e o risco de decisões arquiteturais erradas
por desconhecimento da ferramenta — um fator mais determinante, neste
projeto, do que diferenças teóricas de desempenho entre frameworks modernos.

### Adequação a um frontend estático

O portal é, por decisão arquitetural anterior, um frontend estático hospedado
no GitHub Pages, sem servidor de renderização (ver seção 6.1 de
`docs/initial-architecture.md`). O Vue 3 com Vite produz um build totalmente
estático (HTML, CSS e JS versionados por hash), sem exigir SSR, Node.js em
produção ou infraestrutura adicional — compatível diretamente com GitHub
Pages e com o princípio de que nenhuma credencial privilegiada deve chegar
ao navegador.

### Integração com Tiptap

O Tiptap (decisão registrada em [ADR-0002](0002-editor-tiptap.md)) publica
um pacote de integração oficial para Vue 3 (`@tiptap/vue-3`), com suporte de
primeira classe à Composition API, incluindo o componente `EditorContent` e
o composable `useEditor`. Isso elimina a necessidade de uma camada de
adaptação própria entre o editor e o framework de componentes. A adoção
efetiva do editor Tiptap dentro do Vue fica para a fase em que a edição for
implementada; esta ADR apenas garante que a escolha de framework não cria
atrito com essa integração futura.

### Alternativas consideradas

| Alternativa | Motivo de não adoção |
|---|---|
| React + Next.js | Não é a tecnologia de preferência da equipe; Next.js pressupõe SSR/Node em produção, o que não se alinha ao frontend estático já decidido; migraria a experiência da equipe sem ganho concreto para o escopo do MVP. |
| Svelte/SvelteKit | Equipe sem experiência prévia; ecossistema de integração com Tiptap menos maduro que o de Vue. |
| Frontend sem framework (HTML/JS puro) | Aumentaria o esforço de manter estado de autenticação, roteamento e o editor Tiptap sem as abstrações que um framework oferece, sem redução de complexidade real. |

## Consequências

### Positivas

- Aproveita a experiência e a preferência já existentes da equipe, reduzindo
  risco de execução na Fase 1.
- Build estático nativo, compatível com GitHub Pages sem infraestrutura
  adicional.
- Integração oficial e madura com Tiptap via `@tiptap/vue-3`.
- Vite oferece um ciclo de desenvolvimento local rápido e configuração
  simples de variáveis de ambiente (`import.meta.env`), alinhado ao
  requisito de não embutir segredos no bundle.
- TypeScript reduz erros de integração entre frontend e backend,
  especialmente na tipagem dos contratos descritos em
  [docs/api/openapi.yaml](../api/openapi.yaml).

### Negativas / trade-offs

- Introduz uma tecnologia adicional (Vue) ao ecossistema do projeto, que já
  inclui Python no backend — não há reaproveitamento de código entre as
  camadas.
- O ecossistema de bibliotecas de terceiros para Vue é menor que o do React,
  o que pode exigir mais trabalho próprio em componentes de UI mais
  avançados no futuro.
- Testes end-to-end (Playwright) e testes unitários (Vitest) são
  ferramentas adicionais a manter configuradas e atualizadas no CI.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 6.1.
- [ADR-0002](0002-editor-tiptap.md) — editor Tiptap.
- [ADR-0005](0005-backend-lambda-api-gateway.md) — backend e hospedagem do
  frontend no GitHub Pages.
- [docs/phase-1-plan.md](../phase-1-plan.md).
