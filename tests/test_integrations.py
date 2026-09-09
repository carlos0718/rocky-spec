import json

from rocky_spec import scaffold
from rocky_spec.integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME


def test_registry_has_claude_and_cursor():
    assert set(INTEGRATION_REGISTRY.keys()) == {"claude", "cursor"}


def test_claude_integration_generates_skill_md(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    commands = scaffold.all_commands()
    entries = INTEGRATION_REGISTRY["claude"].install(tmp_path, commands)
    paths = [e.path for e in entries]
    assert ".claude/skills/rocky-spec/SKILL.md" in paths
    skill_file = tmp_path / ".claude/skills/rocky-spec/SKILL.md"
    assert skill_file.exists()
    assert "name: rocky-spec" in skill_file.read_text()


def test_cursor_integration_generates_one_command_per_step_plus_rule(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    commands = scaffold.all_commands()
    entries = INTEGRATION_REGISTRY["cursor"].install(tmp_path, commands)
    paths = [e.path for e in entries]
    assert ".cursor/rules/rocky.mdc" in paths
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

    skill_file = tmp_path / ".claude/skills/rocky-spec/SKILL.md"
    skill_file.write_text(skill_file.read_text() + "\n<!-- edición manual -->")

    removed = integration.uninstall(tmp_path, entries)
    assert removed == 0  # el archivo fue editado a mano, no se toca
    assert skill_file.exists()


def _settings(root):
    import json

    return json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))


def test_permission_rules_created_when_no_settings_exist(tmp_path):
    from rocky_spec.integrations.claude import PERMISSION_ASK_RULES, ensure_permission_rules

    result = ensure_permission_rules(tmp_path)

    assert result["added"] == PERMISSION_ASK_RULES
    assert _settings(tmp_path)["permissions"]["ask"] == PERMISSION_ASK_RULES


def test_permission_rules_never_overwrite_user_settings(tmp_path):
    # El punto central: rocky-spec SUMA reglas, no pisa la config del usuario.
    import json

    from rocky_spec.integrations.claude import ensure_permission_rules

    (tmp_path / ".claude").mkdir()
    original = {
        "model": "opus",
        "env": {"MI_VAR": "valor-del-usuario"},
        "permissions": {"allow": ["Bash(npm run *)"], "ask": ["Bash(rm -rf *)"]},
        "hooks": {"PreToolUse": []},
    }
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps(original), encoding="utf-8")

    ensure_permission_rules(tmp_path)
    after = _settings(tmp_path)

    assert after["model"] == "opus"
    assert after["env"] == {"MI_VAR": "valor-del-usuario"}
    assert after["hooks"] == {"PreToolUse": []}
    assert after["permissions"]["allow"] == ["Bash(npm run *)"]
    assert after["permissions"]["ask"][0] == "Bash(rm -rf *)", "se perdió la regla del usuario"


def test_permission_rules_are_idempotent(tmp_path):
    from rocky_spec.integrations.claude import ensure_permission_rules

    ensure_permission_rules(tmp_path)
    segunda = ensure_permission_rules(tmp_path)
    reglas = _settings(tmp_path)["permissions"]["ask"]

    assert segunda["added"] == [], "un segundo init no debería agregar nada"
    assert len(reglas) == len(set(reglas)), "reglas duplicadas"


def test_permission_rules_report_rules_shadowed_by_allow(tmp_path):
    # En Claude Code un `allow` gana sobre el mismo comando en `ask`: la
    # confirmación nunca aparecería. No se saca del allow (sería pisar una
    # decisión del usuario), se avisa.
    import json

    from rocky_spec.integrations.claude import ensure_permission_rules

    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps({"permissions": {"allow": ["Bash(git push *)"]}}), encoding="utf-8"
    )

    result = ensure_permission_rules(tmp_path)

    assert result["shadowed"] == ["Bash(git push *)"]
    assert _settings(tmp_path)["permissions"]["allow"] == ["Bash(git push *)"]


def test_permission_rules_leave_a_corrupt_settings_file_untouched(tmp_path):
    from rocky_spec.integrations.claude import ensure_permission_rules

    (tmp_path / ".claude").mkdir()
    roto = "{ esto no es JSON válido,,, }"
    (tmp_path / ".claude" / "settings.json").write_text(roto, encoding="utf-8")

    result = ensure_permission_rules(tmp_path)

    assert result["invalid"] == [".claude/settings.json"]
    assert (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8") == roto


def test_settings_json_is_not_tracked_in_the_manifest(tmp_path):
    # uninstall borra los archivos del manifiesto cuyo hash no cambió. Si el
    # settings.json del usuario estuviera trackeado, desinstalar rocky-spec le
    # borraría su configuración entera en vez de solo las reglas agregadas.
    from rocky_spec import scaffold
    from rocky_spec.integrations import INTEGRATION_REGISTRY

    scaffold.ensure_shared_knowledge(tmp_path)
    entries = INTEGRATION_REGISTRY["claude"].install(tmp_path, scaffold.all_commands())

    assert all("settings.json" not in e.path for e in entries)


def test_claude_md_missing_is_not_created_by_install(tmp_path):
    # CLAUDE.md lo genera `rocky build` (necesita los valores del proyecto),
    # no `rocky init` -- install() no debe crearlo de la nada.
    scaffold.ensure_shared_knowledge(tmp_path)
    INTEGRATION_REGISTRY["claude"].install(tmp_path, scaffold.all_commands())
    assert not (tmp_path / "CLAUDE.md").exists()


def test_claude_md_anchor_is_repaired_without_touching_the_rest(tmp_path):
    from rocky_spec.integrations.claude import ClaudeIntegration

    original = "# Contexto del proyecto: demo\n\nNotas mías que no quiero perder.\n"
    (tmp_path / "CLAUDE.md").write_text(original, encoding="utf-8")

    scaffold.ensure_shared_knowledge(tmp_path)
    integration = ClaudeIntegration()
    integration.install(tmp_path, scaffold.all_commands())

    repaired = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "@AGENTS.md" in repaired
    assert "Notas mías que no quiero perder." in repaired
    assert integration.last_claude_md_result == "repaired"


def test_claude_md_with_anchor_is_left_untouched(tmp_path):
    from rocky_spec.integrations.claude import ClaudeIntegration

    original = "# demo\n\n@AGENTS.md\n\nMi nota.\n"
    (tmp_path / "CLAUDE.md").write_text(original, encoding="utf-8")

    scaffold.ensure_shared_knowledge(tmp_path)
    integration = ClaudeIntegration()
    integration.install(tmp_path, scaffold.all_commands())

    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == original
    assert integration.last_claude_md_result is None


def test_cursor_rule_pointer_is_repaired_without_wiping_custom_content(tmp_path):
    from rocky_spec.integrations.cursor import CursorIntegration

    rule_path = tmp_path / ".cursor" / "rules" / "rocky.mdc"
    rule_path.parent.mkdir(parents=True)
    original = "---\nalwaysApply: true\n---\n# regla vieja\nMi seccion propia.\n"
    rule_path.write_text(original, encoding="utf-8")

    scaffold.ensure_shared_knowledge(tmp_path)
    integration = CursorIntegration()
    integration.install(tmp_path, scaffold.all_commands())

    repaired = rule_path.read_text(encoding="utf-8")
    assert ".rocky-spec/" in repaired
    assert "Mi seccion propia." in repaired
    assert integration.last_rule_result == "repaired"


def test_cursor_rule_with_pointer_is_left_untouched(tmp_path):
    from rocky_spec.integrations.cursor import CursorIntegration

    rule_path = tmp_path / ".cursor" / "rules" / "rocky.mdc"
    rule_path.parent.mkdir(parents=True)
    original = "---\nalwaysApply: true\n---\nMi regla ya apunta a .rocky-spec/ bien.\n"
    rule_path.write_text(original, encoding="utf-8")

    scaffold.ensure_shared_knowledge(tmp_path)
    integration = CursorIntegration()
    integration.install(tmp_path, scaffold.all_commands())

    assert rule_path.read_text(encoding="utf-8") == original
    assert integration.last_rule_result == "ok"
