from rocky_spec.scripts.anchor_check import check_anchors


def test_no_findings_when_no_anchor_files_exist(tmp_path):
    report = check_anchors(tmp_path)
    assert report.findings == []


def test_no_findings_when_anchors_are_intact(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# demo\n\n@AGENTS.md\n", encoding="utf-8")
    rules_dir = tmp_path / ".cursor" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "rocky.mdc").write_text("apunta a .rocky-spec/\n", encoding="utf-8")

    report = check_anchors(tmp_path)
    assert report.findings == []


def test_flags_claude_md_missing_the_anchor(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# demo sin ancla\n", encoding="utf-8")

    report = check_anchors(tmp_path)
    assert report.has_critical
    assert any("CLAUDE.md" in f.message for f in report.findings)


def test_flags_rocky_mdc_missing_the_pointer(tmp_path):
    rules_dir = tmp_path / ".cursor" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "rocky.mdc").write_text("regla sin puntero\n", encoding="utf-8")

    report = check_anchors(tmp_path)
    assert report.has_critical
    assert any(".cursor/rules/rocky.mdc" in f.message for f in report.findings)
