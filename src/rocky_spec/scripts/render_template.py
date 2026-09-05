"""
Renderizador determinista de templates.

Hasta ahora, rellenar un `.template` (SPEC.md.template, SECURITY.md.template...)
dependía 100% de que el LLM leyera la prosa de instrucciones y sustituyera
cada ``{{PLACEHOLDER}}`` a mano. Funciona, pero no es reproducible: dos
corridas del mismo paso pueden rellenar el mismo placeholder de formas
sutilmente distintas, o directamente saltearse uno.

Esta función hace la parte mecánica de forma determinista — el LLM sigue
decidiendo *qué valor* le corresponde a cada placeholder (eso requiere
criterio), pero la sustitución en sí ya no depende de que lo haga bien
"a mano" cada vez.

Soporta dos formas de placeholder:
    {{NOMBRE}}                      -> se reemplaza si está en `values`,
                                        se deja intacto si no (para que el
                                        chequeo de completitud lo detecte)
    {{NOMBRE, default: el valor}}   -> si `values` no trae NOMBRE, usa el
                                        default embebido en el propio template
"""
from __future__ import annotations

import re
from pathlib import Path

_PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)(?:\s*,\s*default:\s*([^}]*))?\}\}")


def render(template_text: str, values: dict[str, str]) -> str:
    """Sustituye placeholders en `template_text` usando `values`, cayendo al
    default inline del template si no hay valor provisto."""

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        inline_default = match.group(2)
        if name in values:
            return values[name]
        if inline_default is not None:
            return inline_default.strip()
        return match.group(0)  # sin valor y sin default -> se deja igual

    return _PLACEHOLDER_RE.sub(_replace, template_text)


def render_file(template_path: Path, output_path: Path, values: dict[str, str]) -> list[str]:
    """Renderiza un archivo completo y lo escribe en `output_path`. Devuelve
    la lista de placeholders que quedaron SIN resolver (ni valor ni default) —
    útil para que `rocky check qa` los reporte sin tener que grepear texto."""
    template_text = template_path.read_text(encoding="utf-8")
    rendered = render(template_text, values)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return find_unresolved(rendered)


def find_unresolved(text: str) -> list[str]:
    """Devuelve los nombres de placeholder que sobrevivieron al render —
    equivalente determinista al grep de placeholders que usa P7.5."""
    return sorted({m.group(1) for m in _PLACEHOLDER_RE.finditer(text)})
