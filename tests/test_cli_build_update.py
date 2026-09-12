import json

from click.testing import CliRunner

from rocky_spec.cli import main


def _write_values(tmp_path, **values):
    values_path = tmp_path / "values.json"
    values_path.write_text(json.dumps(values), encoding="utf-8")
    return values_path


def test_update_requires_template_and_output(tmp_path):
    values_path = _write_values(tmp_path, PROJECT_NAME="demo")

    result = CliRunner().invoke(main, ["build", str(tmp_path), "--values", str(values_path), "--update"])

    assert result.exit_code != 0
    assert "--update requiere --template y --output" in result.output


def test_update_rejects_force(tmp_path):
    values_path = _write_values(tmp_path, PROJECT_NAME="demo")

    result = CliRunner().invoke(
        main,
        [
            "build", str(tmp_path),
            "--values", str(values_path),
            "--template", "AGENTS.md.template",
            "--output", "AGENTS.md",
            "--update",
            "--force",
        ],
    )

    assert result.exit_code != 0
    assert "no se usan juntos" in result.output


def test_update_happy_path_reports_backup_and_sections(tmp_path):
    templates_dir = tmp_path / ".rocky-spec" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "AGENTS.md.template").write_text("## Stack\n\n## Servicios externos\n")
    (tmp_path / "AGENTS.md").write_text("## Stack\n\n## Gotchas\n", encoding="utf-8")
    values_path = _write_values(tmp_path, PROJECT_NAME="demo")

    result = CliRunner().invoke(
        main,
        [
            "build", str(tmp_path),
            "--values", str(values_path),
            "--template", "AGENTS.md.template",
            "--output", "AGENTS.md",
            "--update",
        ],
    )

    assert result.exit_code == 0
    assert "Backup: _AGENTS.md" in result.output
    assert "Servicios externos" in result.output
    assert "Gotchas" in result.output
    assert (tmp_path / "_AGENTS.md").exists()
    assert (tmp_path / "AGENTS.md").read_text() == "## Stack\n\n## Servicios externos\n"


def test_update_reports_error_without_crashing_when_output_missing(tmp_path):
    templates_dir = tmp_path / ".rocky-spec" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "AGENTS.md.template").write_text("## Stack\n")
    values_path = _write_values(tmp_path, PROJECT_NAME="demo")

    result = CliRunner().invoke(
        main,
        [
            "build", str(tmp_path),
            "--values", str(values_path),
            "--template", "AGENTS.md.template",
            "--output", "AGENTS.md",
            "--update",
        ],
    )

    assert result.exit_code == 0
    assert "no existe" in result.output
