from __future__ import annotations

from pathlib import Path

from .base import (
    CommandDefinition,
    IntegrationBase,
    InstallManifestEntry,
    SHARED_DIR_NAME,
    sha256_of,
    write_tracked,
)

CURSOR_RULE_PATH = ".cursor/rules/rocky.mdc"

# El único contenido de rocky.mdc que rocky-spec necesita proteger: el
# puntero al conocimiento compartido. Si el usuario extendió la regla con
# secciones propias, no queremos pisarla entera en el próximo `rocky init`
# — solo garantizar que el puntero siga ahí.
CURSOR_RULE_ANCHOR = f"{SHARED_DIR_NAME}/"

# Formato real de Cursor Commands (.cursor/commands/*.md): Markdown plano,
# SIN frontmatter, invocado como /nombre-del-archivo. Confirmado en la doc
# oficial de Cursor (changelog 1.6) — no inventar campos que no existen.
COMMAND_TEMPLATE = """# {title}

Actuá como el analista funcional + arquitecto de software del framework rocky-spec. Leé y seguí al pie de la letra las instrucciones del paso "{key}", que están en:

`{shared_dir}/commands/{relative_source}`

Ese archivo ya referencia `{shared_dir}/reference/` y `{shared_dir}/templates/` con las rutas correctas para este proyecto — son las mismas que usa la integración de Claude, no hace falta traducir nada.
"""

RULE_TEMPLATE = """---
description: Contexto persistente del framework rocky-spec — principios de código, seguridad y arquitectura que no se negocian en este proyecto.
alwaysApply: true
---

# rocky — contexto persistente

Este proyecto usa el framework `rocky-spec` (Spec-Driven Development, nivel Spec-Anchored). Antes de proponer o escribir código:

1. Si existe `CONSTITUTION.md` en la raíz del proyecto, sus artículos son innegociables — no proponer nada que los contradiga sin avisar explícitamente.
2. Si existe `SPEC.md`, es la fuente de verdad de qué se está construyendo — actualizarlo ANTES de un cambio de alcance, no después (ver `{shared_dir}/reference/methodologies.md` sección SDD).
3. Los comandos `/rocky-*` (ver `.cursor/commands/`) cubren cada paso del ciclo de vida — spec, arquitectura, seguridad, observabilidad, etc. Si el usuario pide algo que corresponde a uno de esos pasos, sugerir el comando en vez de improvisar.
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
                    project_root, f".cursor/commands/rocky-{slug}.md", content
                )
            )

        entry, self.last_rule_result = self._ensure_rule(project_root)
        manifest.append(entry)
        return manifest

    def _ensure_rule(self, project_root: Path) -> tuple[InstallManifestEntry, str]:
        """Escribe ``rocky.mdc`` si no existe. Si ya existe, no lo pisa
        entero — evita perder secciones propias que el usuario le haya
        agregado — pero repara el puntero a ``.rocky-spec/`` si se lo
        borraron a mano. Devuelve la entrada de manifiesto y el estado
        (``"created"`` | ``"repaired"`` | ``"ok"``) para que el CLI lo
        reporte."""
        rule_path = project_root / CURSOR_RULE_PATH
        if not rule_path.exists():
            rule_content = RULE_TEMPLATE.format(shared_dir=SHARED_DIR_NAME)
            return write_tracked(project_root, CURSOR_RULE_PATH, rule_content), "created"

        content = rule_path.read_text(encoding="utf-8")
        if CURSOR_RULE_ANCHOR in content:
            return InstallManifestEntry(path=CURSOR_RULE_PATH, sha256=sha256_of(content)), "ok"

        repaired = content.rstrip("\n") + f"\n\n<!-- rocky-spec: puntero restaurado -->\n{CURSOR_RULE_ANCHOR}\n"
        rule_path.write_text(repaired, encoding="utf-8")
        return InstallManifestEntry(path=CURSOR_RULE_PATH, sha256=sha256_of(repaired)), "repaired"
