"""
rocky build — conecta ``render_template.py`` al flujo real de generación
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

import json
from dataclasses import dataclass, field
from pathlib import Path

from .render_template import extract_headers, find_unresolved, render

TEMPLATES_DIR_NAME = "templates"
SHARED_DIR_NAME = ".rocky-spec"
VALUES_FILE_NAME = "build-values.json"

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


def _persist_values(project_root: Path, values: dict[str, str]) -> None:
    """Guarda ``values`` en ``.rocky-spec/build-values.json`` -- el mismo
    archivo que P6 (``commands/p6-p7-files-todo.md``) ya documenta que el
    agente arma a mano antes de la primera corrida de ``rocky build`` --
    mezclado con lo que ya hubiera (nunca lo pisa entero), para que una
    regeneración puntual posterior (``only=``, ej. remediación de drift de
    contenido) no dependa de reconstruirlo de cero."""
    values_path = project_root / SHARED_DIR_NAME / VALUES_FILE_NAME
    existing: dict[str, str] = {}
    if values_path.exists():
        try:
            existing = json.loads(values_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}
    merged = {**existing, **values}
    values_path.parent.mkdir(parents=True, exist_ok=True)
    values_path.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(
    project_root: Path,
    values: dict[str, str],
    force: bool = False,
    only: tuple[str, str] | None = None,
) -> BuildResult:
    """Renderiza los archivos base del proyecto desde ``.rocky-spec/templates/``
    usando ``values``. No pisa un archivo que ya exista salvo ``force=True``
    — mismo criterio de instalación no destructiva que ``rocky init``.

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
            continue  # .rocky-spec/ incompleto o desactualizado -- no es tarea de build arreglarlo

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

    if values:
        _persist_values(project_root, values)

    return result


@dataclass
class UpdateFileResult:
    error: str | None = None
    backup_path: str | None = None
    generated: str | None = None
    only_in_backup: list[str] = field(default_factory=list)
    only_in_fresh: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)


def update_file(
    project_root: Path,
    values: dict[str, str],
    template_name: str,
    output_relative: str,
) -> UpdateFileResult:
    """Regenera un archivo raíz que **ya existe** preservando un backup —
    automatiza los pasos 1-2 de la receta manual de remediación de RF-22
    (ver "Caso especial — drift de contenido" en ``mode-adopt.md`` MA-6):
    backup del archivo actual y regeneración fresca desde el template
    vigente. El paso 3 (mergear con criterio) sigue a cargo del agente —
    para eso, reporta qué encabezados (``##``/``###``) quedaron solo en el
    backup (candidatos a portar a mano) y cuáles trajo el template como
    nuevos, reusando ``extract_headers`` (compartida con ``drift_check.py``).

    Nunca pisa un backup ya existente de una corrida anterior sin resolver
    — mismo criterio de "preguntar, no asumir" que el resto del kit."""
    templates_dir = project_root / SHARED_DIR_NAME / TEMPLATES_DIR_NAME
    template_path = templates_dir / template_name
    output_path = project_root / output_relative

    if not template_path.exists():
        return UpdateFileResult(error=f"No existe `{TEMPLATES_DIR_NAME}/{template_name}`.")

    if not output_path.exists():
        return UpdateFileResult(
            error=f"`{output_relative}` no existe -- --update regenera un archivo que ya "
            "existe. Para crearlo por primera vez, usá `rocky build` sin --update."
        )

    backup_path = output_path.with_name(f"_{output_path.name}")
    if backup_path.exists():
        return UpdateFileResult(
            error=f"Ya existe un backup en `{backup_path.relative_to(project_root)}` de una "
            "actualización anterior sin resolver -- mergealo o borralo antes de correr "
            "--update de nuevo."
        )

    backup_content = output_path.read_text(encoding="utf-8")
    output_path.rename(backup_path)

    template_text = template_path.read_text(encoding="utf-8")
    rendered = render(template_text, values)
    output_path.write_text(rendered, encoding="utf-8")

    backup_headers = extract_headers(backup_content)
    fresh_headers = extract_headers(rendered)
    backup_set, fresh_set = set(backup_headers), set(fresh_headers)

    if values:
        _persist_values(project_root, values)

    return UpdateFileResult(
        backup_path=str(backup_path.relative_to(project_root)),
        generated=output_relative,
        only_in_backup=[h for h in backup_headers if h not in fresh_set],
        only_in_fresh=[h for h in fresh_headers if h not in backup_set],
        unresolved=find_unresolved(rendered),
    )
