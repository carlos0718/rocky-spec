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
    "javascript": ("js", "jsx"),
    "vue": ("vue",),
    "svelte": ("svelte",),
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


# check -> extensiones que lee.
CHECK_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "size": CODE_EXTENSIONS,
    "secrets": ("ts", "js", "py", "go"),
    "observability": _extensions_of("typescript", "javascript", "python"),
    "accessibility": ("html", "jsx", "tsx"),
    "contrast": ("css", "html", "jsx", "tsx"),
    "ui": ("html", "jsx", "tsx"),
}


def extensions_for(check: str) -> tuple[str, ...]:
    return CHECK_EXTENSIONS[check]


def is_ignored(path: Path, root: Path) -> bool:
    """Solo mira las carpetas *dentro* de ``root``: un proyecto que vive bajo una
    carpeta llamada como una de IGNORED_DIRS (ej. ``WORKDIR /build`` en Docker)
    no debe quedar entero ignorado."""
    return any(part in IGNORED_DIRS for part in path.relative_to(root).parent.parts)


def iter_source_files(root: Path, extensions: tuple[str, ...]) -> Iterator[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if is_ignored(path, root):
            continue
        if path.suffix.lstrip(".") in extensions:
            yield path
