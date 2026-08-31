"""
Versión en código de los chequeos mecánicos de P7.5 (Revisión funcional y de
QA): completitud de placeholders y trazabilidad RF -> US -> tarea, RNF -> tarea.

Lo que requiere criterio (ambigüedad, testabilidad, casos borde) sigue siendo
trabajo del LLM — acá solo se resuelve la parte de "contar y cruzar IDs",
que es 100% mecánica y por lo tanto no debería depender de que el LLM la
haga bien cada vez.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ID_PATTERN = re.compile(r"\b(RF|US|RNF)-(\d+)\b")
IMPLEMENTS_PATTERN = re.compile(r"implementa (RF-\d+)")
PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")


@dataclass
class TraceabilityReport:
    unresolved_placeholders: dict[str, list[str]] = field(default_factory=dict)
    orphan_rf: list[str] = field(default_factory=list)  # RF sin ninguna US
    orphan_us: list[str] = field(default_factory=list)  # US sin ninguna tarea
    unplanned_rnf: list[str] = field(default_factory=list)  # RNF con objetivo real sin tarea

    @property
    def is_clean(self) -> bool:
        return not (
            self.unresolved_placeholders
            or self.orphan_rf
            or self.orphan_us
            or self.unplanned_rnf
        )


def check_placeholder_completeness(*files: Path) -> dict[str, list[str]]:
    """Paso 1 de P7.5 — grep de {{PLACEHOLDER}} sin rellenar, por archivo."""
    result: dict[str, list[str]] = {}
    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        found = sorted(set(PLACEHOLDER_PATTERN.findall(text)))
        if found:
            result[str(f)] = found
    return result


def check_traceability(spec_path: Path, *todo_paths: Path) -> TraceabilityReport:
    """Paso 4 de P7.5 — cadena RF -> US -> tarea, y RNF con objetivo real -> tarea."""
    report = TraceabilityReport()
    if not spec_path.exists():
        return report

    spec_text = spec_path.read_text(encoding="utf-8", errors="ignore")
    todo_text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore") for p in todo_paths if p.exists()
    )

    rf_ids = sorted(set(m.group(2) for m in ID_PATTERN.finditer(spec_text) if m.group(1) == "RF"))
    us_ids = sorted(set(m.group(2) for m in ID_PATTERN.finditer(spec_text) if m.group(1) == "US"))
    rnf_ids = sorted(set(m.group(2) for m in ID_PATTERN.finditer(spec_text) if m.group(1) == "RNF"))
    rf_implemented = {m.group(1) for m in IMPLEMENTS_PATTERN.finditer(spec_text)}

    for rf in rf_ids:
        if f"RF-{rf}" not in rf_implemented:
            report.orphan_rf.append(f"RF-{rf}")

    for us in us_ids:
        if f"US-{us}" not in todo_text:
            report.orphan_us.append(f"US-{us}")

    default_markers = (
        "sin objetivo",
        "sin proyección",
        "sin política",
        "un solo idioma",
        "no aplica",
    )
    rnf_lines: dict[str, list[str]] = {}
    for line in spec_text.splitlines():
        for match in re.finditer(r"RNF-(\d+)", line):
            rnf_id = f"RNF-{match.group(1)}"
            rnf_lines.setdefault(rnf_id, []).append(line)

    for rnf_id, lines in rnf_lines.items():
        # Si CUALQUIER mención de este RNF (ej. la fila de la tabla de NFRs)
        # tiene el marcador de default, se considera cubierto — sin importar
        # que otras menciones sueltas (ej. una línea de changelog que solo
        # lista los IDs) no lo tengan. Antes se evaluaba línea por línea de
        # forma aislada, lo que producía falsos positivos con menciones
        # fuera de la tabla de definición (encontrado dogfooding esto mismo
        # sobre spec-charless).
        if any(any(marker in l.lower() for marker in default_markers) for l in lines):
            continue
        if rnf_id not in todo_text:
            report.unplanned_rnf.append(rnf_id)

    return report


def full_report(project_root: Path) -> TraceabilityReport:
    spec = project_root / "SPEC.md"
    todo = project_root / "TODO.md"
    todos_dir = project_root / "todos"
    todo_paths = [todo]
    if todos_dir.is_dir():
        todo_paths.extend(sorted(todos_dir.glob("*.md")))

    report = check_traceability(spec, *todo_paths)

    tracked_files = [
        f
        for f in [
            project_root / "SPEC.md",
            project_root / "SECURITY.md",
            project_root / "OBSERVABILITY.md",
            project_root / "CONSTITUTION.md",
            project_root / "design-system" / "MASTER.md",
        ]
        if f.exists()
    ]
    report.unresolved_placeholders = check_placeholder_completeness(*tracked_files)
    return report
