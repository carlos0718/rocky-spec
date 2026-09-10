"""
rocky check drift / rocky update — detecta proyectos adoptados (Modo
Adopción, MA-6) cuyo `.skill-state.json` es anterior a que el kit generara
algún archivo que la versión vigente de la skill sí genera hoy.

Nace del caso real de `cuotify`: adoptado el 2026-08-10 con una versión de
`mode-adopt.md` que todavía no incluía los pasos de CONSTITUTION.md,
SECURITY.md, OBSERVABILITY.md, CHANGELOG.md ni ACCESSIBILITY.md — sin
ninguna forma automática de notar el hueco hasta una auditoría manual.
"""
from __future__ import annotations

import json
from pathlib import Path

from .health_check import Finding, HealthCheckReport, IGNORED_DIRS

SKILL_STATE_FILE = ".skill-state.json"

# Archivos que MA-6 genera siempre para un proyecto adoptado, en la versión
# vigente de la skill — independiente de si el proyecto tiene interfaz visual.
ALWAYS_GENERATED = ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md")

# Archivos que MA-6 solo genera si el proyecto tiene interfaz visual.
UI_ONLY_GENERATED = ("ACCESSIBILITY.md", "design-system/MASTER.md")

UI_EXTENSIONS = ("html", "jsx", "tsx")


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
    """No-op si el proyecto no fue adoptado (no aplica a proyectos nuevos,
    que ya nacen con el flujo completo de la versión vigente)."""
    report = HealthCheckReport(category="drift")

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
