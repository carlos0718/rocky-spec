"""
rocky check anchors — verifica que los archivos ancla de cada agente
(``CLAUDE.md`` para Claude Code, ``.cursor/rules/rocky.mdc`` para Cursor)
sigan apuntando al conocimiento compartido en ``.rocky-spec/``.

Nace del bug real que motivó toda esta feature: la raíz de este mismo repo
se quedó sin ``CLAUDE.md`` durante semanas y nadie lo notó hasta que se miró
el explorador de archivos a mano. Este check es la versión determinista de
esa inspección manual — no depende de que alguien se acuerde de mirar.
"""
from __future__ import annotations

from pathlib import Path

from ..integrations.claude import CLAUDE_MD_ANCHOR, CLAUDE_MD_PATH
from ..integrations.cursor import CURSOR_RULE_ANCHOR, CURSOR_RULE_PATH
from .health_check import Finding, HealthCheckReport


def check_anchors(project_root: Path) -> HealthCheckReport:
    findings: list[Finding] = []

    claude_md = project_root / CLAUDE_MD_PATH
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if CLAUDE_MD_ANCHOR not in content:
            findings.append(
                Finding(
                    severity="critical",
                    message=f"CLAUDE.md existe pero no tiene `{CLAUDE_MD_ANCHOR}` — "
                    "Claude Code no va a auto-cargar AGENTS.md al arrancar una sesión "
                    "nueva. Corré `rocky init --agent claude` para repararlo.",
                    file=CLAUDE_MD_PATH,
                )
            )

    rocky_mdc = project_root / CURSOR_RULE_PATH
    if rocky_mdc.exists():
        content = rocky_mdc.read_text(encoding="utf-8")
        if CURSOR_RULE_ANCHOR not in content:
            findings.append(
                Finding(
                    severity="critical",
                    message=f"{CURSOR_RULE_PATH} existe pero no apunta a {CURSOR_RULE_ANCHOR} — "
                    "Cursor perdió la referencia al conocimiento compartido. Corré "
                    "`rocky init --agent cursor` para repararlo.",
                    file=CURSOR_RULE_PATH,
                )
            )

    return HealthCheckReport(category="anchors", findings=findings)
