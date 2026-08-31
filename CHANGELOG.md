# Changelog

Todos los cambios notables de `spec-charless` se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

## [0.1.0] - 2026-08-31

### Added
- Arquitectura de integraciones (`IntegrationBase`, `INTEGRATION_REGISTRY`) — plugin pattern inspirado en GitHub Spec Kit.
- Integración de Claude Code (`.claude/skills/charless-ia/SKILL.md`).
- Integración de Cursor (`.cursor/commands/*.md` + `.cursor/rules/charless.mdc`).
- Conocimiento compartido migrado desde la skill original: `commands/` (14 pasos del ciclo de vida), `reference/` (17 documentos de principios/metodologías/arquitecturas), `templates/` (18 plantillas de archivos generados).
- Scripts deterministas: `render_template` (relleno de placeholders), `health_check` (code smells/seguridad/observabilidad), `qa_review` (trazabilidad RF→US→RNF→tarea).
- CLI: `charless init`, `charless check {code,security,observability,qa}`, `charless list-integrations`.
