import json

from rocky_spec.scripts.drift_check import check_drift


def _write_state(tmp_path, **overrides):
    state = {"mode": "adopted", "timestamp": "2026-08-10T00:00:00.000Z", "step": "adoption_complete"}
    state.update(overrides)
    (tmp_path / ".skill-state.json").write_text(json.dumps(state), encoding="utf-8")


def test_no_findings_when_no_skill_state_file(tmp_path):
    report = check_drift(tmp_path)
    assert report.findings == []


def test_no_findings_when_mode_is_not_adopted(tmp_path):
    _write_state(tmp_path, mode="created", license_decision="skipped")
    report = check_drift(tmp_path)
    assert report.findings == []


def test_no_findings_when_all_always_generated_files_and_license_decision_present(tmp_path):
    _write_state(tmp_path, license_decision="skipped")
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    report = check_drift(tmp_path)
    assert report.findings == []


def test_flags_each_missing_always_generated_file(tmp_path):
    _write_state(tmp_path, license_decision="skipped")

    report = check_drift(tmp_path)
    flagged = {f.file for f in report.findings}
    assert flagged == {"CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"}


def test_flags_ui_only_files_when_project_has_ui(tmp_path):
    _write_state(tmp_path, license_decision="skipped")
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")

    report = check_drift(tmp_path)
    flagged = {f.file for f in report.findings}
    assert flagged == {"ACCESSIBILITY.md", "design-system/MASTER.md"}


def test_does_not_flag_ui_only_files_without_ui(tmp_path):
    _write_state(tmp_path, license_decision="skipped")
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    report = check_drift(tmp_path)
    assert report.findings == []


def test_flags_missing_license_when_no_license_decision_recorded(tmp_path):
    _write_state(tmp_path)
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    report = check_drift(tmp_path)
    assert any(f.file == "LICENSE" for f in report.findings)
    message = next(f.message for f in report.findings if f.file == "LICENSE")
    assert "nunca se le preguntó" in message


def test_does_not_flag_license_when_decision_was_skipped(tmp_path):
    _write_state(tmp_path, license_decision="skipped")
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    report = check_drift(tmp_path)
    assert not any(f.file == "LICENSE" for f in report.findings)


def test_flags_missing_license_when_decision_was_to_generate_one(tmp_path):
    _write_state(tmp_path, license_decision="mit")
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    report = check_drift(tmp_path)
    message = next(f.message for f in report.findings if f.file == "LICENSE")
    assert "se decidió generar una y no está" in message


def test_no_findings_when_license_actually_exists(tmp_path):
    _write_state(tmp_path)
    for name in ("CONSTITUTION.md", "CHANGELOG.md", "SECURITY.md", "OBSERVABILITY.md", "LICENSE"):
        (tmp_path / name).write_text("ok", encoding="utf-8")

    report = check_drift(tmp_path)
    assert report.findings == []
