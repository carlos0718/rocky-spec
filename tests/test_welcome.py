from spec_charless import scaffold, welcome
from spec_charless.integrations import INTEGRATION_REGISTRY


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
