/**
 * Extensões do Tiptap compartilhadas entre a visualização somente leitura
 * (Fase 2.1) e a edição (Fase 2.2). Restrita deliberadamente ao whitelist
 * de nós da ADR-0002 / ADR-0009: desabilita blockquote, codeBlock, strike
 * e underline do StarterKit para que o editor nunca produza um nó que o
 * serializer (`tiptapToMarkdown.ts`) não saiba serializar. A defesa em
 * profundidade (o serializer lança um erro tratado para nós
 * desconhecidos) continua valendo, mas restringir a superfície de edição
 * é a primeira linha de defesa.
 */

import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'

export const tiptapExtensions = [
  StarterKit.configure({
    blockquote: false,
    codeBlock: false,
    strike: false,
    underline: false,
    link: { openOnClick: false, autolink: false },
  }),
  Image,
]
