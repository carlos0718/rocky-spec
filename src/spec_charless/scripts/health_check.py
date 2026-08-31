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

IGNORED_DIRS = {"node_modules", ".git", "dist", "build", ".venv", "__pycache__"}

FILE_SIZE_LIMITS = {
    # extensión -> (ideal, revisar, dividir_si_o_si)
    "component": (150, 250, 400),
    "service": (200, 300, 400),
    "default": (200, 300, 500),
}

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


def _iter_source_files(root: Path, extensions: tuple[str, ...]) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lstrip(".") in extensions:
            files.append(path)
    return files


def check_file_sizes(root: Path) -> HealthCheckReport:
    """Equivalente determinista de MA-1.5 — límites de coding-principles.md."""
    report = HealthCheckReport(category="code")
    for path in _iter_source_files(root, ("ts", "tsx", "js", "jsx", "py", "go", "rs")):
        try:
            n_lines = sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if n_lines >= 1000:
            report.findings.append(
                Finding("critical", f"{n_lines} líneas — techo duro de 1000 sin excepción", str(path))
            )
        elif n_lines >= 400:
            report.findings.append(
                Finding("warning", f"{n_lines} líneas — dividir sí o sí (ver coding-principles.md)", str(path))
            )
        elif n_lines >= 250:
            report.findings.append(
                Finding("warning", f"{n_lines} líneas — zona de revisar", str(path))
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

    for path in _iter_source_files(root, ("ts", "js", "py", "go")):
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

    for path in _iter_source_files(root, ("ts", "tsx", "js", "jsx", "py")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(r"Sentry\.init|@sentry/|bugsnag|rollbar", text, re.IGNORECASE):
            has_error_tracking = True
        if re.search(r"""['"](/health|/healthz|/status)['"]""", text):
            has_health_endpoint = True
        console_log_count += len(re.findall(r"console\.log\(", text))

    if not has_error_tracking:
        report.findings.append(Finding("warning", "no encontré error tracking configurado (Sentry u otro)"))
    if not has_health_endpoint:
        report.findings.append(Finding("warning", "no encontré un endpoint de health check"))
    if console_log_count > 15:
        report.findings.append(
            Finding("warning", f"{console_log_count} apariciones de console.log — sin logging estructurado")
        )

    return report


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
