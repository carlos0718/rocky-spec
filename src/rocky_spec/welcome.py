"""
Interfaz de bienvenida del CLI — lo primero que ve alguien al correr
``rocky`` sin argumentos, o justo antes de que ``init`` arranque a
escribir archivos. Usa `rich` para algo prolijo en vez de texto plano
suelto — mismo espíritu que la pantalla inicial de ``specify init``.

El arte ASCII de ambos bloques (ROCKY y SPEC) se generó una sola vez con
``pyfiglet`` (fuente ``ansi_shadow``) y quedó hardcodeado acá — así el CLI
no necesita esa dependencia en runtime, solo para regenerarlo si el día de
mañana cambia el texto.
"""
from __future__ import annotations

import json
from pathlib import Path

from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME

console = Console()

_BANNER_RAW = r"""
██████╗  ██████╗  ██████╗██╗  ██╗██╗   ██╗    ███████╗██████╗ ███████╗ ██████╗
██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝╚██╗ ██╔╝    ██╔════╝██╔══██╗██╔════╝██╔════╝
██████╔╝██║   ██║██║     █████╔╝  ╚████╔╝     ███████╗██████╔╝█████╗  ██║
██╔══██╗██║   ██║██║     ██╔═██╗   ╚██╔╝      ╚════██║██╔═══╝ ██╔══╝  ██║
██║  ██║╚██████╔╝╚██████╗██║  ██╗   ██║       ███████║██║     ███████╗╚██████╗
╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝       ╚══════╝╚═╝     ╚══════╝ ╚═════╝
""".strip("\n")

# Ancho natural del arte ASCII -- si la terminal no entra, se muestra un
# título compacto en vez de romper el arte a la mitad (ver _banner_renderable).
BANNER_WIDTH = max(len(line) for line in _BANNER_RAW.splitlines())

# Cada línea se rellena con espacios hasta BANNER_WIDTH -- pyfiglet genera
# todas las líneas con el mismo ancho, pero un editor que recorta espacios
# finales al guardar puede perder ese padding en alguna línea sin que se
# note en el código; con justify="center" eso descuadra el arte entera
# (cada línea se centra por separado). Se recalcula acá en vez de confiar
# en que el string hardcodeado nunca pierda espacios de nuevo.
BANNER = "\n".join(line.ljust(BANNER_WIDTH) for line in _BANNER_RAW.splitlines())
COMPACT_TITLE = "ROCKY SPEC"

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
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column()
    for abbr, meaning in GLOSSARY:
        table.add_row(abbr, meaning)
    return table


def _commands_table() -> Table:
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2, 0, 0))
    table.add_column("Comando", style="cyan", no_wrap=True)
    table.add_column("Qué hace")
    for command, description in COMMANDS:
        table.add_row(command, description)
    return table


def _banner_renderable(available_width: int) -> Text:
    """Arte ASCII completo si entra; si no, un título compacto en vez de
    dejar que Rich reparta cada línea a la mitad (lo que rompía el diseño
    al angostar la terminal por debajo de BANNER_WIDTH)."""
    if available_width >= BANNER_WIDTH:
        return Text(BANNER, style="bold cyan", justify="center", no_wrap=True, overflow="crop")
    return Text(COMPACT_TITLE, style="bold cyan", justify="center")


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
            border_style="cyan",
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
            "\nPróximos pasos: [cyan]rocky check qa .[/cyan] · "
            "[cyan]rocky init --agent <otro>[/cyan] para sumar un agente más · "
            "[cyan]rocky commands[/cyan] para ver todos los comandos"
        )
    else:
        integrations_panel = Panel(
            _integrations_table(),
            title="[bold]Agentes soportados[/bold]",
            border_style="cyan",
            expand=False,
        )
        body.append(_centered_panels(available_width, glossary_panel, integrations_panel))
        body.append(
            "\nEmpezar: [cyan]rocky init . --agent claude[/cyan] "
            "(repetí --agent para instalar más de uno) · "
            "[cyan]rocky commands[/cyan] para ver todos los comandos"
        )

    console.print(Panel(Group(*body), border_style="cyan", padding=(1, 2)))


def show_init_banner(agents: tuple[str, ...]) -> None:
    """Banner corto antes de escribir archivos — no repite todo el onboarding,
    solo confirma qué se está por instalar."""
    names = ", ".join(INTEGRATION_REGISTRY[a].display_name for a in agents)
    console.print(Panel.fit(f"[bold cyan]rocky-spec[/bold cyan] → instalando: {names}", border_style="cyan"))
