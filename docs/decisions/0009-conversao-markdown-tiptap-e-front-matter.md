# ADR-0009: Conversão Markdown ↔ Tiptap e preservação do front matter na Fase 2

## Status

Aceita

## Contexto

A Fase 2 ([docs/phase-2-plan.md](../phase-2-plan.md)) implementa o caminho
crítico de edição: carregar um documento Markdown existente no editor
Tiptap (Fase 2.1) e devolvê-lo em Markdown depois de editado (Fase 2.2),
sem ainda gravar nada no `central-ajuda` (isso é Fase 3).

[ADR-0002](0002-editor-tiptap.md) já define que o Tiptap opera sobre um
modelo de nós controlado (parágrafos, títulos, listas, negrito, itálico,
links, imagens, tabelas, blocos de aviso, blocos de código, passos
numerados, separadores) e exige que a conversão seja determinística, com
testes de round-trip — mas não decide *como* essa conversão é feita, nem o
que acontece com o front matter YAML durante o processo. Essas duas
lacunas precisavam ser fechadas antes de dividir o trabalho em sub-fases.

## Decisão

### Front matter: preservado como texto bruto, não editado nem reserializado

Nesta fase, o front matter **não é editável**. O backend separa o
documento em duas partes ao lê-lo:

- `front_matter_raw`: o bloco YAML original, incluindo os delimitadores
  `---`, exatamente como está no arquivo;
- `body`: o Markdown após o segundo delimitador.

Ao reconstruir o documento (Fase 2.2), o backend concatena
`front_matter_raw` (inalterado) com o `body` serializado a partir do
Tiptap. O front matter **não passa** por um ciclo `YAML → dict → YAML`.
Isso elimina de saída um risco real de round-trip: reserializar YAML pode
reordenar chaves, mudar estilo de aspas ou espaçamento, produzindo um
diff cosmético gigante e enganoso em um Pull Request futuro (Fase 3), sem
nenhuma mudança de conteúdo.

Um dicionário `front_matter` (parseado, somente leitura) também é
retornado pela API para exibição na interface — mas apenas para exibição.
A fonte de verdade para reconstrução do arquivo é sempre `front_matter_raw`.

### Separação front matter / corpo: feita no backend

A divisão do arquivo em `front_matter_raw` + `body` é responsabilidade do
backend (Python), não do frontend. Justificativa:

- o backend já lê o arquivo bruto do GitHub;
- [ADR-0003](0003-formato-markdown-front-matter.md) já atribui ao backend
  a validação do front matter — manter o parsing no mesmo lugar evita
  duplicar um parser YAML/delimitador em TypeScript;
- mantém a Fase 2.1 focada, no frontend, exclusivamente na conversão
  Markdown ↔ Tiptap.

### Conversão Markdown → Tiptap (parsing, Fase 2.1): no frontend, com parser controlado

O `body` (Markdown puro, sem front matter) é convertido para o documento
JSON do Tiptap no frontend, em TypeScript, usando um parser baseado em
tokens de Markdown (avaliar `markdown-it`, já usado internamente pelo
ecossistema Tiptap) mapeados explicitamente para o whitelist de nós de
[ADR-0002](0002-editor-tiptap.md). Qualquer construção de Markdown fora
desse whitelist deve ser rejeitada ou normalizada de forma previsível
(nunca silenciosamente descartada sem log), não convertida em HTML livre.

### Conversão Tiptap → Markdown (serialização, Fase 2.2): serializer próprio, não delegado integralmente a uma lib genérica

A serialização do documento JSON do Tiptap de volta para Markdown é
escrita como um serializer próprio, percorrendo a árvore de nós do
Tiptap/ProseMirror nó a nó, em vez de depender inteiramente da
serialização de uma biblioteca genérica de terceiros. Bibliotecas
genéricas de Markdown para Tiptap tendem a cobrir um superconjunto maior
de sintaxe do que o whitelist do projeto e a fazer escolhas de formatação
não necessariamente estáveis entre versões. Um serializer próprio, ainda
que mais trabalho inicial, é mais fácil de testar exaustivamente contra o
whitelist de nós e de manter determinístico — requisito explícito da
ADR-0002.

Uma biblioteca de parsing (ex.: `markdown-it`) pode e deve ser reutilizada
para o lado de *parsing*; a decisão de "serializer próprio" vale
especificamente para o sentido Tiptap → Markdown.

## Consequências

- O contrato de leitura de documento (`GET /api/documents/sample` e,
  futuramente, `GET /api/documents/{path}`) muda de um único campo
  `content` para `front_matter`, `front_matter_raw` e `body` — é uma
  mudança de contrato aceitável porque nenhum consumidor externo depende
  do formato da Fase 1 (era um spike). Os testes e a especificação OpenAPI
  existentes precisam ser atualizados na Fase 2.1.
- Testes de round-trip da Fase 2.2 só precisam cobrir `body ↔ Tiptap`; o
  front matter é comparado por igualdade de string simples (`front_matter_raw`
  inalterado), não por comparação semântica de YAML.
- Editar campos do front matter (título, categoria, tags etc.) fica fora
  do escopo da Fase 2 — é uma extensão natural para uma fase futura, uma
  vez que o modelo de edição do corpo esteja validado.
- O escopo exato de nós Markdown suportados no parser (ex.: se blocos de
  aviso e passos numerados, que não têm sintaxe Markdown padrão, entram já
  na Fase 2.1/2.2 ou ficam para depois) é decidido durante a implementação
  de cada sub-fase, dentro do whitelist já fechado pela ADR-0002.

## Referências

- [ADR-0002](0002-editor-tiptap.md) — modelo de nós do Tiptap e exigência de determinismo/round-trip.
- [ADR-0003](0003-formato-markdown-front-matter.md) — formato Markdown + front matter e responsabilidade de validação do backend.
- [docs/phase-2-plan.md](../phase-2-plan.md), [docs/phase-2.1-plan.md](../phase-2.1-plan.md), [docs/phase-2.2-plan.md](../phase-2.2-plan.md).
