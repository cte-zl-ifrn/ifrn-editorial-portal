# IFRN Editorial Portal

## Documentação inicial de arquitetura e produto

- **Projeto:** `ifrn-editorial-portal`
- **Repositório de conteúdo:** `cte-zl-ifrn/central-ajuda`
- **Status:** proposta inicial
- **Formato editorial:** Markdown com front matter YAML
- **Editor:** Tiptap
- **Integração:** GitHub App
- **Backend recomendado:** AWS Lambda + API Gateway HTTP API

## 1. Visão geral

O `ifrn-editorial-portal` é um portal editorial para usuários autorizados criarem e alterarem conteúdo da Central de Ajuda sem precisarem conhecer Git, GitHub ou a sintaxe Markdown.

O portal será um projeto separado do repositório `central-ajuda`. O repositório de conteúdo continuará sendo a fonte de verdade dos documentos publicados, enquanto o portal fornecerá a experiência de autoria, validação, autenticação, autorização e submissão.

Toda alteração editorial deverá ser proposta por meio de uma branch temporária e um Pull Request. O portal não deverá fazer push direto na branch `main`.

## 2. Objetivos

### Objetivos principais

- Oferecer edição visual e estruturada por meio do Tiptap.
- Permitir criação e edição de documentos Markdown.
- Permitir envio de imagens para `assets/images`.
- Permitir envio de arquivos para `assets/files`.
- Usar GitHub App para integração segura com o GitHub.
- Restringir o sistema ao repositório `cte-zl-ifrn/central-ajuda`.
- Preservar revisão, histórico e rastreabilidade por Pull Request.
- Reduzir a necessidade de interação direta do usuário com a interface do GitHub.
- Manter o repositório de conteúdo independente do código do portal.

### Objetivos não funcionais

- Não expor credenciais privilegiadas no navegador.
- Impedir alterações fora dos caminhos permitidos.
- Validar documentos e assets antes da submissão.
- Preservar a autoria humana da solicitação.
- Permitir operação local para desenvolvimento.
- Automatizar testes e implantação.
- Considerar requisitos de segurança, acessibilidade e LGPD.

## 3. Escopo

### Incluído no MVP

- Login com GitHub.
- Verificação da permissão do usuário no repositório.
- Listagem de documentos Markdown.
- Criação de novos documentos.
- Edição de documentos existentes.
- Editor visual Tiptap.
- Prévia renderizada.
- Conversão controlada de Tiptap para Markdown.
- Validação de front matter, conteúdo e links básicos.
- Upload de imagens.
- Upload de arquivos autorizados.
- Criação de branch por submissão.
- Criação de Pull Request.
- Registro da autoria e da justificativa.
- Consulta do status da submissão.
- Logs técnicos e tratamento de erros.
- Documentação de desenvolvimento, implantação e operação.

### Fora do MVP

- Edição colaborativa em tempo real.
- Publicação direta na branch principal.
- Suporte a múltiplos repositórios.
- Suporte inicial a RST ou Sphinx.
- Integração inicial com SUAP, LDAP ou outro diretório institucional.
- Aprovação editorial completa dentro do portal.
- Edição offline.
- Workflow editorial com múltiplos níveis de aprovação.
- Banco de dados como fonte principal do conteúdo.
- Armazenamento permanente de rascunhos complexos.

## 4. Princípios arquiteturais

1. O repositório `central-ajuda` é a fonte de verdade do conteúdo.
2. O portal é uma camada de autoria e submissão, não um CMS independente.
3. Nenhuma credencial privilegiada deve chegar ao frontend.
4. Nenhuma alteração deve ser enviada diretamente para `main`.
5. Cada submissão deve ser isolada em uma branch própria.
6. Cada submissão deve resultar em um Pull Request.
7. O usuário edita um modelo editorial controlado, e não uma sintaxe livre.
8. O caminho dos arquivos deve ser calculado e validado pelo backend.
9. A autenticação e a autorização são responsabilidades distintas.
10. O design deve permitir futura mudança do gerador de site ou formato de saída.

## 5. Repositórios

### 5.1 Repositório de conteúdo

```text
cte-zl-ifrn/central-ajuda
```

Responsabilidades:

- documentos Markdown;
- front matter;
- imagens;
- arquivos para download;
- configuração do Jekyll;
- layouts e includes;
- navegação;
- workflows de validação e publicação;
- histórico editorial;
- Pull Requests de conteúdo.

### 5.2 Repositório do portal

```text
cte-zl-ifrn/ifrn-editorial-portal
```

Estrutura inicial sugerida:

```text
ifrn-editorial-portal/
├── frontend/
├── backend/
├── infra/
├── docs/
├── tests/
├── .github/
│   └── workflows/
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

Responsabilidades:

- frontend do portal;
- editor Tiptap;
- autenticação e sessão;
- autorização;
- integração com GitHub;
- conversão para Markdown;
- validação de documentos e assets;
- criação de branches e Pull Requests;
- infraestrutura como código;
- testes e observabilidade.

## 6. Arquitetura de referência

```text
+-----------------------+
| Usuário autorizado    |
+-----------+-----------+
            |
            | HTTPS
            v
+-----------------------+
| Frontend estático     |
| GitHub Pages          |
| Tiptap                |
+-----------+-----------+
            |
            | HTTPS, cookie de sessão
            v
+-----------------------+
| API Gateway           |
| HTTP API              |
+-----------+-----------+
            |
            v
+-----------------------+
| AWS Lambda            |
| API e regras de       |
| negócio               |
+---+-------+-------+---+
    |       |       |
    |       |       +----------------+
    |       |                        |
    |       v                        v
    |  Secrets Manager          CloudWatch
    |  GitHub App PEM            Logs e métricas
    |
    v
+-----------------------+
| GitHub App            |
| Instalação no         |
| central-ajuda         |
+-----------+-----------+
            |
            v
+-----------------------+
| cte-zl-ifrn/          |
| central-ajuda         |
| branch + Pull Request |
+-----------------------+
```

### 6.1 Frontend

O frontend será uma aplicação estática publicada no GitHub Pages, construída
com Vue 3, TypeScript e Vite (ver [ADR-0008](decisions/0008-frontend-vue-3.md)).
Ele deverá:

- apresentar o login;
- exibir a identidade do usuário;
- listar documentos disponíveis;
- carregar o conteúdo atual;
- oferecer o editor Tiptap;
- exibir prévia;
- permitir seleção e upload de assets;
- mostrar erros de validação;
- solicitar justificativa da alteração;
- exibir o resultado da submissão;
- acompanhar o status do Pull Request.

O frontend não deverá conter:

- chave privada da GitHub App;
- token de instalação;
- client secret;
- credencial de AWS;
- permissões fixas que substituam a autorização no backend.

### 6.2 Backend

O backend será composto inicialmente por funções AWS Lambda expostas por API Gateway HTTP API. Pode ser implementado em Python com FastAPI adaptado para Lambda, ou com handlers Lambda mais diretos.

Responsabilidades:

- gerenciar autenticação e sessão;
- identificar o usuário autenticado;
- verificar a permissão no repositório;
- validar requisições;
- buscar conteúdo no GitHub;
- converter e validar Markdown;
- gerar nomes de arquivos;
- processar assets;
- criar branch;
- gravar alterações;
- criar Pull Request;
- retornar status;
- registrar eventos e erros.

### 6.3 GitHub App

A GitHub App deverá ser instalada exclusivamente no repositório:

```text
cte-zl-ifrn/central-ajuda
```

Permissões iniciais sugeridas:

| Recurso | Permissão | Motivo |
|---|---|---|
| Contents | Read and write | Ler e gravar documentos e assets |
| Pull requests | Read and write | Criar e consultar Pull Requests |
| Metadata | Read-only | Consultar informações básicas |

Não solicitar inicialmente permissões para:

- workflows;
- administração da organização;
- usuários;
- secrets;
- deployments;
- issues, salvo necessidade futura.

O backend deverá gerar um JWT para a aplicação e solicitar um installation access token de curta duração. Tokens e chaves não deverão ser persistidos no frontend.

## 7. Usuários e autorização

### 7.1 Autenticação

O usuário deverá autenticar-se com sua conta GitHub. O sistema deverá criar uma sessão própria após validar o retorno do GitHub.

Fluxo conceitual:

```text
1. Usuário inicia login.
2. Backend gera estado de autorização.
3. Usuário autoriza no GitHub.
4. GitHub redireciona para o callback.
5. Backend valida estado e código.
6. Backend identifica o usuário.
7. Backend verifica a permissão no repositório.
8. Backend cria sessão segura.
9. Frontend acessa a API usando a sessão.
```

A sessão deverá preferencialmente ser mantida por cookie `HttpOnly`, `Secure` e com política `SameSite` adequada. O tempo de expiração deverá ser curto e renovável de forma controlada.

### 7.2 Regra de acesso

O portal ficará disponível para usuários que possuam permissão compatível no repositório `central-ajuda`.

Sugestão inicial:

| Permissão GitHub | Comportamento |
|---|---|
| Sem acesso | Acesso negado |
| Leitura | Visualização opcional |
| Triage | Visualização; edição conforme política definida |
| Write | Criar e enviar alterações |
| Maintain | Criar, enviar e acompanhar alterações |
| Admin | Todas as funções administrativas futuras |

A implementação do MVP pode permitir apenas usuários com permissão `write`, `maintain` ou `admin` para operações editoriais.

## 8. Fluxo editorial

### 8.1 Edição de documento

```text
1. Usuário autentica.
2. Portal verifica autorização.
3. Usuário seleciona documento.
4. Backend lê a versão atual.
5. Portal converte o Markdown para o modelo do Tiptap.
6. Usuário edita o conteúdo.
7. Portal apresenta prévia.
8. Portal executa validações locais.
9. Usuário informa resumo da alteração.
10. Backend repete as validações.
11. Backend verifica se a versão não mudou.
12. Backend cria uma branch.
13. Backend grava o Markdown e assets relacionados.
14. Backend cria o Pull Request.
15. Usuário recebe o identificador e o link do PR.
16. Workflow do repositório executa validações.
17. Revisor aprova e faz merge.
18. O site é publicado pelo repositório de conteúdo.
```

### 8.2 Criação de documento

O portal deverá gerar o caminho a partir de categoria e slug controlados:

```text
_docs/{categoria}/{slug}.md
```

O usuário não deverá informar um caminho arbitrário.

### 8.3 Branches

Formato sugerido:

```text
portal/{tipo}/{ano}/{id}-{slug}
```

Exemplo:

```text
portal/update/2026/000123-acesso-moodle
```

A branch deverá ser derivada da versão atual de `main`. O identificador da submissão deverá ser único.

### 8.4 Pull Request

Cada Pull Request deverá conter:

- título objetivo;
- resumo da alteração;
- usuário solicitante;
- data e hora;
- tipo de alteração;
- lista de arquivos modificados;
- resultado das validações;
- observações para o revisor;
- referência ao portal.

Modelo inicial:

```markdown
## Alteração proposta

<!-- Resumo gerado ou informado pelo autor. -->

## Autor da solicitação

- Usuário: @usuario
- Data: 2026-08-25T10:27:00-03:00
- Origem: ifrn-editorial-portal

## Arquivos alterados

<!-- Lista gerada automaticamente. -->

## Validações

- [ ] Markdown válido
- [ ] Front matter válido
- [ ] Links verificados
- [ ] Texto alternativo informado para imagens
- [ ] Revisão institucional
```

## 9. Modelo editorial Markdown

O formato de armazenamento será Markdown com front matter YAML.

Exemplo:

```markdown
---
title: "Como acessar o Moodle"
description: "Orientações para o primeiro acesso ao Moodle institucional."
category: "moodle"
audience: "Servidores e estudantes"
tags:
  - acesso
  - autenticação
status: "published"
---

# Como acessar o Moodle

Conteúdo do documento.
```

Campos sugeridos:

| Campo | Origem | Obrigatório |
|---|---|---:|
| `title` | Usuário/sistema | Sim |
| `description` | Usuário | Recomendado |
| `category` | Configuração | Sim |
| `audience` | Usuário | Recomendado |
| `tags` | Usuário | Não |
| `status` | Sistema/revisor | Sim |
| `author` | Sistema | Sim |
| `created_at` | Sistema | Sim para novos documentos |
| `updated_at` | Sistema | Sim |
| `submission_id` | Sistema | Recomendado |

O portal não deverá permitir edição livre de campos que possam alterar o comportamento do site, como `layout`, `permalink`, configurações de build ou scripts.

## 10. Tiptap

### 10.1 Modelo permitido

O editor deverá aceitar inicialmente:

- parágrafos;
- títulos;
- listas com marcadores;
- listas numeradas;
- negrito;
- itálico;
- links;
- imagens;
- tabelas;
- blocos de aviso;
- blocos de código;
- passos numerados;
- separadores;
- texto alternativo de imagens.

### 10.2 Conversão

O fluxo recomendado é:

```text
Markdown existente
        ↓
Parser controlado
        ↓
Documento JSON do Tiptap
        ↓
Edição
        ↓
Validação do JSON
        ↓
Serializer Markdown
        ↓
Markdown validado
```

A conversão deverá ser determinística sempre que possível. O sistema deve evitar alterações cosméticas desnecessárias no documento quando o usuário não tiver alterado determinado trecho.

### 10.3 HTML e conteúdo perigoso

O portal deverá remover ou rejeitar:

- JavaScript;
- handlers HTML como `onclick`;
- iframes não autorizados;
- scripts embutidos;
- URLs com esquemas perigosos;
- SVG contendo scripts;
- atributos HTML não permitidos.

## 11. Assets

### 11.1 Estrutura

```text
assets/
├── images/
│   ├── moodle/
│   ├── sistemas/
│   ├── processos/
│   └── institucional/
└── files/
    ├── manuais/
    ├── formularios/
    └── modelos/
```

### 11.2 Imagens

Formato sugerido:

```text
assets/images/{categoria}/{slug}-{id}.{extensão}
```

Exemplo:

```text
assets/images/moodle/acesso-moodle-000123.png
```

Regras:

- aceitar somente extensões configuradas;
- validar MIME type e assinatura do arquivo;
- limitar tamanho;
- exigir texto alternativo;
- normalizar o nome;
- impedir traversal de diretórios;
- impedir sobrescrita não autorizada;
- rejeitar conteúdo SVG perigoso;
- preservar a imagem no mesmo Pull Request do documento.

Referência gerada:

```markdown
![Tela de acesso ao Moodle](../../assets/images/moodle/acesso-moodle-000123.png)
```

O caminho final deve ser calculado segundo a localização real do documento e validado pelo backend.

### 11.3 Arquivos

Formato sugerido:

```text
assets/files/{categoria}/{slug}-{id}.{extensão}
```

Formatos iniciais possíveis:

```text
.pdf
.docx
.xlsx
.odt
.ods
.zip
```

A lista deve ser configurável. Arquivos executáveis, scripts e formatos não autorizados devem ser rejeitados.

Referência gerada:

```markdown
[Baixar o manual de acesso ao Moodle](../../assets/files/manuais/manual-acesso-000123.pdf)
```

## 12. API inicial

Endpoints sugeridos:

```text
GET  /health
GET  /auth/login
GET  /auth/callback
POST /auth/logout
GET  /api/me
GET  /api/documents
GET  /api/documents/{path}
POST /api/submissions
GET  /api/submissions/{id}
GET  /api/submissions/{id}/status
POST /api/assets/validate
```

### 12.1 Regras da API

- O backend deve validar autenticação em todos os endpoints protegidos.
- O backend deve impor o proprietário e o repositório configurados.
- O frontend não deve escolher o repositório de destino.
- O backend deve validar tamanho e estrutura do payload.
- O backend deve recusar caminhos fora das raízes permitidas.
- O backend deve usar idempotência para evitar submissões duplicadas.
- Erros não devem revelar tokens, chaves ou detalhes internos.
- Respostas devem possuir identificadores úteis para rastreamento.

### 12.2 Submissão conceitual

```json
{
  "document": {
    "path": "_docs/moodle/acesso.md",
    "title": "Como acessar o Moodle",
    "content": "# Como acessar o Moodle\n\nConteúdo...",
    "base_sha": "sha-da-versao-lida"
  },
  "assets": [
    {
      "kind": "image",
      "filename": "tela-login.png",
      "alt": "Tela de acesso ao Moodle",
      "content": "base64"
    }
  ],
  "summary": "Atualização das instruções de primeiro acesso",
  "change_type": "update"
}
```

Os campos `owner`, `repo`, `branch`, `author`, caminho definitivo e estado da submissão devem ser controlados pelo backend.

## 13. Conflitos e concorrência

Antes de gravar, o backend deve verificar se o documento ainda possui a mesma versão que foi carregada.

Se a versão mudou:

1. não sobrescrever o conteúdo;
2. retornar erro de conflito;
3. informar que o documento foi atualizado;
4. permitir recarregar a versão atual;
5. oferecer comparação quando possível.

O sistema nunca deve ocultar uma alteração concorrente.

## 14. Segurança

### Segredos

Armazenar no AWS Secrets Manager:

- chave privada da GitHub App;
- client secret, se aplicável;
- segredos de sessão;
- chaves auxiliares de integração.

Não armazenar segredos em:

- código-fonte;
- arquivos `.env` versionados;
- bundle do frontend;
- `localStorage`;
- parâmetros de URL;
- logs.

### Requisições

- usar HTTPS;
- validar origem e CORS;
- usar proteção contra CSRF quando aplicável;
- aplicar limitação de requisições;
- validar tamanho dos uploads;
- validar tipos e extensões;
- normalizar nomes;
- impedir path traversal;
- aplicar Content Security Policy;
- configurar cabeçalhos de segurança;
- evitar mensagens de erro detalhadas em produção.

### GitHub

- limitar a GitHub App ao único repositório;
- solicitar somente permissões necessárias;
- usar tokens de curta duração;
- não usar token pessoal de administrador como credencial da aplicação;
- proteger a branch `main`;
- exigir status checks antes do merge;
- revisar alterações de workflow separadamente.

## 15. LGPD e privacidade

O sistema deverá coletar somente dados necessários para autenticação, autorização, auditoria e comunicação.

Dados potencialmente tratados:

- identificador GitHub;
- nome público;
- nome de usuário;
- avatar, se necessário;
- e-mail, somente se necessário;
- registros de submissão;
- endereço IP e dados técnicos nos logs, conforme política institucional.

Medidas sugeridas:

- documentar a finalidade do tratamento;
- definir prazo de retenção dos logs;
- restringir acesso aos dados;
- não armazenar tokens de usuário além do necessário;
- registrar a base institucional aplicável;
- fornecer política de privacidade do portal;
- evitar inserir dados pessoais desnecessários no conteúdo publicado;
- revisar os dados incluídos automaticamente no Pull Request.

A análise jurídica e institucional deverá ser realizada pela organização responsável antes da produção.

## 16. CI/CD

### Portal

O pipeline do portal deverá executar:

- lint;
- formatação;
- testes unitários;
- testes de integração;
- build do frontend;
- verificação de dependências;
- análise estática;
- verificação de segredos;
- implantação em ambiente de desenvolvimento;
- implantação em produção mediante aprovação.

### Conteúdo

O repositório `central-ajuda` deverá validar Pull Requests com:

- build do Jekyll;
- validação de front matter;
- verificação de links;
- verificação de referências a assets;
- teste de arquivos permitidos;
- checagem de acessibilidade básica;
- geração de prévia quando possível.

## 17. Infraestrutura

Estrutura sugerida:

```text
infra/
├── sam/
│   ├── template.yaml
│   └── parameters/
├── iam/
├── environments/
│   ├── development.yaml
│   └── production.yaml
└── README.md
```

AWS SAM é uma opção adequada para o MVP por sua proximidade com Lambda e API Gateway. Terraform ou OpenTofu podem ser adotados caso a governança institucional exija uma ferramenta de infraestrutura mais abrangente.

Serviços iniciais:

- GitHub Pages para o frontend;
- API Gateway HTTP API;
- AWS Lambda;
- AWS Secrets Manager;
- Amazon CloudWatch;
- IAM.

Serviços futuros, somente se necessários:

- S3 para uploads temporários;
- DynamoDB para estado de submissões;
- SQS para processamento assíncrono;
- WAF para proteção adicional;
- X-Ray ou ferramenta equivalente para rastreamento.

## 18. Persistência

O MVP deve evitar banco de dados como fonte de verdade do conteúdo.

Estado mínimo pode ser reconstruído a partir de:

- Pull Requests;
- commits;
- branches;
- metadados de autenticação de curta duração.

Um banco de dados pode ser adicionado quando houver necessidade de:

- rascunhos persistentes;
- painel de solicitações;
- métricas editoriais;
- auditoria adicional;
- notificações e preferências;
- idempotência distribuída.

Se necessário, DynamoDB seria uma opção natural para estado pequeno e orientado a chave.

## 19. Observabilidade

Registrar eventos sem dados sensíveis:

- login iniciado;
- login concluído ou rejeitado;
- autorização negada;
- documento consultado;
- validação rejeitada;
- submissão criada;
- branch criada;
- Pull Request criado;
- conflito detectado;
- erro da API do GitHub;
- falha de upload;
- duração das operações.

Cada operação deve possuir um `correlation_id`.

Nunca registrar:

- chave privada;
- tokens;
- cookies;
- conteúdo completo de documentos em logs comuns;
- dados pessoais além do necessário.

Métricas iniciais:

- número de logins;
- número de submissões;
- taxa de erro;
- tempo médio de criação do PR;
- conflitos por documento;
- rejeições por validação;
- uploads por tipo;
- Pull Requests aprovados ou fechados.

## 20. Testes

### Backend

- autenticação;
- autorização por permissão no repositório;
- geração e expiração de sessão;
- validação de caminhos;
- validação de front matter;
- validação de Markdown;
- conversão Tiptap/Markdown;
- conflitos de versão;
- geração de branch;
- criação de PR;
- falhas e limites da API do GitHub.

### Frontend

- login;
- carregamento do editor;
- criação e edição;
- prévia;
- validações;
- upload;
- mensagens de erro;
- acessibilidade por teclado;
- comportamento responsivo.

### Integração

- fluxo completo de autenticação;
- leitura do repositório;
- criação de branch;
- gravação de documento;
- gravação de assets;
- criação de Pull Request;
- execução do build do site.

Não usar o repositório de produção para testes destrutivos. Criar ambiente ou repositório de homologação quando os testes exigirem alterações reais.

## 21. Roadmap

### Fase 1 — Fundação

- definir modelo Markdown;
- criar GitHub App;
- configurar permissões mínimas;
- criar frontend mínimo;
- criar Lambda e API Gateway;
- implementar sessão;
- documentar desenvolvimento local.

### Fase 2 — Edição

- integrar Tiptap;
- implementar parser Markdown;
- implementar serializer Markdown;
- criar prévia;
- implementar criação e edição de documentos;
- adicionar validações.

### Fase 3 — Assets e Pull Requests

- implementar upload de imagens;
- implementar upload de arquivos;
- criar branches;
- gravar múltiplos arquivos em uma submissão;
- criar Pull Requests;
- mostrar status.

### Fase 4 — Segurança e operação

- configurar Secrets Manager;
- configurar CloudWatch;
- aplicar rate limiting;
- adicionar testes de segurança;
- automatizar CI/CD;
- documentar LGPD e operação.

### Fase 5 — Evolução

- rascunhos persistentes;
- notificações;
- prévias por Pull Request;
- integração institucional;
- papéis editoriais mais refinados;
- suporte a mais tipos de conteúdo;
- eventual suporte a RST/Sphinx.

## 22. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Conversão imperfeita Tiptap/Markdown | Alto | Modelo de nós controlado e testes de round-trip |
| Token exposto no frontend | Alto | Toda operação privilegiada no backend |
| Alteração em caminho indevido | Alto | Caminhos gerados e validados no backend |
| Conflito de edição | Médio | Comparação de versão antes da gravação |
| Upload malicioso | Alto | MIME, assinatura, extensão, tamanho e sanitização |
| Dependência excessiva do GitHub | Médio | Adaptadores de integração e modelo editorial próprio |
| Custos AWS não monitorados | Médio | Budgets, métricas e limites |
| Dados pessoais em PRs | Médio | Política de dados e template controlado |
| Complexidade prematura | Médio | MVP sem banco e sem múltiplos repositórios |

## 23. Critérios de aceite do MVP

O MVP será considerado funcional quando um usuário autorizado conseguir:

1. autenticar com GitHub;
2. ser reconhecido como autorizado pelo repositório;
3. selecionar um documento existente;
4. editar o conteúdo no Tiptap;
5. visualizar a prévia;
6. enviar uma imagem ou arquivo permitido;
7. receber validação clara quando houver erro;
8. submeter a alteração;
9. gerar uma branch sem alterar `main`;
10. gerar um Pull Request com autoria e resumo;
11. acompanhar o link e o estado do PR;
12. permitir que o repositório valide e publique a alteração após o merge.

## 24. Decisões em aberto

As decisões abaixo ainda devem ser confirmadas:

- framework ou estilo de implementação do backend Python;
- método exato de autenticação da GitHub App;
- uso de OAuth com PKCE ou fluxo de instalação associado à aplicação;
- lista final de permissões por papel;
- categorias oficiais de documentos;
- campos obrigatórios do front matter;
- extensões e limites de arquivos;
- domínio do portal;
- estratégia de CORS e cookies entre GitHub Pages e API;
- existência de ambiente de homologação;
- método de prévia do Pull Request;
- política institucional de retenção de logs;
- responsável por revisar e fazer merge.

## 25. Resumo executivo

O `ifrn-editorial-portal` deve ser implementado como um portal editorial independente, com frontend estático em GitHub Pages, editor Tiptap, backend serverless em AWS Lambda e integração com o repositório `cte-zl-ifrn/central-ajuda` por meio de uma GitHub App.

O usuário não deverá editar diretamente o GitHub nem publicar alterações. O portal deverá transformar a edição visual em Markdown validado, criar uma branch temporária e abrir um Pull Request. O repositório de conteúdo continuará responsável por revisão, merge, build e publicação.

Essa separação preserva o histórico e a governança do Git, melhora a experiência do usuário final e permite que a interface evolua sem transformar o repositório de conteúdo em um sistema monolítico.
