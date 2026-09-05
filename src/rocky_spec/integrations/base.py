"""
Integration registry — arquitectura de plugins para soportar múltiples agentes
de código (Claude, Cursor, y los que se agreguen) sin duplicar contenido.

El conocimiento (commands/, reference/, templates/) es UNO SOLO y vive en
``.rocky-spec/`` dentro del repo del proyecto, versionado junto al código.
Cada integración es solo un adaptador delgado: sabe en qué formato y en qué
carpeta el agente correspondiente espera encontrar sus comandos, y genera un
puntero hacia ``.rocky-spec/`` — nunca copia el contenido pesado dos veces.

Esto es deliberado: si mañana se agrega una tercera integración (Windsurf,
Copilot), el conocimiento no se toca — solo se escribe un adaptador nuevo.
"""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

SHARED_DIR_NAME = ".rocky-spec"


@dataclass(frozen=True)
class CommandDefinition:
    """Un paso del ciclo de vida (spec, architecture, security...), agnóstico
    de qué agente lo va a ejecutar. El contenido real vive en
    ``.rocky-spec/commands/<key>.md`` — texto plano, sin frontmatter, pensado
    para que cualquier LLM lo pueda seguir igual."""

    key: str  # "spec", "architecture", "security", "adopt", "resume"...
    title: str  # "Especificación y requisitos (SDD Spec-Anchored)"
    relative_source: str  # "spec.md" — nombre del archivo dentro de commands/


@dataclass(frozen=True)
class InstallManifestEntry:
    """Un archivo generado por una integración, con el hash de su contenido
    en el momento de instalarlo — permite desinstalar sin pisar ediciones
    manuales del usuario (mismo criterio que usa spec-kit)."""

    path: str
    sha256: str


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_tracked(project_root: Path, relative_path: str, content: str) -> InstallManifestEntry:
    """Escribe un archivo y devuelve su entrada de manifiesto. Helper
    compartido por todas las integraciones — evita repetir la lógica de
    tracking en cada una."""
    full_path = project_root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return InstallManifestEntry(path=relative_path, sha256=sha256_of(content))


class IntegrationBase(ABC):
    """Clase base — cada agente soportado es una subclase de esto.

    Contrato mínimo: declarar ``key``/``display_name`` e implementar
    ``install``. ``uninstall`` ya viene resuelto acá porque la lógica de
    hash-tracking es igual para todas las integraciones.
    """

    key: str
    display_name: str

    @abstractmethod
    def install(
        self, project_root: Path, commands: list[CommandDefinition]
    ) -> list[InstallManifestEntry]:
        """Genera los archivos específicos del agente, apuntando al
        conocimiento compartido en ``.rocky-spec/``. Devuelve el manifiesto de
        instalación."""
        raise NotImplementedError

    def uninstall(self, project_root: Path, manifest: list[InstallManifestEntry]) -> int:
        """Borra solo los archivos que no fueron editados a mano desde el
        install. Devuelve cuántos se borraron efectivamente."""
        removed = 0
        for entry in manifest:
            file_path = project_root / entry.path
            if not file_path.exists():
                continue
            current_hash = sha256_of(file_path.read_text(encoding="utf-8"))
            if current_hash == entry.sha256:
                file_path.unlink()
                removed += 1
            # si el hash no matchea, el usuario lo editó a mano — no se toca
        return removed
