"""Validação de assets (Fase 3.2) — ver ADR-0007 e a seção 11 de
docs/initial-architecture.md.

O nome final do arquivo é sugerido pelo frontend (que já conhece o corpo
Markdown e precisa referenciá-lo antes da submissão existir — ver
docs/phase-3.2-plan.md), mas o backend nunca confia nele sem validar: só
aceita um nome de arquivo simples (sem `/`, sem `..`), com extensão
permitida, cujo conteúdo realmente corresponde à extensão declarada
(assinatura/magic bytes). O diretório (`assets/images/{categoria}/` ou
`assets/files/{categoria}/`) é sempre calculado pelo backend a partir do
documento fixo — nunca a partir do que o cliente envia.

SVG está deliberadamente fora do escopo de imagens permitidas nesta fase:
a seção 11.2 do documento de arquitetura exige "rejeitar conteúdo SVG
perigoso", o que exigiria sanitização de XML/script — não necessário para
o MVP, já que nenhum documento real usa SVG hoje.
"""

from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass

from ..config import Settings
from ..errors import InvalidAssetError

_FILENAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+$")

_ALLOWED_EXTENSIONS = {
    "image": {"png", "jpg", "jpeg", "gif", "webp"},
    "file": {"pdf", "docx", "xlsx", "odt", "ods", "zip"},
}

_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "gif": (b"GIF87a", b"GIF89a"),
    "webp": (b"RIFF",),
    "pdf": (b"%PDF-",),
    "docx": (b"PK\x03\x04",),
    "xlsx": (b"PK\x03\x04",),
    "odt": (b"PK\x03\x04",),
    "ods": (b"PK\x03\x04",),
    "zip": (b"PK\x03\x04",),
}


@dataclass(frozen=True)
class ValidatedAsset:
    kind: str
    filename: str
    binary_content: bytes
    alt: str | None


def validate_asset(
    settings: Settings,
    *,
    kind: str,
    filename: str,
    content_base64: str,
    alt: str | None,
) -> ValidatedAsset:
    if kind not in ("image", "file"):
        raise InvalidAssetError(f"Tipo de asset desconhecido: '{kind}'.")

    if kind == "image" and not (alt and alt.strip()):
        raise InvalidAssetError("Texto alternativo é obrigatório para imagens.")

    if not _FILENAME_PATTERN.match(filename):
        raise InvalidAssetError(
            "Nome de arquivo inválido — use apenas letras minúsculas, números, "
            "hífens e uma extensão (ex.: 'documento-abc123.png')."
        )

    extension = filename.rsplit(".", 1)[-1]
    if extension not in _ALLOWED_EXTENSIONS[kind]:
        raise InvalidAssetError(f"Extensão '.{extension}' não permitida para {kind}.")

    try:
        binary_content = base64.b64decode(content_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidAssetError("Conteúdo do asset não é base64 válido.") from exc

    if len(binary_content) == 0:
        raise InvalidAssetError("Arquivo vazio.")

    max_size = settings.max_image_size_bytes if kind == "image" else settings.max_file_size_bytes
    if len(binary_content) > max_size:
        raise InvalidAssetError(f"Arquivo maior que o limite permitido ({max_size} bytes).")

    signatures = _SIGNATURES.get(extension, ())
    if signatures and not any(binary_content.startswith(sig) for sig in signatures):
        raise InvalidAssetError(
            f"Conteúdo do arquivo não corresponde à extensão '.{extension}' "
            "(assinatura/magic bytes inválidos)."
        )
    if extension == "webp" and b"WEBP" not in binary_content[:16]:
        raise InvalidAssetError("Conteúdo do arquivo não corresponde a um WEBP válido.")

    return ValidatedAsset(
        kind=kind, filename=filename, binary_content=binary_content, alt=alt
    )
