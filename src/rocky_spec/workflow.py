"""
Política de trabajo del proyecto destino — hoy, qué acciones de git piden
confirmación al humano (RF-33, Artículo 7 de ``CONSTITUTION.md``).

Vive en ``.rocky-spec/workflow.json``. Si el archivo no existe (proyectos
generados antes de RF-33) o está roto, rige ``DEFAULT_CONFIRMATIONS``: push a
``feature/*``/``fix/*`` y borrado de la rama después de su merge automáticos.
Lo que no es configurable — merge, bump/tag/release, ``branch -D``, push a
ramas principales — no se guarda acá: siempre pregunta.
"""
from __future__ import annotations

import json
from pathlib import Path

SHARED_DIR_NAME = ".rocky-spec"
WORKFLOW_FILE_NAME = "workflow.json"

AUTO = "auto"
ASK = "ask"
CONFIRMATION_MODES = (AUTO, ASK)

# Acciones configurables y su default. Agregar una acción acá la vuelve
# configurable desde `rocky config confirmations`.
DEFAULT_CONFIRMATIONS: dict[str, str] = {
    "push": AUTO,
    "branch_delete": AUTO,
}


# Placeholders de los templates cuyo texto depende de la política, y qué
# acción los decide. El texto vive en
# ``templates/fragments/confirmations/<PLACEHOLDER>.<auto|ask>.md`` — conocimiento
# en español editable como cualquier template, no strings en el código.
CONFIRMATION_FRAGMENTS: dict[str, str] = {
    "CONFIRM_ROW_PUSH": "push",
    "PUSH_STEP": "push",
    "CONFIRM_ROW_BRANCH_DELETE": "branch_delete",
    "BRANCH_DELETE_AFTER_MERGE": "branch_delete",
    "BRANCH_DELETE_RELEASE_STEP": "branch_delete",
}
FRAGMENTS_SUBDIR = ("fragments", "confirmations")


def confirmation_fragment_values(templates_dir: Path, policy: dict[str, str]) -> dict[str, str]:
    """Valores de los placeholders de política para ``policy``, leídos de los
    archivos de fragmento. Un fragmento que falta (``.rocky-spec/`` anterior a
    RF-33) simplemente no se incluye: el placeholder queda sin resolver y
    ``rocky build`` lo reporta, que es la señal de correr ``rocky update``."""
    base = templates_dir.joinpath(*FRAGMENTS_SUBDIR)
    values: dict[str, str] = {}
    for placeholder, action in CONFIRMATION_FRAGMENTS.items():
        path = base / f"{placeholder}.{policy[action]}.md"
        if path.exists():
            values[placeholder] = path.read_text(encoding="utf-8").strip()
    return values


def workflow_path(project_root: Path) -> Path:
    return project_root / SHARED_DIR_NAME / WORKFLOW_FILE_NAME


def _read_raw(project_root: Path) -> dict:
    path = workflow_path(project_root)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def load_confirmations(project_root: Path) -> dict[str, str]:
    """Política vigente: defaults pisados por lo que haya en ``workflow.json``.
    Un valor desconocido (ni ``auto`` ni ``ask``) se ignora y rige el default
    — ante la duda, nunca se inventa una política más permisiva que la del
    archivo, porque el default ya es el comportamiento documentado."""
    policy = dict(DEFAULT_CONFIRMATIONS)
    stored = _read_raw(project_root).get("confirmations")
    if isinstance(stored, dict):
        for action, mode in stored.items():
            if action in policy and mode in CONFIRMATION_MODES:
                policy[action] = mode
    return policy


def save_confirmations(project_root: Path, changes: dict[str, str]) -> dict[str, str]:
    """Aplica ``changes`` sobre la política vigente y la persiste, conservando
    cualquier otra clave que ya tuviera ``workflow.json``. Devuelve la política
    resultante. Lanza ``ValueError`` ante una acción o un modo desconocidos."""
    for action, mode in changes.items():
        if action not in DEFAULT_CONFIRMATIONS:
            raise ValueError(f"acción desconocida: {action}")
        if mode not in CONFIRMATION_MODES:
            raise ValueError(f"modo desconocido para {action}: {mode}")

    raw = _read_raw(project_root)
    policy = load_confirmations(project_root)
    policy.update(changes)
    raw["confirmations"] = policy

    path = workflow_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return policy
