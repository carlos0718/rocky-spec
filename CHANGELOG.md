# Changelog

Todos los cambios notables de `spec-charless` se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Changed
- Rename del paquete: `charless-cli` → `spec-charless` (el comando sigue siendo `charless`, corto para tipear).

### Added
- `SPEC.md`, `CONSTITUTION.md`, `AGENTS.md`, `SECURITY.md`, `OBSERVABILITY.md`, `TODO.md` generados vía Modo Adopción — el framework aplicado sobre sí mismo.

### Fixed
- `qa_review.check_traceability`: una mención suelta de un `RNF-N` fuera de su fila de definición (ej. en el Historial de cambios) generaba un falso positivo de "sin plan de trabajo", ignorando el marcador de default de la fila real.
- Agregado el marcador `"no aplica"` a los reconocidos como default en NFRs — antes solo se reconocían las frases exactas del template.

## [0.1.0] - 2026-08-31

### Added
- Arquitectura de integraciones (`IntegrationBase`, `INTEGRATION_REGISTRY`) — plugin pattern inspirado en GitHub Spec Kit.
- Integración de Claude Code (`.claude/skills/charless-ia/SKILL.md`).
- Integración de Cursor (`.cursor/commands/*.md` + `.cursor/rules/charless.mdc`).
- Conocimiento compartido migrado desde la skill original: `commands/` (14 pasos del ciclo de vida), `reference/` (17 documentos de principios/metodologías/arquitecturas), `templates/` (18 plantillas de archivos generados).
- Scripts deterministas: `render_template` (relleno de placeholders), `health_check` (code smells/seguridad/observabilidad), `qa_review` (trazabilidad RF→US→RNF→tarea).
- CLI: `charless init`, `charless check {code,security,observability,qa}`, `charless list-integrations`.
