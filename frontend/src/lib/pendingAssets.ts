/**
 * Resolve imagens inseridas como upload local (Fase 3.2, ver ADR-0007).
 *
 * O caminho final de um asset só existe depois que a submissão é criada
 * no backend (categoria calculada a partir do documento fixo) — mas o
 * corpo Markdown precisa referenciar esse caminho *antes* de a submissão
 * existir, já que documento e asset são gravados na mesma branch/commit.
 * Por isso o caminho é calculado aqui, no frontend, com a mesma lógica
 * que o backend usa a partir do mesmo documento fixo (ver
 * backend/src/services/submission_service.py); o backend segue sendo
 * quem valida e decide o diretório de verdade, nunca aceitando o nome
 * cegamente.
 *
 * Enquanto o usuário edita, a imagem é mostrada via uma `data:` URL (para
 * ter uma prévia real do arquivo escolhido). Só no momento de gerar o
 * corpo final (prévia ou envio) essa `data:` URL é trocada pelo caminho
 * relativo definitivo, e o conteúdo binário é extraído para envio como
 * asset — ver docs/phase-3.2-plan.md.
 */

import type { TiptapDocument, TiptapNode } from '../types/tiptap'
import type { SubmissionAsset } from '../types'

const MIME_TO_EXTENSION: Record<string, string> = {
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'image/gif': 'gif',
  'image/webp': 'webp',
}

/** Única fonte de verdade dos tipos aceitos — usada tanto pelo seletor de
 * arquivo (`DocumentViewer.vue`) quanto pela resolução abaixo. */
export const ACCEPTED_IMAGE_MIME_TYPES = Object.keys(MIME_TO_EXTENSION)

const DATA_URL_PATTERN = /^data:([^;]+);base64,(.+)$/

export function computeDocumentSlug(documentPath: string): string {
  const name = documentPath.split('/').pop() ?? documentPath
  return name.replace(/\.md$/, '')
}

/** Documentos seguem `_docs/{categoria}/{arquivo}.md` (ver seção 8.2 do
 * documento de arquitetura) — o mesmo segmento é a categoria dos assets. */
export function computeCategory(documentPath: string): string {
  return documentPath.split('/')[1] ?? ''
}

export function computeAssetPathPrefix(documentPath: string): string {
  const segments = documentPath.split('/')
  const depth = Math.max(segments.length - 1, 0)
  const up = '../'.repeat(depth)
  return `${up}assets/images/${computeCategory(documentPath)}/`
}

function generateAssetId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID().replace(/-/g, '').slice(0, 8)
  }
  return Math.random().toString(16).slice(2, 10)
}

export function resolvePendingAssets(
  doc: TiptapDocument,
  documentPath: string,
): { doc: TiptapDocument; assets: SubmissionAsset[] } {
  const assets: SubmissionAsset[] = []
  const prefix = computeAssetPathPrefix(documentPath)
  const slug = computeDocumentSlug(documentPath)

  function walk(node: TiptapNode): TiptapNode {
    if (node.type === 'image' && typeof node.attrs?.src === 'string') {
      const match = DATA_URL_PATTERN.exec(node.attrs.src)
      if (match) {
        const [, mime, base64] = match
        const extension = MIME_TO_EXTENSION[mime]
        if (!extension) {
          // Invariante: só chega aqui uma `data:` URL criada por
          // `setImage` (DocumentViewer.vue), que já rejeita tipos fora de
          // ACCEPTED_IMAGE_MIME_TYPES antes de gerar a `data:` URL. Um
          // mime não mapeado aqui indica que essa garantia foi violada —
          // falhar alto em vez de rotular silenciosamente como `.png`.
          throw new Error(`Tipo de imagem não suportado: ${mime}`)
        }
        const filename = `${slug}-${generateAssetId()}.${extension}`
        const alt = typeof node.attrs.alt === 'string' ? node.attrs.alt : ''
        assets.push({ kind: 'image', filename, content: base64, alt })
        return { ...node, attrs: { ...node.attrs, src: `${prefix}${filename}` } }
      }
    }
    if (node.content) {
      return { ...node, content: node.content.map(walk) }
    }
    return node
  }

  return { doc: { ...doc, content: doc.content.map(walk) }, assets }
}
