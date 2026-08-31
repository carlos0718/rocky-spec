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
- [ ] Primer commit + repo en GitHub

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
- [x] Interfaz de bienvenida con rich (banner SPEC+CHARLESS, autoría, features, glosario, estado del proyecto)
- [ ] Publicar en PyPI (US-7)
- [ ] Integración con Gemini CLI
- [ ] Integración con Codex CLI
- [ ] Integración con Windsurf

## Calidad
- [x] Suite de tests (30 tests — render_template, health_check, qa_review, integrations)
- [ ] CI/CD (correr tests automáticamente en cada push)
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
