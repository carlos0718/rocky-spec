"""
Fuente única de qué archivos lee cada health-check.

Antes cada check tenía su propia lista de extensiones y se desincronizaron:
`check code` leía `.cs` y `check security` no, `check security` no leía `.tsx`
y `check observability` sí. Acá hay una tabla de lenguajes y un alcance
explícito por check (`CHECK_EXTENSIONS`); ningún check escribe su propia lista.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

IGNORED_DIRS = {
    "node_modules", ".git", "dist", "build", ".venv", "__pycache__",
    # generados o de terceros — no son código del proyecto
    "venv", "vendor", "obj", "target", ".next", "coverage",
}

# lenguaje -> extensiones: los stacks de reference/stacks-code.md, más C#.
LANGUAGES: dict[str, tuple[str, ...]] = {
    "typescript": ("ts", "tsx"),
    "javascript": ("js", "jsx", "mjs", "cjs"),
    "vue": ("vue",),
    "svelte": ("svelte",),
    "astro": ("astro",),
    "python": ("py",),
    "go": ("go",),
    "rust": ("rs",),
    "java": ("java",),
    "kotlin": ("kt",),
    "csharp": ("cs",),
    "ruby": ("rb",),
    "php": ("php",),
}

CODE_EXTENSIONS: tuple[str, ...] = tuple(ext for exts in LANGUAGES.values() for ext in exts)


def _extensions_of(*languages: str) -> tuple[str, ...]:
    return tuple(ext for name in languages for ext in LANGUAGES[name])


# Vistas y templates que alojan HTML, más allá de los componentes de UI de LANGUAGES.
# "blade.php" es compuesta: el sufijo real de una vista Laravel es `.php`, igual que el de
# una API PHP sin UI, así que se distingue por el nombre completo.
TEMPLATE_EXTENSIONS: tuple[str, ...] = (
    "html", "htm",
    "cshtml", "razor",  # .NET: Razor Pages / MVC, Blazor
    "erb", "haml", "slim",  # Rails
    "blade.php", "twig",  # PHP: Laravel, Symfony
    "ejs", "hbs", "handlebars", "njk", "pug",  # Node
    "jinja", "j2",  # Python (Django/Flask usan `.html`)
    "jsp",  # Java
    "gohtml",  # Go
    "liquid", "mustache",
)

# ¿Este proyecto tiene interfaz visual? Templates + componentes de UI.
UI_EXTENSIONS: tuple[str, ...] = TEMPLATE_EXTENSIONS + _extensions_of("vue", "svelte", "astro") + ("jsx", "tsx")


# check -> extensiones que lee.
CHECK_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "size": CODE_EXTENSIONS,
    "secrets": CODE_EXTENSIONS,  # la regex no depende del lenguaje: `clave = "valor"`
    "observability": _extensions_of("typescript", "javascript", "python"),
    "accessibility": ("html", "jsx", "tsx"),
    "contrast": ("css", "html", "jsx", "tsx"),
    "ui": UI_EXTENSIONS,
}


# Lenguajes que un check con patrones propios NO lee, con el motivo. Cada lenguaje de
# LANGUAGES debe leerse o estar acá (test_source_files.py lo exige): un lenguaje nuevo
# no entra solo a un check que no tiene patrones para él.
_NODE_PYTHON_ONLY = "sus patrones (Sentry, /health, console.log) son de Node/Python; falta el equivalente para este lenguaje"
NOT_READ: dict[str, dict[str, str]] = {
    "observability": {
        name: _NODE_PYTHON_ONLY
        for name in ("vue", "svelte", "astro", "go", "rust", "java", "kotlin", "csharp", "ruby", "php")
    },
}


def extensions_for(check: str) -> tuple[str, ...]:
    return CHECK_EXTENSIONS[check]


def languages_read(check: str) -> set[str]:
    scope = set(extensions_for(check))
    return {name for name, extensions in LANGUAGES.items() if set(extensions) <= scope}


def unread_language_counts(root: Path, check: str) -> dict[str, int]:
    """Cuántos archivos de cada lenguaje que ``check`` no lee hay en el proyecto."""
    owner = {ext: name for name in NOT_READ.get(check, {}) for ext in LANGUAGES[name]}
    counts: dict[str, int] = {}
    for path in iter_source_files(root, tuple(owner)):
        name = owner[path.suffix.lstrip(".").lower()]
        counts[name] = counts.get(name, 0) + 1
    return counts


def is_ignored(path: Path, root: Path) -> bool:
    """Solo mira las carpetas *dentro* de ``root``: un proyecto que vive bajo una
    carpeta llamada como una de IGNORED_DIRS (ej. ``WORKDIR /build`` en Docker)
    no debe quedar entero ignorado."""
    return any(part in IGNORED_DIRS for part in path.relative_to(root).parent.parts)


def iter_source_files(root: Path, extensions: tuple[str, ...]) -> Iterator[Path]:
    """Archivos bajo ``root`` cuyo nombre termina en alguna de ``extensions``, sin
    distinguir mayúsculas (Windows) y aceptando extensiones compuestas (``blade.php``)."""
    suffixes = tuple(f".{ext}" for ext in extensions)
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if is_ignored(path, root):
            continue
        if path.name.lower().endswith(suffixes):
            yield path
