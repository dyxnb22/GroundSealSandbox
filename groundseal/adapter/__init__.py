"""Thin integration adapter for parent workflow systems."""

from groundseal.adapter.models import IntegrationRequest, IntegrationResponse
from groundseal.adapter.workflow import execute_workflow

__all__ = [
    "IntegrationRequest",
    "IntegrationResponse",
    "execute_workflow",
]
