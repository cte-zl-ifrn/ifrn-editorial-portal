# Frontend — `ifrn-editorial-portal` (Fase 1 / Fase 2.1)

Frontend em Vue 3 + TypeScript + Vite (ver
[ADR-0008](../docs/decisions/0008-frontend-vue-3.md)), publicado como
build estático (compatível com GitHub Pages).

Escopo: [docs/phase-1-plan.md](../docs/phase-1-plan.md) e
[docs/phase-2.1-plan.md](../docs/phase-2.1-plan.md). Contrato completo da
API consumida: [docs/api/openapi.yaml](../docs/api/openapi.yaml).

## Estrutura

```text
frontend/
├── src/
│   ├── components/    # StatusMessage, FrontMatterPanel, DocumentViewer (Tiptap)
│   ├── composables/   # useSession, useSampleDocument
│   ├── services/      # apiClient, authService, documentService
│   ├── lib/             # markdownToTiptap (parser controlado, Fase 2.1)
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

## Renderização do documento (Fase 2.1)

`HomeView.vue` converte `document.body` (Markdown) em um documento Tiptap
via `markdownToTiptap` (`src/lib/markdownToTiptap.ts`, baseado em
`markdown-it`) e renderiza em `DocumentViewer.vue` com `editable: false`
— edição é Fase 2.2. `document.front_matter` (já parseado pelo backend)
é exibido separadamente em `FrontMatterPanel.vue`, também somente
leitura. Ver [ADR-0009](../docs/decisions/0009-conversao-markdown-tiptap-e-front-matter.md)
para a estratégia de conversão e as limitações conhecidas do parser
(escopo mínimo de nós, fallback seguro para Markdown/HTML fora desse
escopo).

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
