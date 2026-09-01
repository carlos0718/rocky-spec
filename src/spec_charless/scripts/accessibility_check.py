"""
Health-check determinista de accesibilidad web — corre sobre HTML/JSX/TSX
generados o adoptados. Complementa (no reemplaza) la prosa de
`reference/ui-design-guidelines.md` y la regla base "HTML semántico" de
`reference/coding-principles.md`: esas siguen guiando *cómo escribir* el
código; esto audita *lo que ya se escribió*.

Como el resto de los `check_*` de este paquete, es puramente diagnóstico —
encuentra y reporta, nunca edita código. Un `alt`/`aria-label` autogenerado
sin contexto real (¿qué dice la imagen? ¿qué hace el botón?) puede ser peor
que no tenerlo — esa decisión sigue siendo del LLM o de quien programa,
con el contexto real del componente.

Cada heurístico documenta explícitamente qué NO cubre — son regex sobre
texto, no un parser de HTML/JSX real, así que hay casos borde conocidos
(spread props, texto oculto vía CSS, custom properties). Preferible avisar
la limitación que fingir cobertura completa.
"""
from __future__ import annotations

import re
from pathlib import Path

from .health_check import Finding, HealthCheckReport, _iter_source_files

# --- Heurístico 1: <img> sin alt ---
IMG_TAG = re.compile(r"<img\b[^>]*/?>", re.IGNORECASE | re.DOTALL)
ALT_ATTR = re.compile(r"\balt\s*=", re.IGNORECASE)
SPREAD_PROPS = re.compile(r"\{\s*\.\.\.")  # {...props} -- puede traer alt sin que se vea acá

# --- Heurístico 2: <html> sin lang ---
HTML_TAG = re.compile(r"<html\b[^>]*>", re.IGNORECASE)
LANG_ATTR = re.compile(r"\blang\s*=", re.IGNORECASE)

# --- Heurístico 3: <div onClick> sin role/tabIndex ---
DIV_ONCLICK = re.compile(r"<div\b[^>]*\bon[Cc]lick\s*=[^>]*>", re.IGNORECASE | re.DOTALL)
ROLE_OR_TABINDEX = re.compile(r"\b(role|tabIndex|tabindex)\s*=", re.IGNORECASE)

# --- Heurístico 4: <button> solo-ícono sin aria-label ---
BUTTON_TAG = re.compile(r"<button\b([^>]*)>(.*?)</button>", re.IGNORECASE | re.DOTALL)
ICON_ONLY_CHILD = re.compile(r"<(svg|Icon\w*|FontAwesome\w*|\w*Icon)\b", re.IGNORECASE)
ARIA_LABEL_ATTR = re.compile(r"\baria-label\s*=", re.IGNORECASE)
STRIP_TAGS = re.compile(r"<[^>]+>")

# --- Heurístico 5: contraste WCAG AA básico ---
CSS_BLOCK = re.compile(r"[^{}]+\{([^{}]*)\}")
INLINE_STYLE_ATTR = re.compile(r'style\s*=\s*"([^"]*)"', re.IGNORECASE)
COLOR_PROP = re.compile(r"(?<!background-)\bcolor\s*:\s*([^;]+)", re.IGNORECASE)
BG_PROP = re.compile(r"\bbackground(?:-color)?\s*:\s*([^;]+)", re.IGNORECASE)
CSS_VAR_USAGE = re.compile(r"var\(--")
HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGB_COLOR = re.compile(r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,[^)]+)?\)$", re.IGNORECASE)

WCAG_AA_NORMAL_TEXT_RATIO = 4.5


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_img_alt(root: Path) -> list[Finding]:
    """<img> sin `alt`. NO flaggea si el tag tiene `{...spread}` -- puede
    traer `alt` inyectado dinámicamente, no se ve en el texto."""
    findings: list[Finding] = []
    for path in _iter_source_files(root, ("html", "jsx", "tsx")):
        text = _read(path)
        if text is None:
            continue
        for match in IMG_TAG.finditer(text):
            tag = match.group(0)
            if SPREAD_PROPS.search(tag):
                continue
            if not ALT_ATTR.search(tag):
                findings.append(
                    Finding("warning", "<img> sin atributo alt", str(path), _line_at(text, match.start()))
                )
    return findings


def check_html_lang(root: Path) -> list[Finding]:
    """<html> sin `lang`. Bajo riesgo de falso positivo -- sin excepciones."""
    findings: list[Finding] = []
    for path in _iter_source_files(root, ("html", "jsx", "tsx")):
        text = _read(path)
        if text is None:
            continue
        for match in HTML_TAG.finditer(text):
            if not LANG_ATTR.search(match.group(0)):
                findings.append(
                    Finding("critical", "<html> sin atributo lang", str(path), _line_at(text, match.start()))
                )
    return findings


def check_clickable_div_role(root: Path) -> list[Finding]:
    """<div onClick>/<div onclick> sin `role`/`tabIndex` en el mismo tag --
    no es focuseable ni anunciado como interactivo sin eso."""
    findings: list[Finding] = []
    for path in _iter_source_files(root, ("html", "jsx", "tsx")):
        text = _read(path)
        if text is None:
            continue
        for match in DIV_ONCLICK.finditer(text):
            if not ROLE_OR_TABINDEX.search(match.group(0)):
                findings.append(
                    Finding(
                        "warning",
                        "<div> con onClick sin role/tabIndex — no es focuseable ni anunciado como interactivo",
                        str(path),
                        _line_at(text, match.start()),
                    )
                )
    return findings


def check_icon_only_button(root: Path) -> list[Finding]:
    """<button> cuyo contenido es solo un ícono, sin ningún texto ni
    aria-label. Heurístico más frágil del set: cualquier texto dentro del
    tag cuenta como "tiene nombre accesible" -- incluye correctamente el
    patrón `sr-only`/`visually-hidden` (texto real para el screen reader,
    oculto solo visualmente), pero por la misma razón NO detecta el caso
    inverso: texto oculto con `display:none`/`visibility:hidden`, que no
    le da nombre accesible a nadie (ni screen reader) y sigue sin
    flaggearse -- falso negativo conocido, no falso positivo."""
    findings: list[Finding] = []
    for path in _iter_source_files(root, ("html", "jsx", "tsx")):
        text = _read(path)
        if text is None:
            continue
        for match in BUTTON_TAG.finditer(text):
            attrs, inner = match.group(1), match.group(2)
            if ARIA_LABEL_ATTR.search(attrs):
                continue
            if not ICON_ONLY_CHILD.search(inner):
                continue
            visible_text = STRIP_TAGS.sub("", inner).strip()
            if visible_text:
                continue
            findings.append(
                Finding(
                    "warning",
                    "<button> solo-ícono sin aria-label",
                    str(path),
                    _line_at(text, match.start()),
                )
            )
    return findings


def parse_color(value: str) -> tuple[int, int, int] | None:
    """Hex (#RGB/#RRGGBB) o rgb()/rgba(). None para `var(--x)`, colores por
    palabra clave (`white`, `red`...) u otro valor no parseable -- fuera de
    alcance en esta primera versión, ver docstring del módulo."""
    value = value.strip()
    if HEX_COLOR.match(value):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        return tuple(int(digits[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    rgb_match = RGB_COLOR.match(value)
    if rgb_match:
        return tuple(int(rgb_match.group(i)) for i in (1, 2, 3))  # type: ignore[return-value]
    return None


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Luminancia relativa sRGB, fórmula W3C (WCAG 2.x)."""

    def channel(c: int) -> float:
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb_a: tuple[int, int, int], rgb_b: tuple[int, int, int]) -> float:
    """(L1 + 0.05) / (L2 + 0.05), con L1 el más claro de los dos."""
    l1 = relative_luminance(rgb_a)
    l2 = relative_luminance(rgb_b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _check_declaration_block(decl: str, path: Path, full_text: str, offset: int, findings: list[Finding]) -> None:
    color_match = COLOR_PROP.search(decl)
    bg_match = BG_PROP.search(decl)
    if not color_match or not bg_match:
        return
    color_val, bg_val = color_match.group(1).strip(), bg_match.group(1).strip()
    if CSS_VAR_USAGE.search(color_val) or CSS_VAR_USAGE.search(bg_val):
        return  # custom property -- no se resuelve el valor real, fuera de alcance
    color_rgb = parse_color(color_val)
    bg_rgb = parse_color(bg_val)
    if color_rgb is None or bg_rgb is None:
        return  # color por palabra clave, gradiente, u otro valor no parseable
    ratio = contrast_ratio(color_rgb, bg_rgb)
    if ratio < WCAG_AA_NORMAL_TEXT_RATIO:
        findings.append(
            Finding(
                "warning",
                f"contraste {ratio:.2f}:1 entre color y background — mínimo WCAG AA {WCAG_AA_NORMAL_TEXT_RATIO}:1 (texto normal)",
                str(path),
                _line_at(full_text, offset),
            )
        )


def check_color_contrast(root: Path) -> list[Finding]:
    """Pares `color`/`background(-color)` hardcodeados (hex o rgb()/rgba())
    en el mismo bloque CSS o el mismo `style="..."` inline. NO detecta
    clases de utilidades (Tailwind) ni `var(--x)` -- limitación conocida,
    no falso negativo silencioso: simplemente no hay valor de color que
    resolver desde el texto solo."""
    findings: list[Finding] = []
    for path in _iter_source_files(root, ("css", "html", "jsx", "tsx")):
        text = _read(path)
        if text is None:
            continue
        for match in CSS_BLOCK.finditer(text):
            _check_declaration_block(match.group(1), path, text, match.start(), findings)
        for match in INLINE_STYLE_ATTR.finditer(text):
            _check_declaration_block(match.group(1), path, text, match.start(), findings)
    return findings


def check_accessibility(root: Path) -> HealthCheckReport:
    report = HealthCheckReport(category="accessibility")
    report.findings += check_img_alt(root)
    report.findings += check_html_lang(root)
    report.findings += check_clickable_div_role(root)
    report.findings += check_icon_only_button(root)
    report.findings += check_color_contrast(root)
    return report
