# Contexto del proyecto: rocky-spec

@AGENTS.md

> **Nota para Claude Code**: la línea `@AGENTS.md` de arriba importa el contenido de `AGENTS.md` (stack, comandos, convenciones, y el pointer a `CONSTITUTION.md`) a esta sesión, incluida la tabla acción → mecanismo del Artículo 7 (`AskUserQuestion` obligatorio antes de `git push`, `git merge`, `git tag` y borrar ramas — nunca una confirmación en texto libre). Si tu versión de Claude Code no soporta imports con `@`, leé `AGENTS.md` y `CONSTITUTION.md` al arrancar la sesión.
>
> Este archivo faltaba en el repo — `AGENTS.md` lo daba por existente ("`CLAUDE.md` importa este archivo para Claude Code") pero nunca se creó, así que después de un `/clear` la regla de confirmación de Git dejaba de estar en contexto hasta que algo forzaba releer `AGENTS.md`/`CONSTITUTION.md` a mano.

## Todo lo demás

Stack, comandos, convenciones y el flujo de este proyecto viven en **`AGENTS.md`** (importado arriba). Las reglas que no se negocian — principios de código, seguridad, y la tabla de confirmaciones del Artículo 7 — viven en **`CONSTITUTION.md`**, referenciado desde `AGENTS.md`.
