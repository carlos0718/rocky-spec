from __future__ import annotations

from .base import CommandDefinition, IntegrationBase, InstallManifestEntry, SHARED_DIR_NAME
from .claude import ClaudeIntegration
from .cursor import CursorIntegration

INTEGRATION_REGISTRY: dict[str, IntegrationBase] = {}


def _register(integration: IntegrationBase) -> None:
    INTEGRATION_REGISTRY[integration.key] = integration


_register(ClaudeIntegration())
_register(CursorIntegration())

__all__ = [
    "CommandDefinition",
    "IntegrationBase",
    "InstallManifestEntry",
    "INTEGRATION_REGISTRY",
    "SHARED_DIR_NAME",
]
