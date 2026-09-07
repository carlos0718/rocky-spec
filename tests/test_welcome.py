from rocky_spec import scaffold, welcome
from rocky_spec.integrations import INTEGRATION_REGISTRY


def test_show_welcome_runs_without_error_on_empty_dir(tmp_path):
    welcome.show_welcome(tmp_path)  # no debe tirar excepción


def test_show_welcome_runs_without_error_on_initialized_project(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    entries = INTEGRATION_REGISTRY["claude"].install(tmp_path, scaffold.all_commands())
    import json

    manifest_path = tmp_path / scaffold.SHARED_DIR_NAME / "install-manifest.json"
    manifest_path.write_text(json.dumps({"claude": [{"path": e.path, "sha256": e.sha256} for e in entries]}))
    welcome.show_welcome(tmp_path)  # no debe tirar excepción


def test_show_init_banner_runs_without_error():
    welcome.show_init_banner(("claude", "cursor"))


def test_show_commands_runs_without_error():
    welcome.show_commands()


def test_banner_lines_all_have_the_same_width():
    # Guarda sobre el string generado: todas las líneas del arte ASCII
    # deben medir lo mismo antes de renderizar.
    widths = {len(line) for line in welcome.BANNER.splitlines()}
    assert len(widths) == 1, f"líneas de BANNER con anchos distintos: {widths}"


def test_banner_lines_are_vertically_aligned_when_rendered(tmp_path):
    # Guarda sobre el render real, no sobre el string: el test de arriba
    # pasaba en verde mientras el banner se veía descuadrado, porque Rich
    # descarta los espacios finales al medir cada línea con
    # justify="center" y termina centrando cada fila por separado según su
    # contenido visible. Acá se renderiza show_welcome() completo y se
    # verifica que todas las filas del arte arranquen en la misma columna.
    import io

    from rich.console import Console

    original_console = welcome.console
    buf = io.StringIO()
    welcome.console = Console(file=buf, width=100)
    try:
        welcome.show_welcome(tmp_path)
    finally:
        welcome.console = original_console

    rendered = buf.getvalue().splitlines()
    # Se busca cada fila con sus espacios iniciales propios intactos (solo
    # se recorta la cola), así el índice encontrado es el borde izquierdo
    # del bloque entero -- si se buscara el primer carácter visible, la
    # primera fila daría un offset distinto por el espacio propio del glifo
    # de la "R", que no es una desalineación.
    banner_rows = [line.rstrip() for line in welcome.BANNER.splitlines() if line.strip()]
    starts = []
    for rendered_line in rendered:
        for row in banner_rows:
            if row and row in rendered_line:
                starts.append(rendered_line.index(row))
                break

    assert len(starts) == len(banner_rows), (
        f"no se encontraron todas las filas del banner en el render: {len(starts)}/{len(banner_rows)}"
    )
    assert len(set(starts)) == 1, f"filas del banner desalineadas, columnas de inicio: {starts}"


def test_commands_table_matches_registered_integrations_keys_used_in_invocation_hint():
    # INVOCATION_HINT es un diccionario a mano -- si se agrega una integración
    # nueva (Windsurf, Copilot) y nadie suma su entrada, mejor fallar acá que
    # mostrar "—" en silencio en la pantalla de bienvenida.
    for key in INTEGRATION_REGISTRY:
        assert key in welcome.INVOCATION_HINT, f"falta INVOCATION_HINT para '{key}'"


def test_every_command_has_a_purpose():
    # Si se suma un paso a COMMAND_CATALOG y nadie escribe para qué sirve,
    # la tabla de `rocky commands` mostraría una celda "—" en silencio.
    from rocky_spec.scaffold import COMMAND_CATALOG

    for key, _title, _source in COMMAND_CATALOG:
        assert key in welcome.AGENT_COMMAND_PURPOSE, f"falta AGENT_COMMAND_PURPOSE para '{key}'"


def test_cursor_hint_matches_the_real_command_count(tmp_path):
    # Guarda contra el bug original: INVOCATION_HINT decía "14 comandos"
    # cuando `rocky init --agent cursor` ya generaba 15. El número se compara
    # contra los archivos REALMENTE instalados, no contra COMMAND_CATALOG —
    # si se comparara contra la constante de la que ahora se deriva, el test
    # pasaría en verde aunque la instalación generase otra cantidad.
    import re

    from rocky_spec import scaffold
    from rocky_spec.integrations import INTEGRATION_REGISTRY

    scaffold.ensure_shared_knowledge(tmp_path)
    INTEGRATION_REGISTRY["cursor"].install(tmp_path, scaffold.all_commands())

    instalados = list((tmp_path / ".cursor" / "commands").glob("rocky-*.md"))
    declarados = int(re.search(r"(\d+) comandos", welcome.INVOCATION_HINT["cursor"]).group(1))

    assert declarados == len(instalados), (
        f"INVOCATION_HINT declara {declarados} comandos pero se instalaron {len(instalados)}"
    )


def test_show_commands_lists_both_levels():
    # `rocky commands` tiene que mostrar los dos niveles (CLI y agente) y la
    # diferencia de invocación entre Claude y Cursor -- que es justamente lo
    # que se confundía.
    import io

    from rich.console import Console

    original = welcome.console
    buf = io.StringIO()
    welcome.console = Console(file=buf, width=120)
    try:
        welcome.show_commands()
    finally:
        welcome.console = original

    out = buf.getvalue()
    assert "CLI `rocky`" in out
    assert "Comandos del agente" in out
    assert "/rocky-mode-resume" in out
    assert "se auto-invoca" in out or "solo" in out
