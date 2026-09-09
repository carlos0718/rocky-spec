import json

from rocky_spec import scaffold
from rocky_spec.integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME
from rocky_spec.scripts import update


def _age_install(tmp_path, old_version="0.0.0"):
    """Simula un proyecto instalado con una versión vieja del paquete —
    ensure_shared_knowledge ya deja VERSION al día, así que hay que
    envejecerlo a mano para que update.py encuentre algo que hacer."""
    version_file = tmp_path / SHARED_DIR_NAME / "VERSION"
    version_file.write_text(old_version + "\n", encoding="utf-8")


def test_already_up_to_date_is_a_noop(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)

    report = update.apply_update(tmp_path)

    assert report.already_up_to_date is True
    assert report.updated == []


def test_edited_file_is_preserved_not_overwritten(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    _age_install(tmp_path)
    edited = tmp_path / SHARED_DIR_NAME / "commands" / "p1-spec-ddd.md"
    edited.write_text("EDITADO A MANO", encoding="utf-8")

    report = update.apply_update(tmp_path)

    assert "commands/p1-spec-ddd.md" in report.preserved_edited
    assert edited.read_text(encoding="utf-8") == "EDITADO A MANO"


def test_missing_file_is_added_back(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    _age_install(tmp_path)
    missing = tmp_path / SHARED_DIR_NAME / "reference" / "security.md"
    missing.unlink()

    report = update.apply_update(tmp_path)

    assert "reference/security.md" in report.added
    assert missing.exists()


def test_file_without_baseline_hash_is_preserved_and_flagged(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    _age_install(tmp_path)
    manifest_path = tmp_path / SHARED_DIR_NAME / scaffold.SHARED_MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["reference/security.md"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    target = tmp_path / SHARED_DIR_NAME / "reference" / "security.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nEDITADO SIN MANIFEST", encoding="utf-8")

    report = update.apply_update(tmp_path)

    assert "reference/security.md" in report.preserved_no_baseline
    assert "EDITADO SIN MANIFEST" in target.read_text(encoding="utf-8")


def test_file_no_longer_in_package_is_reported_not_deleted(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    _age_install(tmp_path)
    leftover = tmp_path / SHARED_DIR_NAME / "reference" / "ya-no-existe.md"
    leftover.write_text("contenido viejo", encoding="utf-8")

    report = update.apply_update(tmp_path)

    assert "reference/ya-no-existe.md" in report.removed_from_kit
    assert leftover.exists()  # se reporta, nunca se borra solo


def test_dry_run_does_not_write_anything(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    _age_install(tmp_path)
    edited = tmp_path / SHARED_DIR_NAME / "commands" / "p1-spec-ddd.md"
    edited.write_text("EDITADO A MANO", encoding="utf-8")
    version_file = tmp_path / SHARED_DIR_NAME / "VERSION"

    report = update.check_update(tmp_path)

    assert "commands/p1-spec-ddd.md" in report.preserved_edited
    assert version_file.read_text(encoding="utf-8").strip() == "0.0.0"  # no se tocó


def test_refreshes_kit_only_files_of_installed_agents(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    _age_install(tmp_path)
    integration = INTEGRATION_REGISTRY["claude"]
    entries = integration.install(tmp_path, scaffold.all_commands())
    manifest_path = tmp_path / SHARED_DIR_NAME / "install-manifest.json"
    manifest_path.write_text(
        json.dumps({"claude": [{"path": e.path, "sha256": e.sha256} for e in entries]}),
        encoding="utf-8",
    )

    report = update.apply_update(tmp_path)

    assert report.agents_refreshed == ["claude"]
    skill_file = tmp_path / ".claude/skills/rocky-spec/SKILL.md"
    assert skill_file.exists()
