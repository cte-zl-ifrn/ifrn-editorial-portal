# Frontend — `ifrn-editorial-portal` (Fase 1 / Fase 2.1 / Fase 2.2)

Frontend em Vue 3 + TypeScript + Vite (ver
[ADR-0008](../docs/decisions/0008-frontend-vue-3.md)), publicado como
build estático (compatível com GitHub Pages).

Escopo: [docs/phase-1-plan.md](../docs/phase-1-plan.md),
[docs/phase-2.1-plan.md](../docs/phase-2.1-plan.md) e
[docs/phase-2.2-plan.md](../docs/phase-2.2-plan.md). Contrato completo da
API consumida: [docs/api/openapi.yaml](../docs/api/openapi.yaml).

## Estrutura

```text
frontend/
├── src/
│   ├── components/    # StatusMessage, FrontMatterPanel, DocumentViewer (Tiptap)
│   ├── composables/   # useSession, useSampleDocument
│   ├── services/      # apiClient, authService, documentService
│   ├── lib/             # markdownToTiptap, tiptapToMarkdown, tiptapExtensions
│   ├── types/          # tipos compartilhados (espelham a API) e tiptap.ts
│   ├── views/           # HomeView, LoginView, UnauthorizedView
│   ├── router/           # rotas e guarda de navegação por sessão
│   ├── App.vue
│   └── main.ts
├── tests/               # testes unitários (Vitest + @vue/test-utils)
├── package.json
├── tsconfig*.json
├── vite.config.ts        # inclui configuração do Vitest
└── eslint.config.mjs
```

## Edição do documento (Fase 2.1 + Fase 2.2)

`HomeView.vue` converte `document.body` (Markdown) em um documento Tiptap
via `markdownToTiptap` (`src/lib/markdownToTiptap.ts`, baseado em
`markdown-it`) e renderiza em `DocumentViewer.vue`, que agora é editável
(`editable`), com uma toolbar mínima (negrito, itálico, H1–H3, listas,
link, imagem). A cada alteração, `DocumentViewer` emite o documento Tiptap
atual (`update:content`); `HomeView.vue` serializa esse documento de volta
para Markdown com `tiptapToMarkdown` (`src/lib/tiptapToMarkdown.ts`,
serializer próprio, não delegado a uma lib genérica) e exibe a prévia do
resultado (`document.front_matter_raw` + corpo serializado) — **nada é
enviado ao backend ou ao GitHub**; a prévia é só client-side, para
inspeção manual (Fase 2.2.5).

`document.front_matter` (já parseado pelo backend) continua somente
leitura em `FrontMatterPanel.vue` — front matter não é editável nesta
fase. A superfície de edição do Tiptap é restrita em
`src/lib/tiptapExtensions.ts` ao mesmo whitelist de nós do parser
(desabilita blockquote, codeBlock, strike e underline do StarterKit), para
que o editor nunca produza um nó que o serializer não saiba serializar.

Ver [ADR-0009](../docs/decisions/0009-conversao-markdown-tiptap-e-front-matter.md)
para a estratégia completa de conversão, preservação do front matter e as
limitações conhecidas (normalizações cosmética documentadas no cabeçalho
de `tiptapToMarkdown.ts`).

## Configuração

```bash
cp .env.example .env.local
```

`VITE_API_BASE_URL` é a única variável usada — aponta para o backend local
(`http://localhost:8000` por padrão). Nenhum segredo é ou deve ser colocado
em variáveis `VITE_*`: tudo que começa com esse prefixo é embutido no
bundle público (RNF-21).

## Executando localmente

```bash
npm install
npm run dev
```

Requer o backend rodando (ver [../backend/README.md](../backend/README.md))
para que o login e a leitura do documento funcionem; sem backend, a
aplicação fica no estado de "erro de comunicação com a API".

## Login

O login **não** é feito por uma chamada de API — o botão em `LoginView.vue`
redireciona o navegador inteiro para `GET {VITE_API_BASE_URL}/auth/login`
(ver `src/services/authService.ts`). O frontend nunca troca código ou token
OAuth diretamente (ver
[docs/architecture/authentication-flow.md](../docs/architecture/authentication-flow.md)).

## Estados da interface

A navegação (`src/router/index.ts`) resolve o estado de sessão
(`useSession`) antes de decidir a rota, e redireciona para:

| Estado da sessão | Rota | Componente |
|---|---|---|
| `unauthenticated` | `/login` | `LoginView.vue` |
| `unauthorized` | `/unauthorized` | `UnauthorizedView.vue` |
| `authorized` | `/` | `HomeView.vue` (carrega o documento de exemplo) |
| `loading` | qualquer | tela de carregamento em `App.vue` |
| `error` (falha de comunicação com a API) | qualquer | mensagem de erro com opção de tentar novamente, em `App.vue` |

`HomeView.vue` também trata os estados de carregamento, erro e sucesso da
leitura do documento (`useSampleDocument`), de forma independente do estado
de sessão.

## Testes e qualidade

```bash
npm run test          # Vitest
npm run test:coverage # Vitest com cobertura (v8)
npm run lint           # ESLint (Vue + TypeScript)
npm run type-check     # vue-tsc
npm run build          # build de produção (usado também como verificação de tipos + bundling)
```

Chamadas de API são isoladas com mocks de `fetch`/módulo nos testes — não
há dependência de rede ou do backend real (RNF-18).
