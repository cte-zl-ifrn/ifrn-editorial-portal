# Fase 1.5 — Validação manual

Conclusão operacional da validação manual do caminho crítico de leitura da
Fase 1 (ver [docs/phase-1-plan.md](phase-1-plan.md)) contra o GitHub real —
OAuth App e GitHub App reais, em vez dos mocks usados nos testes
automatizados (`respx`/Vitest). Esta era a única lacuna registrada como
limitação ao final da Fase 1.

Data: 2026-08-25

## Resultados

- [x] Login com usuário autorizado: sessão criada e documento lido
- [x] Login com usuário sem permissão: acesso negado corretamente

## Ambiente

- OAuth App criada para desenvolvimento local
- Homepage URL: `http://localhost:5173`
- Redirect URI: `http://localhost:8000/auth/callback`

## Observações

- Client secret gerado e armazenado localmente, fora do repositório
- Fluxo validado em máquina Linux

## Efeito nos critérios de aceite da Fase 1

Confirma, contra o GitHub real, os seguintes critérios de aceite listados em
[docs/phase-1-plan.md](phase-1-plan.md#critérios-de-aceite):

- login funcional no ambiente de desenvolvimento local;
- `GET /api/me` retornando a identidade correta para o usuário autorizado;
- a GitHub App consegue ler o conteúdo permitido (documento lido com
  sucesso para o usuário autorizado);
- usuário sem permissão compatível no repositório rejeitado (RF-16);
- nenhum segredo (client secret) versionado no repositório.

Com isso, a única lacuna apontada como limitação ao final da Fase 1 —
validação do fluxo fim a fim contra o GitHub real, fora dos mocks dos
testes automatizados — está encerrada.
