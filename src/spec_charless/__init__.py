"""
La versión se lee UNA sola vez, desde los metadatos del paquete instalado
(que a su vez vienen de `pyproject.toml`) — no se hardcodea acá ni en
ningún otro módulo. Antes había tres declaraciones sueltas (`pyproject.toml`,
`scaffold.CHARLESS_VERSION`, y este mismo `__version__`, que ni se usaba en
ningún lado) que había que acordarse de mover juntas en cada release. Con
esto, moverla en un solo lugar (`pyproject.toml`) alcanza.
"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("spec-charless")
except PackageNotFoundError:
    # Corriendo desde el código fuente sin `pip install -e .` todavía.
    __version__ = "0.0.0+sin-instalar"

__all__ = ["__version__"]
