# Fase 3.2.5 — Validação manual

Conclusão operacional da validação manual da Fase 3.2
([docs/phase-3.2-plan.md](phase-3.2-plan.md)): upload de imagem local
pela toolbar do Tiptap, gravado como asset na mesma branch/Pull Request
do documento, testado localmente contra o backend e o `central-ajuda`
reais.

Data: 2026-08-26

## Resultados

- [x] Inserir uma imagem real (arquivo local) no Tiptap, enviar, e
      confirmar que ela aparece no Pull Request em
      `assets/images/{categoria}/`, referenciada corretamente no
      Markdown do documento. Confirmado em
      [cte-zl-ifrn/central-ajuda#2](https://github.com/cte-zl-ifrn/central-ajuda/pull/2)
      (duas imagens na mesma edição, cada uma com nome próprio) e depois
      em [#5](https://github.com/cte-zl-ifrn/central-ajuda/pull/5), já
      com a referência final em URL absoluta.
- [x] Tentar selecionar um arquivo de tipo não permitido (`.exe`
      renomeado com extensão `.png`) → rejeitado imediatamente na
      seleção, com aviso claro, sem criar prévia nem tentar o envio.
- [x] Tentar um nome de arquivo com `../` → não aplicável via UI, por
      desenho (o frontend gera o próprio nome do arquivo); protegido e
      coberto por 18 testes automatizados em
      `backend/tests/test_asset_validation.py`.
- [x] Fechar (sem merge) ou confirmar o merge dos Pull Requests de
      teste com o mantenedor institucional — todos os PRs de teste
      gerados nesta validação
      ([#1](https://github.com/cte-zl-ifrn/central-ajuda/pull/1),
      [#2](https://github.com/cte-zl-ifrn/central-ajuda/pull/2),
      [#3](https://github.com/cte-zl-ifrn/central-ajuda/pull/3),
      [#5](https://github.com/cte-zl-ifrn/central-ajuda/pull/5)) foram
      **mergeados de verdade** pelo próprio mantenedor institucional
      (`@kelsoncm`), decisão explicitamente dele.

## Achados durante a validação (e correções)

Dois problemas reais foram descobertos ao testar além do roteiro
mínimo — ambos corrigidos antes de fechar a fase:

1. **Tipo de arquivo inválido não era bloqueado na seleção**: o
   atributo `accept` do `<input type="file">` é só uma dica de UI; o
   sistema operacional permitiu escolher um `.exe`, que era inserido
   como imagem quebrada sem aviso algum (a gravação em si já era
   bloqueada no backend, por assinatura de arquivo, mas a UX escondia o
   problema). Corrigido em `DocumentViewer.vue` (checagem de
   `file.type` antes de prosseguir) e `pendingAssets.ts` (mime não
   mapeado agora falha alto, em vez de rotular como `.png` em
   silêncio).
2. **Caminho relativo da imagem não funcionava de forma consistente**:
   correto na visualização do GitHub (resolvido a partir do arquivo
   fonte, 2 níveis), mas incorreto no site publicado pelo Jekyll
   (resolvido a partir da URL de saída do `permalink` da coleção, 4
   níveis) — e por isso também não aparecia ao reabrir o documento no
   portal. Corrigido gravando uma **URL absoluta do GitHub**
   (`raw.githubusercontent.com`, apontando para `main`) em vez de um
   caminho relativo — ver [ADR-0007](decisions/0007-organizacao-de-assets.md)
   para a decisão completa e o trade-off aceito.

   Achado correlato, em `cte-zl-ifrn/central-ajuda` (repositório
   separado, corrigido lá via
   [PR #4](https://github.com/cte-zl-ifrn/central-ajuda/pull/4), já
   mergeado): o `permalink` da coleção `docs` duplicava o segmento
   `docs/docs` na URL publicada — não é uma decisão do portal, mas
   contribuía para a divergência de profundidade acima.

## Confirmação final (depois das correções)

Depois do merge de [PR #5](https://github.com/cte-zl-ifrn/central-ajuda/pull/5)
(imagem inserida já com a URL absoluta) e do
[PR #4](https://github.com/cte-zl-ifrn/central-ajuda/pull/4) (permalink
corrigido), confirmado diretamente:

```
curl -sI https://raw.githubusercontent.com/cte-zl-ifrn/central-ajuda/main/assets/images/proitec/como-fazer-cursos-56a35995.png
→ HTTP/2 200

curl -sI https://cte-zl-ifrn.github.io/central-ajuda/docs/proitec/como-fazer-cursos/
→ HTTP/2 200 (URL sem "docs/docs" duplicado)
```

A imagem resolve corretamente tanto pela URL absoluta gravada quanto
pela página publicada, com a URL de permalink já corrigida.

## Efeito nos critérios de aceite da Fase 3.2 e da Fase 3

Todos os itens do roteiro de validação manual definido em
[docs/phase-3.2-plan.md](phase-3.2-plan.md#roteiro-de-validação-manual-fase-325)
foram confirmados. A Fase 3.2 está concluída — implementação e
validação manual — e, com isso, **a Fase 3 como um todo
([docs/phase-3-plan.md](phase-3-plan.md)) está concluída**: documento e
assets são gravados de forma real e confiável no `central-ajuda`, do
carregamento à publicação no site.
