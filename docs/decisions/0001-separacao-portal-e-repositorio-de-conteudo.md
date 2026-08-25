# ADR-0001: Separação entre o portal e o repositório de conteúdo

## Status

Aceita

## Contexto

O conteúdo publicado pela Central de Ajuda já é versionado no repositório
`cte-zl-ifrn/central-ajuda`, que também contém a configuração do Jekyll, os
layouts, a navegação e os workflows de build/publicação do site. Era preciso
decidir se o portal editorial seria incorporado a esse mesmo repositório
(como uma pasta ou aplicação interna) ou mantido como um projeto próprio.

## Decisão

- O `ifrn-editorial-portal` é um projeto separado do repositório
  `cte-zl-ifrn/central-ajuda`.
- `cte-zl-ifrn/central-ajuda` continua sendo o único repositório de conteúdo
  e a fonte de verdade dos documentos publicados.
- O portal é restrito a esse único repositório: ele não deve oferecer suporte
  a múltiplos repositórios de conteúdo no MVP, nem misturar código do portal
  com conteúdo editorial no mesmo repositório.

## Consequências

- O portal pode evoluir (frontend, backend, infraestrutura) sem afetar o
  histórico, os workflows ou a governança do repositório de conteúdo.
- Qualquer alteração editorial feita pelo portal chega ao `central-ajuda`
  exclusivamente via Pull Request (ver [ADR-0006](0006-fluxo-branch-e-pull-request.md)).
- Suporte a múltiplos repositórios fica fora do MVP e exigiria uma nova
  decisão arquitetural caso se torne necessário no futuro.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seções 1, 3 e 4.
