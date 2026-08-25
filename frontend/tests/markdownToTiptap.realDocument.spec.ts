import { describe, expect, it } from 'vitest'
import { markdownToTiptap } from '../src/lib/markdownToTiptap'

/**
 * Corpo real de `_docs/proitec/como-fazer-cursos.md` no `central-ajuda`
 * (documento de demonstração desta fase, ver docs/phase-2.1-plan.md),
 * sem o front matter. Congelado como fixture para não depender de rede
 * nos testes — se o arquivo mudar no repositório de conteúdo, este teste
 * não é afetado automaticamente (é um teste de regressão do parser, não
 * um teste de integração com o GitHub).
 */
const REAL_DOCUMENT_BODY = `
# Como fazer os cursos do ProITEC?

O **Programa de Iniciação Tecnológica e Cidadania (ProITEC)** é uma ação institucional do IFRN destinada aos estudantes de escolas públicas do estado do Rio Grande do Norte, com o objetivo de aprofundar a aprendizagem e preparar os alunos para o Exame de Seleção.

Neste tutorial, você aprenderá passo a passo como acessar a plataforma online, navegar pelos módulos de estudo e emitir o seu certificado de conclusão.

---

## Sumário

- [#passo-1-acesse-os-cursos](#passo-1-acesse-os-cursos)
- [#passo-2-faça-os-cursos](#passo-2-faça-os-cursos)
- [#passo-3-adquira-seu-certificado](#passo-3-adquira-seu-certificado)
- [#perguntas-frequentes](#perguntas-frequentes)
- [#links-relacionados](#links-relacionados)

---

<blockquote class="dica">
  <p><strong>Dica</strong>: Recomendamos utilizar um computador ou notebook com navegador atualizado (Google Chrome, Firefox ou Edge) para uma melhor experiência no ambiente virtual de aprendizagem.</p>
</blockquote>

## Passo 1: Acesse os cursos

Para iniciar seus estudos no ProITEC, siga o fluxo de acesso descrito abaixo:

1. Acesse o portal do **Ambiente Virtual de Aprendizagem (AVA)** através do endereço: \`https://ajuda.ead.ifrn.edu.br/\` ou direto pelo Moodle do IFRN.
2. Na barra superior, clique no botão **Login** ou **Entrar**.
3. Digite sua **Matrícula / CPF** no campo de usuário e sua **senha cadastrada**.
4. Após realizar o login, navegue até a seção **Meus Cursos** no painel principal.
5. Selecione o curso correspondente ao ProITEC no qual você está matriculado.

<blockquote class="importante">
  <p><strong>Importante</strong>: Caso seja seu primeiro acesso e você não lembre da sua senha, utilize a opção "Esqueceu o seu usuário ou senha?" na tela de login para redefini-la via e-mail cadastrado no SUAP.</p>
</blockquote>

---

## Passo 2: Faça os cursos

Os cursos do ProITEC são estruturados em módulos para facilitar o seu aprendizado contínuo.

### Módulo de Início (Acolhimento)

- **Boas-vindas e Apresentação**: Assista ao vídeo de introdução dos professores.
- **Guia do Estudante**: Leia atentamente o regulamento e o cronograma do programa.
- **Fórum de Apresentação**: Deixe uma mensagem para seus colegas e tutores.

### Unidade 1: Língua Portuguesa e Leitura

- Estudo dos textos base e materiais em PDF.
- Resolução da **Atividade Prática 1**.
- Participação no fórum de discussão temática.

### Unidade 2: Matemática e Raciocínio Lógico

- Visualização das vídeo-aulas explicativas.
- Exercícios fixadores interativos.
- Realização do simulado de verificação de aprendizagem.

---

## Passo 3: Adquira seu certificado

Para ter direito ao certificado digital de conclusão do curso ProITEC, você precisa cumprir os requisitos listados no checklist a seguir:

- [x] Ter completado 100% da visualização dos módulos obrigatórios.
- [x] Ter obtido nota mínima de **6,0 (seis)** nas atividades avaliativas do curso.
- [x] Preencher o **Questionário de Avaliação do Curso** no Moodle.

Após cumprir os requisitos:

1. Acesse a aba **Certificação** ao final da página do curso.
2. Clique no link **Gerar Certificado**.
3. O documento PDF será gerado automaticamente com um código de verificação autêntico do IFRN.
4. Faça o download e salve uma cópia em seu dispositivo.

---

## Perguntas Frequentes

### 1. Não consigo acessar o Moodle. O que devo fazer?
Verifique se seus dados de login no SUAP estão atualizados. Se o erro persistir, abra um chamado na Central de Serviços ou envie e-mail para a equipe de suporte.

### 2. O curso tem horário fixo para assistir às aulas?
Não. Os cursos são assíncronos, o que significa que você pode estudar nos horários que forem mais convenientes para sua rotina, respeitando apenas os prazos das avaliações.

---

## Links relacionados

- [Ambiente Virtual de Aprendizagem (AVA)]({{ site.baseurl }}/category/ambiente_virtual/)
- [Portal Oficial do IFRN](https://portal.ifrn.edu.br/)
- [Sistema Unificado de Administração Pública (SUAP)](https://suap.ifrn.edu.br/)
`

describe('markdownToTiptap — documento real de demonstração', () => {
  it('converte o corpo inteiro sem lançar exceção', () => {
    expect(() => markdownToTiptap(REAL_DOCUMENT_BODY)).not.toThrow()
  })

  it('produz uma árvore não vazia com os tipos de nó esperados', () => {
    const doc = markdownToTiptap(REAL_DOCUMENT_BODY)
    const types = new Set(doc.content.map((node) => node.type))

    expect(doc.content.length).toBeGreaterThan(10)
    expect(types).toContain('heading')
    expect(types).toContain('bulletList')
    expect(types).toContain('orderedList')
    expect(types).toContain('horizontalRule')
  })

  it('preserva os blocos HTML crus como texto literal, sem quebrar a árvore', () => {
    const doc = markdownToTiptap(REAL_DOCUMENT_BODY)
    const flatText = JSON.stringify(doc)

    expect(flatText).toContain('blockquote class=\\"dica\\"')
    expect(flatText).not.toContain('"type":"blockquote"')
  })

  it('preserva o link com sintaxe de template do Jekyll como href opaco', () => {
    const doc = markdownToTiptap(REAL_DOCUMENT_BODY)
    const flatText = JSON.stringify(doc)

    expect(flatText).toContain('{{ site.baseurl }}/category/ambiente_virtual/')
  })
})
