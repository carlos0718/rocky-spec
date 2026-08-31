# Changelog

Todos los cambios notables de `spec-charless` se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- **Rediseño de la pantalla de bienvenida** (`welcome.py`): todo el contenido queda envuelto en un borde único, título/autoría/tagline centrados, y la versión instalada visible junto al autor (`by Carlos Jesus · v0.3.1`).
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
