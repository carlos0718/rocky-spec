import json

from spec_charless import scaffold
from spec_charless.integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME


def test_registry_has_claude_and_cursor():
    assert set(INTEGRATION_REGISTRY.keys()) == {"claude", "cursor"}


def test_claude_integration_generates_skill_md(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    commands = scaffold.all_commands()
    entries = INTEGRATION_REGISTRY["claude"].install(tmp_path, commands)
    paths = [e.path for e in entries]
    assert ".claude/skills/spec-charless/SKILL.md" in paths
    skill_file = tmp_path / ".claude/skills/spec-charless/SKILL.md"
    assert skill_file.exists()
    assert "name: spec-charless" in skill_file.read_text()


def test_cursor_integration_generates_one_command_per_step_plus_rule(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    commands = scaffold.all_commands()
    entries = INTEGRATION_REGISTRY["cursor"].install(tmp_path, commands)
    paths = [e.path for e in entries]
    assert ".cursor/rules/charless.mdc" in paths
    assert len([p for p in paths if p.startswith(".cursor/commands/")]) == len(commands)


def test_ensure_shared_knowledge_copies_all_three_dirs(tmp_path):
    copied = scaffold.ensure_shared_knowledge(tmp_path)
    assert set(copied) == {"commands", "reference", "templates"}
    shared = tmp_path / SHARED_DIR_NAME
    assert (shared / "commands" / "p1-spec-ddd.md").exists()
    assert (shared / "reference" / "security.md").exists()
    assert (shared / "templates" / "SPEC.md.template").exists()
    assert (shared / "VERSION").exists()


def test_ensure_shared_knowledge_does_not_overwrite_without_force(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    custom_file = tmp_path / SHARED_DIR_NAME / "commands" / "p1-spec-ddd.md"
    custom_file.write_text("EDITADO A MANO")
    copied = scaffold.ensure_shared_knowledge(tmp_path)  # sin force
    assert copied == []
    assert custom_file.read_text() == "EDITADO A MANO"


def test_uninstall_removes_only_untouched_files(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    integration = INTEGRATION_REGISTRY["claude"]
    entries = integration.install(tmp_path, scaffold.all_commands())

    skill_file = tmp_path / ".claude/skills/spec-charless/SKILL.md"
    skill_file.write_text(skill_file.read_text() + "\n<!-- edición manual -->")

    removed = integration.uninstall(tmp_path, entries)
    assert removed == 0  # el archivo fue editado a mano, no se toca
    assert skill_file.exists()
