"""
charless build — conecta ``render_template.py`` al flujo real de generación
de archivos (P6/P7 del ciclo de vida de la skill).

Hasta acá, `render_template.render()`/`render_file()` existían y funcionaban
(con tests propios), pero nada los llamaba: el LLM copiaba cada
`.template` y reemplazaba `{{PLACEHOLDER}}` a mano durante la conversación.
Funciona, pero es exactamente el problema no-determinista que
`render_template.py` fue escrito para resolver, sin conectar.

El LLM sigue decidiendo *qué valor* le corresponde a cada placeholder (eso
requiere criterio, no se automatiza) — lo vuelca a un JSON plano después de
recolectar las respuestas conversando, y este módulo hace la sustitución
mecánica de forma determinista y reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .render_template import find_unresolved, render

TEMPLATES_DIR_NAME = "templates"
SHARED_DIR_NAME = ".charless"

# (nombre del .template, ruta relativa del archivo generado en el proyecto)
# Alcance: el set "código/híbrido" de P6/P7 (ver commands/p6-p7-files-todo.md).
# LICENSE se maneja aparte (elige uno de tres templates según LICENSE_CHOICE).
# Fuera de alcance por ahora: design-system/MASTER.md (condicional a P4.5) y
# los templates exclusivos de proyectos creativos (BRIEF/STORYBOARD/prompts).
BASE_FILES: list[tuple[str, str]] = [
    ("CONSTITUTION.md.template", "CONSTITUTION.md"),
    ("SPEC.md.template", "SPEC.md"),
    ("AGENTS.md.template", "AGENTS.md"),
    ("CLAUDE.md.template", "CLAUDE.md"),
    ("SECURITY.md.template", "SECURITY.md"),
    ("OBSERVABILITY.md.template", "OBSERVABILITY.md"),
    ("CHANGELOG.md.template", "CHANGELOG.md"),
    ("README.md.template", "README.md"),
    ("TODO.md.template", "TODO.md"),
]

LICENSE_CHOICES = {"mit", "apache2", "proprietary"}
LICENSE_VALUES_KEY = "LICENSE_CHOICE"


@dataclass
class BuildResult:
    generated: list[str] = field(default_factory=list)
    skipped_existing: list[str] = field(default_factory=list)
    unresolved: dict[str, list[str]] = field(default_factory=dict)
    invalid_license_choice: str | None = None

    @property
    def is_clean(self) -> bool:
        return not self.unresolved and not self.invalid_license_choice


def _license_entry(values: dict[str, str]) -> tuple[str, str] | None:
    choice = values.get(LICENSE_VALUES_KEY)
    if not choice:
        return None
    if choice not in LICENSE_CHOICES:
        return None  # se reporta en build() vía invalid_license_choice
    return (f"LICENSE-{choice}.template", "LICENSE")


def build(
    project_root: Path,
    values: dict[str, str],
    force: bool = False,
    only: tuple[str, str] | None = None,
) -> BuildResult:
    """Renderiza los archivos base del proyecto desde ``.charless/templates/``
    usando ``values``. No pisa un archivo que ya exista salvo ``force=True``
    — mismo criterio de instalación no destructiva que ``charless init``.

    ``only=(template_name, output_relative)`` renderiza un solo template en
    vez del set fijo de ``BASE_FILES`` — para templates condicionales que no
    aplican a todo proyecto (``MASTER.md.template``, ``ACCESSIBILITY.md.template``),
    que antes quedaban afuera de este mecanismo determinista por completo."""
    templates_dir = project_root / SHARED_DIR_NAME / TEMPLATES_DIR_NAME
    result = BuildResult()

    if only:
        entries = [only]
    else:
        entries = list(BASE_FILES)

        choice = values.get(LICENSE_VALUES_KEY)
        if choice and choice not in LICENSE_CHOICES:
            result.invalid_license_choice = choice
        else:
            license_entry = _license_entry(values)
            if license_entry:
                entries.append(license_entry)

    for template_name, output_relative in entries:
        template_path = templates_dir / template_name
        output_path = project_root / output_relative

        if not template_path.exists():
            continue  # .charless/ incompleto o desactualizado -- no es tarea de build arreglarlo

        if output_path.exists() and not force:
            result.skipped_existing.append(output_relative)
            continue

        template_text = template_path.read_text(encoding="utf-8")
        rendered = render(template_text, values)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        result.generated.append(output_relative)

        remaining = find_unresolved(rendered)
        if remaining:
            result.unresolved[output_relative] = remaining

    return result
