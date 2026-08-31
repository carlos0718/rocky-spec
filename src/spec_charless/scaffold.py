from __future__ import annotations

import shutil
from importlib import resources
from pathlib import Path

from .integrations import CommandDefinition, SHARED_DIR_NAME

CHARLESS_VERSION = "0.1.0"

# key -> (título legible, nombre de archivo dentro de commands/)
# El orden acá es el orden real del flujo de creación (P0 -> P8.5).
COMMAND_CATALOG: list[tuple[str, str, str]] = [
    ("workspace", "P0 · Detectar workspace y popular perfil", "p0-workspace.md"),
    ("spec", "P1 · Describe el proyecto + SPEC.md (SDD + DDD)", "p1-spec-ddd.md"),
    ("stack", "P3 · Confirma o edita el stack", "p3-stack.md"),
    ("architecture", "P4 · Recomendar y decidir arquitectura", "p4-architecture.md"),
    ("design", "P4.5 · UI/UX Design System", "p4.5-design-system.md"),
    ("commands", "P5 · Comandos a ejecutar", "p5-commands.md"),
    ("deploy", "P5.5 · Infraestructura de deploy", "p5.5-deploy.md"),
    ("security", "P5.6 · Seguridad", "p5.6-security.md"),
    ("observability", "P5.7 · Observabilidad", "p5.7-observability.md"),
    ("build", "P6 y P7 · Archivos base y TODO", "p6-p7-files-todo.md"),
    ("review", "P7.5 · Revisión funcional y de QA (Three Amigos)", "p7.5-qa-review.md"),
    ("validate", "P8 · Reporte de validación", "p8-p8.5-validation-systemprompt.md"),
    ("mode-adopt", "Modo Adopción", "mode-adopt.md"),
    ("mode-resume", "Modo Reanudación", "mode-resume.md"),
]


def all_commands() -> list[CommandDefinition]:
    return [CommandDefinition(key=k, title=t, relative_source=f) for k, t, f in COMMAND_CATALOG]


def _package_dir(name: str) -> Path:
    return Path(str(resources.files("spec_charless"))) / name


def ensure_shared_knowledge(project_root: Path, force: bool = False) -> list[str]:
    """Copia commands/, reference/ y templates/ empaquetados en el CLI hacia
    ``.charless/`` dentro del proyecto destino. Es la única copia real de
    contenido pesado — todas las integraciones apuntan a esta carpeta en vez
    de llevarse su propia copia.

    Devuelve la lista de carpetas efectivamente copiadas (para el mensaje al
    usuario). Si ``.charless/`` ya existe y ``force`` es False, no pisa nada.
    """
    shared_root = project_root / SHARED_DIR_NAME
    copied = []

    for sub in ("commands", "reference", "templates"):
        source = _package_dir(sub)
        target = shared_root / sub
        if target.exists() and not force:
            continue
        if target.exists() and force:
            shutil.rmtree(target)
        shutil.copytree(source, target)
        copied.append(sub)

    version_file = shared_root / "VERSION"
    if not version_file.exists() or force:
        version_file.write_text(CHARLESS_VERSION + "\n", encoding="utf-8")

    return copied
