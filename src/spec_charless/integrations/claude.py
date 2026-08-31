from __future__ import annotations

from pathlib import Path

from .base import (
    CommandDefinition,
    IntegrationBase,
    InstallManifestEntry,
    SHARED_DIR_NAME,
    write_tracked,
)

SKILL_ROOT_TEMPLATE = """---
name: spec-charless
description: 'Crea proyectos desde cero, los retoma en sesiones siguientes o adopta proyectos ya iniciados. Soporta código (web app, API, fullstack, script, mobile), creativos (video ad, motion) e híbridos. Genera CONSTITUTION.md, SPEC.md, AGENTS.md, SECURITY.md, OBSERVABILITY.md, CHANGELOG.md, TODO.md y arquitectura documentada, nivel SDD Spec-Anchored. Tres modos — (1) nuevo: "nuevo proyecto", "armar proyecto", "iniciar proyecto"; (2) reanudación: "continuemos", "qué sigue", "retomemos"; (3) adopción de proyecto existente: "tengo un proyecto ya avanzado", "adoptar proyecto".'
---

# /spec-charless — Skill de ciclo de vida de proyectos (integración Claude)

> Este archivo es la integración de **Claude** dentro del framework `spec-charless`. El conocimiento real (pasos del flujo, principios, templates) vive en `{shared_dir}/` en la raíz del proyecto — versionado junto al código, no dentro de esta skill — así cualquier otro agente (Cursor, y los que se agreguen) lee exactamente lo mismo.

## Cómo usar esta skill

1. Verificar que existe `{shared_dir}/` en el cwd. Si no existe, correr `charless init --agent claude` antes de continuar (o avisar al usuario que lo haga).
2. Detectar el modo: **Adopción** (hay código sin `.skill-state.json`) → leer `{shared_dir}/commands/mode-adopt.md`. **Reanudación** (hay `.skill-state.json` o el usuario usa frases de continuación) → leer `{shared_dir}/commands/mode-resume.md`. **Creación** → seguir el índice de abajo.
3. Cada paso del índice abre su archivo correspondiente en `{shared_dir}/commands/` recién cuando el flujo llega a ese punto — no antes (progressive disclosure).

## Índice del flujo de creación

{commands_index}

## Conocimiento compartido

- `{shared_dir}/reference/` — principios de código, seguridad, observabilidad, versionado, dependencias, metodologías (SDD/TDD/BDD/DDD), arquitecturas, diseño.
- `{shared_dir}/templates/` — plantillas de todos los archivos que se generan en el proyecto (SPEC.md, CONSTITUTION.md, AGENTS.md, SECURITY.md, etc.).
- `{shared_dir}/commands/` — el detalle completo de cada paso del índice de arriba, más `mode-adopt.md` y `mode-resume.md`.
"""


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
                project_root, ".claude/skills/spec-charless/SKILL.md", skill_content
            )
        )
        return manifest
