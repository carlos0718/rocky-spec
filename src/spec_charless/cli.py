from __future__ import annotations

import json
from pathlib import Path

import click

from . import scaffold
from .integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME
from .scripts import health_check, qa_review


@click.group()
@click.version_option(scaffold.CHARLESS_VERSION, prog_name="charless")
def main() -> None:
    """charless — toolkit multi-agente de Spec-Driven Development (nivel Spec-Anchored)."""


@main.command()
@click.argument("path", type=click.Path(file_okay=False, path_type=Path), default=".")
@click.option(
    "--agent",
    "agents",
    multiple=True,
    type=click.Choice(sorted(INTEGRATION_REGISTRY.keys())),
    required=True,
    help="Agente(s) a instalar. Repetir la opción para instalar más de uno.",
)
@click.option("--force", is_flag=True, help="Sobrescribir .charless/ si ya existe.")
def init(path: Path, agents: tuple[str, ...], force: bool) -> None:
    """Inicializa el proyecto en PATH con el/los agente(s) elegidos."""
    project_root = path.resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    copied = scaffold.ensure_shared_knowledge(project_root, force=force)
    if copied:
        click.echo(f"✓ Conocimiento compartido instalado en {SHARED_DIR_NAME}/ ({', '.join(copied)})")
    else:
        click.echo(f"· {SHARED_DIR_NAME}/ ya existía — usá --force para regenerarlo")

    commands = scaffold.all_commands()
    manifest_path = project_root / SHARED_DIR_NAME / "install-manifest.json"
    full_manifest: dict[str, list[dict]] = {}
    if manifest_path.exists():
        full_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for agent_key in agents:
        integration = INTEGRATION_REGISTRY[agent_key]
        entries = integration.install(project_root, commands)
        full_manifest[agent_key] = [{"path": e.path, "sha256": e.sha256} for e in entries]
        click.echo(f"✓ Integración {integration.display_name} instalada:")
        for e in entries:
            click.echo(f"    {e.path}")

    manifest_path.write_text(json.dumps(full_manifest, indent=2), encoding="utf-8")
    click.echo(f"\nListo. {len(agents)} integración(es) activa(s) en {project_root}")


@main.command(name="list-integrations")
def list_integrations() -> None:
    """Lista los agentes soportados."""
    for key, integration in sorted(INTEGRATION_REGISTRY.items()):
        click.echo(f"{key:10s} {integration.display_name}")


@main.group()
def check() -> None:
    """Health-checks deterministas (equivalentes a MA-1.5 / MA-1.6 / MA-1.7 / P7.5)."""


@check.command(name="code")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_code(path: Path) -> None:
    """Tamaño de archivo y code smells estructurales."""
    _print_report(health_check.check_file_sizes(path.resolve()))


@check.command(name="security")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_security(path: Path) -> None:
    """.env commiteado, secrets hardcodeados, vulnerabilidades conocidas."""
    _print_report(health_check.check_security(path.resolve()))


@check.command(name="observability")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_observability(path: Path) -> None:
    """Error tracking, health endpoint, logging estructurado."""
    _print_report(health_check.check_observability(path.resolve()))


@check.command(name="qa")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_qa(path: Path) -> None:
    """Completitud de placeholders + trazabilidad RF -> US -> RNF -> tarea (P7.5)."""
    report = qa_review.full_report(path.resolve())
    if report.is_clean:
        click.echo("✅ Sin hallazgos — placeholders completos y trazabilidad sin huérfanos.")
        return
    for file, placeholders in report.unresolved_placeholders.items():
        click.echo(f"⚠️  {file}: placeholders sin rellenar — {', '.join(placeholders)}")
    for rf in report.orphan_rf:
        click.echo(f"⚠️  {rf} no tiene ninguna historia que lo implemente")
    for us in report.orphan_us:
        click.echo(f"⚠️  {us} no tiene ninguna tarea en el TODO")
    for rnf in report.unplanned_rnf:
        click.echo(f"⚠️  {rnf} tiene un objetivo concreto pero ninguna tarea que lo aborde")


def _print_report(report: health_check.HealthCheckReport) -> None:
    if not report.findings:
        click.echo(f"✅ {report.category}: sin hallazgos")
        return
    for f in report.findings:
        icon = "🔴" if f.severity == "critical" else "🟡"
        location = f" ({f.file}:{f.line})" if f.file and f.line else f" ({f.file})" if f.file else ""
        click.echo(f"{icon} {f.message}{location}")


if __name__ == "__main__":
    main()
