# Project Spec — rocky-spec

> **Nivel SDD: Spec-Anchored.** Este documento es la fuente de verdad del proyecto — no un artefacto de planificación que se abandona al empezar a codear. Se actualiza **cada vez que cambia el alcance**, antes de tocar código (ver `AGENTS.md` sección "Agregar o modificar features"). Historial de cambios al final del archivo.

## Descripción

Toolkit multi-agente para Spec-Driven Development, nivel Spec-Anchored. Nació como una skill de Claude (`rocky-spec`) y se convirtió en un framework agnóstico de agente: una sola base de conocimiento (`.rocky-spec/` en el proyecto destino) sirve para Claude Code, Cursor, y los agentes que se agreguen — sin duplicar contenido entre integraciones.

## Usuarios objetivo

Desarrolladores individuales o equipos chicos que usan uno o más agentes de código (Claude Code, Cursor, y a futuro Gemini CLI / Codex CLI) y quieren un ciclo de vida de proyecto consistente entre todos ellos — spec, arquitectura, seguridad, observabilidad — sin reescribir las convenciones para cada agente por separado.

## Features — MVP

| ID | Prioridad | Feature | Descripción breve |
|----|-----------|---------|-------------------|
| RF-1 | P0 (must) | Scaffolding multi-agente | `rocky init --agent <x>` genera el conocimiento compartido y la integración del agente elegido en el proyecto destino |
| RF-2 | P0 (must) | Arquitectura de integraciones extensible | Registry de plugins (`IntegrationBase`) — agregar un agente nuevo no requiere tocar el conocimiento compartido ni las integraciones existentes |
| RF-3 | P0 (must) | Health-checks deterministas | `rocky check {code,security,observability,qa}` — código real, no prosa que un LLM interpreta cada vez |
| RF-4 | P1 (should) | Instalación no destructiva | Tracking por hash de instalación — desinstalar nunca pisa archivos editados a mano por el usuario |
| RF-5 | P1 (should) | Instalación reproducible desde el repo | `pip install git+https://github.com/carlos0718/rocky-spec.git` en Windows, Linux y macOS, sin clonar ni compilar |
| RF-6 | P3 (opcional) | Publicación en registry público | Distribución vía PyPI (`pip install rocky-spec`). No bloquea el uso: RF-5 ya cubre la instalación en las tres plataformas |
| RF-7 | P1 (should) | Sugerencia determinista de versión | `rocky check version` — clasifica los commits desde el último tag por Conventional Commits, aplica la regla "el más alto gana" (MAJOR > MINOR > PATCH, nunca se apilan varios bumps) y calcula el próximo `X.Y.Z` exacto con el reset de componentes correspondiente, en vez de depender de que el agente "se acuerde" |
| RF-8 | P1 (should) | Generación determinista de archivos base | `rocky build --values <json>` — renderiza `CONSTITUTION.md`, `SPEC.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `OBSERVABILITY.md`, `CHANGELOG.md`, `LICENSE`, `README.md`, `TODO.md` desde `.rocky-spec/templates/*.template` usando `render_template.py` (existía pero no estaba conectado a nada), en vez de que el LLM copie el template y reemplace cada marcador `{{...}}` a mano durante P6/P7 |
| RF-9 | P2 (nice) | Health-check determinista de accesibilidad | `rocky check accessibility` — heurísticos por regex sobre HTML/JSX/TSX (`img` sin `alt`, `html` sin `lang`, `div` con `onClick`/`onclick` sin `role`/`tabIndex`, `button` solo-ícono sin `aria-label`) y contraste WCAG básico sobre pares `color`/`background` hardcodeados en CSS o inline — no ve clases de utilidades (Tailwind) ni JSX con spread props, se reporta como límite conocido |

## User Stories clave

- **US-1** (implementa RF-1): Como desarrollador, quiero correr `rocky init` con uno o más `--agent`, para tener el proyecto listo con las integraciones que uso sin duplicar contenido entre ellas
- **US-2** (implementa RF-1): Como desarrollador, quiero que `.rocky-spec/` no se sobreescriba si ya existe, para no perder ediciones manuales al correr `init` de nuevo
- **US-3** (implementa RF-2): Como mantenedor del framework, quiero agregar una integración nueva escribiendo solo una clase, para que sumar agentes no implique reescribir el conocimiento compartido
- **US-4** (implementa RF-3): Como desarrollador, quiero correr `rocky check security` sobre mi proyecto, para detectar secrets hardcodeados y archivos fuera de límite sin depender de que un LLM lo interprete bien cada vez
- **US-5** (implementa RF-3): Como desarrollador, quiero correr `rocky check qa`, para saber si hay historias de usuario sin tarea asociada o requisitos no funcionales sin plan de trabajo
- **US-6** (implementa RF-4): Como desarrollador, quiero desinstalar una integración sin perder los archivos que edité a mano después de instalarla
- **US-7** (implementa RF-5): Como desarrollador en Windows, Linux o macOS, quiero instalar la herramienta con un solo comando apuntando al repo, para usarla sin clonarlo ni configurar un entorno de desarrollo
- **US-8** (implementa RF-6): Como mantenedor, quiero publicar el paquete en PyPI, para que se instale con `pip install rocky-spec` con un nombre corto y versiones fijadas
- **US-9** (implementa RF-7): Como desarrollador, quiero correr `rocky check version` antes de mergear una rama `feature/*`/`fix/*` a `dev`/`master`, para saber el bump de SemVer exacto que corresponde (y recibir un aviso si la rama acumuló muchos `fix` dentro de una misma feature) sin llevar la cuenta manualmente
- **US-10** (implementa RF-8): Como agente ejecutando el flujo P6/P7 de la skill, quiero volcar los valores recolectados en la conversación a un JSON y correr `rocky build`, para que el llenado de placeholders sea reproducible en vez de reescribir cada archivo a mano
- **US-11** (implementa RF-9): Como desarrollador (o agente en Modo Adopción, MA-1.8), quiero correr `rocky check accessibility` sobre un proyecto con interfaz visual, para detectar imágenes sin `alt`, `div`s clickeables sin rol/foco, botones solo-ícono sin `aria-label` y contraste WCAG insuficiente sin depender de que el LLM lo recuerde al generar o revisar código

## Criterios de aceptación — MVP listo cuando:

- [x] `rocky init` genera correctamente las integraciones de Claude y Cursor sin duplicar el conocimiento compartido
- [x] Los tests automatizados (89) pasan
- [x] Los tres health-checks (`code`, `security`, `observability`) corren sin depender de que un LLM interprete bash
- [ ] El chequeo de trazabilidad (`qa`) corre sobre un proyecto real generado por la propia herramienta
- [ ] Al menos una integración adicional (Gemini o Codex) funcionando de punta a punta
- [x] El README documenta la instalación desde el repo para Windows, Linux y macOS (US-7)
- [x] `rocky check version` calcula el bump de SemVer correcto sobre un historial de commits real, con mezcla de tipos (US-9)
- [x] `rocky build` renderiza los 10 archivos base desde `.rocky-spec/templates/` a partir de un JSON de valores, reportando placeholders sin resolver (US-10)
- [x] `rocky check accessibility` detecta los cinco heurísticos (alt, lang, div clickeable sin rol, botón solo-ícono, contraste WCAG) sobre un proyecto real con hallazgos conocidos (US-11)

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

- Publicación en PyPI (RF-6) — se instala directo desde el repo con `pip install git+...`, que cubre las tres plataformas; PyPI queda como mejora de conveniencia, no como requisito de uso
- Integraciones con Windsurf, GitHub Copilot, Gemini CLI, Codex CLI — la arquitectura las soporta, faltan escribirse
- CI/CD automatizado (tests corren manualmente, no hay pipeline)
- Sistema de extensiones/presets al estilo Spec Kit (por ahora la única forma de customizar es editar `.rocky-spec/` directamente en el proyecto)

---

## Historial de cambios

| Fecha | Cambio | Commit |
|-------|--------|--------|
| 2026-08-31 | Spec inicial vía Modo Adopción — RF-1 a RF-5, US-1 a US-6, RNF-1 a RNF-5 | `a855f64` |
| 2026-08-31 | RF-5 redefinido: la instalación reproducible desde el repo (las tres plataformas) reemplaza a PyPI como requisito. PyPI pasa a RF-6/US-8, prioridad opcional. Nueva US-7 para la instalación multiplataforma | `88db0fa` |
| 2026-08-31 | Nueva RF-7/US-9: `charless check version`, pedido explícito del usuario al notar que el recordatorio de bump de versión del Workflow de Git era prosa vaga en vez de un cálculo real sobre los commits | `8da96ec` |
| 2026-08-31 | Nueva RF-8/US-10: `charless build`, conecta `render_template.py` (existía, código huérfano) al flujo real — el usuario preguntó por qué `init` no rellenaba los templates y quién lo hacía; la respuesta fue "el LLM a mano, sin usar el renderer determinista que ya está escrito" | `c045465` |
| 2026-08-31 | Nueva RF-9/US-11: `charless check accessibility`, pedido explícito del usuario al notar que no existía ningún chequeo determinista de accesibilidad — solo prosa en `ui-design-guidelines.md`/`coding-principles.md` | `c47b505` |
| 2026-09-04 | Rename completo del proyecto — `spec-charless`/`charless` → `rocky-spec`/`rocky` — pedido explícito del usuario. No cambia ningún RF/US existente, solo el nombre bajo el que se distribuyen. Esta fila y las siguientes usan los nombres nuevos; las filas anteriores describen los nombres reales de cada momento pasado, sin reescribir | `1944777` |
