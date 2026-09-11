"""
rocky check drift / rocky update — detecta dos clases de drift entre un
proyecto ya generado y la versión vigente del kit:

1. Archivos raíz completamente ausentes en proyectos adoptados (Modo
   Adopción, MA-6) cuyo `.skill-state.json` es anterior a que el kit
   generara ese archivo. Nace del caso real de `cuotify`: adoptado el
   2026-08-10 con una versión de `mode-adopt.md` que todavía no incluía los
   pasos de CONSTITUTION.md, SECURITY.md, OBSERVABILITY.md, CHANGELOG.md ni
   ACCESSIBILITY.md — sin ninguna forma automática de notar el hueco hasta
   una auditoría manual. (RF-20)

2. Secciones (`##`/`###`) que el template vigente en `.rocky-spec/templates/`
   ya tiene pero que un archivo raíz ya generado (`AGENTS.md`,
   `CONSTITUTION.md`...) no tiene, porque se generó antes de que el template
   ganara esa sección. A diferencia de (1), esto corre para **cualquier**
   proyecto con `.rocky-spec/templates/` instalado, no solo los adoptados —
   nace del caso real de este propio repo: su `AGENTS.md` no tenía la
   sección "Servicios externos" que `AGENTS.md.template` ganó con RF-12.
   Heurístico por encabezado, no diff literal: estos archivos llevan
   contenido customizado por diseño (a diferencia de `commands/`/
   `reference/`/`templates/`, que sí se comparan por hash exacto vía
   `shared-manifest.json`). (RF-22)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .build import BASE_FILES, SHARED_DIR_NAME as BUILD_SHARED_DIR_NAME, TEMPLATES_DIR_NAME
from .health_check import Finding, HealthCheckReport, IGNORED_DIRS

SKILL_STATE_FILE = ".skill-state.json"

HEADER_PATTERN = re.compile(r"^(#{2,3})[ \t]+(\S.*?)\s*$", re.MULTILINE)

# Archivos que MA-6 genera siempre para un proyecto adoptado, en la versión
# vigente de la skill — independiente de si el proyecto tiene interfaz visual.
ALWAYS_GENERATED = ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md")

# Archivos que MA-6 solo genera si el proyecto tiene interfaz visual.
UI_ONLY_GENERATED = ("ACCESSIBILITY.md", "design-system/MASTER.md")

UI_EXTENSIONS = ("html", "jsx", "tsx")


def _extract_headers(text: str) -> list[str]:
    """Encabezados `##`/`###` de un documento Markdown, en orden. Descarta
    los que todavía tienen un placeholder sin resolver (ej. "## [0.1.0] -
    {{DATE}}" en CHANGELOG.md.template) -- son contenido de ejemplo por
    instancia, no una etiqueta de sección fija que tenga sentido comparar."""
    headers = []
    for level, title in HEADER_PATTERN.findall(text):
        if "{{" in title:
            continue
        headers.append(f"{level} {title}")
    return headers


def _content_drift_findings(root: Path) -> list[Finding]:
    """Secciones del template vigente ausentes en el archivo raíz ya
    generado correspondiente -- ver punto 2 del docstring del módulo."""
    templates_dir = root / BUILD_SHARED_DIR_NAME / TEMPLATES_DIR_NAME
    if not templates_dir.exists():
        return []

    findings: list[Finding] = []
    for template_name, output_relative in BASE_FILES:
        template_path = templates_dir / template_name
        output_path = root / output_relative
        if not template_path.exists() or not output_path.exists():
            continue  # sin template no hay contra qué comparar; sin archivo generado es tarea de RF-20, no de esto

        template_headers = _extract_headers(template_path.read_text(encoding="utf-8"))
        project_headers = set(_extract_headers(output_path.read_text(encoding="utf-8")))

        for header in template_headers:
            if header in project_headers:
                continue
            title = header.lstrip("#").strip()
            findings.append(
                Finding(
                    severity="warning",
                    message=f"`{output_relative}` no tiene la sección \"{title}\" que "
                    f"`{TEMPLATES_DIR_NAME}/{template_name}` ya tiene — puede ser una sección "
                    "nueva que el template ganó después de que este archivo se generó. "
                    "Revisar si corresponde portarla a mano.",
                    file=output_relative,
                )
            )

    return findings


def _project_has_ui(root: Path) -> bool:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lstrip(".") in UI_EXTENSIONS:
            return True
    return False


def check_drift(root: Path) -> HealthCheckReport:
    """Corre las dos clases de drift descriptas en el docstring del módulo.

    El drift de contenido (2) corre para cualquier proyecto con
    `.rocky-spec/templates/` instalado. El drift de archivos ausentes (1)
    sigue siendo no-op si el proyecto no fue adoptado (no aplica a proyectos
    nuevos, que ya nacen con el flujo completo de la versión vigente)."""
    report = HealthCheckReport(category="drift")
    report.findings.extend(_content_drift_findings(root))

    state_path = root / SKILL_STATE_FILE
    if not state_path.exists():
        return report

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return report

    if state.get("mode") != "adopted":
        return report

    timestamp = state.get("timestamp", "fecha desconocida")

    for relative in ALWAYS_GENERATED:
        if not (root / relative).exists():
            report.findings.append(
                Finding(
                    severity="warning",
                    message=f"`{relative}` no existe — este proyecto fue adoptado el {timestamp}, "
                    "antes de que Modo Adopción (MA-6) generara este archivo en la versión "
                    "vigente de la skill. Pedile al agente que lo genere.",
                    file=relative,
                )
            )

    if _project_has_ui(root):
        for relative in UI_ONLY_GENERATED:
            if not (root / relative).exists():
                report.findings.append(
                    Finding(
                        severity="warning",
                        message=f"`{relative}` no existe — este proyecto fue adoptado el {timestamp} "
                        "y tiene interfaz visual, pero MA-6 no generó este archivo en su momento. "
                        "Pedile al agente que lo genere.",
                        file=relative,
                    )
                )

    license_decision = state.get("license_decision")
    license_exists = (root / "LICENSE").exists()
    if not license_exists:
        if license_decision is None:
            report.findings.append(
                Finding(
                    severity="warning",
                    message=f"`LICENSE` no existe y este proyecto (adoptado el {timestamp}) no tiene "
                    "`license_decision` registrada — probablemente nunca se le preguntó, porque la "
                    "adopción corrió antes de que MA-6 guardara esta decisión. Pedile al agente que "
                    "pregunte si corresponde agregar una LICENSE.",
                    file="LICENSE",
                )
            )
        elif license_decision != "skipped":
            report.findings.append(
                Finding(
                    severity="warning",
                    message=f"`LICENSE` no existe pero `.skill-state.json` registra "
                    f"`license_decision: \"{license_decision}\"` — se decidió generar una y no está. "
                    "Pedile al agente que la regenere.",
                    file="LICENSE",
                )
            )

    return report
