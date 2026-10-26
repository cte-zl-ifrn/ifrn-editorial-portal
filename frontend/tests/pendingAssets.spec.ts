import { describe, expect, it, vi } from 'vitest'
import {
  computeAssetUrl,
  computeCategory,
  computeDocumentSlug,
  resolvePendingAssets,
} from '../src/lib/pendingAssets'
import type { TiptapDocument } from '../src/types/tiptap'

const DOCUMENT_PATH = '_docs/proitec/como-fazer-cursos.md'

describe('computeDocumentSlug', () => {
  it('strips the directory and the .md extension', () => {
    expect(computeDocumentSlug(DOCUMENT_PATH)).toBe('como-fazer-cursos')
  })
})

describe('computeCategory', () => {
  it('extracts the category segment (_docs/{categoria}/{arquivo}.md)', () => {
    expect(computeCategory(DOCUMENT_PATH)).toBe('proitec')
  })
})

describe('computeAssetUrl', () => {
  it('builds an absolute raw.githubusercontent.com URL, not a relative path', () => {
    expect(computeAssetUrl(DOCUMENT_PATH, 'como-fazer-cursos-a1b2c3d4.png')).toBe(
      'https://raw.githubusercontent.com/cte-zl-ifrn/central-ajuda/main/assets/images/proitec/como-fazer-cursos-a1b2c3d4.png',
    )
  })
})

describe('resolvePendingAssets', () => {
  it('leaves a document with no images untouched and returns no assets', () => {
    const doc: TiptapDocument = {
      type: 'doc',
      content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Olá' }] }],
    }

    const result = resolvePendingAssets(doc, DOCUMENT_PATH)

    expect(result.doc).toEqual(doc)
    expect(result.assets).toEqual([])
  })

  it('leaves an already-hosted image (http URL) untouched', () => {
    const doc: TiptapDocument = {
      type: 'doc',
      content: [
        { type: 'image', attrs: { src: 'https://exemplo.org/foto.png', alt: 'Foto', title: null } },
      ],
    }

    const result = resolvePendingAssets(doc, DOCUMENT_PATH)

    expect(result.doc).toEqual(doc)
    expect(result.assets).toEqual([])
  })

  it('replaces a data: URL image with the final absolute GitHub URL and extracts the asset', () => {
    vi.stubGlobal('crypto', { randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee' })

    const base64Content = 'iVBORw0KGgo='
    const doc: TiptapDocument = {
      type: 'doc',
      content: [
        {
          type: 'image',
          attrs: { src: `data:image/png;base64,${base64Content}`, alt: 'Tela de login' },
        },
      ],
    }

    const result = resolvePendingAssets(doc, DOCUMENT_PATH)

    const expectedFilename = 'como-fazer-cursos-aaaaaaaa.png'
    expect(result.doc.content[0].attrs?.src).toBe(computeAssetUrl(DOCUMENT_PATH, expectedFilename))
    expect(result.assets).toEqual([
      { kind: 'image', filename: expectedFilename, content: base64Content, alt: 'Tela de login' },
    ])

    vi.unstubAllGlobals()
  })

  it('resolves images nested inside list items', () => {
    vi.stubGlobal('crypto', { randomUUID: () => '11111111-2222-3333-4444-555555555555' })

    const doc: TiptapDocument = {
      type: 'doc',
      content: [
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                {
                  type: 'image',
                  attrs: { src: 'data:image/jpeg;base64,AAA=', alt: 'Item' },
                },
              ],
            },
          ],
        },
      ],
    }

    const result = resolvePendingAssets(doc, DOCUMENT_PATH)

    const image = result.doc.content[0].content?.[0].content?.[0]
    expect(image?.attrs?.src).toBe(
      computeAssetUrl(DOCUMENT_PATH, 'como-fazer-cursos-11111111.jpg'),
    )
    expect(result.assets).toHaveLength(1)
    expect(result.assets[0].filename).toBe('como-fazer-cursos-11111111.jpg')

    vi.unstubAllGlobals()
  })

  it('throws instead of silently defaulting the extension for an unrecognized mime type', () => {
    // Não deveria ser alcançável via `DocumentViewer.vue` (que já rejeita
    // tipos fora da whitelist antes de gerar a `data:` URL), mas o guard
    // aqui precisa falhar alto, nunca rotular como `.png` em silêncio.
    const doc: TiptapDocument = {
      type: 'doc',
      content: [
        {
          type: 'image',
          attrs: { src: 'data:application/x-msdownload;base64,TVo=', alt: 'Não é imagem' },
        },
      ],
    }

    expect(() => resolvePendingAssets(doc, DOCUMENT_PATH)).toThrow(/Tipo de imagem não suportado/)
  })
})
