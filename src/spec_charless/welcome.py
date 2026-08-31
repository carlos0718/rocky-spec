"""
Interfaz de bienvenida del CLI — lo primero que ve alguien al correr
``charless`` sin argumentos, o justo antes de que ``init`` arranque a
escribir archivos. Usa `rich` para algo prolijo en vez de texto plano
suelto — mismo espíritu que la pantalla inicial de ``specify init``.

El arte ASCII de ambos bloques (SPEC y CHARLESS) se generó una sola vez con
``pyfiglet`` (fuente ``ansi_shadow``) y quedó hardcodeado acá — así el CLI
no necesita esa dependencia en runtime, solo para regenerarlo si el día de
mañana cambia el texto.
"""
from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import scaffold
from .integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME

console = Console()

BANNER = r"""
███████╗██████╗ ███████╗ ██████╗
██╔════╝██╔══██╗██╔════╝██╔════╝
███████╗██████╔╝█████╗  ██║
╚════██║██╔═══╝ ██╔══╝  ██║
███████║██║     ███████╗╚██████╗
╚══════╝╚═╝     ╚══════╝ ╚═════╝

 ██████╗██╗  ██╗ █████╗ ██████╗ ██╗     ███████╗███████╗███████╗
██╔════╝██║  ██║██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝██╔════╝
██║     ███████║███████║██████╔╝██║     █████╗  ███████╗███████╗
██║     ██╔══██║██╔══██║██╔══██╗██║     ██╔══╝  ╚════██║╚════██║
╚██████╗██║  ██║██║  ██║██║  ██║███████╗███████╗███████║███████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
"""

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


def _integrations_table(active: set[str] | None = None) -> Table:
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2, 0, 0))
    table.add_column("Agente")
    table.add_column("Comando")
    table.add_column("Estado")
    for key, integration in sorted(INTEGRATION_REGISTRY.items()):
        status = "[green]✓ activo[/green]" if active and key in active else "[dim]disponible[/dim]"
        table.add_row(integration.display_name, f"--agent {key}", status)
    return table


def _glossary_table() -> Table:
    table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column()
    for abbr, meaning in GLOSSARY:
        table.add_row(abbr, meaning)
    return table


def show_welcome(project_root: Path | None = None) -> None:
    """Pantalla de bienvenida. Si ``project_root`` ya tiene ``.charless/``,
    muestra el estado actual del proyecto en vez del onboarding genérico."""
    console.print(Text(BANNER, style="bold cyan"))
    console.print(Text(AUTHOR, style="dim italic"))
    console.print(Text(TAGLINE, style="italic"))
    console.print()

    console.print(Text("Qué hace este kit", style="bold"))
    for line in FEATURES:
        console.print(f"  • {line}")
    console.print()

    console.print(
        Panel(_glossary_table(), title="[bold]Glosario[/bold]", border_style="dim", expand=False)
    )
    console.print()

    shared = (project_root or Path(".")) / SHARED_DIR_NAME
    manifest_path = shared / "install-manifest.json"

    if shared.is_dir():
        version = (shared / "VERSION").read_text().strip() if (shared / "VERSION").exists() else "?"
        active: set[str] = set()
        if manifest_path.exists():
            active = set(json.loads(manifest_path.read_text()).keys())

        console.print(
            Panel(
                _integrations_table(active),
                title=f"[bold]Este proyecto ya usa spec-charless[/bold] (.charless/ v{version})",
                border_style="green",
                expand=False,
            )
        )
        console.print(
            "\nPróximos pasos: [cyan]charless check qa .[/cyan] · "
            "[cyan]charless init --agent <otro>[/cyan] para sumar un agente más\n"
        )
    else:
        console.print(
            Panel(
                _integrations_table(),
                title="[bold]Agentes soportados[/bold]",
                border_style="cyan",
                expand=False,
            )
        )
        console.print(
            "\nEmpezar: [cyan]charless init . --agent claude[/cyan] "
            "(repetí --agent para instalar más de uno)\n"
        )


def show_init_banner(agents: tuple[str, ...]) -> None:
    """Banner corto antes de escribir archivos — no repite todo el onboarding,
    solo confirma qué se está por instalar."""
    names = ", ".join(INTEGRATION_REGISTRY[a].display_name for a in agents)
    console.print(Panel.fit(f"[bold cyan]spec-charless[/bold cyan] → instalando: {names}", border_style="cyan"))
