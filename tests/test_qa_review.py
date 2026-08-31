from spec_charless.scripts import qa_review


def test_check_placeholder_completeness_finds_unresolved(tmp_path):
    f = tmp_path / "SECURITY.md"
    f.write_text("Escala: {{SECURITY_SCALE}}\nAuth: {{AUTH_PATTERN}}\n")
    result = qa_review.check_placeholder_completeness(f)
    assert str(f) in result
    assert set(result[str(f)]) == {"SECURITY_SCALE", "AUTH_PATTERN"}


def test_check_placeholder_completeness_empty_when_resolved(tmp_path):
    f = tmp_path / "SECURITY.md"
    f.write_text("Escala: Producto real\n")
    result = qa_review.check_placeholder_completeness(f)
    assert result == {}


def test_traceability_detects_orphan_rf(tmp_path):
    spec = tmp_path / "SPEC.md"
    spec.write_text("RF-1 Login\nRF-2 Perfil\nUS-1 (implementa RF-1): login\n")
    report = qa_review.check_traceability(spec)
    assert "RF-2" in report.orphan_rf
    assert "RF-1" not in report.orphan_rf


def test_traceability_detects_orphan_us(tmp_path):
    spec = tmp_path / "SPEC.md"
    spec.write_text("US-1 (implementa RF-1): login\n")
    todo = tmp_path / "TODO.md"
    todo.write_text("- [ ] Setup inicial\n")
    report = qa_review.check_traceability(spec, todo)
    assert "US-1" in report.orphan_us


def test_traceability_us_with_task_is_not_orphan(tmp_path):
    spec = tmp_path / "SPEC.md"
    spec.write_text("US-1 (implementa RF-1): login\n")
    todo = tmp_path / "TODO.md"
    todo.write_text("- [ ] Endpoint de login (US-1)\n")
    report = qa_review.check_traceability(spec, todo)
    assert report.orphan_us == []


def test_traceability_rnf_with_concrete_target_and_no_task_is_flagged(tmp_path):
    spec = tmp_path / "SPEC.md"
    spec.write_text("RNF-1 | El login responde en <200ms\n")
    todo = tmp_path / "TODO.md"
    todo.write_text("- [ ] Setup inicial\n")
    report = qa_review.check_traceability(spec, todo)
    assert "RNF-1" in report.unplanned_rnf


def test_traceability_rnf_with_default_value_is_not_flagged(tmp_path):
    spec = tmp_path / "SPEC.md"
    spec.write_text("RNF-1 | sin objetivo estricto — proyecto chico/prototipo\n")
    todo = tmp_path / "TODO.md"
    todo.write_text("- [ ] Setup inicial\n")
    report = qa_review.check_traceability(spec, todo)
    assert report.unplanned_rnf == []


def test_full_report_is_clean_for_well_formed_project(tmp_path):
    (tmp_path / "SPEC.md").write_text(
        "RF-1 Login\nUS-1 (implementa RF-1): login\n"
        "RNF-1 | sin objetivo estricto\n"
    )
    (tmp_path / "TODO.md").write_text("- [ ] Endpoint de login (US-1)\n")
    report = qa_review.full_report(tmp_path)
    assert report.is_clean


def test_traceability_rnf_no_aplica_marker_is_recognized(tmp_path):
    spec = tmp_path / "SPEC.md"
    spec.write_text("RNF-5 | Retención de datos | No aplica — no se almacenan datos de usuarios\n")
    todo = tmp_path / "TODO.md"
    todo.write_text("- [ ] Setup inicial\n")
    report = qa_review.check_traceability(spec, todo)
    assert report.unplanned_rnf == []


def test_traceability_rnf_default_marker_not_confused_by_unrelated_mention(tmp_path):
    """Regresión: una mención suelta del mismo RNF-N fuera de la fila de
    definición (ej. una línea de changelog que solo lista el ID) no debe
    hacer que se ignore el marcador de default presente en la fila real."""
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        "| RNF-1 | Performance | Global | sin objetivo estricto | — |\n"
        "\n"
        "## Historial de cambios\n"
        "| 2026-01-01 | Spec inicial — define RNF-1 | abc123 |\n"
    )
    todo = tmp_path / "TODO.md"
    todo.write_text("- [ ] Setup inicial\n")
    report = qa_review.check_traceability(spec, todo)
    assert report.unplanned_rnf == []
