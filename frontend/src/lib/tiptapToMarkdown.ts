/**
 * Serializer Tiptap → Markdown (Fase 2.2), escrito à mão conforme
 * decidido em ADR-0009 — não delegado a uma biblioteca genérica, para
 * garantir determinismo e testabilidade de round-trip contra o mesmo
 * escopo de nós do parser (markdownToTiptap.ts).
 *
 * Normalizações cosmética conhecidas e aceitas (documentadas em
 * docs/phase-2.2-plan.md):
 * - itálico é sempre serializado com `*...*` (nunca `_..._`), mesmo que
 *   o Markdown original tenha usado underscore;
 * - quebras de linha suaves (fim de linha sem linha em branco) e quebras
 *   de linha forçadas viram, ambas, `hardBreak` na Fase 2.1 e são
 *   serializadas de volta como `\` + nova linha.
 * Nenhuma delas perde conteúdo — apenas normalizam a sintaxe de
 * superfície de forma estável (o mesmo nó sempre serializa igual).
 *
 * Um nó fora do whitelist nunca é descartado silenciosamente: lança
 * UnsupportedNodeError, tratado pela UI como erro visível.
 */

import type { TiptapDocument, TiptapMark, TiptapNode } from '../types/tiptap'

export class UnsupportedNodeError extends Error {
  readonly nodeType: string

  constructor(nodeType: string) {
    super(`Tipo de nó não suportado para serialização: '${nodeType}'.`)
    this.nodeType = nodeType
  }
}

export function tiptapToMarkdown(doc: TiptapDocument): string {
  const blocks = doc.content.map((node) => serializeBlock(node, 0))
  return blocks.length > 0 ? `${blocks.join('\n\n')}\n` : ''
}

function serializeBlock(node: TiptapNode, depth: number): string {
  switch (node.type) {
    case 'paragraph':
      return serializeInline(node.content ?? [])
    case 'heading': {
      const level = Number(node.attrs?.level ?? 1)
      const text = serializeInline(node.content ?? [])
      return `${'#'.repeat(level)} ${text}`.trimEnd()
    }
    case 'horizontalRule':
      return '---'
    case 'image':
      return serializeImage(node)
    case 'bulletList':
      return serializeBulletList(node, depth)
    case 'orderedList':
      return serializeOrderedList(node, depth)
    default:
      throw new UnsupportedNodeError(node.type)
  }
}

function serializeImage(node: TiptapNode): string {
  const src = String(node.attrs?.src ?? '')
  const alt = node.attrs?.alt ? String(node.attrs.alt) : ''
  const title = node.attrs?.title
  const titlePart = title ? ` "${String(title)}"` : ''
  return `![${alt}](${src}${titlePart})`
}

function serializeBulletList(node: TiptapNode, depth: number): string {
  return (node.content ?? []).map((item) => serializeListItem(item, depth, '-')).join('\n')
}

function serializeOrderedList(node: TiptapNode, depth: number): string {
  const start = Number(node.attrs?.start ?? 1)
  return (node.content ?? [])
    .map((item, index) => serializeListItem(item, depth, `${start + index}.`))
    .join('\n')
}

function serializeListItem(node: TiptapNode, depth: number, marker: string): string {
  const indent = '  '.repeat(depth)
  const blocks = node.content && node.content.length > 0 ? node.content : [{ type: 'paragraph' }]
  const [firstBlock, ...restBlocks] = blocks
  const firstLine = `${indent}${marker} ${serializeBlock(firstBlock, depth + 1)}`
  const restLines = restBlocks.map((block) => serializeBlock(block, depth + 1))
  return [firstLine, ...restLines].join('\n')
}

function serializeInline(nodes: TiptapNode[]): string {
  return nodes.map(serializeInlineNode).join('')
}

function serializeInlineNode(node: TiptapNode): string {
  if (node.type === 'hardBreak') return '\\\n'
  if (node.type === 'text') return serializeText(node)
  throw new UnsupportedNodeError(node.type)
}

function serializeText(node: TiptapNode): string {
  const marks = node.marks ?? []
  const isCode = marks.some((mark) => mark.type === 'code')
  let text = isCode ? (node.text ?? '') : escapeMarkdown(node.text ?? '')

  for (let i = marks.length - 1; i >= 0; i -= 1) {
    text = wrapWithMark(text, marks[i])
  }

  return text
}

function wrapWithMark(text: string, mark: TiptapMark): string {
  switch (mark.type) {
    case 'bold':
      return `**${text}**`
    case 'italic':
      return `*${text}*`
    case 'code':
      return `\`${text}\``
    case 'link': {
      const href = String(mark.attrs?.href ?? '')
      const title = mark.attrs?.title
      return title ? `[${text}](${href} "${String(title)}")` : `[${text}](${href})`
    }
    default:
      throw new UnsupportedNodeError(`mark:${mark.type}`)
  }
}

/**
 * Escapa caracteres que, se deixados literais, poderiam ser
 * reinterpretados como sintaxe Markdown ao serializar de volta (ex.: um
 * `*` literal no meio de um texto não deve virar ênfase). Colchetes não
 * são escapados deliberadamente — um `[texto]` isolado (sem `(` logo
 * depois) não é um link válido em CommonMark, e escapá-los sempre
 * distorceria visualmente conteúdo comum como checklists em texto puro
 * (`[x] Tarefa`), presentes em documentos reais do central-ajuda.
 */
function escapeMarkdown(text: string): string {
  return text.replace(/([\\`*_])/g, '\\$1')
}
