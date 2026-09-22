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

from .build import BASE_FILES
from .render_template import find_unresolved

ID_PATTERN = re.compile(r"\b(RF|US|RNF)-(\d+)\b")
IMPLEMENTS_PATTERN = re.compile(r"implementa (RF-\d+)")

# Archivos que `rocky build`/P6-P7 genera solo bajo condición (arquitectura
# con UI, P5.8, P5.9, P8.5 opcional) o exclusivos de proyecto creativo -- no
# entran a BASE_FILES porque no todo proyecto los tiene, pero si existen
# también deben quedar libres de placeholders sin resolver. Ver
# commands/p5.8-accessibility.md, p5.9-practices.md, p4.5-design-system.md,
# p8-p8.5-validation-systemprompt.md, p6-p7-files-todo.md sección Creativo.
OPTIONAL_TRACKED_FILES: tuple[str, ...] = (
    "ACCESSIBILITY.md",
    "PRACTICES.md",
    "design-system/MASTER.md",
    "SYSTEM_PROMPT.md",
    "BRIEF.md",
    "STORYBOARD.md",
)


def tracked_file_candidates() -> list[str]:
    """Todo archivo (ruta relativa a la raíz del proyecto) que `rocky check qa`
    podría llegar a revisar si existe. Se deriva de ``BASE_FILES`` en vez de
    mantener una lista aparte -- antes de esto, el título de
    `commands/p7.5-qa-review.md`, su propio grep de fallback y esta función
    tenían tres listas distintas, ninguna coincidía con las otras dos, y
    ninguna incluía `AGENTS.md`/`CLAUDE.md`/`CHANGELOG.md`/`README.md` pese a
    ser archivos base generados por `rocky build` -- ver
    tests/test_placeholder_hygiene.py."""
    return [output for _, output in BASE_FILES] + list(OPTIONAL_TRACKED_FILES)


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
        found = find_unresolved(text)
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
        # sobre rocky-spec).
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
        project_root / relative
        for relative in tracked_file_candidates()
        if (project_root / relative).exists()
    ]
    report.unresolved_placeholders = check_placeholder_completeness(*tracked_files)
    return report
