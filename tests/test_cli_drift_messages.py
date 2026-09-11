import json

from click.testing import CliRunner

from rocky_spec.cli import main


def _write_adopted_state(tmp_path, **overrides):
    state = {"mode": "adopted", "timestamp": "2026-08-10T00:00:00.000Z", "step": "adoption_complete"}
    state.update(overrides)
    (tmp_path / ".skill-state.json").write_text(json.dumps(state), encoding="utf-8")


def test_check_drift_prints_next_steps_when_findings(tmp_path):
    _write_adopted_state(tmp_path, license_decision="skipped")

    result = CliRunner().invoke(main, ["check", "drift", str(tmp_path)])

    assert "Para resolverlo" in result.output
    assert "/rocky-spec" in result.output


def test_check_drift_does_not_print_next_steps_when_clean(tmp_path):
    _write_adopted_state(tmp_path, license_decision="skipped")
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    result = CliRunner().invoke(main, ["check", "drift", str(tmp_path)])

    assert "Para resolverlo" not in result.output
