# TODO — spec-charless

> Generado vía Modo Adopción el 2026-08-31.
>
> **Convención de Git:** cada tarea completada se marca `- [x]` en el mismo commit que el código que la resuelve. Detalle completo en `AGENTS.md` sección "Workflow de Git".
>
> **Trazabilidad**: las tareas que implementan una historia de `SPEC.md` terminan con su ID — `(US-1)`.

## Setup

- [x] Estructura del paquete Python (`pyproject.toml`, `src/spec_charless/`)
- [x] Instalación en modo editable (`pip install -e .`)
- [x] `.gitignore` (agregado al hacer el health-check de seguridad — no existía)
- [x] Primer commit + repo en GitHub (https://github.com/carlos0718/spec-charless)
- [x] Crear rama `dev` desde `master` (ver `AGENTS.md` sección "Branching — GitFlow simplificado")

## Features iniciales

- [x] `charless init` con soporte multi-agente (US-1)
- [x] `.charless/` no se sobreescribe sin `--force` (US-2)
- [x] `IntegrationBase` + `INTEGRATION_REGISTRY` (US-3)
- [x] Integración de Claude Code (US-3)
- [x] Integración de Cursor (US-3)
- [x] `charless check security` — secrets hardcodeados, `.env` sin gitignorar, npm audit (US-4)
- [x] `charless check code` — tamaño de archivo (US-4)
- [x] `charless check observability` — error tracking, health endpoint, console.log (US-4)
- [x] `charless check qa` — trazabilidad RF→US→RNF→tarea (US-5)
- [x] Compatibilidad Python 3.9+, declarada en pyproject.toml (RNF-3)
- [x] Documentación y templates generados en español (RNF-4)
- [x] Tracking por hash de instalación — `uninstall` no pisa ediciones manuales (US-6)
- [x] Interfaz de bienvenida con rich (banner SPEC+CHARLESS, autoría, versión, features, glosario, estado del proyecto, borde único con todo centrado)
- [x] `charless commands` — tabla de comandos con descripción, espejo del README
- [x] Documentar la instalación desde el repo para Windows, Linux y macOS (US-7)
- [x] `charless check version` — sugerencia determinista de bump de SemVer + aviso de fixes acumulados en una feature (US-9)
- [x] `charless build` — conecta render_template.py al flujo real, genera los 10 archivos base desde un JSON de valores (US-10)
- [x] `charless check accessibility` — 5 heurísticos (alt, lang, div clickeable, botón solo-ícono, contraste WCAG básico) sobre HTML/JSX/TSX (US-11)
- [x] `charless build --template/--output` — modo single-file para templates condicionales (arregla MASTER.md, habilita ACCESSIBILITY.md)
- [x] `ACCESSIBILITY.md.template` + `p5.8-accessibility.md` — tercera pieza: template condicional (solo interfaz visual), generado via `charless build` single-file, wireado en `scaffold.py`/`qa_review.py`/`AGENTS.md.template`
- [x] `MA-1.8` en `mode-adopt.md` — wiring de `charless check accessibility` en Modo Adopción, simétrico a MA-1.5/1.6/1.7 (piezas restantes de wiring — `TODO.md.template`, `p7.5-qa-review.md`, `p8-p8.5-validation-systemprompt.md` — siguen diferidas)
- [x] Rename completo del framework: `charless`/`spec-charless` → `rocky`/`rocky-spec` (paquete, módulo Python, comando CLI, skill generada, carpeta compartida `.rocky-spec/`, repo de GitHub) — pedido explícito del usuario, corte limpio sin alias de compatibilidad
- [x] Tabla normativa acción→mecanismo para confirmaciones del humano (Art. 7) en `CONSTITUTION.md` (US-12)
- [x] Reglas de confirmación del Art. 7 instaladas en `.claude/settings.json` del proyecto destino (US-13)
- [x] `rocky commands` muestra los dos niveles (CLI + agente) con conteo derivado (US-14)
- [x] Seguimiento de servicios externos — P3 + secciones en `AGENTS.md`/`TODO.md` (US-15)
- [x] Anclas no destructivas para `CLAUDE.md`/`rocky.mdc` + `rocky check anchors` (US-16)
- [x] `rocky init` lista archivos instalados y el siguiente paso explícito (US-17)
- [x] Protocolo anti-loop en `AGENTS.md`/template (US-18)
- [x] Flujo de release publica el Release en GitHub (`gh release create`), no solo el tag; 6 Releases retroactivos (US-19)
- [x] TODO Drift Check — nuevo paso 0-quater del Workflow de Git: valida que un commit `feat`/`fix` toque `TODO.md`, evitando que features/fixes que surgen en el camino vuelvan a quedar sin registrar
- [x] Recomendación de limpiar sesión (`AskUserQuestion`, graduada por consumo de contexto cuando el agente tiene visibilidad de esa señal) — redefinida: se ofrece al cerrar el flujo completo de integración (push/merge a `development`, version check, tag/release si corresponde, y merge a `master`/`main`), no apenas se mergea a `development` (US-20)
- [x] Actualizar `AGENTS.md` de este repo — mover la sección de recomendación post-merge (US-20) para que dispare al cierre del flujo completo, no en el merge `feature/*`/`fix/*` → `development` (US-20)
- [x] Portar la corrección de timing de US-20 a `templates/AGENTS.md.template` (US-20)
- [x] Renombrar la rama de integración `dev` → `development` (docs de este repo, templates de la skill, `version_check.py` y su test, y la rama real en local/remoto)
- [x] `rocky update` — actualiza `commands`/`reference`/`templates` y los archivos del kit de cada integración instalada a la versión del paquete, sin pisar ediciones manuales (hash-tracking vía `shared-manifest.json`) (US-21)
- [x] Release Sync Check — nuevo paso 5 del flujo de release en `AGENTS.md`: verifica que `origin/master` tenga la versión recién tageada de `pyproject.toml` y ofrece el merge `development → master` con `AskUserQuestion` ahí mismo, evitando que `uv tool install`/`upgrade` (que clona el HEAD de `master`) instale una versión vieja
- [x] Trigger Ambiguity Check — nuevo chequeo en `AGENTS.md`: al redactar una regla nueva con disparador basado en eventos, buscar triggers parecidos ya existentes y dejar la diferencia explícita en el texto de ambas; incluye la aclaración cruzada entre US-20 (limpieza de sesión) y el paso 6 de release (limpieza de ramas), que se habían confundido en la práctica
- [x] Portar Release Sync Check + Trigger Ambiguity Check + aclaración US-20/limpieza de ramas a `templates/AGENTS.md.template`, para que los proyectos generados por la skill no hereden la misma ambigüedad
- [ ] el TODO se puede integrar via MCP a la sección de Project elijiendo la vista kamban?
- [x] MA-6 guarda `license_decision` en `.skill-state.json` al responder la pregunta de `LICENSE` (US-23, RF-20)
- [x] `rocky check drift` — detecta archivos que MA-6 genera hoy (`CONSTITUTION.md`/`CHANGELOG.md`/`SECURITY.md`/`OBSERVABILITY.md`/`ACCESSIBILITY.md`/`design-system/MASTER.md`/`LICENSE`) pero faltan en proyectos adoptados con una versión vieja de la skill (US-23, RF-20)
- [x] Enganchar `rocky check drift` dentro de `rocky update` (US-23, RF-20)
- [x] `rocky update`/`rocky check drift` terminan con un mensaje accionable de próximo paso cuando hay hallazgos de drift, en vez de solo listarlos (US-24, RF-21)
- [ ] `mode-resume.md` — nuevo paso 0 del checklist de Reanudación: revalida `.skill-state.json` contra `rocky check drift` y resuelve los hallazgos siguiendo la tabla P6 de `mode-adopt.md` antes de seguir con el TODO (US-25, RF-21)
- [ ] Publicar en PyPI — opcional, no bloquea el uso (US-8)
- [ ] Integración con Gemini CLI
- [ ] Integración con Codex CLI
- [ ] Integración con Windsurf

## Calidad

- [x] Suite de tests (render_template, health_check, qa_review, integrations, version_check, versioning, build, welcome, accessibility_check, update) — correr `pytest -q` para el conteo actual, no se mantiene un número fijo acá porque queda desactualizado con cada feature que suma tests.
- [x] CI/CD — GitHub Actions corre `pytest` (matrix Python 3.9/3.12) en cada push/PR a `development` y `master` (US-22)
- [ ] Coverage report

## Documentación

- [x] README.md
- [x] CHANGELOG.md
- [ ] Documentar cómo agregar una integración nueva (guía paso a paso, hoy solo está en el README a alto nivel)

## Infraestructura / Deploy

- [ ] No aplica todavía — no hay deploy de un CLI, solo distribución (ver Publicar en PyPI arriba)

## Seguridad

- [x] `.env` en `.gitignore`
- [ ] Revisar si corresponde firmar los paquetes publicados en PyPI (trusted publishing)

## Observabilidad

- [x] No aplica en el sentido tradicional — es un CLI, no un servicio corriendo en producción (ver `OBSERVABILITY.md`)
