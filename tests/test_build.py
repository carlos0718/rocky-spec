from rocky_spec.scripts import build


def _make_templates(tmp_path):
    templates_dir = tmp_path / ".rocky-spec" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "SPEC.md.template").write_text("# {{PROJECT_NAME}}\n{{DESCRIPTION, default: sin descripción}}\n")
    (templates_dir / "CONSTITUTION.md.template").write_text("Reglas de {{PROJECT_NAME}}\n")
    (templates_dir / "LICENSE-mit.template").write_text("MIT © {{YEAR}} {{COPYRIGHT_HOLDER}}\n")
    return templates_dir


def test_build_renders_only_files_present_in_templates_dir(tmp_path):
    _make_templates(tmp_path)
    result = build.build(tmp_path, {"PROJECT_NAME": "demo"})

    assert "SPEC.md" in result.generated
    assert "CONSTITUTION.md" in result.generated
    assert (tmp_path / "SPEC.md").read_text() == "# demo\nsin descripción\n"
    assert (tmp_path / "CONSTITUTION.md").read_text() == "Reglas de demo\n"
    # AGENTS.md.template no existe en este fixture -- no debe fallar, solo omitirse
    assert "AGENTS.md" not in result.generated
    assert not (tmp_path / "AGENTS.md").exists()


def test_build_reports_unresolved_placeholders(tmp_path):
    _make_templates(tmp_path)
    result = build.build(tmp_path, {})  # sin PROJECT_NAME, y sin default

    assert result.unresolved["SPEC.md"] == ["PROJECT_NAME"]
    assert not result.is_clean


def test_build_does_not_overwrite_existing_file_without_force(tmp_path):
    _make_templates(tmp_path)
    (tmp_path / "SPEC.md").write_text("editado a mano\n")

    result = build.build(tmp_path, {"PROJECT_NAME": "demo"})

    assert "SPEC.md" in result.skipped_existing
    assert (tmp_path / "SPEC.md").read_text() == "editado a mano\n"


def test_build_overwrites_with_force(tmp_path):
    _make_templates(tmp_path)
    (tmp_path / "SPEC.md").write_text("editado a mano\n")

    result = build.build(tmp_path, {"PROJECT_NAME": "demo"}, force=True)

    assert "SPEC.md" in result.generated
    assert (tmp_path / "SPEC.md").read_text() == "# demo\nsin descripción\n"


def test_build_generates_license_when_choice_provided(tmp_path):
    _make_templates(tmp_path)
    result = build.build(tmp_path, {"LICENSE_CHOICE": "mit", "YEAR": "2026", "COPYRIGHT_HOLDER": "Carlos"})

    assert "LICENSE" in result.generated
    assert (tmp_path / "LICENSE").read_text() == "MIT © 2026 Carlos\n"


def test_build_skips_license_when_choice_absent(tmp_path):
    _make_templates(tmp_path)
    result = build.build(tmp_path, {"PROJECT_NAME": "demo"})

    assert "LICENSE" not in result.generated
    assert not (tmp_path / "LICENSE").exists()


def test_build_reports_invalid_license_choice(tmp_path):
    _make_templates(tmp_path)
    result = build.build(tmp_path, {"LICENSE_CHOICE": "gpl3"})

    assert result.invalid_license_choice == "gpl3"
    assert "LICENSE" not in result.generated
    assert not result.is_clean


def test_build_on_empty_templates_dir_generates_nothing(tmp_path):
    (tmp_path / ".rocky-spec" / "templates").mkdir(parents=True)
    result = build.build(tmp_path, {})

    assert result.generated == []
    assert result.skipped_existing == []


# --- modo single-file (only=) ---


def test_build_only_renders_single_template_ignoring_base_files(tmp_path):
    templates_dir = _make_templates(tmp_path)
    (templates_dir / "MASTER.md.template").write_text("Design system de {{PROJECT_NAME}}\n")

    result = build.build(
        tmp_path,
        {"PROJECT_NAME": "demo"},
        only=("MASTER.md.template", "design-system/MASTER.md"),
    )

    assert result.generated == ["design-system/MASTER.md"]
    assert (tmp_path / "design-system" / "MASTER.md").read_text() == "Design system de demo\n"
    # el modo single-file no toca el set fijo, aunque los templates existan
    assert not (tmp_path / "SPEC.md").exists()
    assert not (tmp_path / "CONSTITUTION.md").exists()


def test_build_only_respects_no_overwrite_without_force(tmp_path):
    templates_dir = _make_templates(tmp_path)
    (templates_dir / "MASTER.md.template").write_text("Design system de {{PROJECT_NAME}}\n")
    output = tmp_path / "design-system" / "MASTER.md"
    output.parent.mkdir(parents=True)
    output.write_text("editado a mano\n")

    result = build.build(
        tmp_path,
        {"PROJECT_NAME": "demo"},
        only=("MASTER.md.template", "design-system/MASTER.md"),
    )

    assert result.skipped_existing == ["design-system/MASTER.md"]
    assert output.read_text() == "editado a mano\n"


def test_build_only_overwrites_with_force(tmp_path):
    templates_dir = _make_templates(tmp_path)
    (templates_dir / "MASTER.md.template").write_text("Design system de {{PROJECT_NAME}}\n")
    output = tmp_path / "design-system" / "MASTER.md"
    output.parent.mkdir(parents=True)
    output.write_text("editado a mano\n")

    result = build.build(
        tmp_path,
        {"PROJECT_NAME": "demo"},
        only=("MASTER.md.template", "design-system/MASTER.md"),
        force=True,
    )

    assert result.generated == ["design-system/MASTER.md"]
    assert output.read_text() == "Design system de demo\n"


def test_build_only_reports_unresolved_placeholders(tmp_path):
    templates_dir = _make_templates(tmp_path)
    (templates_dir / "MASTER.md.template").write_text("Design system de {{PROJECT_NAME}}\n")

    result = build.build(tmp_path, {}, only=("MASTER.md.template", "design-system/MASTER.md"))

    assert result.unresolved["design-system/MASTER.md"] == ["PROJECT_NAME"]
    assert not result.is_clean


def test_build_only_ignores_license_choice_key(tmp_path):
    # LICENSE_CHOICE es una clave del modo batch -- en modo single-file no
    # debe intentar generar LICENSE ni fallar por una clave invalida.
    templates_dir = _make_templates(tmp_path)
    (templates_dir / "MASTER.md.template").write_text("Design system de {{PROJECT_NAME}}\n")

    result = build.build(
        tmp_path,
        {"PROJECT_NAME": "demo", "LICENSE_CHOICE": "not-a-real-license"},
        only=("MASTER.md.template", "design-system/MASTER.md"),
    )

    assert result.invalid_license_choice is None
    assert "LICENSE" not in result.generated
    assert result.generated == ["design-system/MASTER.md"]
