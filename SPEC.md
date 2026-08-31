# Project Spec — spec-charless

> **Nivel SDD: Spec-Anchored.** Este documento es la fuente de verdad del proyecto — no un artefacto de planificación que se abandona al empezar a codear. Se actualiza **cada vez que cambia el alcance**, antes de tocar código (ver `AGENTS.md` sección "Agregar o modificar features"). Historial de cambios al final del archivo.

## Descripción

Toolkit multi-agente para Spec-Driven Development, nivel Spec-Anchored. Nació como una skill de Claude (`charless-ia`) y se convirtió en un framework agnóstico de agente: una sola base de conocimiento (`.charless/` en el proyecto destino) sirve para Claude Code, Cursor, y los agentes que se agreguen — sin duplicar contenido entre integraciones.

## Usuarios objetivo

Desarrolladores individuales o equipos chicos que usan uno o más agentes de código (Claude Code, Cursor, y a futuro Gemini CLI / Codex CLI) y quieren un ciclo de vida de proyecto consistente entre todos ellos — spec, arquitectura, seguridad, observabilidad — sin reescribir las convenciones para cada agente por separado.

## Features — MVP

| ID | Prioridad | Feature | Descripción breve |
|----|-----------|---------|-------------------|
| RF-1 | P0 (must) | Scaffolding multi-agente | `charless init --agent <x>` genera el conocimiento compartido y la integración del agente elegido en el proyecto destino |
| RF-2 | P0 (must) | Arquitectura de integraciones extensible | Registry de plugins (`IntegrationBase`) — agregar un agente nuevo no requiere tocar el conocimiento compartido ni las integraciones existentes |
| RF-3 | P0 (must) | Health-checks deterministas | `charless check {code,security,observability,qa}` — código real, no prosa que un LLM interpreta cada vez |
| RF-4 | P1 (should) | Instalación no destructiva | Tracking por hash de instalación — desinstalar nunca pisa archivos editados a mano por el usuario |
| RF-5 | P2 (nice) | Publicación en registry público | Distribución vía PyPI (`pip install spec-charless`), hoy se instala en modo editable desde el repo |

## User Stories clave

- **US-1** (implementa RF-1): Como desarrollador, quiero correr `charless init` con uno o más `--agent`, para tener el proyecto listo con las integraciones que uso sin duplicar contenido entre ellas
- **US-2** (implementa RF-1): Como desarrollador, quiero que `.charless/` no se sobreescriba si ya existe, para no perder ediciones manuales al correr `init` de nuevo
- **US-3** (implementa RF-2): Como mantenedor del framework, quiero agregar una integración nueva escribiendo solo una clase, para que sumar agentes no implique reescribir el conocimiento compartido
- **US-4** (implementa RF-3): Como desarrollador, quiero correr `charless check security` sobre mi proyecto, para detectar secrets hardcodeados y archivos fuera de límite sin depender de que un LLM lo interprete bien cada vez
- **US-5** (implementa RF-3): Como desarrollador, quiero correr `charless check qa`, para saber si hay historias de usuario sin tarea asociada o requisitos no funcionales sin plan de trabajo
- **US-6** (implementa RF-4): Como desarrollador, quiero desinstalar una integración sin perder los archivos que edité a mano después de instalarla
- **US-7** (implementa RF-5): Como mantenedor, quiero publicar el paquete en PyPI, para que se instale con `pip install spec-charless` en vez de clonar el repo

## Criterios de aceptación — MVP listo cuando:

- [x] `charless init` genera correctamente las integraciones de Claude y Cursor sin duplicar el conocimiento compartido
- [x] Los tests automatizados (28) pasan
- [x] Los tres health-checks (`code`, `security`, `observability`) corren sin depender de que un LLM interprete bash
- [ ] El chequeo de trazabilidad (`qa`) corre sobre un proyecto real generado por la propia herramienta
- [ ] Al menos una integración adicional (Gemini o Codex) funcionando de punta a punta

## Requisitos no funcionales

| ID | Categoría | Alcance | Requisito | Detalle |
|---|---|---|---|---|
| RNF-1 | Performance | Global | Sin objetivo estricto — herramienta CLI de uso interactivo, no hay carga concurrente que optimizar | — |
| RNF-2 | Escalabilidad | Global | Sin proyección — la escalabilidad real acá es "cuántas integraciones soporta sin reescribir el núcleo", ya cubierto por RF-2 | — |
| RNF-3 | Compatibilidad | Global | Python 3.9+ (declarado en `pyproject.toml`), sin dependencias de sistema operativo específico | Probado en Python 3.12 |
| RNF-4 | Localización / i18n | Global | Documentación, comandos y templates generados en español; nombres de funciones/variables en inglés (convención del código Python) | — |
| RNF-5 | Retención de datos | Global | No aplica — la herramienta no almacena datos de usuarios, solo lee/escribe archivos dentro del proyecto destino | — |
| — | Seguridad | — | Ver `SECURITY.md` | — |
| — | Disponibilidad / monitoreo | — | Ver `OBSERVABILITY.md` — no aplica en el sentido tradicional (no es un servicio que corra en producción) | — |

## Fuera del alcance (v1)

- Publicación en PyPI — hoy se instala en modo editable (`pip install -e .`) desde el repo
- Integraciones con Windsurf, GitHub Copilot, Gemini CLI, Codex CLI — la arquitectura las soporta, faltan escribirse
- CI/CD automatizado (tests corren manualmente, no hay pipeline)
- Sistema de extensiones/presets al estilo Spec Kit (por ahora la única forma de customizar es editar `.charless/` directamente en el proyecto)

---

## Historial de cambios

| Fecha | Cambio | Commit |
|-------|--------|--------|
| 2026-08-31 | Spec inicial vía Modo Adopción — RF-1 a RF-5, US-1 a US-6, RNF-1 a RNF-5 | (pendiente del primer commit) |
