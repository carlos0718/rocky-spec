from __future__ import annotations

import json
from pathlib import Path

from .base import (
    CommandDefinition,
    IntegrationBase,
    InstallManifestEntry,
    SHARED_DIR_NAME,
    write_tracked,
)

# Las acciones de la tabla "acción → mecanismo" del Artículo 7 del
# CONSTITUTION.md, en formato de regla de permisos de Claude Code. La regla
# escrita ya viaja en los templates; esto es lo que la hace cumplir cuando el
# agente se olvida de preguntar — que pasa.
#
# Van en ``ask`` y no en ``deny`` a propósito: ``deny`` impediría ejecutarlas
# incluso con autorización explícita del usuario, y estas son operaciones
# legítimas del día a día. ``ask`` frena y deja decidir.
PERMISSION_ASK_RULES = [
    "Bash(git push *)",
    "Bash(git merge *)",
    "Bash(git tag *)",
    "Bash(git branch -d *)",
    "Bash(git branch -D *)",
]

CLAUDE_SETTINGS_PATH = ".claude/settings.json"

# La línea que hace que Claude Code auto-cargue AGENTS.md (stack, comandos,
# convenciones, y la tabla de confirmaciones del Artículo 7) en cada sesión
# nueva. Es el único contenido de CLAUDE.md que rocky-spec necesita proteger
# — el resto (roles de expertise, notas del proyecto) es del usuario.
CLAUDE_MD_PATH = "CLAUDE.md"
CLAUDE_MD_ANCHOR = "@AGENTS.md"

# Nota que acompaña al ancla cuando se repara un CLAUDE.md que la perdió.
# Fija a propósito -- ver docstring de ensure_claude_md_anchor: antes de esto,
# la nota se redactaba en prosa cada vez que alguien (LLM o humano) reparaba
# un CLAUDE.md a mano, y terminó con dos versiones distintas del mismo texto
# en este mismo repo. Es una versión más corta que la de CLAUDE.md.template
# a propósito: acá no se está agregando la sección de roles de expertise que
# esa nota da por hecho que existe, así que no puede prometerla.
CLAUDE_MD_ANCHOR_NOTE = (
    "> **Nota para Claude Code**: la línea `@AGENTS.md` de arriba importa el "
    "contenido de `AGENTS.md` (stack, comandos, convenciones, y el flujo "
    "Spec-Anchored) a esta sesión. Si tu versión de Claude Code no soporta "
    "imports con `@`, pedile directamente a Claude que lea `AGENTS.md` al "
    "arrancar la sesión — tiene toda la info operativa del proyecto."
)


def ensure_claude_md_anchor(project_root: Path) -> str | None:
    """Si ``CLAUDE.md`` existe pero perdió la línea ``@AGENTS.md`` (borrada a
    mano, o el archivo viene de antes de que existiera esta convención — el
    caso real que motivó esto: pasó en la raíz de este mismo repo), reinserta
    el ancla **y** su nota explicativa (``CLAUDE_MD_ANCHOR_NOTE``, fija, no
    redactada en el momento) sin tocar el resto del archivo.

    No crea ``CLAUDE.md`` si no existe — eso requiere los valores del
    proyecto (nombre, etc.) y es responsabilidad de ``rocky build``, no de
    ``rocky init``.

    Devuelve ``"repaired"`` si tuvo que insertar el ancla, o ``None`` si no
    existía el archivo o ya estaba bien.
    """
    claude_md = project_root / CLAUDE_MD_PATH
    if not claude_md.exists():
        return None

    content = claude_md.read_text(encoding="utf-8")
    if CLAUDE_MD_ANCHOR in content:
        return None

    block = CLAUDE_MD_ANCHOR + "\n\n" + CLAUDE_MD_ANCHOR_NOTE
    lines = content.splitlines()
    if lines and lines[0].startswith("# "):
        heading, rest = lines[0], lines[1:]
        repaired = heading + "\n\n" + block + "\n\n" + "\n".join(rest).lstrip("\n")
    else:
        repaired = block + "\n\n" + content

    if not repaired.endswith("\n"):
        repaired += "\n"
    claude_md.write_text(repaired, encoding="utf-8")
    return "repaired"

SKILL_ROOT_TEMPLATE = """---
name: rocky-spec
description: 'Crea proyectos desde cero, los retoma en sesiones siguientes o adopta proyectos ya iniciados. Soporta código (web app, API, fullstack, script, mobile), creativos (video ad, motion) e híbridos. Genera CONSTITUTION.md, SPEC.md, AGENTS.md, SECURITY.md, OBSERVABILITY.md, CHANGELOG.md, TODO.md y arquitectura documentada, nivel SDD Spec-Anchored. Tres modos — (1) nuevo: "nuevo proyecto", "armar proyecto", "iniciar proyecto"; (2) reanudación: "continuemos", "qué sigue", "retomemos"; (3) adopción de proyecto existente: "tengo un proyecto ya avanzado", "adoptar proyecto".'
---

# /rocky-spec — Skill de ciclo de vida de proyectos (integración Claude)

> Este archivo es la integración de **Claude** dentro del framework `rocky-spec`. El conocimiento real (pasos del flujo, principios, templates) vive en `{shared_dir}/` en la raíz del proyecto — versionado junto al código, no dentro de esta skill — así cualquier otro agente (Cursor, y los que se agreguen) lee exactamente lo mismo.

## Cómo usar esta skill

1. Verificar que existe `{shared_dir}/` en el cwd. Si no existe, correr `rocky init --agent claude` antes de continuar (o avisar al usuario que lo haga).
2. Detectar el modo: **Adopción** (hay código sin `.skill-state.json`) → leer `{shared_dir}/commands/mode-adopt.md`. **Reanudación** (hay `.skill-state.json` o el usuario usa frases de continuación) → leer `{shared_dir}/commands/mode-resume.md`. **Creación** → seguir el índice de abajo.
3. Cada paso del índice abre su archivo correspondiente en `{shared_dir}/commands/` recién cuando el flujo llega a ese punto — no antes (progressive disclosure).

## Índice del flujo de creación

{commands_index}

## Conocimiento compartido

- `{shared_dir}/reference/` — principios de código, seguridad, observabilidad, versionado, dependencias, metodologías (SDD/TDD/BDD/DDD), arquitecturas, diseño.
- `{shared_dir}/templates/` — plantillas de todos los archivos que se generan en el proyecto (SPEC.md, CONSTITUTION.md, AGENTS.md, SECURITY.md, etc.).
- `{shared_dir}/commands/` — el detalle completo de cada paso del índice de arriba, más `mode-adopt.md` y `mode-resume.md`.
"""


def ensure_permission_rules(project_root: Path) -> dict[str, list[str]]:
    """Suma las reglas del Artículo 7 a ``.claude/settings.json`` **sin pisar**
    lo que el usuario ya tenga: si el archivo existe se leen sus claves, se
    agregan solo las reglas que falten, y todo lo demás se conserva tal cual.

    Devuelve un dict con tres listas para que el CLI informe qué pasó:
    ``added`` (reglas nuevas), ``shadowed`` (reglas que quedan sin efecto
    porque el usuario tiene el mismo comando en ``allow``) e ``invalid``
    (el archivo existe pero no es JSON parseable — no se toca nada).

    **No pasa por el manifiesto a propósito.** ``uninstall`` borra los archivos
    trackeados cuyo hash no cambió, así que registrar acá el ``settings.json``
    del usuario significaría poder borrarle su configuración entera al
    desinstalar, no solo las reglas que agregó rocky-spec.

    Por qué ``ask`` y no ``deny``: ver ``PERMISSION_ASK_RULES``. Y por qué
    importa el ``shadowed``: en Claude Code una regla de ``allow`` **gana**
    sobre la misma regla en ``ask`` — el comando queda pre-aprobado y la
    confirmación nunca aparece. Se avisa en vez de sacarla del ``allow``,
    que sería pisar una decisión del usuario.
    """
    result: dict[str, list[str]] = {"added": [], "shadowed": [], "invalid": []}
    settings_path = project_root / CLAUDE_SETTINGS_PATH

    settings: dict = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            result["invalid"].append(CLAUDE_SETTINGS_PATH)
            return result
        if not isinstance(settings, dict):
            result["invalid"].append(CLAUDE_SETTINGS_PATH)
            return result

    permissions = settings.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        result["invalid"].append(CLAUDE_SETTINGS_PATH)
        return result

    ask = permissions.setdefault("ask", [])
    allow = permissions.get("allow", [])
    if not isinstance(ask, list) or not isinstance(allow, list):
        result["invalid"].append(CLAUDE_SETTINGS_PATH)
        return result

    for rule in PERMISSION_ASK_RULES:
        if rule not in ask:
            ask.append(rule)
            result["added"].append(rule)
        if rule in allow:
            result["shadowed"].append(rule)

    if not result["added"]:
        return result  # nada que escribir: no tocar el archivo ni su mtime

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


class ClaudeIntegration(IntegrationBase):
    key = "claude"
    display_name = "Claude Code"

    def install(
        self, project_root: Path, commands: list[CommandDefinition]
    ) -> list[InstallManifestEntry]:
        manifest: list[InstallManifestEntry] = []

        index_lines = []
        for cmd in commands:
            if cmd.key in ("mode-adopt", "mode-resume"):
                continue  # esos se referencian aparte, no van en el índice lineal
            index_lines.append(
                f"### {cmd.title}\n→ `{SHARED_DIR_NAME}/commands/{cmd.relative_source}`\n"
            )

        skill_content = SKILL_ROOT_TEMPLATE.format(
            shared_dir=SHARED_DIR_NAME,
            commands_index="\n".join(index_lines),
        )

        manifest.append(
            write_tracked(
                project_root, ".claude/skills/rocky-spec/SKILL.md", skill_content
            )
        )

        # Fuera del manifiesto a propósito -- ver el docstring de
        # ensure_permission_rules. El resultado queda en el atributo para que
        # el CLI pueda reportarlo sin cambiar la firma de `install`, que es
        # parte del contrato de IntegrationBase y comparten las demás
        # integraciones.
        self.last_permission_result = ensure_permission_rules(project_root)

        # Mismo motivo que arriba: CLAUDE.md no es un archivo que instale
        # esta integración (lo genera `rocky build`, no `rocky init`), así
        # que su reparación no entra en el manifiesto tampoco.
        self.last_claude_md_result = ensure_claude_md_anchor(project_root)
        return manifest
