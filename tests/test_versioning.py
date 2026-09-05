import re
from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent / "src" / "rocky_spec"


def test_version_is_declared_in_exactly_one_place():
    """Regresión: hasta hace poco la versión estaba hardcodeada en tres
    lugares (pyproject.toml, scaffold.ROCKY_SPEC_VERSION, __init__.__version__)
    que había que acordarse de mover juntos en cada release — y no se movían.
    Ahora `__init__.py` la lee de los metadatos del paquete (que a su vez
    vienen de pyproject.toml) — este test falla si alguien vuelve a
    hardcodear un número de versión suelto en el código fuente."""
    hardcoded_version = re.compile(r'["\']?\d+\.\d+\.\d+["\']?\s*$', re.MULTILINE)
    offenders = []
    for py_file in SRC_ROOT.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue  # acá SÍ está permitido — es la única fuente de verdad
        text = py_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r'=\s*["\']?\d+\.\d+\.\d+["\']?\s*$', stripped):
                offenders.append(f"{py_file.relative_to(SRC_ROOT)}: {stripped}")
    assert offenders == [], f"Versión hardcodeada fuera de __init__.py: {offenders}"


def test_scaffold_version_matches_package_metadata():
    from rocky_spec import __version__
    from rocky_spec.scaffold import ROCKY_SPEC_VERSION

    assert ROCKY_SPEC_VERSION == __version__
