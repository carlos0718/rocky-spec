from __future__ import annotations

import json
from pathlib import Path

import click

from . import scaffold
from .integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME
from .integrations.cursor import CURSOR_RULE_PATH
from .scripts import accessibility_check
from .scripts import anchor_check
from .scripts import build as build_script
from .scripts import drift_check
from .scripts import health_check, qa_review, update as update_script, version_check
from .welcome import show_commands, show_init_banner, show_welcome


@click.group(invoke_without_command=True)
@click.version_option(scaffold.ROCKY_SPEC_VERSION, prog_name="rocky")
@click.pass_context
def main(ctx: click.Context) -> None:
    """rocky — toolkit multi-agente de Spec-Driven Development (nivel Spec-Anchored)."""
    if ctx.invoked_subcommand is None:
        show_welcome(Path("."))
        click.echo(ctx.get_help())


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
@click.option("--force", is_flag=True, help="Sobrescribir .rocky-spec/ si ya existe.")
def init(path: Path, agents: tuple[str, ...], force: bool) -> None:
    """Inicializa el proyecto en PATH con el/los agente(s) elegidos."""
    show_init_banner(agents)
    project_root = path.resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    copied = scaffold.ensure_shared_knowledge(project_root, force=force)
    if copied:
        total = sum(len(files) for files in copied.values())
        click.echo(f"✓ Conocimiento compartido instalado en {SHARED_DIR_NAME}/ ({total} archivos)")
        for sub, files in copied.items():
            click.echo(f"    {SHARED_DIR_NAME}/{sub}/ ({len(files)})")
            for f in files:
                click.echo(f"        {sub}/{f}")
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

        # Reglas de permisos (solo Claude Code las tiene; ver
        # claude.ensure_permission_rules). Se reporta aparte de los archivos
        # del manifiesto porque el settings.json NO se trackea: es del usuario,
        # rocky-spec solo le suma las reglas que falten.
        perms = getattr(integration, "last_permission_result", None)
        if perms:
            if perms["invalid"]:
                click.echo(
                    "    ⚠️  .claude/settings.json existe pero no es JSON válido — "
                    "no se tocó. Agregá las reglas del Artículo 7 a mano."
                )
            elif perms["added"]:
                click.echo(
                    f"    + {len(perms['added'])} regla(s) de confirmación en "
                    ".claude/settings.json (permissions.ask)"
                )
            if perms["shadowed"]:
                click.echo(
                    "    ⚠️  estas reglas no van a pedir confirmación porque el mismo "
                    "comando está en permissions.allow (allow gana sobre ask):"
                )
                for rule in perms["shadowed"]:
                    click.echo(f"         {rule}")

        # Anclas al conocimiento compartido (CLAUDE.md -> @AGENTS.md, rocky.mdc
        # -> puntero a .rocky-spec/). Ninguna de las dos entra al manifiesto:
        # ver ensure_claude_md_anchor / _ensure_rule.
        if getattr(integration, "last_claude_md_result", None) == "repaired":
            click.echo("    🔧 CLAUDE.md existía pero le faltaba `@AGENTS.md` — se reinsertó")

        rule_result = getattr(integration, "last_rule_result", None)
        if rule_result == "repaired":
            click.echo(f"    🔧 {CURSOR_RULE_PATH} existía pero le faltaba el puntero a {SHARED_DIR_NAME}/ — se restauró")

    manifest_path.write_text(json.dumps(full_manifest, indent=2), encoding="utf-8")
    click.echo(f"\nListo. {len(agents)} integración(es) activa(s) en {project_root}")
    click.echo(
        "\nEsto solo instaló los archivos — todavía no arrancó ningún flujo.\n"
        "Para que el agente empiece a hacer preguntas (perfil, SPEC, stack...), "
        "abrí una sesión de Claude Code en este proyecto y decile algo como "
        "\"quiero armar un proyecto nuevo\" (o \"continuemos\" / \"tengo un proyecto "
        "ya avanzado\" según el caso) — ahí la skill lee .rocky-spec/ y arranca "
        "el flujo P0 en adelante."
    )


@main.command(name="build")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
@click.option(
    "--values",
    "values_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="JSON plano {PLACEHOLDER: valor} para rellenar los templates. Clave especial "
    "LICENSE_CHOICE (mit/apache2/proprietary) para generar LICENSE.",
)
@click.option("--force", is_flag=True, help="Sobrescribir archivos que ya existan en el proyecto.")
@click.option(
    "--template",
    "template_name",
    type=str,
    default=None,
    help="Renderizar un solo template (ej. MASTER.md.template) en vez del set fijo de archivos base. Usar junto con --output.",
)
@click.option(
    "--output",
    "output_relative",
    type=str,
    default=None,
    help="Ruta relativa de salida para --template (ej. design-system/MASTER.md).",
)
def build(path: Path, values_path: Path, force: bool, template_name: str | None, output_relative: str | None) -> None:
    """Renderiza los archivos base (SPEC.md, CONSTITUTION.md, AGENTS.md...) desde .rocky-spec/templates/."""
    if bool(template_name) != bool(output_relative):
        raise click.UsageError("--template y --output tienen que usarse juntos.")

    project_root = path.resolve()
    values = json.loads(values_path.read_text(encoding="utf-8"))
    only = (template_name, output_relative) if template_name else None
    result = build_script.build(project_root, values, force=force, only=only)

    for f in result.generated:
        click.echo(f"✓ {f}")
    for f in result.skipped_existing:
        click.echo(f"⏭  {f} ya existe — usá --force para regenerarlo")
    for f, placeholders in result.unresolved.items():
        click.echo(f"⚠️  {f}: placeholders sin rellenar — {', '.join(placeholders)}")
    if result.invalid_license_choice:
        click.echo(
            f"⚠️  LICENSE_CHOICE='{result.invalid_license_choice}' no es válido "
            f"({', '.join(sorted(build_script.LICENSE_CHOICES))}) — LICENSE no se generó"
        )

    if not result.generated and not result.skipped_existing:
        click.echo("Nada para generar — ¿corriste `rocky init` antes? (falta .rocky-spec/templates/)")


@main.command(name="update")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
@click.option("--dry-run", is_flag=True, help="Mostrar qué cambiaría sin escribir nada.")
def update(path: Path, dry_run: bool) -> None:
    """Actualiza commands/, reference/, templates/ y los archivos del kit de cada
    integración instalada a la versión del paquete, sin pisar ediciones manuales."""
    project_root = path.resolve()
    if not (project_root / SHARED_DIR_NAME).exists():
        click.echo(f"No hay {SHARED_DIR_NAME}/ en {project_root} — corré `rocky init` primero.")
        return

    report = update_script.check_update(project_root) if dry_run else update_script.apply_update(project_root)

    if report.already_up_to_date:
        click.echo(f"✅ Ya estás en la última versión ({report.target_version}).")
        return

    click.echo(f"📦 Instalado: {report.installed_version or 'desconocido'} → Paquete: {report.target_version}")
    prefix = "Se actualizaría" if dry_run else "Actualizado"
    prefix_add = "Se agregaría" if dry_run else "Agregado"

    for f in report.updated:
        click.echo(f"✓ {prefix}: {f}")
    for f in report.added:
        click.echo(f"+ {prefix_add}: {f}")
    for f in report.preserved_edited:
        click.echo(f"⏭  {f} — tiene ediciones manuales, no se tocó")
    for f in report.preserved_no_baseline:
        click.echo(f"⚠️  {f} — instalado antes de esta versión, no se pudo verificar si tiene ediciones, no se tocó")
    for f in report.removed_from_kit:
        click.echo(f"ℹ️  {f} ya no forma parte del kit — no se borró, revisalo a mano")
    if report.agents_refreshed:
        agentes = ", ".join(report.agents_refreshed)
        verbo = "Se regenerarían" if dry_run else "Regenerados"
        click.echo(f"🔄 {verbo} los archivos del kit de: {agentes}")

    if not any([report.updated, report.added, report.preserved_edited, report.preserved_no_baseline, report.agents_refreshed]):
        click.echo("Nada para actualizar.")

    if dry_run:
        click.echo("\n(dry-run: no se escribió nada — corré sin --dry-run para aplicar)")

    drift_report = drift_check.check_drift(project_root)
    if drift_report.findings:
        click.echo("\n⚠️  Drift de Modo Adopción detectado:")
        _print_report(drift_report)
        _print_drift_next_steps()


@main.command(name="commands")
def commands() -> None:
    """Lista todos los comandos de la CLI con su descripción."""
    show_commands()


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


@check.command(name="accessibility")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_accessibility(path: Path) -> None:
    """alt text, lang, div clickeable sin rol, botón solo-ícono, contraste WCAG básico."""
    _print_report(accessibility_check.check_accessibility(path.resolve()))


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


@check.command(name="anchors")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_anchors(path: Path) -> None:
    """CLAUDE.md / rocky.mdc siguen apuntando al conocimiento compartido."""
    _print_report(anchor_check.check_anchors(path.resolve()))


@check.command(name="drift")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_drift(path: Path) -> None:
    """Archivos que MA-6 genera hoy pero faltan en un proyecto adoptado con una versión vieja de la skill."""
    report = drift_check.check_drift(path.resolve())
    _print_report(report)
    if report.findings:
        _print_drift_next_steps()


@check.command(name="version")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_version(path: Path) -> None:
    """Calcula el bump de SemVer que corresponde según los commits desde el último tag."""
    report = version_check.check_version(path.resolve())

    if report.current_tag:
        click.echo(f"📦 Última versión taggeada: {report.current_tag}")
    else:
        click.echo("📦 Sin tags todavía — baseline 0.0.0")

    c = report.classification
    click.echo(
        f"🔍 Commits en rama '{report.branch}' desde ahí: "
        f"{len(c.breaking)} breaking, {len(c.feat)} feat, {len(c.fix)} fix, "
        f"{len(c.other)} sin impacto en changelog"
    )

    if report.bump == "none":
        click.echo("✅ Sin cambios que ameriten un bump de versión.")
    else:
        click.echo(f"⬆️  Bump sugerido: {report.bump.upper()} → {report.suggested_version}")

    if report.pre_1_0_note:
        click.echo(f"ℹ️  {report.pre_1_0_note}")

    if report.fix_budget_warning:
        click.echo(report.fix_budget_warning)


def _print_report(report: health_check.HealthCheckReport) -> None:
    if not report.findings:
        click.echo(f"✅ {report.category}: sin hallazgos")
        return
    for f in report.findings:
        icon = "🔴" if f.severity == "critical" else "🟡"
        location = f" ({f.file}:{f.line})" if f.file and f.line else f" ({f.file})" if f.file else ""
        click.echo(f"{icon} {f.message}{location}")


def _print_drift_next_steps() -> None:
    click.echo(
        "\n👉 Para resolverlo: abrí una sesión de tu agente en este proyecto y escribí "
        '"/rocky-spec" (o el comando equivalente de tu agente) — el flujo de Reanudación '
        "va a revalidar esto y generar lo que falte siguiendo mode-adopt.md P6."
    )


if __name__ == "__main__":
    main()
