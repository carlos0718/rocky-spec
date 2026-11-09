"""RF-33: el texto de la política de confirmaciones en CONSTITUTION.md y
AGENTS.md sale de fragmentos que resuelve `rocky build` desde workflow.json,
no de lo que redacte el LLM."""
import re
import shutil
from importlib import resources
from pathlib import Path

import pytest

from rocky_spec.scripts import build
from rocky_spec.workflow import CONFIRMATION_FRAGMENTS, CONFIRMATION_MODES, save_confirmations

PACKAGE_TEMPLATES = Path(str(resources.files("rocky_spec"))) / "templates"
POLICY_TEMPLATES = ("CONSTITUTION.md.template", "AGENTS.md.template")


def _project(tmp_path):
    """Proyecto con los templates reales del paquete en .rocky-spec/templates."""
    shutil.copytree(PACKAGE_TEMPLATES, tmp_path / ".rocky-spec" / "templates")
    return tmp_path


def _fragment(placeholder, mode):
    path = PACKAGE_TEMPLATES / "fragments" / "confirmations" / f"{placeholder}.{mode}.md"
    return path.read_text(encoding="utf-8").strip()


@pytest.mark.parametrize("placeholder", sorted(CONFIRMATION_FRAGMENTS))
@pytest.mark.parametrize("mode", CONFIRMATION_MODES)
def test_every_fragment_exists_for_every_mode(placeholder, mode):
    assert _fragment(placeholder, mode)


def test_templates_use_exactly_the_declared_fragment_placeholders():
    # Anti-drift: un placeholder de política nuevo en un template tiene que
    # estar declarado en CONFIRMATION_FRAGMENTS, y viceversa.
    used = set()
    for name in POLICY_TEMPLATES:
        text = (PACKAGE_TEMPLATES / name).read_text(encoding="utf-8")
        used |= {p for p in re.findall(r"\{\{([A-Z_]+)\}\}", text) if p in CONFIRMATION_FRAGMENTS
                 or p.startswith(("CONFIRM_ROW_", "PUSH_STEP", "BRANCH_DELETE_"))}
    assert used == set(CONFIRMATION_FRAGMENTS)


def test_build_with_default_policy_writes_automatic_push_and_delete(tmp_path):
    project = _project(tmp_path)
    build.build(project, {})

    constitution = (project / "CONSTITUTION.md").read_text(encoding="utf-8")
    agents = (project / "AGENTS.md").read_text(encoding="utf-8")

    assert _fragment("CONFIRM_ROW_PUSH", "auto") in constitution
    assert _fragment("CONFIRM_ROW_BRANCH_DELETE", "auto") in constitution
    assert _fragment("PUSH_STEP", "auto") in agents
    assert _fragment("BRANCH_DELETE_AFTER_MERGE", "auto") in agents
    assert _fragment("BRANCH_DELETE_RELEASE_STEP", "auto") in agents
    for text in (constitution, agents):
        for placeholder in CONFIRMATION_FRAGMENTS:
            assert "{{" + placeholder + "}}" not in text


def test_build_with_ask_policy_writes_ask_fragments(tmp_path):
    project = _project(tmp_path)
    save_confirmations(project, {"push": "ask", "branch_delete": "ask"})
    build.build(project, {})

    constitution = (project / "CONSTITUTION.md").read_text(encoding="utf-8")
    agents = (project / "AGENTS.md").read_text(encoding="utf-8")

    assert _fragment("CONFIRM_ROW_PUSH", "ask") in constitution
    assert _fragment("CONFIRM_ROW_PUSH", "auto") not in constitution
    assert _fragment("PUSH_STEP", "ask") in agents


def test_fragments_are_not_persisted_in_build_values(tmp_path):
    project = _project(tmp_path)
    build.build(project, {"PROJECT_NAME": "demo"})

    values = (project / ".rocky-spec" / "build-values.json").read_text(encoding="utf-8")
    assert "PUSH_STEP" not in values


def test_stale_policy_docs_detects_docs_generated_with_another_policy(tmp_path):
    project = _project(tmp_path)
    build.build(project, {})
    assert build.stale_policy_docs(project) == []

    save_confirmations(project, {"push": "ask"})

    assert sorted(build.stale_policy_docs(project)) == ["AGENTS.md", "CONSTITUTION.md"]


def test_update_file_applies_current_policy(tmp_path):
    project = _project(tmp_path)
    build.build(project, {})
    save_confirmations(project, {"push": "ask"})

    result = build.update_file(project, {}, "CONSTITUTION.md.template", "CONSTITUTION.md")

    assert result.error is None
    assert _fragment("CONFIRM_ROW_PUSH", "ask") in (project / "CONSTITUTION.md").read_text(encoding="utf-8")
    assert build.stale_policy_docs(project) == ["AGENTS.md"]
