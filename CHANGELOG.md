# Changelog

Todos los cambios notables de `rocky-spec` (antes `spec-charless`) se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

## [0.7.0] - 2026-09-04

### Changed
- **Rename completo: `spec-charless`/`charless` → `rocky-spec`/`rocky`** — pedido explícito del usuario. Toca prácticamente todo el repo:
  - Paquete pip: `spec-charless` → `rocky-spec`. Módulo Python: `src/spec_charless/` → `src/rocky_spec/` (`git mv`, historial de archivos preservado).
  - Comando de terminal: `charless` → `rocky` (sin alias de compatibilidad — corte limpio, decisión explícita dado que el proyecto está en `0.x.y` sin usuarios externos conocidos).
  - Carpeta compartida en cada proyecto destino: `.charless/` → `.rocky-spec/`.
  - Skill de Claude Code generada: `.claude/skills/spec-charless/` → `.claude/skills/rocky-spec/` (`/rocky-spec`). Comandos de Cursor: `.cursor/commands/charless-*.md` → `.cursor/commands/rocky-*.md`, `.cursor/rules/charless.mdc` → `.cursor/rules/rocky.mdc`.
  - Repo de GitHub: `carlos0718/spec-charless` → `carlos0718/rocky-spec` (GitHub redirige la URL vieja).
  - Banner de bienvenida regenerado con `pyfiglet` (fuente `ansi_shadow`): "ROCKY" + "SPEC" en vez de "SPEC" + "CHARLESS". Título compacto (terminales angostas) → "ROCKY SPEC".
  - Las 68 referencias en `commands/*.md`/`reference/*.md`/`templates/*.template` (incluida la skill fuente, ya renombrada externamente de `charless-ia` a `rocky-spec`) actualizadas para que el paquete generado quede en sync con la skill que lo produce.
  - `SPEC.md`/`SECURITY.md`/`OBSERVABILITY.md` de este mismo repo: contenido vivo actualizado; la sección "Historial de cambios" de `SPEC.md` **no se reescribió** — sigue describiendo los nombres reales que existían en cada momento pasado, con sus hashes de commit sin tocar.
  - De paso, dos gaps reales encontrados haciendo el audit de consistencia (no relacionados al rename en sí, pero corregidos de una): `rocky check accessibility` y el modo single-file de `rocky build` (`--template`/`--output`) nunca se habían agregado a la tabla de comandos del README ni a `welcome.py`.
  - Sin alias `charless` de compatibilidad — quien ya lo tenía instalado necesita reinstalar (`uv tool uninstall spec-charless && uv tool install git+https://github.com/carlos0718/rocky-spec.git`).

### Fixed
- **Hashes de commit rotos en el "Historial de cambios" de `SPEC.md`/`SECURITY.md`/`OBSERVABILITY.md`** — la reescritura de identidad de git (`git-filter-repo`, ver `v0.3.1`) cambió el SHA de todos los commits del repo; las referencias sueltas en prosa que se habían escrito antes de esa reescritura (`b90cf74`, `0b8c761`, `HEAD` literal, `(pendiente del primer commit)`) quedaron apuntando a revisiones inexistentes o ambiguas. Reemplazadas por los hashes reales actuales (`a855f64`, `88db0fa`, `8da96ec`, `c045465`, `c47b505`), verificados uno por uno contra `git log`. Encontrado por el usuario al revisar `SECURITY.md`.
## [0.6.1] - 2026-09-01

### Added
- **`MA-1.8` en `mode-adopt.md`** — wiring de `charless check accessibility` en Modo Adopción, simétrico a `MA-1.5`/`MA-1.6`/`MA-1.7`: si el proyecto detectado tiene interfaz visual, corre el chequeo determinista (o un heurístico manual reducido de fallback, con nota explícita de que 3 de los 5 heurísticos no tienen aproximación confiable en bash). Nueva fila `ACCESSIBILITY.md` en la tabla `MA-6`, condicional como `design-system/MASTER.md`. Cierra la pieza de "testear código ya escrito" que faltaba — `P5.8` (creación) genera el documento de decisiones, `MA-1.8` (adopción) audita código real, misma distinción que ya existe entre `P5.6`/`P5.7` y `MA-1.6`/`MA-1.7`. El resto del wiring diferido (`TODO.md.template`, `p7.5-qa-review.md`, `p8-p8.5-validation-systemprompt.md`) sigue pendiente.
- **`reference/flow-diagram.md`** — 4 diagramas Mermaid (router de detección de modo, Modo Creación P0→P8.5, Modo Adopción MA-1→MA-8, Modo Reanudación) con los condicionales reales de cada paso (`**Saltear si:**` de cada `commands/*.md`), para entender de un vistazo cómo itera la skill sin leer los 14 archivos de comandos. Enlazado desde `README.md`.

### Changed
- **Limpieza de ramas después de cada release** (`AGENTS.md` sección "Versionado y releases", y su template): tras mergear a la rama principal, el flujo ahora incluye listar las ramas ya mergeadas y preguntarle al usuario cuáles borrar (local + remoto) — nunca automático, nunca ofrecer una rama que no esté 100% mergeada.

## [0.6.0] - 2026-08-31

### Added
- **`charless check accessibility`** (RF-9/US-11) — health-check determinista de accesibilidad web, primera pieza de tres para cerrar el gap encontrado en conversación (no existía ningún chequeo automático, solo prosa en `ui-design-guidelines.md`/`coding-principles.md`). Corre sobre `.html`/`.jsx`/`.tsx` (y `.css` para contraste): `<img>` sin `alt`, `<html>` sin `lang`, `<div onClick>` sin `role`/`tabIndex`, `<button>` solo-ícono sin `aria-label`, y contraste WCAG AA básico (4.5:1) sobre pares `color`/`background` hardcodeados. Puramente diagnóstico, como el resto de los `check` — nunca edita código. Cada heurístico documenta explícitamente sus límites conocidos (spread props, `var(--x)`, Tailwind, texto oculto con `display:none`) en vez de esconderlos.
- **`charless build --template/--output`** — segunda pieza: modo de un solo archivo, para templates condicionales que no aplican a todo proyecto. Cierra un gap real encontrado al diseñar `ACCESSIBILITY.md.template`: `MASTER.md.template` (design system, P4.5) se generaba a mano por el LLM, fuera del mecanismo determinista de `build()` — mismo problema no-determinista que `build()` ya había resuelto para los otros 9 archivos, sin conectar. `p4.5-design-system.md` ahora prefiere `charless build . --template MASTER.md.template --output design-system/MASTER.md` en vez de reescribir el archivo a mano.
- **`ACCESSIBILITY.md.template` + nuevo paso `P5.8 · Accesibilidad`** — tercera y última pieza: documento vivo por proyecto, mismo patrón que `SECURITY.md`/`OBSERVABILITY.md` (nivel de exigencia, decisiones, checklist `- [ ]` que arranca sin marcar), condicional a que el proyecto tenga interfaz visual — se genera igual que `design-system/MASTER.md`, vía el nuevo modo single-file de `charless build`. `p5.8-accessibility.md` documenta el paso completo (detección automática, confirmación, generación). Wireado en `scaffold.py` (`COMMAND_CATALOG`), `qa_review.py` (entra al chequeo de placeholders sin resolver) y `AGENTS.md.template` (línea "Generado por"). El wiring en Modo Adopción (`MA-1.8`, `TODO.md.template`) queda diferido para una iteración posterior — documentado explícitamente, no perdido.

## [0.5.1] - 2026-08-31

### Fixed
- **El diseño del welcome se rompía al angostar la terminal** — `Text(BANNER, ...)` no tenía `no_wrap`/`overflow` seteados en el `console.print()` real, así que Rich repartía cada línea del ASCII art a la mitad e intercalaba los pedazos con la línea siguiente. Ahora usa `no_wrap=True, overflow="crop"` (crop limpio, sin corrupción), y por debajo de `BANNER_WIDTH` (~103 cols) muestra un título compacto ("SPEC CHARLESS") en vez de un banner recortado a la mitad.

### Changed
- **El merge nunca es automático** (`AGENTS.md` sección "Branching", `CONSTITUTION.md` Artículo 7, y sus templates): después de commitear y pushear una rama `feature/*`/`fix/*` (o de dejar `dev` lista para un release), el flujo ahora exige parar y mostrar un resumen del cambio antes de ejecutar `git merge`, esperando confirmación explícita — nunca encadenar commit → push → merge sin que el usuario vea qué se integra a `dev`/`master`. Pedido explícito del usuario tras notar que los merges se venían haciendo en cadena sin pausa.
- **Los recuadros "Glosario" y "Agentes soportados"/"Este proyecto ya usa spec-charless" ahora se arman en dos columnas lado a lado cuando el ancho de la terminal alcanza para los dos** (`rich.columns.Columns`, centrado como grupo) — si no entran, se apilan uno debajo del otro, cada uno igual centrado (antes quedaban pegados a la izquierda). El layout se recalcula contra `console.width` en cada corrida, no queda fijo.

## [0.5.0] - 2026-08-31

### Fixed
- **`charless check qa` no detectaba placeholders con sintaxis `{{NOMBRE, default: valor}}`** que sobrevivían sin rellenar en el archivo final — `qa_review.py` tenía su propio regex, separado y más simple que el de `render_template.py`, que solo reconocía `{{NOMBRE}}`. Unificado: ahora reusa `render_template.find_unresolved()`, la misma fuente de verdad para "qué es un placeholder sin resolver" en todo el proyecto.

### Changed
- **`mode-adopt.md` (MA-1.5/1.6/1.7) y `p7.5-qa-review.md` (Pasos 1 y 4) ahora prefieren los `charless check *` deterministas** en vez de duplicar la misma lógica en heurísticos de `find`/`grep`/`wc -l` como único camino — el heurístico en prosa queda como fallback explícito para cuando `charless` no está instalado. `health_check.py` ya se declaraba a sí mismo "equivalente determinista" de estos pasos en sus propios docstrings; faltaba conectarlo. Segundo paso de tres para cerrar la brecha entre los checks en código y las instrucciones que sigue el LLM.

### Added
- **`charless build`** (RF-8/US-10) — conecta `render_template.py` (existía, con tests propios, pero nada lo llamaba) al flujo real de P6/P7. Toma un JSON plano de valores y renderiza `CONSTITUTION.md`, `SPEC.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `OBSERVABILITY.md`, `CHANGELOG.md`, `README.md`, `TODO.md` y `LICENSE` (si se pasa `LICENSE_CHOICE`) desde `.charless/templates/*.template` en una sola pasada — no pisa un archivo que ya exista salvo `--force`, y reporta placeholders sin resolver por archivo (mismo `find_unresolved()` que ya usa `check qa`). `p6-p7-files-todo.md` documenta correrlo en vez de que el LLM copie cada template y reemplace los marcadores a mano. Tercer y último paso del plan para cerrar la brecha entre los checks deterministas y las instrucciones en prosa del flujo P0-P8.5.

## [0.4.0] - 2026-08-31

### Added
- **Rediseño de la pantalla de bienvenida** (`welcome.py`): todo el contenido queda envuelto en un borde único, título/autoría/tagline centrados, y la versión instalada visible junto al autor (`by Carlos Jesus · v0.4.0`).
- **`charless commands`** — comando nuevo que imprime la tabla completa de comandos con su descripción (espejo de la tabla del README), para no tener que ir a buscarla fuera de la terminal.
- La tabla de "Agentes soportados" del welcome ahora incluye una columna "Se invoca con", aclarando que `/spec-charless` (Claude Code) y `/charless-*` (Cursor) son comandos del **agente**, distintos de `charless` (la CLI).
- README: nueva sección "Tres nombres parecidos, tres cosas distintas" — desambigua `charless` (comando), `spec-charless` (paquete pip + skill generada en el proyecto destino) y `charless-ia` (la skill original con la que se construye este framework).

## [0.3.1] - 2026-08-31

### Fixed
- **README — instalación con `uv`/`pipx` daba error en la práctica**, por dos motivos que faltaba documentar: (1) el README asumía que `uv`/`pipx` ya estaban instalados, sin explicar cómo instalarlos; (2) después de `uv tool install`/`pipx install`, el ejecutable queda en una carpeta que no está en el PATH de la sesión actual hasta correr `uv tool update-shell`/`pipx ensurepath` y reabrir la terminal — el instalador no lo hace solo. Reproducido y verificado contra `v0.3.0` real antes de escribir la corrección.

## [0.3.0] - 2026-08-31

### Fixed
- **La versión estaba hardcodeada en tres lugares** (`pyproject.toml`, `scaffold.CHARLESS_VERSION`, `__init__.__version__` — este último ni se usaba en ningún lado) — ahora `__init__.py` la lee de los metadatos del paquete instalado, una sola fuente de verdad. Bug real encontrado al usar la skill en un IDE separado y notar que la versión no había cambiado tras un fix.

### Added
- Tests de regresión para la fuente única de verdad de la versión (`test_versioning.py`).
- **Branching GitFlow simplificado**, portado desde la skill original (`~/.claude/skills/charless-ia`) a los templates de este paquete: nueva sección "Branching" en `AGENTS.md.template` (`main`/`dev`/`feature/*`/`fix/*`, con el recordatorio de bump de versión al mergear a `dev`/`main`), un **Branch Discipline Check** como paso 0-ter del Workflow de Git, dos artículos nuevos en `CONSTITUTION.md.template` (Boundaries y Versionado), una fila de detección de estado de branching en el scan de `mode-adopt.md` (MA-1), y la tarea "Crear rama `dev` desde `main`" en `TODO.md.template`.
- **Flujo de iteración Plan → Confirmar → Implementar**, también portado desde la skill original: reemplaza el flujo "Agregar o modificar features (Spec-Anchored)" de `AGENTS.md.template`, que solo cubría cambios de alcance. Ahora cualquier pedido de cambio (feature o corrección) pasa primero por un plan breve y espera confirmación explícita antes de tocar código — Paso 1 decide si afecta `SPEC.md` (Paso 2a) o no (Paso 2b), y el Paso 3 implementa recién con el ok del usuario.
- **`charless check version`** (RF-7/US-9) — calcula el bump de SemVer exacto a partir de los commits reales desde el último tag (Conventional Commits, regla "el más alto gana": MAJOR > MINOR > PATCH, sin apilar bumps), reemplazando el recordatorio en prosa de `AGENTS.md`. Maneja el caso pre-1.0 (breaking change sugiere MINOR, no salto automático a `1.0.0`) y avisa con umbrales escalonados (🟡 3-5, 🔴 6+) si una rama `feature/*` acumuló demasiados `fix` comparado contra `dev`. El cálculo se dispara al mergear `feature/*`/`fix/*` → `dev` (o `fix/*` → `master` en un hotfix) — nunca al mergear `dev` → `master`, donde la versión se hereda tal cual. El footer `BREAKING CHANGE:` se detecta anclado a inicio de línea, no en cualquier parte del body — una mención suelta dentro de una viñeta (ej. un commit que *describe* la feature) no cuenta como footer real.

### Docs
- `references/versioning.md` (skill y framework): dos lecciones nuevas encontradas en producción — (1) la versión debe leerse de una única fuente en runtime, nunca hardcodeada en más de un lugar; (2) distribución vía `git+https://...` antes de publicar en un registry hace que cada push sea una publicación de hecho, exige taguear con más disciplina en esa etapa. Ambas ahora también en `CONSTITUTION.md.template` Artículo 7, para que todo proyecto nuevo las tenga desde el arranque.

## [0.2.0] - 2026-08-31

### Added
- Interfaz de bienvenida (`welcome.py`, con `rich`) — banner al correr `charless` sin argumentos, con estado del proyecto (agentes activos) si ya tiene `.charless/`, o la lista de agentes disponibles si es la primera vez. Banner corto antes de `init`.
- Banner ampliado: "CHARLESS" ahora tiene el mismo arte ASCII (fuente `ansi_shadow`) que "SPEC", con "by Carlos Jesus" como autoría. Sumada una reseña de features del kit y un glosario de siglas propias (RF, US, RNF, MA, P) antes de la tabla de integraciones.

### Changed
- Instalación: el README documenta `uv tool install` / `pipx install` / `pip install` desde el repo (`git+https://...`) para Windows, Linux y macOS, con verificación, actualización y desinstalación. PyPI deja de ser requisito de uso y pasa a mejora opcional (RF-6/US-8).

### Fixed
- El wheel no se podía construir: `tool.hatch.build.targets.wheel.force-include` volvía a agregar `commands/`, `reference/` y `templates/`, que `packages` ya incluye por vivir dentro de `src/spec_charless/`, y hatchling abortaba con "A second file is being added to the wheel archive at the same path". Esto rompía `pip install git+...` y cualquier build para PyPI; `pip install -e .` no lo exponía porque el modo editable no construye el wheel.
- URLs del proyecto en `pyproject.toml` — apuntaban a `github.com/charly` (usuario inexistente) y a la rama `main`; el repo publicado es `carlos0718/spec-charless` en `master`.
- `qa_review.check_traceability`: una mención suelta de un `RNF-N` fuera de su fila de definición (ej. en el Historial de cambios) generaba un falso positivo de "sin plan de trabajo", ignorando el marcador de default de la fila real. Mismo fix propagado a `.charless/commands/p7.5-qa-review.md` y a la skill original `charless-ia`.
- Agregado el marcador `"no aplica"` a los reconocidos como default en NFRs — antes solo se reconocían las frases exactas del template.
- **`v0.1.0` nunca había sido tagueado** — la sección del CHANGELOG existía pero el release nunca se completó (le faltaba el paso de `git tag`). Tagueado retroactivamente sobre el commit que corresponde a ese contenido.

## [0.1.0] - 2026-08-31

### Added
- Arquitectura de integraciones (`IntegrationBase`, `INTEGRATION_REGISTRY`) — plugin pattern inspirado en GitHub Spec Kit.
- Integración de Claude Code (`.claude/skills/spec-charless/SKILL.md`).
- Integración de Cursor (`.cursor/commands/*.md` + `.cursor/rules/charless.mdc`).
- Conocimiento compartido migrado desde la skill original: `commands/` (14 pasos del ciclo de vida), `reference/` (17 documentos de principios/metodologías/arquitecturas), `templates/` (18 plantillas de archivos generados).
- Scripts deterministas: `render_template` (relleno de placeholders), `health_check` (code smells/seguridad/observabilidad), `qa_review` (trazabilidad RF→US→RNF→tarea).
- CLI: `charless init`, `charless check {code,security,observability,qa}`, `charless list-integrations`.
- `SPEC.md`, `CONSTITUTION.md`, `AGENTS.md`, `SECURITY.md`, `OBSERVABILITY.md`, `TODO.md` generados vía Modo Adopción — el framework aplicado sobre sí mismo.

### Changed
- Rename del paquete: `charless-cli` → `spec-charless` (el comando sigue siendo `charless`, corto para tipear).
