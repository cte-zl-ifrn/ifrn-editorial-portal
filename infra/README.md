# Infraestrutura — `ifrn-editorial-portal`

Infraestrutura mínima para a Fase 1 (ver
[docs/phase-1-plan.md](../docs/phase-1-plan.md)) e para uma futura
implantação real, conforme
[ADR-0005](../docs/decisions/0005-backend-lambda-api-gateway.md).

**Nesta fase, nenhum recurso AWS real é criado.** O conteúdo deste
diretório é template e documentação, validável localmente.

## Estrutura

```text
infra/
├── sam/
│   ├── template.yaml       # API Gateway HTTP API + Lambda (backend)
│   ├── parameters/          # parâmetros por ambiente (SAM)
│   └── README.md
└── environments/
    ├── development.yaml    # configuração conceitual de desenvolvimento
    └── production.yaml     # configuração conceitual de produção (placeholders)
```

## Execução local sem AWS

O caminho recomendado para desenvolver e validar a Fase 1 **não** passa por
este diretório: rode o backend com `uvicorn` e o frontend com `npm run dev`
diretamente (ver `backend/README.md` e `frontend/README.md`). O template
SAM é relevante apenas quando alguém for validar ou planejar uma
implantação real.

## Segredos

Nenhum segredo é definido neste diretório. Em produção, os segredos
(client secret da OAuth App, chave privada da GitHub App, segredo de
sessão) ficam no AWS Secrets Manager, referenciado pelo parâmetro
`SecretsManagerSecretArn` do template SAM — ver
[infra/sam/README.md](sam/README.md).
