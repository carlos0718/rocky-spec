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
    # Con justify="center" cada línea del banner se centra por separado --
    # si una línea pierde el padding con espacios al final (ej. un editor
    # que recorta espacios en blanco al guardar), el arte ASCII queda
    # descuadrado entre filas sin que salte ningún error. Bug real
    # encontrado por el usuario en Warp/Windows Terminal tras el rename.
    widths = {len(line) for line in welcome.BANNER.splitlines()}
    assert len(widths) == 1, f"líneas de BANNER con anchos distintos: {widths}"


def test_commands_table_matches_registered_integrations_keys_used_in_invocation_hint():
    # INVOCATION_HINT es un diccionario a mano -- si se agrega una integración
    # nueva (Windsurf, Copilot) y nadie suma su entrada, mejor fallar acá que
    # mostrar "—" en silencio en la pantalla de bienvenida.
    for key in INTEGRATION_REGISTRY:
        assert key in welcome.INVOCATION_HINT, f"falta INVOCATION_HINT para '{key}'"
