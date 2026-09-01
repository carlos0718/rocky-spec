# Diagrama de flujo — cómo itera la skill

> Referencia visual de `charless-ia`. No agrega reglas nuevas — es un mapa de los pasos y condicionales que ya están descriptos en `commands/*.md`, para ver de un vistazo cómo se conectan sin tener que leer los 14 archivos. Si algo acá contradice a un `commands/*.md`, ese archivo es la fuente de verdad, no este diagrama.

## 1 · Detección de modo (el router)

Lo primero que corre siempre, antes de cualquier otro paso — decide cuál de los tres modos sigue.

```mermaid
flowchart TD
    start(["Se invoca la skill"]) --> q1{"¿cwd tiene señal de proyecto\niniciado (.git/, package.json,\nrequirements.txt, Cargo.toml, go.mod)\nY NO tiene .skill-state.json?"}
    q1 -->|sí| adopcion["Modo Adopción\n→ mode-adopt.md"]
    q1 -->|no| q2{"¿Existe .skill-state.json,\nO hay frase de continuación\nY ya existen AGENTS.md/CLAUDE.md/\nTODO.md/SPEC.md?"}
    q2 -->|sí| resume["Modo Reanudación\n→ mode-resume.md"]
    q2 -->|no| creacion["Modo Creación\n→ flujo P0 → P8.5"]
```

## 2 · Modo Creación (P0 → P8.5)

Orden real de `scaffold.py` (`COMMAND_CATALOG`), con los condicionales tal como están escritos en cada `commands/*.md` (`**Saltear si:**`).

```mermaid
flowchart TD
    P0["P0 · Detectar workspace\n(solo primera vez)"] --> P1["P1 · Describir proyecto\n+ SPEC.md (SDD + DDD)"]
    P1 --> P3["P3 · Confirmar / editar stack"]
    P3 --> P4["P4 · Arquitectura"]
    P4 --> qVisual1{"¿Tiene interfaz\nvisual?"}
    qVisual1 -->|sí| P45["P4.5 · Design System\n→ design-system/MASTER.md"]
    qVisual1 -->|no| P5
    P45 --> P5["P5 · Comandos a ejecutar"]
    P5 --> qDeploy{"¿Es librería, CLI\no creativo puro?"}
    qDeploy -->|sí, saltear| P56
    qDeploy -->|no| P55["P5.5 · Infraestructura\nde deploy"]
    P55 --> P56["P5.6 · Seguridad\n(mínimo si no hay backend/secrets)"]
    P56 --> P57["P5.7 · Observabilidad\n(mínimo si no hay backend)"]
    P57 --> qVisual2{"¿Tiene interfaz\nvisual?"}
    qVisual2 -->|sí| P58["P5.8 · Accesibilidad\n→ ACCESSIBILITY.md"]
    qVisual2 -->|no, saltear| P67
    P58 --> P67["P6 + P7 · Archivos base + TODO\n(charless build)"]
    P67 --> qScale{"¿Mini/Chico\no prototipo?"}
    qScale -->|sí| P75liviano["P7.5 · QA liviano\n(solo completitud)"]
    qScale -->|no| P75["P7.5 · QA completo\n(Three Amigos)"]
    P75liviano --> P8
    P75 --> P8["P8 / P8.5 · Validación\n+ SYSTEM_PROMPT.md opcional"]
```

**Notas de los condicionales** (no repetir la letra chica de cada `commands/*.md`, solo la señal):
- `P4.5`/`P5.8` — condición idéntica ("¿tiene interfaz visual?"), pero distinto comportamiento sin ella: `P4.5` simplemente no corre; `P5.8` tampoco genera nada mínimo (a diferencia de `P5.6`/`P5.7`, que sí generan una versión chica igual).
- `P5.5` — se saltea directo a `P5.6` si es librería/CLI/creativo puro.
- `P5.6`/`P5.7` — nunca se saltean del todo: sin backend, generan la versión mínima del archivo (política de reporte de vulnerabilidades / logging del build).
- `P7.5` — no se saltea, se aliviana (Mini/Chico o prototipo → solo el paso mecánico de completitud).

## 3 · Modo Adopción (MA-1 → MA-8)

```mermaid
flowchart TD
    MA1["MA-1 · Scan automático\n(runtime, stack, arquitectura, branching)"] --> MA15["MA-1.5 · Health check\ntamaño de archivo"]
    MA15 --> MA16["MA-1.6 · Health check\nseguridad"]
    MA16 --> MA17["MA-1.7 · Health check\nobservabilidad"]
    MA17 --> qVisualMA{"¿Tiene interfaz\nvisual?"}
    qVisualMA -->|sí| MA18["MA-1.8 · Health check\naccesibilidad"]
    qVisualMA -->|no, saltear| MA2
    MA18 --> MA2["MA-2 · Presentar hallazgos\n+ pedir descripción"]
    MA2 --> MA3["MA-3 · Análisis SDD + DDD\n(adaptado a código existente)"]
    MA3 --> MA4["MA-4 · Documentar arquitectura\n(adaptado a código existente)"]
    MA4 --> qVisualMA2{"¿Tiene interfaz\nvisual?"}
    qVisualMA2 -->|sí| MA5["MA-5 · Design System"]
    qVisualMA2 -->|no, saltear| MA6
    MA5 --> MA6["MA-6 · Generar archivos\nfaltantes (nunca sobreescribe)"]
    MA6 --> MA7["MA-7 · TODO desde\nestado actual"]
    MA7 --> MA75["MA-7.5 · Revisión\nfuncional y de QA"]
    MA75 --> MA8["MA-8 · Reporte\nde adopción"]
```

Cada `MA-1.x` de la izquierda alimenta directamente una fila de la tabla `MA-6` (`SECURITY.md`, `OBSERVABILITY.md`, `ACCESSIBILITY.md`) — los ítems con hallazgo arrancan sin marcar en el checklist, nunca asumidos como resueltos.

## 4 · Modo Reanudación

```mermaid
flowchart TD
    start(["Modo Reanudación"]) --> qState{"¿Existe\n.skill-state.json?"}
    qState -->|sí| ask["Preguntar: ¿continuar desde\nel paso guardado, o\narrancar de cero?"]
    ask -->|continuar| nextStep["Saltar directo al\npaso siguiente guardado"]
    ask -->|de cero| renombrar["Renombrar a\n.skill-state.bak.json\n→ empezar P1"]
    qState -->|no| qDev{"¿Ya existen CLAUDE.md /\nTODO.md / SPEC.md y hay\nfrase de continuación?"}
    qDev -->|sí| verif["Leer SPEC.md + TODO.md →\n¿feature nueva? → Spec-Anchored\n¿cierre de fase? → snapshot en specs/\nsi no → próxima tarea del TODO"]
```

## Cómo se conectan los tres diagramas de arriba con el código Python

Ninguno de estos pasos es código — son instrucciones en `.md` que el LLM sigue conversando. Lo único determinista en toda esta cadena son los `charless check *`/`charless build` que algunos pasos invocan (`MA-1.5`–`MA-1.8`, y `P4.5`/`P5.8` al generar `MASTER.md`/`ACCESSIBILITY.md`) — ver el diagrama de arquitectura en el [`README.md`](../../../README.md) del paquete para esa otra mitad del sistema (`init`/`.charless/`/integraciones).
