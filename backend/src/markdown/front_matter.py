"""Separação de front matter YAML e corpo Markdown.

Ver ADR-0009: o front matter é preservado como texto bruto
(`front_matter_raw`), nunca reserializado, para que a reconstrução do
documento (Fase 2.2) não corra o risco de um diff cosmético de YAML.
`front_matter_raw + body` reproduz sempre o texto original exatamente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml

from ..errors import InvalidFrontMatterError

_DELIMITER = "---"


@dataclass(frozen=True)
class FrontMatterSplit:
    front_matter: dict[str, Any]
    front_matter_raw: str
    body: str


def split_front_matter(raw_text: str) -> FrontMatterSplit:
    lines = raw_text.splitlines(keepends=True)

    if not lines or lines[0].rstrip("\r\n") != _DELIMITER:
        return FrontMatterSplit(front_matter={}, front_matter_raw="", body=raw_text)

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == _DELIMITER:
            closing_index = index
            break

    if closing_index is None:
        raise InvalidFrontMatterError(
            "Front matter não terminado: delimitador de fechamento '---' não encontrado."
        )

    front_matter_raw = "".join(lines[: closing_index + 1])
    yaml_text = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1 :])

    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise InvalidFrontMatterError(f"Front matter YAML inválido: {exc}") from exc

    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        raise InvalidFrontMatterError(
            "Front matter deve ser um mapeamento YAML (chave: valor), "
            f"recebido {type(parsed).__name__}."
        )

    return FrontMatterSplit(front_matter=parsed, front_matter_raw=front_matter_raw, body=body)
