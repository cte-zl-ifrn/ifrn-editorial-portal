# ADR-0005: Backend inicial em AWS Lambda + API Gateway HTTP API

## Status

Aceita

## Contexto

O portal precisa de um backend que concentre autenticação, autorização,
validação e a integração privilegiada com o GitHub, mantendo o frontend
estático e sem credenciais sensíveis. É preciso escolher uma base de
infraestrutura para o MVP sem incorrer em complexidade operacional
desnecessária.

## Decisão

O backend será composto inicialmente por funções AWS Lambda expostas por um
API Gateway HTTP API. O frontend será uma aplicação estática publicada no
GitHub Pages. Segredos (chave privada da GitHub App, client secret, segredos
de sessão) ficam no AWS Secrets Manager; logs e métricas em Amazon
CloudWatch.

## Consequências

- O MVP evita banco de dados como fonte de verdade do conteúdo; estado pode
  ser reconstruído a partir de Pull Requests, commits, branches e metadados
  de autenticação de curta duração.
- Serviços adicionais (S3, DynamoDB, SQS, WAF, X-Ray) só devem ser
  adicionados quando houver necessidade concreta.
- AWS SAM é a opção sugerida para infraestrutura como código; Terraform ou
  OpenTofu podem ser adotados se a governança institucional exigir.
- Essa escolha é rotulada como "recomendada" no documento de arquitetura
  inicial — deve ser revisitada se restrições institucionais (custo, política
  de nuvem) tornarem outra plataforma mais adequada.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seções 6.2, 17, 18.
