# Cómo es una sesión real, de punta a punta

Este documento no repite lo que ya está en el [README](README.md) (instalación,
comandos, arquitectura del paquete). Es la otra mitad: qué se siente trabajar
con `rocky-spec` instalado en un proyecto — dónde para a preguntar, qué
archivos se actualizan solos, y cómo se ve el flujo de Git en la práctica. No
es un generador de documentación que corre una vez y se desactualiza: es un
colaborador que planifica antes de tocar código y frena en los puntos donde
una decisión es tuya, no suya.

## Planificación — nada se toca sin plan ni confirmación

Antes de que se escriba una sola línea de código o de `SPEC.md`, cualquier
pedido (feature nueva o corrección) pasa por esto:

1. **¿Cambia el alcance de `SPEC.md`?**
   - **Sí** (ej. *"quiero agregar login con Google"*) → primero se escriben
     `RF-N` (la feature, en la tabla de prioridades P0/P1/P2), las `US-N`
     que la implementan (cada una etiquetada `(implementa RF-N)`), y si
     corresponde un `RNF-N` (ej. *"el login responde en menos de 300ms"*) —
     todo en `SPEC.md`, con su línea en "Historial de cambios". Recién
     después se muestra el plan técnico: qué archivos, en qué orden
     (Dominio/DB → API → Frontend, o por feature), **y qué rama se va a
     crear** (`feature/google-auth`).
   - **No** (una corrección puntual) → se describe el cambio en 3-5 líneas,
     sin tocar `SPEC.md`, con la rama que correspondería (`fix/<algo>`).
2. En los dos casos, el plan termina con una pregunta explícita — *"¿Avanzo
   con esto?"* — y se espera la respuesta. Nunca se adelanta código en el
   mismo turno en que se recibe el pedido, aunque el pedido ya se haya
   entendido del todo.
3. Recién con la confirmación arranca la implementación — que es donde entra
   todo lo de la sección siguiente.

Este mismo archivo es un ejemplo real del mecanismo, no uno armado para la
ocasión: se mostró un plan de estructura, el usuario pidió dos ajustes (sumar
esta sección y la de capturas del final) antes de aprobar nada, y solo
después de la confirmación se creó la rama y se escribió el contenido.

![Plan y pregunta antes de crear la rama](assets/usage-plan-question.png)

## GitFlow, paso a paso

Con la confirmación en mano, así se ve una tarea de punta a punta:

1. **Antes de commitear**, tres chequeos corren solos: ¿el diff agrega algo
   que no está en `SPEC.md`? ¿la rama actual es `master`/`development` en vez
   de una propia? ¿el commit es `feat`/`fix` y no tocó `TODO.md`? Cualquiera
   de los tres avisa antes de seguir, no bloquea en silencio.
2. **Commit local**: el checkbox de `TODO.md` (`- [ ]` → `- [x]`), el código,
   y la línea de `CHANGELOG.md` (si el tipo del commit entra al changelog)
   viajan **siempre juntos**, con el formato
   `<tipo>: <descripción> (TODO: <texto exacto de la tarea>)`.
3. **Antes del `push`** — pausa explícita, siempre, sin importar el tamaño
   del cambio: se muestra un resumen (qué se hizo, qué archivos, resultado de
   tests) y se pregunta con opciones cerradas — Sí/No por rama, nunca una
   frase libre en el chat.
4. Push.
5. **Antes del `merge`** (`feature/*`/`fix/*` → `development`, o
   `development` → `master` en un release) — la misma pausa, el mismo
   mecanismo. Nunca se encadena commit → push → merge sin que el humano vea
   qué se está por integrar.
6. **Al mergear a `development`**: se corre el cálculo de versión —
   Conventional Commits, "el más alto gana" (MAJOR > MINOR > PATCH, nunca se
   apilan) — y se pregunta si taguear ahora o dejarlo para cuando se junten
   más cambios. Nunca se taguea sin que lo pidas.
7. **Si se decide el release**: mover `[Unreleased]` del changelog a la
   versión, actualizar el archivo de versión del paquete, commit
   `chore(release)`, tag, push del tag, publicar el Release, merge a la rama
   principal, y un chequeo de que esa rama quedó con el número correcto (no
   solo el tag).
8. **Cierre**: se listan las ramas ya mergeadas y se pregunta cuáles borrar,
   y se ofrece limpiar la sesión — el estado del trabajo vive en los
   archivos, no en la conversación.

Esto no es teórico: es exactamente lo que pasó en este mismo repo al cerrar
sus últimas dos versiones — se puede seguir en `git log --oneline` y en
`CHANGELOG.md`.

![Confirmación antes de pushear](assets/usage-push-confirm.png)

![Confirmación antes de mergear](assets/usage-merge-confirm.png)

![Cálculo de versión y pregunta de taguear](assets/usage-version-check.png)

![Qué ramas borrar y oferta de limpiar la sesión](assets/usage-branch-cleanup.png)

## `AskUserQuestion` — qué es y en qué momentos aparece

Es una confirmación con **opciones cerradas** (ej. "Sí, pushear" / "No,
todavía no"), no una pregunta abierta que se responde con un "dale" suelto en
el chat. La razón: una frase libre no distingue entre aprobar *solo* el push
y aprobar además el tag y el merge que suelen venir después — las opciones
cerradas sí. Aparece en puntos concretos, siempre los mismos:

- Antes de crear una rama nueva, cuando el plan lo requiere.
- Antes de cualquier `git push`.
- Antes de cualquier `git merge` (en cualquiera de los dos sentidos).
- Al decidir si se taguea una versión.
- Al borrar ramas ya mergeadas.
- Al ofrecer limpiar la sesión una vez cerrado el flujo.

En Claude Code, además, estas cuatro acciones (`push`, `merge`, `tag`, borrar
rama) quedan agregadas a `permissions.ask` de `.claude/settings.json` al
correr `rocky init --agent claude` — la regla no depende solo de que el
agente se acuerde de preguntar, Claude Code la exige aunque se olvide.

## TODO único vs. orquestador (`todos/`)

Un proyecto chico usa un solo `TODO.md`. Uno fullstack activo, o con
arquitectura Grande (Clean/Hexagonal), o de equipo/largo plazo, divide desde
el arranque en una carpeta `todos/` — un archivo por capa
(`dominio-db.md`, `api-backend.md`, `frontend-ui.md`) o por feature
(`login.md`, `checkout.md`), según cómo prefiera trabajar el equipo. En ese
modo, `TODO.md` pasa a ser un orquestador: conserva Setup/Calidad/Documentación
inline y agrega una tabla "Estado por grupo" con el progreso de cada archivo,
que se actualiza solo cuando se completa la **última tarea de un grupo
entero** — no en cada commit individual.

![Estructura de carpeta todos/ en modo orquestador](assets/usage-todo-orchestrator.png)

## Trazabilidad RF → US → RNF → tarea

`SPEC.md` numera tres tipos de requisito: `RF-N` (una feature), `US-N` (una
historia de usuario, que declara qué `RF-N` implementa), `RNF-N` (un
requisito no funcional, como performance o accesibilidad). Cada tarea del
TODO que resuelve una historia termina con su ID entre paréntesis —
`- [ ] Endpoint POST /login (US-1)`. Esto no es solo convención: `rocky check
qa` recorre la cadena completa y avisa si algo quedó suelto — un `RF-N` sin
ninguna `US-N` que lo implemente, una `US-N` sin ninguna tarea en el TODO, o
un `RNF-N` con un objetivo concreto (no el default) pero sin ningún trabajo
que lo aborde. Es código, no un LLM releyendo `SPEC.md` cada vez con la
esperanza de no saltearse nada.

## Otros checks deterministas

Los mismos que agrupa `rocky check` — tamaño de archivo y code smells,
secrets hardcodeados, error tracking y health endpoint, criterios básicos de
accesibilidad, y el cálculo de versión ya mencionado arriba. Corren como
código Python, no como instrucciones que un agente interpreta de nuevo en
cada sesión — el detalle completo de cada uno está en la tabla de comandos
del [README](README.md#health-checks-rocky-check).

## Capturas pendientes

Todavía no hay screenshots reales en este repo — solo el banner de
`assets/`. Las imágenes de arriba están referenciadas por nombre de archivo;
en cuanto se agreguen a `assets/` con esos nombres, se ven solas, sin tocar
este documento de nuevo.

| Archivo | Qué debería mostrar | Sección |
|---|---|---|
| `assets/usage-plan-question.png` | El plan de una tarea + la pregunta antes de crear la rama | Planificación |
| `assets/usage-push-confirm.png` | `AskUserQuestion` confirmando un `git push` | GitFlow |
| `assets/usage-merge-confirm.png` | `AskUserQuestion` confirmando un `git merge` | GitFlow |
| `assets/usage-version-check.png` | Salida de `rocky check version` + la pregunta de taguear | GitFlow |
| `assets/usage-branch-cleanup.png` | `AskUserQuestion` preguntando qué ramas borrar + oferta de limpiar sesión | GitFlow |
| `assets/usage-todo-orchestrator.png` | Estructura de carpeta `todos/` en el explorador de archivos | TODO orquestador |
