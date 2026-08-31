> Referencia de **charless-ia** — Pasos P6 y P7 del flujo de creación: archivos base del proyecto y TODO colaborativo.

### P6 · Genera archivos base

Crear, dentro del directorio del proyecto, copiando desde `.charless/templates/`:

**Rellenar la sección "Stack" y "Overview del proyecto" de `AGENTS.md`** con la tabla final de P3 (`{{FRONTEND}}`, `{{BACKEND}}`, `{{ORM_DB}}`, `{{STYLES}}`, `{{TESTING}}`, `{{OTHER_TOOLS}}`) y el tipo de proyecto de P1 (`{{PROJECT_TYPE}}`, `{{PROJECT_DESCRIPTION}}` — mismo texto que `SPEC.md` "Descripción", no reescribir). Si alguna capa no aplica (ej. proyecto sin backend), completar con "—", no dejar el placeholder ni inventar un valor.

**Código / híbrido**:
- `CONSTITUTION.md` (desde `CONSTITUTION.md.template` — principios inmutables: código, seguridad, arquitectura, boundaries)
- `SPEC.md` (desde `SPEC.md.template`, con lo definido en P1.7 — SDD nivel Spec-Anchored)
- `AGENTS.md` (desde `AGENTS.md.template`, rellenado con el stack, arquitectura y convenciones elegidos — instrucciones universales para cualquier agente)
- `CLAUDE.md` (desde `CLAUDE.md.template`, importa `AGENTS.md` + roles de expertise)
- `SECURITY.md` (desde `SECURITY.md.template`, con las decisiones de P5.6 — ver `.charless/commands/p5.6-security.md`)
- `OBSERVABILITY.md` (desde `OBSERVABILITY.md.template`, con las decisiones de P5.7 — ver `.charless/commands/p5.7-observability.md`)
- `CHANGELOG.md` (desde `CHANGELOG.md.template`, formato Keep a Changelog + SemVer — ver `.charless/reference/versioning.md`)
- `LICENSE` (desde `LICENSE-mit.template` / `LICENSE-apache2.template` / `LICENSE-proprietary.template` según lo elegido — ver "Licencia" más abajo)
- `README.md` (desde `README.md.template`)
- `TODO.md` (desde `TODO.md.template`, vacío salvo encabezados)

**Creativo**:
- `BRIEF.md` (desde `BRIEF.md.template`)
- `prompts.md` (desde `prompts.md.template`)
- `STORYBOARD.md` (desde `STORYBOARD.md.template`)
- `CLAUDE.md`, `AGENTS.md`, `README.md`, `TODO.md` (también — sin `SPEC.md`, salvo que el proyecto creativo tenga lógica de negocio, ver P1.7)
- `LICENSE` — solo si el usuario lo pide explícitamente (un proyecto creativo no siempre necesita una licencia de software)

Además crear las carpetas según la arquitectura de P4.

#### Licencia

Antes de generar los archivos, si no se preguntó ya, una sola pregunta liviana (no amerita un paso P propio):

```
¿Qué licencia usamos?
1) MIT — permisiva, la más común en open source (default)
2) Apache 2.0 — permisiva + protección explícita de patentes
3) Propietaria — privado, no redistribuible
4) Ninguna todavía — proyecto interno/descartable, se decide después
```

**Default sin preguntar** si ya hay señal clara: el usuario dijo "open source" o "quiero publicarlo" → MIT. El usuario dijo "interno", "privado", "de la empresa" → Propietaria. Si no hay señal → preguntar.

Generar `LICENSE` copiando `.charless/templates/LICENSE-mit.template` / `LICENSE-apache2.template` / `LICENSE-proprietary.template` según lo elegido (opción 4 → no generar el archivo). Completar `{{YEAR}}` (año actual) y `{{COPYRIGHT_HOLDER}}` (nombre del usuario o de su organización, de `~/.claude/profile.md` si está — si no, preguntar una vez y no de nuevo en futuros proyectos si se puede guardar en el perfil).

Rellenar el placeholder `{{LICENSE}}` de `README.md` con una línea corta, **no** el texto completo de la licencia:
> "MIT — ver [`LICENSE`](./LICENSE)" (o el nombre correspondiente; si se eligió opción 4, dejar "Sin licencia definida todavía")

**Reglas base — siempre activas, no dependen del perfil** (ver `.charless/reference/coding-principles.md` sección "Reglas base — no son opt-in"):

- **Etiquetas semánticas HTML** (solo proyectos con interfaz visual): usar `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>` en vez de `<div>` genérico cuando la semántica del contenido lo permite. Jerarquía de headings sin saltos (`<h1>`→`<h2>`→`<h3>`). Mejora SEO (los buscadores entienden la estructura) y accesibilidad (landmarks para lectores de pantalla).
- **Sin estilos inline** (solo proyectos con interfaz visual): orden de prioridad — (1) clases del framework/librería del stack elegido (Tailwind, Bootstrap, etc.), (2) sistema de estilos del framework (CSS Modules, styled-components), (3) si el stack es HTML/CSS/JS vanilla sin sistema de clases, crear un archivo `.css` propio y enlazarlo. Nunca `style="..."` ni `style={{}}`, salvo valores dinámicos calculados en runtime.
- **Límite de tamaño de archivo** (cualquier proyecto de código): al generar scaffolding, no crear archivos que ya nazcan grandes. Si un archivo (componente de formulario complejo, servicio con muchos métodos) va a superar el umbral "revisar" de la tabla en `coding-principles.md`, generarlo ya dividido desde el arranque (subcomponentes, hook custom, archivo de tipos separado) en vez de esperar a que crezca.
- **Separar tipos/interfaces** (lenguaje tipado — TS, Python con type hints, Go, Rust): si la entidad del dominio definida en P1.7 tiene 2+ campos o se comparte entre capas, generar el archivo de tipos separado (`<entidad>.types.ts`, `types/`, `schemas.py`, etc.) desde el arranque, no mezclado con la lógica de implementación.

Si el usuario pide explícitamente desactivar alguna de estas para el proyecto puntual, confirmar antes de aplicar el cambio (ver wording sugerido en `coding-principles.md`).

**Principios de código del perfil** (opt-in, ver `.charless/reference/coding-principles.md`): cuando la skill genera código de scaffolding (componentes ejemplo, configs, archivos base), respetar los principios activos del perfil:

- Si "Early returns" está activo → el código generado usa early returns en vez de pirámides de `if`.
- Si "Tipado explícito" está activo y es TS → tipos explícitos en props y returns, evitar `any`.
- Si "Funciones < 30 líneas" está activo → no generar funciones largas; partir en helpers.
- Si "Logs estructurados" está activo → usar `logger.info({ key: val })` en vez de `console.log("texto")`.
- Siempre (no es opt-in) → evitar introducir los code smells del catálogo de `coding-principles.md` (magic numbers, listas de parámetros largas, God File, etc.) en el código de scaffolding.

**Generar `CONSTITUTION.md`** usando `.charless/templates/CONSTITUTION.md.template` (los principios SOLID/DRY/KISS/YAGNI/Clean Code, code smells, y reglas base de seguridad ya vienen escritos — no son placeholders, aplican siempre). Solo completar:
- `{{RATIFICATION_DATE}}` con la fecha de hoy (y `{{LAST_AMENDED_DATE}}` igual, es la primera versión).
- `{{ARCHITECTURE_NAME}}` con la arquitectura elegida en P4.
- `{{ACTIVE_PATTERNS}}` con los patrones relevantes según esa arquitectura (ej. Repository, Factory, Observer, Strategy). Si el perfil tiene patrones activos, incluirlos también.
- `{{STYLE_TECH}}` con la tecnología de estilos elegida (Tailwind / styled-components / CSS Modules / etc.).
- `{{LOCKFILE_NAME}}` (Artículo 8) con el lockfile real del stack (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`) — mismo valor que se usa en `AGENTS.md`, no volver a preguntar.
- `{{LOCAL_OVERRIDE_*}}` dejar vacío salvo que el usuario haya pedido explícitamente romper alguna regla — en ese caso, no alcanza con completarlo en silencio: confirmar con el usuario que quiere ratificar esa excepción antes de guardarla (ver "Cómo enmendar" en el propio archivo).

**Rellenar `{{ACTIVE_PATTERNS}}` en `AGENTS.md`** (sección "Code style — boundaries", que ahora es solo un puntero a `CONSTITUTION.md` + los patrones activos) con el mismo valor que se usó arriba.

**Rellenar "Decisiones del setup" de `AGENTS.md`**:
- `{{ARCHITECTURE_DECISION_RATIONALE}}`: la síntesis guardada en P4 (Paso 3) — 1-2 líneas, no la explicación completa que ya se mostró en el chat.
- `{{TDD_DECISION}}`: la respuesta guardada en P3 ("Sí — ciclo Red→Green→Refactor, ver `.charless/reference/methodologies.md`" o el default "No — tests después de implementar").
- Ítem libre adicional solo si hubo alguna otra decisión no trivial (ej. plataforma de deploy elegida por una razón específica, no solo el default) — si no hubo ninguna, omitir la línea en vez de dejar un placeholder vacío.

**Rellenar el `AGENTS.md` generado con la sección "Infraestructura de deploy"** (datos de P5.5):
- `{{DOCKER}}` → "sí (Dockerfile + docker-compose.yml generados)" | "no" | "pendiente (tarea en TODO)"
- `{{DEPLOY_PLATFORM}}` → nombre de la plataforma elegida | "pendiente"
- `{{CICD}}` → "CI básico (.github/workflows/ci.yml)" | "CI/CD completo" | "no configurado"
- `{{INFRA_CONFIG_FILE}}` → nombre del archivo generado (render.yaml, fly.toml, etc.) | "—"

**Rellenar el `AGENTS.md` generado con la sección "Spec Drift Check"** (usa el stack real elegido en P2/P3):

1. `{{ORM_DB}}` → nombre del ORM/DB elegido (ej. "Prisma", "SQLAlchemy") | "—" si el proyecto no tiene DB.
2. **Si el proyecto no tiene backend** (frontend-only) o **no tiene DB** (backend sin persistencia) → el placeholder correspondiente se completa directo con `echo "# no aplica — este proyecto no tiene backend/DB"`, sin pasar por los pasos siguientes. No es una limitación de la skill, es que no hay nada que chequear.
3. Para el resto, buscar el backend y el ORM/DB de este proyecto en las tablas de `.charless/reference/stacks-code.md` sección "Patrones de detección — Spec Drift Check".
4. **Si están en la tabla** → usar ese patrón directo: `{{ROUTE_DRIFT_CHECK_COMMAND}}` / `{{DB_DRIFT_CHECK_COMMAND}}` se completan como `git diff --staged | grep -E "^\+.*<patrón de la tabla>"`.
5. **Si NO están en la tabla** (framework nuevo, poco común, o directamente no está cargado todavía) → no deshabilitar de entrada. Derivar el patrón ahí mismo, igual que se razonaría para explicarle a alguien cómo se ve una ruta o un modelo en ese framework (ej. si es Elysia: `.get(`/`.post(` sobre una instancia de `new Elysia()`; si es tRPC: `.query(`/`.mutation(` dentro de un router). Usar ese patrón derivado para completar el placeholder.
   - Mostrarle al usuario el patrón antes de guardarlo: *"No tenía un patrón de detección para [framework] todavía — armé este basado en su sintaxis de rutas: `<patrón>`. ¿Lo agrego a `stacks-code.md` para que quede disponible en tus próximos proyectos con este stack?"*
   - Si confirma → agregar la fila a la tabla correspondiente de `.charless/reference/stacks-code.md` (mismo formato que las existentes). La tabla crece con el uso real, igual que `project-patterns/` con los patterns de proyecto completo.
   - Si prefiere no guardarlo → usar igual el patrón derivado para este proyecto puntual, simplemente no persistirlo en la tabla.
6. **Solo si Claude no tiene confianza real en la sintaxis** del framework elegido (algo muy nuevo o muy de nicho) → ahí sí, en vez de inventar un patrón poco confiable, dejarlo explícito: `echo "# deshabilitado — no pude derivar un patrón confiable para este stack, avisá si tenés un ejemplo de ruta/modelo para armarlo"`. Esto debería ser la excepción, no el default.

Si alguno quedó realmente deshabilitado (paso 6), avisar al cerrar P6 (una sola línea, no hace falta un bloque aparte):
> "El Spec Drift Check de [rutas|tablas] queda desactivado en este proyecto — no tengo certeza de la sintaxis de {{BACKEND}} / {{ORM_DB}} como para armar un patrón confiable. Si me pasás un ejemplo de una ruta o un modelo ya escrito, lo armo."

**Rellenar la sección "Gestión de dependencias" de `AGENTS.md`**: `{{LOCKFILE_NAME}}` con el lockfile real del stack (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`). `{{DEPENDENCY_UPDATE_CADENCE}}` y `{{LICENSE_COMPLIANCE_NEEDED}}` quedan en su default salvo que el proyecto sea explícitamente una librería/paquete a publicar u open source (ahí sí, `{{LICENSE_COMPLIANCE_NEEDED}}` pasa a "sí").

**Rellenar `OBSERVABILITY.md`**: con las decisiones de P5.7 (`{{OBSERVABILITY_SCALE}}` — mismo dato que `{{SECURITY_SCALE}}` de P5.6, es una sola escala para todo el proyecto — y el resto de placeholders con lo confirmado en esa pantalla). `{{DATE}}`/`{{INITIAL_COMMIT}}` del Historial de cambios, igual que el resto de documentos vivos.

**Rellenar `CHANGELOG.md`**: `{{DATE}}` con la fecha de hoy, `[Unreleased]` queda vacío (se llena a partir del primer commit real, ver `AGENTS.md` sección "Workflow de Git" paso 1-bis). La versión `[0.1.0]` inicial representa el setup del proyecto — no hace falta tagear todavía, eso se decide en el primer release real.

**Rellenar `TODO.md`** (el modo — único u orquestador — se decide en P7, ver esa sección para el criterio completo; acá van los datos una vez decidido):
- Modo único: descomentar Docker/CI en "Infraestructura / Deploy" según corresponda, reemplazar `{{DEPLOY_PLATFORM}}`, completar `{{SECURITY_TODO_ITEMS}}` en la sección "Seguridad" con lo de P5.6 Paso 5, y `{{OBSERVABILITY_TODO_ITEMS}}` en la sección "Observabilidad" con lo de P5.7 Paso 5.
- Modo orquestador: esos mismos ítems van en `todos/infraestructura-deploy.md`, `todos/seguridad.md` y `todos/observabilidad.md` respectivamente (generados con `.charless/templates/todo-group.md.template`), y `TODO.md` solo lleva la tabla "Estado por grupo" con el conteo de cada uno.

### P7 · TODO colaborativo

Ofrecer 4 modos al usuario:

- **A · Manual** — el usuario dicta, Claude solo escribe.
- **B · Colaborativo** (default recomendado) — back-and-forth, Claude sugiere si dudás.
- **C · Auto** — Claude propone un TODO completo basado en el tipo de proyecto + arquitectura, el usuario aprueba o edita.
- **D · Skip** — queda vacío, el usuario lo completa después.

Si el `profile.md` tiene `default_todo_mode` seteado, usarlo sin preguntar.

Si el usuario elige B o C, el TODO debe tener **secciones mínimas**: `Setup`, `Features iniciales` (organizadas por capa o por feature, ver más abajo), `Calidad (tests/lint)`, `Documentación`, `Infraestructura / Deploy`, `Seguridad`. Cada ítem en formato `- [ ] Tarea`. Para creativo: `Brief`, `Referencias`, `Prompts`, `Frames`, `Edit`, `Exports`.

#### Trazabilidad de requisitos

`SPEC.md` numera tres tipos de requisito: `RF-N` (feature), `US-N` (historia — implementa un `RF-N`), `RNF-N` (no funcional). Cada tarea que implementa una historia termina con su ID entre paréntesis: `- [ ] Endpoint POST /login (US-1)`. Una tarea puede referenciar más de una historia (`(US-1, US-3)`) si aplica a ambas, y sumar un `RNF-N` si además existe específicamente para cumplir un requisito no funcional (`(US-4, RNF-1)` para una tarea de caché que cumple un objetivo de performance). Tareas de infraestructura/setup/calidad sin requisito asociado (ej. "Configurar linter") no llevan ID — no todo tiene por qué venir de un requisito.

No hace falta taguear con `RF-N` directamente en el TODO — alcanza con `US-N`, porque cada historia ya declara en `SPEC.md` de qué `RF-N` sale (`US-1 (implementa RF-1)`). Taguear ambos en la tarea sería redundante.

Esto responde directamente "¿qué tareas implementan este requisito?" con un grep por `RF-N`/`US-N`/`RNF-N` sobre `SPEC.md` + el TODO (o `todos/` si el proyecto usa el modo orquestador) — sin mantener una tabla de mapeo aparte que se puede desincronizar.

Al armar el TODO en B o C, ir asignando el ID correspondiente a cada tarea a medida que se deriva de un requisito — no es un paso extra al final, es parte de escribir la tarea.

#### Organización de "Features iniciales" — ¿por capas o por features?

Hay dos formas válidas de ordenar el trabajo, y no dependen del tamaño del proyecto sino de **cómo va a trabajar el equipo**. Preguntar siempre que el proyecto sea fullstack o backend con DDD (si es frontend puro o backend sin capas distintas, esta pregunta no aplica — hay una sola forma natural de ordenar):

```
¿Cómo organizamos el desarrollo de las features?

1) Por capas (Dominio/DB → Backend → Frontend)
   Se completa toda una capa antes de pasar a la siguiente. Ideal si hay
   personas distintas para backend y frontend — una vez que el contrato de
   API está en SPEC.md, cada una avanza en su capa en paralelo sin
   pisarse. Contras: no hay nada visible en pantalla hasta que el
   backend de esa parte esté listo.

2) Por features (cada tarea = una historia de punta a punta)
   Cada tarea toca lo que haga falta de dominio + backend + frontend
   para esa historia puntual, de principio a fin. Ideal para un
   desarrollador fullstack solo, o un equipo chico donde la misma
   persona toca todas las capas. Progreso visible desde la primera
   tarea — a cambio, exige más disciplina para no diseñar la DB en
   base a lo que la primera pantalla necesita (ver DDD en
   .charless/reference/methodologies.md).
```

**Default sugerido** (no obliga, solo orienta la pregunta): si el usuario mencionó equipo o roles separados (mismo criterio que "proyecto de equipo" de la sección siguiente) → sugerir **por capas**. Si es un desarrollador individual o mencionó que va a tocar todo el stack → sugerir **por features**.

Si `profile.md` tiene `default_build_order` seteado (`layers` | `features`), usarlo sin preguntar — salvo que el usuario pida explícitamente cambiarlo para este proyecto puntual.

**Por capas** → las tareas de "Features iniciales" (o los archivos de `todos/` en modo orquestador) se agrupan en `Dominio / Base de datos` → `API / Backend` → `Frontend / UI`, en ese orden (ver razonamiento DDD en `.charless/reference/methodologies.md`).

**Por features** → cada historia de usuario (`US-1`, `US-2`...) es su propio grupo de tareas, sin importar qué capas toque cada una — el grupo se llama como la feature, no como una capa (ej. "Login", "Checkout", no "Backend").

#### ¿TODO único o dividido — y por qué eje?

Un `TODO.md` con todas las secciones inline funciona bien al principio, pero en un proyecto fullstack activo puede terminar siendo el mismo problema de God File que ya resolvimos para código (ver `.charless/reference/coding-principles.md` sección "Tamaño de archivo") — solo que en la documentación. La skill usa el mismo criterio de tamaño de archivo Markdown (`.charless/reference/coding-principles.md`: ideal <500 líneas, dividir sí o sí a partir de 500) aplicado de forma **proactiva**, no solo reactiva.

**Dividir desde el arranque (crear carpeta `todos/`) si se cumple cualquiera de estas:**
- El proyecto es **fullstack** (tiene frontend y backend) — casi siempre implica 2+ grupos con tareas propias que crecen de forma independiente.
- La arquitectura elegida en P4 es **Grande** (Clean/Hexagonal) — señal de dominio complejo y proyecto de larga vida.
- El usuario menciona que es un proyecto de equipo o de largo plazo.

**Si no se cumple ninguna** (Mini/Chico, una sola capa, arquitectura no Grande): un solo `TODO.md`, sin carpeta `todos/`. No dividir el TODO de una landing page.

**Mecanismo de split** (si aplica) — el contenido de cada archivo sale de la elección de la pregunta anterior:

1. Crear `todos/` en la raíz del proyecto.
2. Generar un archivo por grupo usando `.charless/templates/todo-group.md.template`:
   - **Si se eligió por capas**: `todos/dominio-db.md`, `todos/api-backend.md`, `todos/frontend-ui.md` — solo las que el proyecto realmente tiene.
   - **Si se eligió por features**: `todos/<feature-slug>.md` — uno por historia de usuario o grupo de historias relacionadas (ej. `todos/login.md`, `todos/checkout.md`), con slug en minúsculas y guiones.
   - En ambos casos, además: `todos/infraestructura-deploy.md` (si el proyecto va a producción), `todos/seguridad.md` (si P5.6 generó ítems de checklist), y `todos/observabilidad.md` (si P5.7 generó ítems pendientes).
3. `TODO.md` se convierte en el **orquestador**: conserva `Setup`, `Calidad`, `Documentación` inline (son acotadas, no crecen indefinidamente) y agrega una tabla de estado en vez de la sección "Features iniciales" completa:

   ```markdown
   ## Estado por grupo

   <!-- Ejemplo modo "por capas" -->
   | Grupo | Progreso | Archivo |
   |---|---|---|
   | Dominio / Base de datos | {{DOMAIN_DONE}}/{{DOMAIN_TOTAL}} | `todos/dominio-db.md` |
   | API / Backend | {{BACKEND_DONE}}/{{BACKEND_TOTAL}} | `todos/api-backend.md` |
   | Frontend / UI | {{FRONTEND_DONE}}/{{FRONTEND_TOTAL}} | `todos/frontend-ui.md` |
   | Infraestructura / Deploy | {{DEPLOY_DONE}}/{{DEPLOY_TOTAL}} | `todos/infraestructura-deploy.md` |
   | Seguridad | {{SECURITY_DONE}}/{{SECURITY_TOTAL}} | `todos/seguridad.md` |

   <!-- Ejemplo modo "por features" -->
   | Grupo | Historias | Progreso | Archivo |
   |---|---|---|---|
   | Login | US-1 | {{DONE}}/{{TOTAL}} | `todos/login.md` |
   | Checkout | US-2, US-3 | {{DONE}}/{{TOTAL}} | `todos/checkout.md` |
   | Infraestructura / Deploy | — | {{DONE}}/{{TOTAL}} | `todos/infraestructura-deploy.md` |
   | Seguridad | — | {{DONE}}/{{TOTAL}} | `todos/seguridad.md` |
   ```

   Omitir las filas de grupos que el proyecto no tiene (ej. sin backend → no hay fila de API/Backend ni de Dominio/DB).

4. El commit de cada tarea sigue tocando **un solo archivo de grupo** (no el orquestador) — la tabla del orquestador se actualiza solo cuando se completa la **última tarea de un grupo entero** (mismo trigger que README sync, ver abajo), no en cada commit individual. Esto evita que cada tarea chica obligue a tocar dos archivos.

**Split diferido (proyecto que arrancó simple y creció):** el `AGENTS.md` de cada proyecto incluye un **TODO Size Check** (paso 0-bis del Workflow de Git, junto al Spec Drift Check) que avisa cuando `TODO.md` se acerca al umbral — en ese momento se puede migrar a `todos/` con este mismo mecanismo, moviendo las tareas ya existentes por grupo en vez de perderlas. Preguntar en ese momento (si no se preguntó antes) por capas o por features, con el mismo criterio de arriba.

Completar los placeholders de `AGENTS.md`: `{{TODO_MODE_LAYOUT}}` con "único" o "orquestador con `todos/`", y `{{BUILD_ORDER}}` con "por capas" o "por features", según lo que se haya decidido acá.

Si el usuario no tenía `default_build_order` en `profile.md` y eligió explícitamente una opción (no fue un caso donde la pregunta no aplicaba), preguntar si quiere guardarla como default para futuros proyectos:
> "¿Guardo 'por [capas/features]' como tu preferencia default para el orden de desarrollo, así no te lo vuelvo a preguntar en cada proyecto?"

#### Convención: README sync al completar secciones

El `TODO.md.template` y el `AGENTS.md.template` incluyen la tabla de mapeo de secciones a README, pero avisarle al usuario explícitamente al cerrar P7 (salvo modo D):

> "Otra regla que quedó en `AGENTS.md`: cuando se completa el **último checkbox de cada sección del TODO** (Setup, Features, Calidad, Deploy, Docs), Claude actualiza la sección correspondiente del README e incluye ese cambio en el mismo commit. Así el README siempre refleja el estado real del proyecto — no quedá desactualizado."

#### Convención: 1 tarea completada = 1 commit + push

El `TODO.md.template` y el `AGENTS.md.template` ya incluyen esta regla, pero avisarle al usuario explícitamente al cerrar P7 (salvo que haya elegido modo D):

> "Una convención que quedó configurada en `AGENTS.md`: cada vez que completes una tarea del TODO, marcá el checkbox y hacé commit + push **en el mismo paso** — checkbox y código siempre van juntos en el mismo commit, con el formato `tipo: descripción (TODO: texto de la tarea)`. Así cualquier agente futuro en este proyecto (Claude Code u otro) va a seguir esa regla automáticamente, tu TODO.md queda siempre sincronizado con lo que realmente está hecho, y el historial de git funciona como registro de qué tarea se resolvió en cada commit."

Si el usuario prefiere no aplicar esta convención (por ejemplo, ya tiene su propio flujo de commits), preguntar:
> "¿Querés que la quite de AGENTS.md, o la dejamos como sugerencia y vos decidís si la seguís?"

Si pide quitarla, borrar la sección "Workflow de Git" del `AGENTS.md` generado y la nota del `TODO.md`.

