"""
Interfaz de bienvenida del CLI — lo primero que ve alguien al correr
``rocky`` sin argumentos, o justo antes de que ``init`` arranque a
escribir archivos. Usa `rich` para algo prolijo en vez de texto plano
suelto — mismo espíritu que la pantalla inicial de ``specify init``.

El arte ASCII "ROCKY SPEC" se genera en runtime con ``pyfiglet``
(fuente ``standard``, la fuente por default de la librería) y se
renderiza con ``rich.Text`` -- centrado, con el color de marca
``BRAND``, y con fallback a ``COMPACT_TITLE`` (texto plano) si la
terminal es más angosta que ``BANNER_WIDTH`` (ver ``_banner_renderable``).

**Causa de los descuadres que se arrastraron desde v0.8.0**: Rich
descarta los espacios finales al medir cada línea de un ``Text`` con
``justify="center"``, así que el relleno de ``ljust`` se ignoraba y cada
fila terminaba centrada según su contenido visible -- las filas que
terminan antes (por la forma de las letras) quedaban corridas a la
derecha la mitad de la diferencia. Se diagnosticó erróneamente como un
problema de renderizado de la terminal del usuario durante varias
iteraciones de cambio de fuente y de librería (``ansi_shadow``,
``epic``, ``chunky``, ``colossal``, ``banner3``; ``pyfiglet`` y ``art``
-- que además generan contenido idéntico carácter por carácter para el
mismo nombre de fuente, porque leen los mismos archivos ``.flf``). El
arreglo real es centrar el bloque entero con ``Align.center`` en vez de
justificar línea por línea. ``test_banner_lines_are_vertically_aligned_when_rendered``
es la guarda: verifica el render completo, no el string (el test viejo
solo miraba el string y pasaba en verde con el bug presente).
"""
from __future__ import annotations

import json
from pathlib import Path

from pyfiglet import figlet_format
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME

console = Console()

# Color de marca -- hsla(15, 63%, 60%, 1), elegido por el usuario. Reemplaza
# "cyan" en todo el CLI (banner, bordes, acentos) menos los colores con
# significado propio (verde = activo/éxito, dim = secundario).
BRAND = "#D97959"

BANNER_TEXT = "ROCKY SPEC"
BANNER_FONT = "standard"

# Se descartan las líneas finales en blanco (pyfiglet deja una fila de
# espacios al final, no vacía: .rstrip("\n") no la saca porque no termina
# en "\n" puro) y se rellena cada línea hasta el ancho máximo. El ljust
# NO alcanza para el alineado del render -- Rich descarta los espacios
# finales al justificar; eso se resuelve en _banner_renderable con
# Align.center sobre el bloque entero.
_raw_banner_lines = figlet_format(BANNER_TEXT, font=BANNER_FONT, width=200).splitlines()
while _raw_banner_lines and not _raw_banner_lines[-1].strip():
    _raw_banner_lines.pop()
BANNER_WIDTH = max(len(line) for line in _raw_banner_lines)
BANNER = "\n".join(line.ljust(BANNER_WIDTH) for line in _raw_banner_lines)
COMPACT_TITLE = BANNER_TEXT

# Borde (1 char c/lado) + padding=(1, 2) (2 chars c/lado) del Panel exterior
# de show_welcome -- se resta al ancho de la consola para saber cuánto
# espacio real tiene el contenido de adentro.
OUTER_PANEL_OVERHEAD = 6

AUTHOR = "by Carlos Jesus"

TAGLINE = "Spec-Driven Development multi-agente · nivel Spec-Anchored"

FEATURES = [
    "Scaffolding multi-agente (Claude Code, Cursor, más por venir) sin duplicar conocimiento entre integraciones",
    "SPEC.md vivo (Spec-Anchored) con requisitos funcionales, historias de usuario y no funcionales, trazables entre sí",
    "CONSTITUTION.md con los principios que no se negocian: código, seguridad, arquitectura",
    "Health-checks deterministas — code smells, seguridad, observabilidad y trazabilidad de requisitos, sin depender de que un LLM interprete bash cada vez",
    "Instalación no destructiva — tracking por hash, nunca pisa archivos que edites a mano",
]

# Siglas propias del proyecto — las que no son obvias para alguien que
# recién arranca. Las metodologías más conocidas (SDD, TDD, BDD, DDD) no
# están acá — están explicadas en reference/methodologies.md, con más
# espacio del que entra en una pantalla de bienvenida.
GLOSSARY = [
    ("RF-N", "Requisito Funcional — una feature (fila de la tabla \"Features\" en SPEC.md)"),
    ("US-N", "User Story — historia de usuario, implementa uno o más RF"),
    ("RNF-N", "Requisito No Funcional — performance, escalabilidad, compatibilidad, etc."),
    ("MA", "Modo Adopción — cuando el proyecto ya tiene código y no arranca de cero"),
    ("P0…P8.5", "Pasos del flujo de creación (P = Paso), ver commands/ en orden"),
]

# Cómo se invoca la skill/los comandos que cada integración genera dentro
# del proyecto destino -- NO es el comando `rocky` (eso es la CLI, corre
# en cualquier terminal); esto es lo que se escribe DENTRO del agente
# correspondiente, después de un `rocky init --agent <x>`.
INVOCATION_HINT = {
    "claude": "/rocky-spec (Claude Code)",
    "cursor": "/rocky-* — 14 comandos en .cursor/commands/ (Cursor)",
}

# Espejo exacto de la tabla "Comandos disponibles" del README -- misma
# fuente de verdad en prosa, acá en datos para poder renderizarla con rich
# vía `rocky commands` en vez de mandar a leer el README.
COMMANDS = [
    ("rocky", "Sin subcomando: banner de bienvenida + ayuda."),
    ("rocky --version", "Imprime la versión instalada."),
    ("rocky commands", "Esta tabla."),
    ("rocky init [PATH] --agent <agente>", "Instala .rocky-spec/ y genera la integración de cada --agent (repetible)."),
    ("rocky init [PATH] --agent <agente> --force", "Igual que arriba, pero regenera .rocky-spec/ aunque ya exista."),
    ("rocky build [PATH] --values <json> [--force]", "Renderiza SPEC.md/CONSTITUTION.md/AGENTS.md/... desde .rocky-spec/templates/ a partir de un JSON de valores."),
    ("rocky build [PATH] --values <json> --template <t> --output <ruta>", "Modo single-file: renderiza un solo template (MASTER.md.template, ACCESSIBILITY.md.template) en vez del set fijo."),
    ("rocky list-integrations", "Lista los agentes soportados por esta versión."),
    ("rocky check code [PATH]", "Health-check: tamaño de archivo y code smells estructurales."),
    ("rocky check security [PATH]", "Health-check: secrets hardcodeados, .env commiteado, vulnerabilidades."),
    ("rocky check observability [PATH]", "Health-check: error tracking, health endpoint, logging estructurado."),
    ("rocky check qa [PATH]", "Trazabilidad RF → US → RNF → tarea y placeholders sin rellenar."),
    ("rocky check version [PATH]", "Bump de SemVer sugerido desde el último tag + aviso de fixes acumulados."),
    ("rocky check accessibility [PATH]", "Health-check: alt, lang, div clickeable sin rol, botón solo-ícono, contraste WCAG básico."),
]


def _integrations_table(active: set[str] | None = None) -> Table:
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2, 0, 0))
    table.add_column("Agente")
    table.add_column("Comando")
    table.add_column("Se invoca con")
    table.add_column("Estado")
    for key, integration in sorted(INTEGRATION_REGISTRY.items()):
        status = "[green]✓ activo[/green]" if active and key in active else "[dim]disponible[/dim]"
        table.add_row(integration.display_name, f"--agent {key}", INVOCATION_HINT.get(key, "—"), status)
    return table


def _glossary_table() -> Table:
    table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    table.add_column(style=f"bold {BRAND}", no_wrap=True)
    table.add_column()
    for abbr, meaning in GLOSSARY:
        table.add_row(abbr, meaning)
    return table


def _commands_table() -> Table:
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2, 0, 0))
    table.add_column("Comando", style=BRAND, no_wrap=True)
    table.add_column("Qué hace")
    for command, description in COMMANDS:
        table.add_row(command, description)
    return table


def _banner_renderable(available_width: int) -> RenderableType:
    """Arte ASCII completo si entra; si no, un título compacto en vez de
    dejar que Rich reparta cada línea a la mitad (lo que rompía el diseño
    al angostar la terminal por debajo de BANNER_WIDTH).

    El arte se centra con ``Align.center`` sobre el bloque entero, **no**
    con ``justify="center"`` en el ``Text``: Rich descarta los espacios
    finales al medir cada línea para justificarla, así que el relleno de
    ``ljust`` se ignora y cada fila termina centrada según su contenido
    visible -- las filas que terminan antes quedan corridas a la derecha
    la mitad de la diferencia, descuadrando el arte. ``Align.center``
    centra el bloque como una unidad y preserva el alineado relativo
    entre filas."""
    if available_width >= BANNER_WIDTH:
        return Align.center(Text(BANNER, style=f"bold {BRAND}", no_wrap=True, overflow="crop"))
    return Text(COMPACT_TITLE, style=f"bold {BRAND}", justify="center")


def _centered_panels(available_width: int, *panels: Panel) -> RenderableType:
    """Panel único: centrado. Dos paneles: en columnas lado a lado si
    entran ambos con margen, si no, apilados (cada uno igual centrado)."""
    if len(panels) == 1:
        return Align.center(panels[0])

    widths = [console.measure(p).maximum for p in panels]
    gap = 2
    if sum(widths) + gap * (len(panels) - 1) <= available_width:
        return Align.center(Columns(panels, padding=(0, gap), expand=False))

    stacked: list[RenderableType] = []
    for i, p in enumerate(panels):
        if i > 0:
            stacked.append("")
        stacked.append(Align.center(p))
    return Group(*stacked)


def show_commands() -> None:
    """``rocky commands`` -- la tabla completa, con descripción, de todo
    lo que la CLI sabe hacer. Espejo del README, no de la skill/agente."""
    console.print(
        Panel(
            _commands_table(),
            title="[bold]rocky — comandos disponibles[/bold]",
            border_style=BRAND,
            expand=False,
        )
    )


def show_welcome(project_root: Path | None = None) -> None:
    """Pantalla de bienvenida. Si ``project_root`` ya tiene ``.rocky-spec/``,
    muestra el estado actual del proyecto en vez del onboarding genérico.

    El layout se recalcula contra el ancho real de la terminal en cada
    corrida (``console.width``) -- nada queda fijo de una corrida a otra."""
    available_width = max(console.width - OUTER_PANEL_OVERHEAD, 20)

    header = Group(
        _banner_renderable(available_width),
        Text(f"{AUTHOR}  ·  v{__version__}", style="dim italic", justify="center"),
        Text(TAGLINE, style="italic", justify="center"),
    )

    body: list = [header, ""]

    body.append(Text("Qué hace este kit", style="bold"))
    for line in FEATURES:
        body.append(f"  • {line}")
    body.append("")

    glossary_panel = Panel(
        _glossary_table(), title="[bold]Glosario[/bold]", border_style="dim", expand=False
    )

    shared = (project_root or Path(".")) / SHARED_DIR_NAME
    manifest_path = shared / "install-manifest.json"

    if shared.is_dir():
        version = (shared / "VERSION").read_text().strip() if (shared / "VERSION").exists() else "?"
        active: set[str] = set()
        if manifest_path.exists():
            active = set(json.loads(manifest_path.read_text()).keys())

        integrations_panel = Panel(
            _integrations_table(active),
            title=f"[bold]Este proyecto ya usa rocky-spec[/bold] (.rocky-spec/ v{version})",
            border_style="green",
            expand=False,
        )
        body.append(_centered_panels(available_width, glossary_panel, integrations_panel))
        body.append(
            f"\nPróximos pasos: [{BRAND}]rocky check qa .[/{BRAND}] · "
            f"[{BRAND}]rocky init --agent <otro>[/{BRAND}] para sumar un agente más · "
            f"[{BRAND}]rocky commands[/{BRAND}] para ver todos los comandos"
        )
    else:
        integrations_panel = Panel(
            _integrations_table(),
            title="[bold]Agentes soportados[/bold]",
            border_style=BRAND,
            expand=False,
        )
        body.append(_centered_panels(available_width, glossary_panel, integrations_panel))
        body.append(
            f"\nEmpezar: [{BRAND}]rocky init . --agent claude[/{BRAND}] "
            f"(repetí --agent para instalar más de uno) · "
            f"[{BRAND}]rocky commands[/{BRAND}] para ver todos los comandos"
        )

    console.print(Panel(Group(*body), border_style=BRAND, padding=(1, 2)))


def show_init_banner(agents: tuple[str, ...]) -> None:
    """Banner corto antes de escribir archivos — no repite todo el onboarding,
    solo confirma qué se está por instalar."""
    names = ", ".join(INTEGRATION_REGISTRY[a].display_name for a in agents)
    console.print(Panel.fit(f"[bold {BRAND}]rocky-spec[/bold {BRAND}] → instalando: {names}", border_style=BRAND))
