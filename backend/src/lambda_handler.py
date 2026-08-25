"""Adaptador Lambda (API Gateway HTTP API) via Mangum — ver ADR-0005."""

from mangum import Mangum

from .app import app

handler = Mangum(app)
