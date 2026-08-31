from __future__ import annotations

from pathlib import Path

from .base import (
    CommandDefinition,
    IntegrationBase,
    InstallManifestEntry,
    SHARED_DIR_NAME,
    write_tracked,
)

# Formato real de Cursor Commands (.cursor/commands/*.md): Markdown plano,
# SIN frontmatter, invocado como /nombre-del-archivo. Confirmado en la doc
# oficial de Cursor (changelog 1.6) — no inventar campos que no existen.
COMMAND_TEMPLATE = """# {title}

Actuá como el analista funcional + arquitecto de software del framework spec-charless. Leé y seguí al pie de la letra las instrucciones del paso "{key}", que están en:

`{shared_dir}/commands/{relative_source}`

Ese archivo ya referencia `{shared_dir}/reference/` y `{shared_dir}/templates/` con las rutas correctas para este proyecto — son las mismas que usa la integración de Claude, no hace falta traducir nada.
"""

RULE_TEMPLATE = """---
description: Contexto persistente del framework spec-charless — principios de código, seguridad y arquitectura que no se negocian en este proyecto.
alwaysApply: true
---

# charless — contexto persistente

Este proyecto usa el framework `spec-charless` (Spec-Driven Development, nivel Spec-Anchored). Antes de proponer o escribir código:

1. Si existe `CONSTITUTION.md` en la raíz del proyecto, sus artículos son innegociables — no proponer nada que los contradiga sin avisar explícitamente.
2. Si existe `SPEC.md`, es la fuente de verdad de qué se está construyendo — actualizarlo ANTES de un cambio de alcance, no después (ver `{shared_dir}/reference/methodologies.md` sección SDD).
3. Los comandos `/charless-*` (ver `.cursor/commands/`) cubren cada paso del ciclo de vida — spec, arquitectura, seguridad, observabilidad, etc. Si el usuario pide algo que corresponde a uno de esos pasos, sugerir el comando en vez de improvisar.
4. Conocimiento completo del framework en `{shared_dir}/reference/` — consultarlo antes de inventar una convención propia.
"""


class CursorIntegration(IntegrationBase):
    key = "cursor"
    display_name = "Cursor"

    def install(
        self, project_root: Path, commands: list[CommandDefinition]
    ) -> list[InstallManifestEntry]:
        manifest: list[InstallManifestEntry] = []

        for cmd in commands:
            slug = cmd.key.replace("_", "-")
            content = COMMAND_TEMPLATE.format(
                title=cmd.title,
                key=cmd.key,
                shared_dir=SHARED_DIR_NAME,
                relative_source=cmd.relative_source,
            )
            manifest.append(
                write_tracked(
                    project_root, f".cursor/commands/charless-{slug}.md", content
                )
            )

        rule_content = RULE_TEMPLATE.format(shared_dir=SHARED_DIR_NAME)
        manifest.append(
            write_tracked(project_root, ".cursor/rules/charless.mdc", rule_content)
        )
        return manifest
