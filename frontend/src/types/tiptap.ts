/**
 * Subconjunto do esquema JSON do Tiptap/ProseMirror usado pelo parser
 * Markdown → Tiptap (Fase 2.1). Ver ADR-0002 (whitelist de nós) e
 * ADR-0009 (estratégia de conversão).
 */

export interface TiptapMark {
  type: string
  attrs?: Record<string, unknown>
}

export interface TiptapNode {
  type: string
  attrs?: Record<string, unknown>
  content?: TiptapNode[]
  text?: string
  marks?: TiptapMark[]
}

export interface TiptapDocument {
  type: 'doc'
  content: TiptapNode[]
}
