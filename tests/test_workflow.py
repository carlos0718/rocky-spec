import json

import pytest

from rocky_spec.workflow import (
    DEFAULT_CONFIRMATIONS,
    load_confirmations,
    save_confirmations,
    workflow_path,
)


def test_missing_file_uses_defaults(tmp_path):
    assert load_confirmations(tmp_path) == {"push": "auto", "branch_delete": "auto"}
    assert load_confirmations(tmp_path) == DEFAULT_CONFIRMATIONS


def test_corrupt_file_falls_back_to_defaults(tmp_path):
    path = workflow_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{ no es json", encoding="utf-8")

    assert load_confirmations(tmp_path) == DEFAULT_CONFIRMATIONS


def test_unknown_values_are_ignored(tmp_path):
    path = workflow_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"confirmations": {"push": "sometimes", "branch_delete": "ask", "otra": "ask"}}),
        encoding="utf-8",
    )

    assert load_confirmations(tmp_path) == {"push": "auto", "branch_delete": "ask"}


def test_save_merges_and_preserves_other_keys(tmp_path):
    path = workflow_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"orchestrator": {"max_parallel_agents": 2}}), encoding="utf-8")

    policy = save_confirmations(tmp_path, {"push": "ask"})

    assert policy == {"push": "ask", "branch_delete": "auto"}
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["orchestrator"] == {"max_parallel_agents": 2}
    assert load_confirmations(tmp_path) == policy


@pytest.mark.parametrize("changes", [{"merge": "auto"}, {"push": "nunca"}])
def test_save_rejects_unknown_action_or_mode(tmp_path, changes):
    # El merge no es configurable: siempre pregunta.
    with pytest.raises(ValueError):
        save_confirmations(tmp_path, changes)
