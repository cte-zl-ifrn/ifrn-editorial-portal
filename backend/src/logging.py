"""Logging estruturado em JSON, com correlation_id por requisição.

Nunca registrar chave privada, tokens, cookies ou conteúdo de documentos —
ver docs/requirements/non-functional-requirements.md (RNF-12, RNF-13).
"""

from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar

_METRICS_NAMESPACE = "IfrnEditorialPortal"

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")

_SENSITIVE_KEYS = {
    "token",
    "access_token",
    "installation_token",
    "private_key",
    "client_secret",
    "cookie",
    "content",
}


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> str:
    return _correlation_id.get()


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            for key, value in extra.items():
                if key.lower() in _SENSITIVE_KEYS:
                    continue
                payload[key] = value
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, message: str, **fields: object) -> None:
    logger.info(message, extra={"extra_fields": fields})


def log_metric(
    metric_name: str,
    value: float = 1,
    *,
    unit: str = "Count",
    dimensions: dict[str, str] | None = None,
) -> None:
    """Emite uma métrica em Embedded Metric Format (EMF, ver
    docs/phase-4.2-plan.md) — o CloudWatch extrai a métrica
    automaticamente de uma linha de log, sem exigir uma chamada
    `PutMetricData` separada. Escreve direto em stdout, fora de
    `logging`: `_JsonFormatter` embrulharia o payload numa envelope
    (`message`, `level`, ...) incompatível com o schema EMF, que exige o
    nome da métrica e as dimensões como chaves de topo do JSON."""
    dimensions = dimensions or {}
    payload: dict[str, object] = {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": _METRICS_NAMESPACE,
                    "Dimensions": [list(dimensions.keys())],
                    "Metrics": [{"Name": metric_name, "Unit": unit}],
                }
            ],
        },
        **dimensions,
        metric_name: value,
    }
    print(json.dumps(payload, default=str, ensure_ascii=False))
