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

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME

console = Console()

BANNER = r"""
███████╗██████╗ ███████╗ ██████╗    ██████╗██╗  ██╗ █████╗ ██████╗ ██╗     ███████╗███████╗███████╗
██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔════╝██║  ██║██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝██╔════╝
███████╗██████╔╝█████╗  ██║         ██║     ███████║███████║██████╔╝██║     █████╗  ███████╗███████╗
╚════██║██╔═══╝ ██╔══╝  ██║         ██║     ██╔══██║██╔══██║██╔══██╗██║     ██╔══╝  ╚════██║╚════██║
███████║██║     ███████╗╚██████╗    ╚██████╗██║  ██║██║  ██║██║  ██║███████╗███████╗███████║███████║
╚══════╝╚═╝     ╚══════╝ ╚═════╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
""".strip("\n")

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
# del proyecto destino -- NO es el comando `charless` (eso es la CLI, corre
# en cualquier terminal); esto es lo que se escribe DENTRO del agente
# correspondiente, después de un `charless init --agent <x>`.
INVOCATION_HINT = {
    "claude": "/spec-charless (Claude Code)",
    "cursor": "/charless-* — 14 comandos en .cursor/commands/ (Cursor)",
}

# Espejo exacto de la tabla "Comandos disponibles" del README -- misma
# fuente de verdad en prosa, acá en datos para poder renderizarla con rich
# vía `charless commands` en vez de mandar a leer el README.
COMMANDS = [
    ("charless", "Sin subcomando: banner de bienvenida + ayuda."),
    ("charless --version", "Imprime la versión instalada."),
    ("charless commands", "Esta tabla."),
    ("charless init [PATH] --agent <agente>", "Instala .charless/ y genera la integración de cada --agent (repetible)."),
    ("charless init [PATH] --agent <agente> --force", "Igual que arriba, pero regenera .charless/ aunque ya exista."),
    ("charless build [PATH] --values <json> [--force]", "Renderiza SPEC.md/CONSTITUTION.md/AGENTS.md/... desde .charless/templates/ a partir de un JSON de valores."),
    ("charless list-integrations", "Lista los agentes soportados por esta versión."),
    ("charless check code [PATH]", "Health-check: tamaño de archivo y code smells estructurales."),
    ("charless check security [PATH]", "Health-check: secrets hardcodeados, .env commiteado, vulnerabilidades."),
    ("charless check observability [PATH]", "Health-check: error tracking, health endpoint, logging estructurado."),
    ("charless check qa [PATH]", "Trazabilidad RF → US → RNF → tarea y placeholders sin rellenar."),
    ("charless check version [PATH]", "Bump de SemVer sugerido desde el último tag + aviso de fixes acumulados."),
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


def show_commands() -> None:
    """``charless commands`` -- la tabla completa, con descripción, de todo
    lo que la CLI sabe hacer. Espejo del README, no de la skill/agente."""
    console.print(
        Panel(
            _commands_table(),
            title="[bold]charless — comandos disponibles[/bold]",
            border_style="cyan",
            expand=False,
        )
    )


def show_welcome(project_root: Path | None = None) -> None:
    """Pantalla de bienvenida. Si ``project_root`` ya tiene ``.charless/``,
    muestra el estado actual del proyecto en vez del onboarding genérico."""
    header = Group(
        Text(BANNER, style="bold cyan", justify="center"),
        Text(f"{AUTHOR}  ·  v{__version__}", style="dim italic", justify="center"),
        Text(TAGLINE, style="italic", justify="center"),
    )

    body: list = [header, ""]

    body.append(Text("Qué hace este kit", style="bold"))
    for line in FEATURES:
        body.append(f"  • {line}")
    body.append("")

    body.append(
        Panel(_glossary_table(), title="[bold]Glosario[/bold]", border_style="dim", expand=False)
    )
    body.append("")

    shared = (project_root or Path(".")) / SHARED_DIR_NAME
    manifest_path = shared / "install-manifest.json"

    if shared.is_dir():
        version = (shared / "VERSION").read_text().strip() if (shared / "VERSION").exists() else "?"
        active: set[str] = set()
        if manifest_path.exists():
            active = set(json.loads(manifest_path.read_text()).keys())

        body.append(
            Panel(
                _integrations_table(active),
                title=f"[bold]Este proyecto ya usa spec-charless[/bold] (.charless/ v{version})",
                border_style="green",
                expand=False,
            )
        )
        body.append(
            "\nPróximos pasos: [cyan]charless check qa .[/cyan] · "
            "[cyan]charless init --agent <otro>[/cyan] para sumar un agente más · "
            "[cyan]charless commands[/cyan] para ver todos los comandos"
        )
    else:
        body.append(
            Panel(
                _integrations_table(),
                title="[bold]Agentes soportados[/bold]",
                border_style="cyan",
                expand=False,
            )
        )
        body.append(
            "\nEmpezar: [cyan]charless init . --agent claude[/cyan] "
            "(repetí --agent para instalar más de uno) · "
            "[cyan]charless commands[/cyan] para ver todos los comandos"
        )

    console.print(Panel(Group(*body), border_style="cyan", padding=(1, 2)))


def show_init_banner(agents: tuple[str, ...]) -> None:
    """Banner corto antes de escribir archivos — no repite todo el onboarding,
    solo confirma qué se está por instalar."""
    names = ", ".join(INTEGRATION_REGISTRY[a].display_name for a in agents)
    console.print(Panel.fit(f"[bold cyan]spec-charless[/bold cyan] → instalando: {names}", border_style="cyan"))
