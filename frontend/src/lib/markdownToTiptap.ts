/**
 * Parser controlado Markdown → documento Tiptap (Fase 2.1).
 *
 * Cobre o escopo mínimo de docs/phase-2.1-plan.md: parágrafos, títulos,
 * listas com marcadores e numeradas, negrito, itálico, links e imagens.
 * `code` (inline) e `horizontalRule` são incluídos incidentalmente por
 * virem de fábrica com o StarterKit do Tiptap, sem custo adicional.
 *
 * Qualquer construção de Markdown fora desse escopo é normalizada de
 * forma previsível — nunca descartada silenciosamente (ver ADR-0009):
 * um bloco desconhecido vira um parágrafo com o texto-fonte bruto
 * daquele trecho; um token inline desconhecido (ex.: imagem misturada a
 * texto no mesmo parágrafo) vira um marcador de texto `[imagem: alt]`.
 * HTML embutido nunca é interpretado (`html: false`) — aparece como texto
 * literal, nunca como nó renderizado, por segurança (ver ADR-0002, seção
 * 10.3 do documento de arquitetura).
 */

import MarkdownIt from 'markdown-it'
import type { Token } from 'markdown-it'
import type { TiptapDocument, TiptapMark, TiptapNode } from '../types/tiptap'

const markdownIt = new MarkdownIt({
  html: false,
  linkify: false,
  typographer: false,
})

export function markdownToTiptap(markdown: string): TiptapDocument {
  const tokens = markdownIt.parse(markdown, {})
  const content = convertBlocks(markdown, tokens, 0, tokens.length)
  return { type: 'doc', content: content.length > 0 ? content : [{ type: 'paragraph' }] }
}

function convertBlocks(source: string, tokens: Token[], start: number, end: number): TiptapNode[] {
  const nodes: TiptapNode[] = []
  let i = start

  while (i < end) {
    const token = tokens[i]

    switch (token.type) {
      case 'heading_open': {
        const level = Number(token.tag.slice(1)) || 1
        const inline = tokens[i + 1]
        const inlineContent = convertInline(inline.children ?? [])
        nodes.push({
          type: 'heading',
          attrs: { level },
          ...(inlineContent.length > 0 ? { content: inlineContent } : {}),
        })
        i += 3 // heading_open, inline, heading_close
        break
      }

      case 'paragraph_open': {
        const inline = tokens[i + 1]
        nodes.push(...convertParagraph(inline))
        i += 3 // paragraph_open, inline, paragraph_close
        break
      }

      case 'bullet_list_open': {
        const closeIndex = findMatchingClose(tokens, i, 'bullet_list')
        nodes.push({
          type: 'bulletList',
          content: convertListItems(source, tokens, i + 1, closeIndex),
        })
        i = closeIndex + 1
        break
      }

      case 'ordered_list_open': {
        const closeIndex = findMatchingClose(tokens, i, 'ordered_list')
        const startAttr = token.attrGet('start')
        const startNumber = startAttr ? Number(startAttr) : 1
        nodes.push({
          type: 'orderedList',
          ...(startNumber !== 1 ? { attrs: { start: startNumber } } : {}),
          content: convertListItems(source, tokens, i + 1, closeIndex),
        })
        i = closeIndex + 1
        break
      }

      case 'hr': {
        nodes.push({ type: 'horizontalRule' })
        i += 1
        break
      }

      default: {
        if (token.nesting === 1) {
          // Contêiner desconhecido (ex.: blockquote real, se algum dia
          // aparecer): preserva o Markdown-fonte como texto visível, em
          // vez de tentar interpretar ou descartar silenciosamente.
          const baseType = token.type.replace(/_open$/, '')
          const closeIndex = findMatchingClose(tokens, i, baseType)
          const raw = sliceSource(source, token, tokens[closeIndex]).trim()
          if (raw) {
            nodes.push({ type: 'paragraph', content: [{ type: 'text', text: raw }] })
          }
          i = closeIndex + 1
        } else if (token.nesting === 0) {
          // Token atômico desconhecido (ex.: fence/code_block): mesma
          // estratégia de fallback, usando o próprio conteúdo do token.
          const raw = (token.content ?? '').trim()
          if (raw) {
            nodes.push({
              type: 'paragraph',
              content: [{ type: 'text', text: raw.replace(/\s*\n+\s*/g, ' ') }],
            })
          }
          i += 1
        } else {
          // Fechamento sem abertura correspondente processada — não deveria
          // ocorrer com um stream de tokens balanceado do markdown-it.
          i += 1
        }
      }
    }
  }

  return nodes
}

function convertListItems(
  source: string,
  tokens: Token[],
  start: number,
  end: number,
): TiptapNode[] {
  const items: TiptapNode[] = []
  let i = start

  while (i < end) {
    const closeIndex = findMatchingClose(tokens, i, 'list_item')
    const innerContent = convertBlocks(source, tokens, i + 1, closeIndex)
    items.push({
      type: 'listItem',
      content: innerContent.length > 0 ? innerContent : [{ type: 'paragraph' }],
    })
    i = closeIndex + 1
  }

  return items
}

/**
 * Converte o conteúdo inline de um parágrafo. Um parágrafo cujo único
 * conteúdo significativo é uma imagem vira um nó `image` de bloco (o nó
 * de imagem do Tiptap é bloco, não inline — não pode ficar dentro de
 * `paragraph.content`). Imagem misturada com texto no mesmo parágrafo é
 * um caso fora do escopo mínimo desta fase (nenhum documento real do
 * central-ajuda faz isso hoje) e cai no fallback de texto do token
 * `image` em `convertInline`.
 */
function convertParagraph(inlineToken: Token): TiptapNode[] {
  const children = inlineToken.children ?? []
  const meaningful = children.filter(
    (token) => !(token.type === 'softbreak' || (token.type === 'text' && token.content.trim() === '')),
  )

  if (meaningful.length === 1 && meaningful[0].type === 'image') {
    return [imageNodeFromToken(meaningful[0])]
  }

  const content = convertInline(children)
  return [{ type: 'paragraph', ...(content.length > 0 ? { content } : {}) }]
}

function imageNodeFromToken(token: Token): TiptapNode {
  return {
    type: 'image',
    attrs: {
      src: token.attrGet('src') ?? '',
      alt: token.content || token.attrGet('alt') || null,
      title: token.attrGet('title') ?? null,
    },
  }
}

function convertInline(children: Token[]): TiptapNode[] {
  const nodes: TiptapNode[] = []
  const markStack: TiptapMark[] = []

  const pushText = (text: string, extraMarks: TiptapMark[] = []) => {
    if (!text) return
    const marks = [...markStack, ...extraMarks]
    nodes.push({ type: 'text', text, ...(marks.length > 0 ? { marks } : {}) })
  }

  for (const token of children) {
    switch (token.type) {
      case 'strong_open':
        markStack.push({ type: 'bold' })
        break
      case 'strong_close':
        popMark(markStack, 'bold')
        break
      case 'em_open':
        markStack.push({ type: 'italic' })
        break
      case 'em_close':
        popMark(markStack, 'italic')
        break
      case 'link_open':
        markStack.push({
          type: 'link',
          attrs: { href: token.attrGet('href') ?? '', title: token.attrGet('title') ?? null },
        })
        break
      case 'link_close':
        popMark(markStack, 'link')
        break
      case 'code_inline':
        pushText(token.content, [{ type: 'code' }])
        break
      case 'softbreak':
      case 'hardbreak':
        nodes.push({ type: 'hardBreak' })
        break
      case 'text':
        pushText(token.content)
        break
      case 'image':
        // Fora do escopo mínimo dentro de texto corrido — ver docstring
        // do módulo. Normalizado como texto visível, não descartado.
        pushText(`[imagem: ${token.content || token.attrGet('alt') || ''}]`)
        break
      default:
        if (token.content) pushText(token.content)
    }
  }

  return nodes
}

function popMark(stack: TiptapMark[], type: string): void {
  const index = stack.map((mark) => mark.type).lastIndexOf(type)
  if (index !== -1) stack.splice(index, 1)
}

function findMatchingClose(tokens: Token[], openIndex: number, baseType: string): number {
  let depth = 0
  for (let i = openIndex; i < tokens.length; i++) {
    const type = tokens[i].type
    if (type === `${baseType}_open`) depth += 1
    else if (type === `${baseType}_close`) {
      depth -= 1
      if (depth === 0) return i
    }
  }
  throw new Error(`Tag de fechamento não encontrada para '${baseType}' a partir do índice ${openIndex}`)
}

function sliceSource(source: string, openToken: Token, closeToken: Token): string {
  const startLine = openToken.map?.[0] ?? 0
  const endLine = closeToken.map?.[1] ?? startLine
  return source.split('\n').slice(startLine, endLine).join('\n')
}
