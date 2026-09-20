"""
Health-checks deterministas — la versión en código de lo que hasta ahora
eran bloques de bash descriptos en prosa (MA-1.5 / MA-1.6 / MA-1.7 del flujo
de Modo Adopción). Correrlos como función Python en vez de "decirle al LLM
qué comando ejecutar" da el mismo resultado sin importar qué agente esté
orquestando la sesión.

El LLM sigue siendo responsable de interpretar los hallazgos y decidir qué
hacer con cada uno — esto solo reemplaza la parte 100% mecánica.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .source_files import extensions_for, iter_source_files, languages_read, unread_language_counts

# Tabla "Tamaño de archivo" de coding-principles.md -> (revisar, dividir_sí_o_sí).
# None = esa fila del doc no da un umbral para ese escalón. "default" cubre componentes
# UI y cualquier archivo sin fila propia en el doc (250/400, el comportamiento histórico).
FILE_SIZE_LIMITS = {
    "default": (250, 400),
    "service": (300, 400),  # servicio / hook / composable
    "types": (300, 500),
    "tests": (500, None),  # el doc dice "dividir por describe/escenario", sin número
    "config": (None, None),  # config/constantes: sin límite práctico
}
HARD_CEILING_LINES = 1000  # regla dura del doc: sin excepción de tipo de archivo

KIND_LABELS = {
    "service": "servicio/hook",
    "types": "tipos",
    "tests": "tests",
    "config": "config/constantes",
}

_TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs"}
_TEST_NAME = re.compile(r"^test_|_tests?$|\.(test|spec)$|[a-z0-9]Tests?$")
_TYPES_NAME = re.compile(r"\.d$|\.types?$|^types?$")
_CONFIG_NAME = re.compile(r"\.config$|^config$|^constants?$")
_SERVICE_DIRS = {"services", "hooks", "composables"}
_SERVICE_NAME = re.compile(r"(?i:service|hook|composable)s?$|^use[A-Z]")

SECRET_PATTERN = re.compile(
    r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
    re.IGNORECASE,
)

PLACEHOLDER_VALUES = {"xxx", "your-key-here", "changeme", "example", "todo", "fixme"}


@dataclass
class Finding:
    severity: str  # "critical" | "warning"
    message: str
    file: str | None = None
    line: int | None = None


@dataclass
class HealthCheckReport:
    category: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def has_critical(self) -> bool:
        return any(f.severity == "critical" for f in self.findings)


def _is_test_dir(part: str) -> bool:
    return part.lower() in _TEST_DIRS or part.lower().endswith((".tests", ".test"))  # MyApp.Tests (C#)


def _file_kind(relative: Path) -> str:
    """Clasifica por nombre/carpetas *relativas al proyecto* (nunca la ruta
    absoluta: un proyecto bajo una carpeta `tests/` no es todo tests). Heurístico,
    no un parser: el orden resuelve solapes (un `UserServiceTests.cs` es tests)."""
    stem = relative.stem
    dirs = relative.parent.parts
    if any(_is_test_dir(d) for d in dirs) or _TEST_NAME.search(stem):
        return "tests"
    if "types" in dirs or _TYPES_NAME.search(stem):
        return "types"
    if _CONFIG_NAME.search(stem):
        return "config"
    if any(d in _SERVICE_DIRS for d in dirs) or _SERVICE_NAME.search(stem):
        return "service"
    return "default"


def check_file_sizes(root: Path) -> HealthCheckReport:
    """Equivalente determinista de MA-1.5 — límites de coding-principles.md."""
    report = HealthCheckReport(category="code")
    for path in iter_source_files(root, extensions_for("size")):
        try:
            n_lines = sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        kind = _file_kind(path.relative_to(root))
        review_at, split_at = FILE_SIZE_LIMITS[kind]
        see = "ver coding-principles.md" if kind == "default" else f"ver coding-principles.md, límite de {KIND_LABELS[kind]}"
        if n_lines >= HARD_CEILING_LINES:
            report.findings.append(
                Finding("critical", f"{n_lines} líneas — techo duro de {HARD_CEILING_LINES} sin excepción", str(path))
            )
        elif split_at is not None and n_lines >= split_at:
            report.findings.append(
                Finding("warning", f"{n_lines} líneas — dividir sí o sí ({see})", str(path))
            )
        elif review_at is not None and n_lines >= review_at:
            report.findings.append(
                Finding("warning", f"{n_lines} líneas — zona de revisar ({see})", str(path))
            )
    return report


def check_security(root: Path) -> HealthCheckReport:
    """Equivalente determinista de MA-1.6."""
    report = HealthCheckReport(category="security")

    gitignore = root / ".gitignore"
    gitignore_text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if not re.search(r"^\.env$", gitignore_text, re.MULTILINE):
        report.findings.append(Finding("warning", ".env no está en .gitignore"))

    tracked = _git_ls_files(root)
    for f in tracked:
        if re.fullmatch(r"\.env(\.[a-z]+)?", Path(f).name) and not f.endswith(".env.example"):
            report.findings.append(Finding("critical", f".env commiteado en el repo: {f}"))

    for path in iter_source_files(root, extensions_for("secrets")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in SECRET_PATTERN.finditer(text):
            value = text[match.start():match.end()]
            if any(ph in value.lower() for ph in PLACEHOLDER_VALUES):
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            # Nunca se guarda ni se muestra el valor — solo archivo y línea.
            report.findings.append(
                Finding("critical", "posible secret hardcodeado", str(path), line_no)
            )

    audit = _run(["npm", "audit", "--audit-level=high", "--json"], cwd=root)
    if audit and '"severity"' in audit:
        report.findings.append(Finding("warning", "npm audit encontró vulnerabilidades high/critical"))

    return report


def check_observability(root: Path) -> HealthCheckReport:
    """Equivalente determinista de MA-1.7."""
    report = HealthCheckReport(category="observability")

    has_error_tracking = False
    has_health_endpoint = False
    console_log_count = 0
    evaluated_files = 0

    for path in iter_source_files(root, extensions_for("observability")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        evaluated_files += 1
        if re.search(r"Sentry\.init|@sentry/|bugsnag|rollbar", text, re.IGNORECASE):
            has_error_tracking = True
        if re.search(r"""['"](/health|/healthz|/status)['"]""", text):
            has_health_endpoint = True
        console_log_count += len(re.findall(r"console\.log\(", text))

    skipped = _describe_counts(unread_language_counts(root, "observability"))
    readable = ", ".join(sorted(languages_read("observability")))

    if evaluated_files == 0:
        # Sin nada que leer, "no encontré error tracking" sería afirmar lo que no se verificó.
        why = f"el proyecto tiene {skipped}, sin patrones para esos lenguajes todavía" if skipped else "no encontré archivos de esos lenguajes"
        report.findings.append(Finding("warning", f"no evaluado: este check solo lee archivos de {readable}; {why}"))
        return report

    if not has_error_tracking:
        report.findings.append(Finding("warning", "no encontré error tracking configurado (Sentry u otro)"))
    if not has_health_endpoint:
        report.findings.append(Finding("warning", "no encontré un endpoint de health check"))
    if console_log_count > 15:
        report.findings.append(
            Finding("warning", f"{console_log_count} apariciones de console.log — sin logging estructurado")
        )
    if skipped:
        report.findings.append(
            Finding(
                "warning",
                f"no se evaluaron {skipped} — sin patrones para esos lenguajes todavía; "
                f"los avisos de arriba solo valen para {readable}",
            )
        )

    return report


def _describe_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{name} ({n} archivo{'s' if n != 1 else ''})" for name, n in sorted(counts.items()))


def _git_ls_files(root: Path) -> list[str]:
    output = _run(["git", "ls-files"], cwd=root)
    return output.splitlines() if output else []


def _run(cmd: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None


def run_all(root: Path) -> list[HealthCheckReport]:
    return [check_file_sizes(root), check_security(root), check_observability(root)]
