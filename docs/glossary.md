# Glossário

Termos usados na documentação do `ifrn-editorial-portal`, para reduzir
ambiguidade entre quem trabalha no portal, no repositório de conteúdo e na
parte institucional.

| Termo | Significado |
|---|---|
| **Portal** | O `ifrn-editorial-portal`: aplicação de autoria, validação, autenticação e submissão de conteúdo. |
| **Central de Ajuda** | O produto/site final publicado a partir do repositório de conteúdo. |
| **Repositório de conteúdo** | `cte-zl-ifrn/central-ajuda` — fonte de verdade dos documentos, assets, layouts e configuração do Jekyll. O único repositório que o portal está autorizado a alterar. |
| **Repositório do portal** | `cte-zl-ifrn/ifrn-editorial-portal` — código do frontend, backend e infraestrutura do portal. |
| **MVP** | Minimum Viable Product — o conjunto mínimo de funcionalidades descrito na seção 3 de [docs/initial-architecture.md](initial-architecture.md), usado para delimitar o que entra e o que fica fora da primeira entrega. |
| **Tiptap** | Editor de texto rico baseado em ProseMirror, usado como editor visual e estruturado do portal (ver [ADR-0002](decisions/0002-editor-tiptap.md)). |
| **Front matter** | Bloco de metadados em YAML no início de um arquivo Markdown (`title`, `category`, `status` etc.), delimitado por `---`. |
| **GitHub App** | Tipo de integração do GitHub com identidade própria (não vinculada a um usuário), usada para autenticar o backend do portal perante o repositório de conteúdo (ver [ADR-0004](decisions/0004-integracao-github-app.md)). |
| **Installation access token** | Token de curta duração emitido para uma instalação específica de uma GitHub App, usado para operações de API em nome da aplicação. |
| **JWT (JSON Web Token)** | Token assinado usado pela GitHub App para se autenticar junto à API do GitHub antes de obter um installation access token. |
| **Submissão** | Uma proposta de alteração de conteúdo enviada pelo portal: inclui documento, assets, resumo e tipo de alteração, e resulta em uma branch e um Pull Request. |
| **Branch de submissão** | Branch temporária criada para uma submissão, no formato `portal/{tipo}/{ano}/{id}-{slug}`. |
| **Pull Request (PR)** | Proposta de merge no GitHub. Todo conteúdo alterado pelo portal chega ao `main` do repositório de conteúdo exclusivamente por PR (ver [ADR-0006](decisions/0006-fluxo-branch-e-pull-request.md)). |
| **Asset** | Arquivo referenciado por um documento: imagem (`assets/images/`) ou arquivo para download (`assets/files/`) (ver [ADR-0007](decisions/0007-organizacao-de-assets.md)). |
| **Slug** | Identificador textual curto, normalizado (sem espaços/acentos), usado para compor caminhos de documentos e assets. |
| **Categoria** | Agrupamento temático de um documento ou asset (ex.: `moodle`, `sistemas`, `institucional`), usado na composição de caminhos. |
| **`base_sha`** | Referência da versão do documento que o usuário estava editando, usada pelo backend para detectar conflitos de edição concorrente antes de gravar. |
| **ADR (Architecture Decision Record)** | Registro curto de uma decisão arquitetural, seu contexto e suas consequências. Ver [docs/decisions/](decisions/README.md). |
| **Definition of Done (DoD)** | Critérios mínimos que uma alteração precisa satisfazer para ser considerada concluída. Ver [docs/definition-of-done.md](definition-of-done.md). |
| **LGPD** | Lei Geral de Proteção de Dados (Lei nº 13.709/2018), referência institucional para o tratamento de dados pessoais coletados pelo portal. |
| **API Gateway HTTP API** | Serviço da AWS usado para expor as funções Lambda do backend como endpoints HTTP. |
| **AWS Lambda** | Serviço de computação serverless da AWS usado para executar o backend do portal (ver [ADR-0005](decisions/0005-backend-lambda-api-gateway.md)). |
| **AWS Secrets Manager** | Serviço da AWS usado para armazenar segredos do backend (chave privada da GitHub App, client secret, segredos de sessão). |
