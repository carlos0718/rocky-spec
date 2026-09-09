# Contexto del proyecto: rocky-spec

@AGENTS.md

> **Nota para Claude Code**: la línea `@AGENTS.md` de arriba importa el contenido de `AGENTS.md` (stack, comandos, convenciones, y el flujo Spec-Anchored) a esta sesión. Si tu versión de Claude Code no soporta imports con `@`, pedile directamente a Claude que lea `AGENTS.md` al arrancar la sesión — tiene toda la info operativa del proyecto.
>
> Esta nota es texto fijo (`CLAUDE_MD_ANCHOR_NOTE` en `integrations/claude.py`), no prosa redactada al momento — es la misma que inserta `rocky check anchors`/`rocky init` si algún día este archivo perdiera la línea `@AGENTS.md` de nuevo (pasó una vez: este archivo faltaba por completo hasta que se detectó que `AGENTS.md` daba por hecho su existencia).

## Todo lo demás

Stack, comandos, convenciones y el flujo de este proyecto viven en **`AGENTS.md`** (importado arriba). Las reglas que no se negocian — principios de código, seguridad, y la tabla de confirmaciones del Artículo 7 — viven en **`CONSTITUTION.md`**, referenciado desde `AGENTS.md`.
