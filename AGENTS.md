# rocky-spec

> Este archivo sigue el estándar abierto [AGENTS.md](https://agents.md/) — instrucciones agnósticas de herramienta para cualquier agente de código (Codex, Cursor, Copilot, Gemini CLI, Windsurf, OpenCode, Claude Code, etc.). Es la fuente de verdad para stack, comandos, convenciones y el flujo de spec de este proyecto.
>
> `CLAUDE.md` importa este archivo para Claude Code. Si trabajás con otro agente, este archivo solo debería ser suficiente.

## Overview del proyecto

- **Nombre**: rocky-spec
- **Tipo**: Código — CLI / herramienta de desarrollo (sin frontend, sin persistencia) (código | creativo | híbrido)
- **Descripción**: Toolkit multi-agente de Spec-Driven Development, nivel Spec-Anchored. Ver SPEC.md.
- **Generado por**: skill `rocky-spec` — ver `CONSTITUTION.md` (reglas que no se negocian), `SPEC.md` (qué se construye), `TODO.md` (qué falta), `SECURITY.md` (decisiones y checklist de seguridad), `OBSERVABILITY.md` (cómo saber si esto está funcionando en producción)

## Stack

- **Frontend**: no aplica — es un CLI
- **Backend**: Python 3.9+ (click para el CLI)
- **ORM / DB**: no aplica — no hay persistencia
- **Estilos**: no aplica
- **Testing**: pytest
- **Otros**: hatchling (build backend)

## Infraestructura de deploy

- **Docker**: no aplica — se distribuye como paquete Python, no como contenedor  <!-- sí (Dockerfile + docker-compose.yml) | no | pendiente -->
- **Plataforma**: PyPI (pendiente — hoy se instala en modo editable)  <!-- Render | Railway | Fly.io | Vercel | AWS | GCP | Azure | pendiente -->
- **CI/CD**: no configurado todavía  <!-- CI básico | CI/CD completo | no configurado -->
- **Archivo de config**: —  <!-- render.yaml | fly.toml | .github/workflows/ci.yml | etc. -->
- **Variables de entorno**: `.env.example` generado — completar valores reales antes del primer deploy

> Las variables de entorno nunca van al repo. `.env` está en `.gitignore`. Los secrets de producción se configuran en el panel de la plataforma elegida (o en GitHub Secrets si usás CI/CD).

## Arquitectura

Plugin registry (Mediano — feature-based)

Resumen de la estructura:

```
rocky-spec/
├── pyproject.toml
├── README.md / LICENSE / CHANGELOG.md
├── src/rocky_spec/
│   ├── cli.py                (comandos: init, check, list-integrations)
│   ├── scaffold.py            (copia el conocimiento a .rocky-spec/)
│   ├── integrations/          (base.py, claude.py, cursor.py, registry)
│   ├── scripts/                (render_template, health_check, qa_review)
│   ├── commands/                (14 pasos del ciclo de vida, agnósticos de agente)
│   ├── reference/                (17 documentos de principios/metodologías)
│   └── templates/                 (18 plantillas de archivos generados)
└── tests/
```

## Decisiones del setup

> El **qué** se eligió (stack, arquitectura) está arriba. Acá va el **por qué** — el razonamiento y los trade-offs que se conversaron al armar el proyecto, para que no se pierdan apenas termina la sesión de setup.

- **Arquitectura**: Registry de plugins para que agregar un agente nuevo (Windsurf, Copilot, Gemini, Codex) no requiera tocar el conocimiento compartido ni las integraciones existentes — mismo principio que separar SPEC.md/AGENTS.md/CONSTITUTION.md por audiencia. <!-- por qué esta y no otra — mismas razones mostradas en P4, no repetir la explicación completa, solo la síntesis -->
- **TDD**: "No — tests se escriben después de implementar, ver Testing en CLAUDE.md" <!-- decisión explícita de P3, nunca inferida -->
- El conocimiento (commands/reference/templates) vive en .rocky-spec/ DENTRO del proyecto destino, no en el paquete del CLI — así viaja versionado con el código del usuario, no solo en su instalación global. <!-- cualquier otra decisión no trivial tomada en el setup — ej. por qué esta plataforma de deploy y no otra, si hubo alternativas descartadas -->

## Convenciones específicas de este repo

- Naming: snake_case para módulos y funciones Python, kebab-case para el nombre del paquete
- Commits: Conventional Commits (feat/fix/docs/test/chore)
- Branches: GitFlow simplificado — main / dev / feature/* / fix/*, ver sección "Branching" abajo
- Todo el conocimiento (commands/reference/templates) en español; el código Python (nombres de funciones/variables/docstrings de una línea) en inglés cuando es más natural, comentarios largos en español

## Code style — boundaries

Los principios de código, seguridad, tamaño de archivo, y las reglas de "preguntar primero"/"nunca" que gobiernan este proyecto **no viven acá** — viven en **`CONSTITUTION.md`**, porque son las reglas que casi nunca cambian (a diferencia de este archivo, que es más operativo y sí evoluciona). Leer `CONSTITUTION.md` antes de tocar código en este proyecto.

**Patrones activos de este proyecto** (según arquitectura elegida en setup — el detalle de por qué está en `CONSTITUTION.md` Artículo 5):
- Registry / Plugin, Adapter  <!-- ej. Repository, Factory, Observer, Strategy -->

## Comandos útiles

```bash
# Dev
pip install -e . && rocky --help

# Test
python3 -m pytest tests/ -v

# Lint
no configurado todavía

# Build
python3 -m build
```

## Gotchas / cosas a recordar

- (vacío al inicio, agregar acá problemas conocidos y workarounds)

## Cuando un arreglo no funciona dos veces seguidas — protocolo anti-loop

**El síntoma:** se aplica un fix, el usuario reporta que el problema sigue, se aplica otro fix de la misma familia, sigue. Cada intento se siente razonable por separado, pero el conjunto es un loop: se está variando un parámetro (una fuente, una librería, un valor) sin haber verificado nunca la hipótesis de fondo.

**Umbrales escalonados** (mismo patrón que el TODO Size Check y el aviso de fixes acumulados de `rocky check version`):

- **1 intento fallido**: normal, seguir.
- **2 intentos fallidos sobre el mismo síntoma** 🟡: parar de aplicar variantes. El tercer paso **no** es otro fix — es un experimento diseñado para *observar* el fenómeno.
- **3+ intentos fallidos** 🔴: la hipótesis de trabajo está mal, no incompleta. Decirlo explícitamente al usuario, listar qué se probó y qué se descartó, y proponer cambiar el método de diagnóstico (no la solución).

**Reglas concretas:**

1. **Prohibido cerrar el diagnóstico en algo que no se puede medir.** "Es el renderizado de la terminal", "es la fuente del usuario", "es un tema del entorno" son **hipótesis sin verificar**, no conclusiones. Antes de aceptar una causa externa, hay que construir una forma de observar el fenómeno desde el código (capturar la salida real a un buffer, escribir a un archivo, medir posiciones/bytes). Si no se puede observar, no se puede afirmar.
2. **Verificar la capa correcta.** Si un test pasa en verde mientras el bug está presente, el test está mirando la capa equivocada — típicamente la **entrada** (el string que se construyó) en vez de la **salida** (lo que realmente se renderizó/escribió/devolvió). El bug vive entre las dos.
3. **Un test de regresión no vale nada hasta verlo fallar.** Antes de dar por bueno el fix, aplicar temporalmente el código con el bug y confirmar que el test nuevo falla. Si nunca falló, no prueba nada.
4. **Aislar variables de a una.** Cambiar fuente + librería + mecanismo en la misma iteración hace imposible saber qué movió la aguja. Si ya se cambiaron varias cosas, volver atrás a una base conocida antes de seguir.
5. **La contra-hipótesis del usuario es dato, no ruido.** Si el usuario insiste en que la causa es otra ("probá alineado a la izquierda", "eso no tiene que ver"), tratarlo como una hipótesis a testear explícitamente, no como algo a refutar con más argumentos. Suele conocer su entorno mejor que el agente.
6. **Documentar la causa real, no la secuencia de intentos.** En `CHANGELOG.md` va qué era y cómo se arregló; el ida y vuelta queda en el historial de commits.

> **Caso de referencia** (v0.8.0 → v0.10.x, banner del welcome): cinco cambios de fuente y dos de librería, con el diagnóstico cerrado en "es el renderizado de Warp". La causa real era que Rich descarta los espacios finales al centrar cada línea de un `Text` con `justify="center"`, ignorando el `ljust` de relleno. Se destrabó capturando el render a un buffer y midiendo el margen de cada fila — un experimento de observación, no otro fix.

## Agregar o modificar código — flujo de iteración (Plan → Confirmar → Implementar)

> **Spec-Anchored** es uno de los niveles reconocidos de Spec-Driven Development (junto a Spec-First y Spec-as-Source — ver `.rocky-spec/reference/methodologies.md` de la skill para el detalle). Significa que `SPEC.md` es un documento **vivo**: se actualiza en cada cambio de alcance, no solo una vez al principio del proyecto.

**Regla ampliada — no negociable:** ante **cualquier** pedido de cambio (feature nueva o corrección), el código nunca se toca en el mismo paso en que se recibe el pedido. Primero se decide si afecta el alcance de `SPEC.md`, después se muestra un plan breve, y recién con **confirmación explícita del usuario** se implementa. Nunca "aprovechar" que ya se entendió el pedido para adelantar el código — eso es exactamente lo que este flujo existe para evitar.

### Paso 1 — ¿Este pedido cambia el alcance de SPEC.md?

- **Sí** — es una feature nueva, cambia comportamiento ya documentado, agrega/quita una entidad de dominio, o cambia un requisito no funcional. Frases típicas: "quiero agregar X", "vamos a incorporar Y", "quitemos Z", "que también haga...".
  → Ir al **Paso 2a**.
- **No** — es una corrección puntual que no cambia lo que `SPEC.md` ya dice que el sistema debe hacer (el comportamiento esperado ya estaba documentado o implícito, y el código no lo cumplía).
  → Ir al **Paso 2b**.

Si hay duda real sobre cuál de los dos es, preguntar antes de asumir — es más barato confirmar acá que deshacer un cambio de alcance no documentado.

### Paso 2a — Si cambia el alcance: actualizar SPEC.md primero, después mostrar el plan

```
1. SPEC.md primero
   └── Agregar / quitar la feature en la tabla de prioridades (P0/P1/P2) con su RF-N
   └── Agregar / quitar user stories (US-N) referenciando el RF-N que implementan
   └── Actualizar criterios de aceptación del MVP y, si aplica, los RNF-N afectados

2. Dominio (si la feature toca entidades o reglas de negocio)
   └── Actualizar diagrama de entidades en SPEC.md
   └── Actualizar DB schema en SPEC.md (agregar/modificar/eliminar tabla o columna)
   └── Actualizar API contracts si cambian endpoints

3. Mostrar el plan de implementación técnica — QUÉ se va a tocar, en qué archivos,
   en qué orden (Dominio/DB → API → Frontend, o por feature si el proyecto usa ese
   modo). NO implementar todavía.

4. Esperar confirmación explícita del usuario.
```

**Recién con la confirmación**, commitear la documentación (`docs: agregar feature X — spec y dominio actualizados`) y pasar al Paso 3 de este documento (Implementar).

### Paso 2b — Si NO cambia el alcance: mostrar el plan sin tocar SPEC.md ni código

```
1. Describir en 3-5 líneas: qué se va a cambiar, en qué archivo(s), y por qué
   esto corrige el comportamiento sin alterar lo que SPEC.md ya documenta.
2. Terminar con una pregunta explícita — "¿Avanzo con esto?" o equivalente.
3. Esperar la respuesta. No continuar en el mismo turno asumiendo que sí.
```

Si en el camino de implementar la corrección se descubre que en realidad **sí** hay un cambio de alcance escondido (el bug era, en el fondo, un requisito mal documentado), pausar y volver al Paso 1 — no seguir de largo.

### Paso 3 — Implementar (solo después de la confirmación, cualquiera de los dos caminos)

```
└── Antes de tocar código: ver "Branching — GitFlow simplificado" más abajo —
    ¿estás en una rama feature/fix, o hay que crear una?
└── Seguir el orden acordado en el plan (Dominio/DB → API → Frontend, o por feature)
└── Cada tarea = 1 commit + push (según la convención de git de este proyecto)
```

### Formato del commit de documentación

```
docs: agregar feature [nombre] — SPEC y dominio actualizados
docs: quitar feature [nombre] — SPEC simplificado
docs: modificar dominio — [entidad] ahora tiene [cambio]
```

### Por qué este orden importa

Si el código va antes que la spec, en 2 semanas el SPEC.md refleja lo que se pensó al principio, no lo que se construyó. El dominio queda desincronizado con la DB real. El TODO.md tiene tareas para features que ya no existen. Spec-Anchored evita eso. Y si el código se implementa sin mostrar el plan primero, se pierde la oportunidad de corregir el rumbo **antes** de escribir — que es mucho más barato que corregirlo después.

---

## README sync — al completar una sección del TODO

**Regla:** cuando se marca el **último checkbox de una sección completa** del `TODO.md` (modo único) **o de un archivo de grupo completo** en `todos/` (modo orquestador, por capas o por features), actualizar la sección correspondiente del `README.md` antes del commit — así el README siempre refleja el estado real del proyecto.

| Sección de TODO.md / archivo de `todos/` | Qué actualizar en README.md                                                                   |
|--------------------------|-----------------------------------------------------------------------------------------------|
| **Setup**                | Verificar/completar scripts (`dev`, `build`, `test`, `lint`), pasos de instalación y variables de entorno |
| **Features iniciales** (modo único) / `todos/dominio-db.md`, `todos/api-backend.md`, `todos/frontend-ui.md` (modo orquestador) | Agregar o actualizar la sección "Features" con lo que realmente se construyó |
| **Calidad**              | Actualizar comando de lint/coverage, agregar badge si aplica                                  |
| **Infraestructura / Deploy** (modo único) / `todos/infraestructura-deploy.md` (modo orquestador) | Agregar URL de producción, hosting, y variables de entorno de prod si corresponde |
| **Seguridad** (modo único) / `todos/seguridad.md` (modo orquestador) | No suele necesitar sección propia en el README, salvo que el proyecto sea open source |
| **Documentación**        | Completar secciones vacías, agregar links a docs adicionales o diagramas generados            |

En modo orquestador, completar un archivo de grupo también actualiza la tabla "Estado por grupo" de `TODO.md` en el mismo commit (ver Workflow de Git, paso 1).

**Formato del commit cuando se hace README sync** (última tarea de la sección + README):
```
docs: update README — sección <nombre> completada (TODO: <última tarea>)
```

**Cuándo NO disparar el sync:**
- Si quedan `- [ ]` sin marcar en la sección — todavía no es el momento.
- Si la sección no tiene impacto visible en el README (ej. refactors internos) — se puede omitir.
- Si el usuario prefiere controlar el README manualmente — respetar, pero avisar al llegar al final de cada sección.

---

## Trazabilidad de requisitos

`SPEC.md` numera tres tipos de requisitos, cada uno con su prefijo: **`RF-N`** (Requisito Funcional — features), **`US-N`** (User Story — cómo se desglosa un RF desde la perspectiva del usuario), **`RNF-N`** (Requisito No Funcional — performance, escalabilidad, etc.). La cadena de trazabilidad completa:

```
RF-N (feature)  →  US-N (historia que la implementa)  →  tarea del TODO (US-N)
RNF-N (no funcional)  →  tarea del TODO (RNF-N), si el requisito tiene un objetivo concreto que exige trabajo puntual
```

Las tareas del TODO que implementan una historia terminan con su ID: `- [ ] Endpoint POST /login (US-1)`. Si además una tarea existe específicamente para cumplir un NFR (ej. agregar caché para cumplir un objetivo de performance), sumar también su ID: `- [ ] Agregar caché de Redis al endpoint de búsqueda (US-4, RNF-1)`. Tareas de infraestructura/setup/calidad genéricas no llevan ningún ID — no todo tiene que derivar de un requisito.

**Para responder "¿qué tareas implementan el RF-N / US-N / RNF-N?"**: `grep -rn "RF-N\|US-N\|RNF-N" SPEC.md TODO.md todos/ 2>/dev/null` — no hay una tabla de mapeo aparte que mantener sincronizada, el ID en cada línea es la fuente de verdad.

**Al agregar un requisito nuevo** (vía el flujo Spec-Anchored de abajo): asignarle el próximo ID disponible del tipo correspondiente en `SPEC.md`, y taguear las tareas nuevas del TODO con ese ID desde que se escriben — no como paso aparte al final.

---

## Workflow de Git — 1 user story / tarea = 1 commit + push

**Regla obligatoria para cualquier sesión de Claude Code en este proyecto:**

El `<tipo>` de cada commit sigue [Conventional Commits](https://www.conventionalcommits.org/) — no es una etiqueta libre, determina si el cambio entra al changelog y qué tan grande es para SemVer (ver `.rocky-spec/reference/versioning.md` de la skill y la sección "Versionado y releases" más abajo):

| Tipo | Cuándo | ¿Changelog? |
|---|---|---|
| `feat` | Feature nueva | Sí — `Added` |
| `fix` | Corrección de bug | Sí — `Fixed` |
| `feat!` / `fix!` / footer `BREAKING CHANGE:` | Rompe compatibilidad | Sí — `Changed` (marcado como breaking) |
| `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore` | Sin impacto para quien usa el proyecto | No |

Cada ítem del `TODO.md` (o del archivo de grupo correspondiente en `todos/`, si este proyecto usa el modo orquestador — ver más abajo) representa una **user story o paso de implementación**. Cuando se completa uno:

0. **Spec Drift Check** (ver detalle completo abajo): ¿el código que estoy por commitear agrega algo que no está en `SPEC.md`? Si sí, actualizar `SPEC.md` primero (con su línea en "Historial de cambios") y commitear ese cambio de doc junto con el código, o en un commit `docs:` separado inmediatamente antes.
0-bis. **TODO Size Check** (ver detalle completo abajo): si este proyecto todavía usa el modo único (sin carpeta `todos/`), ¿`TODO.md` se está acercando al límite de tamaño? Si sí, avisar antes de seguir agregando tareas.
0-ter. **Branch Discipline Check** (ver detalle completo en "Branching — GitFlow simplificado" más abajo): ¿la rama actual es `main` o `dev`? Si sí y el cambio no es trivial, avisar antes de commitear — se espera trabajar en `feature/<nombre>` o `fix/<nombre>`, no directo sobre las ramas principales.
1. Editar `TODO.md` (modo único) o el archivo de grupo en `todos/` (modo orquestador) y marcar el checkbox como hecho: `- [ ]` → `- [x]`. En modo orquestador, si esa era la **última tarea del grupo**, actualizar también la fila correspondiente en la tabla "Estado por grupo" de `TODO.md`, en el mismo commit.
1-bis. **Actualizar `CHANGELOG.md`** si el tipo del commit es `feat`, `fix`, o breaking change (ver tabla de arriba): agregar una línea bajo `[Unreleased]`, en la categoría correspondiente (`Added`/`Fixed`/`Changed`), en el mismo commit. Si el tipo no entra al changelog (`docs`, `test`, `chore`, etc.), no tocar `CHANGELOG.md`.
2. Hacer `git add` de **los archivos de código relacionados a esa tarea + el archivo de TODO editado + `CHANGELOG.md` si se tocó, todo junto** (no mezclar varias tareas en un commit, y no dejar el TODO para un commit aparte)
3. Commitear con mensaje que referencia el texto exacto de la tarea:
   ```
   <tipo>: <descripción corta> (TODO: <texto de la tarea>)
   ```
   Ejemplo:
   ```
   feat: setup JWT auth middleware (TODO: Configurar autenticación)
   feat: render product listing with filters (TODO: Listado de productos con filtros)
   test: add login flow unit tests (TODO: Escribir primer smoke test)
   ```
4. Ofrecer el `git push` inmediatamente — no acumular commits sin pushear —, pero **no ejecutarlo solo**: pedir la confirmación con `AskUserQuestion`, una pregunta por rama, como fija la tabla acción → mecanismo del Artículo 7 de `CONSTITUTION.md` (detalle operativo en "Branching" más abajo). "Inmediatamente" es sobre *cuándo se ofrece*, no sobre saltear la confirmación.

**Regla de sincronía:** el checkbox del TODO (único o de grupo) y el código que resuelve esa tarea viajan **siempre en el mismo commit**. Nunca marcar `- [x]` sin commitear el cambio correspondiente, y nunca commitear una tarea resuelta sin actualizar su checkbox. Si el código está a medias, el checkbox queda en `- [ ]` y el mensaje del commit incluye `(WIP)`.

**Por qué:** cada user story queda trazable en el historial del repo — cualquiera puede ver en qué commit se implementó cada historia, el estado del `TODO.md` en cualquier punto refleja exactamente qué estaba terminado, y el TODO actúa como índice del log de git.

**Excepciones:**
- Si una tarea requiere varios commits (ej. "Configurar CI" = setup + ajustes), está bien — todos referencian la misma tarea.
- Si el usuario pide explícitamente no pushear todavía (rama experimental, trabajo en progreso), respetar y avisar que el push queda pendiente.
- Cambios que no corresponden a ninguna tarea (fixes menores, typos) se commitean normal, sin referencia `(TODO: ...)`.

### Spec Drift Check — el paso 0 en detalle

**Por qué existe:** el flujo Spec-Anchored de más arriba se dispara cuando alguien *anuncia* una feature nueva en el chat ("quiero agregar X"). Pero no todo cambio de alcance se anuncia así — a veces el código simplemente crece un poco de más al resolver una tarea. Este chequeo es la red de seguridad para ese caso: corre **antes de cada commit**, no depende de que alguien se acuerde de avisar.

**Qué chequear** — los dos primeros comandos están armados para el backend y ORM elegidos en el setup de este proyecto (Python 3.9+ (click para el CLI) / no aplica — no hay persistencia), tomados de la tabla de patrones en `.rocky-spec/reference/stacks-code.md` de la skill. Son heurísticos por sintaxis (buscan cómo se escribe una ruta o un modelo en *este* framework puntual), no un analizador exhaustivo — el objetivo es levantar la mano en los casos obvios, no bloquear el commit:

```bash
# Endpoints/rutas nuevos en el diff que se va a commitear
echo "# no aplica — este proyecto no tiene rutas HTTP"

# Tablas/modelos nuevos en el diff que se va a commitear
echo "# no aplica — este proyecto no tiene DB"

# Archivos nuevos bajo domain/ o entities/ (posible entidad de dominio nueva — agnóstico de stack)
git diff --staged --name-only --diff-filter=A | grep -E "(domain|entities)/"
```

> Si alguno de los dos primeros comandos aparece como `# no aplica` es porque este proyecto no tiene backend o DB. Si aparece como `# deshabilitado — no pude derivar un patrón confiable...`, es la excepción rara donde ni la tabla de la skill ni el conocimiento del framework alcanzaron para armar un patrón — pasale un ejemplo de ruta/modelo si eso pasa, así se puede armar. El de `domain/`/`entities/` sí sigue activo siempre porque depende de convención de carpetas, no de sintaxis.

Si alguno de estos comandos devuelve resultados:
1. Comparar contra las secciones correspondientes de `SPEC.md` (`## API Contracts`, `## Schema de DB`, `## Dominio — Entidades y relaciones`).
2. Si lo que aparece en el diff **no** está mencionado en `SPEC.md` → parar antes de commitear y avisar:
   > "Este cambio agrega [endpoint/tabla/entidad] que no está en el SPEC.md. ¿Lo documento ahora (Spec-Anchored) o fue intencional dejarlo fuera?"
3. Si el usuario confirma que hay que documentarlo → actualizar `SPEC.md` (incluyendo la línea en "Historial de cambios") y commitear la doc junto con el código del paso 2 de arriba.
4. Si no hay señales en ninguno de los tres comandos (típico en cambios de frontend puro, estilos, refactors) → seguir directo al paso 1, no hace falta preguntar nada.

**Límite de esto:** aunque los patrones estén bien elegidos para el stack, siguen siendo heurísticos estructurales (rutas, DB, carpetas de dominio), no entienden semántica. Una feature de frontend puro (ej. un nuevo filtro en una lista ya existente) no va a disparar ninguno de los tres comandos — para esos casos seguimos dependiendo del flujo Spec-Anchored conversacional de más arriba.

### TODO Size Check — el paso 0-bis en detalle

**Por qué existe:** un `TODO.md` único (sin carpeta `todos/`) es el mismo tipo de God File que ya se evita en código (ver `.rocky-spec/reference/coding-principles.md` de la skill, sección "Tamaño de archivo") — solo que en la documentación. Este proyecto arrancó con el modo único (único / orquestador con `todos/`), organizado por capas (por capas / por features). Si es único, este chequeo evita que crezca sin límite.

**Solo aplica si este proyecto usa el modo único.** Si ya tiene carpeta `todos/`, no hace falta — cada archivo de grupo es chico por diseño.

```bash
wc -l TODO.md
```

- **< 300 líneas**: sin acción.
- **300-500 líneas**: avisar una vez, sin bloquear: *"`TODO.md` tiene [N] líneas y va camino a superar el límite recomendado — cuando quieras lo migramos a `todos/` (un archivo por capa o por feature, según cómo prefieras organizarlo). No hace falta ahora."*
- **500+ líneas**: proponer la migración activamente antes de seguir agregando tareas nuevas: *"`TODO.md` ya superó las 500 líneas. Te propongo migrarlo a `todos/` ahora, antes de seguir sumando — muevo las tareas existentes por grupo, no se pierde nada, y `TODO.md` queda como orquestador. ¿Lo hacemos, y por capas o por features?"* Si el usuario confirma, aplicar el mecanismo de split de `.rocky-spec/commands/p6-p7-files-todo.md` sección "¿TODO único o dividido — y por qué eje?" usando las tareas ya existentes en vez de generar desde cero.

## Branching — GitFlow simplificado

**Regla:** `master` es siempre estable. `dev` es la rama de integración — el trabajo del día a día nunca se hace directo sobre `master` ni sobre `dev`, sino en una rama propia por feature o corrección.

> Este repo usa `master` como rama troncal (histórica, no `main`) — el resto del esquema GitFlow es el mismo.

- `master` → producción (en este caso, la versión publicada/taggeada del paquete), siempre en estado deployable.
- `dev` → integración. Se crea una sola vez desde `master` al adoptar esta convención (ver tarea en `TODO.md`).
- `feature/<nombre-corto>` → una feature nueva (lo que dispara el Paso 2a del flujo de arriba). Sale de `dev`, vuelve a `dev`.
- `fix/<nombre-corto>` → una corrección (Paso 2b). Sale de `dev` (o de `master` si es un hotfix urgente), vuelve a la misma rama de la que salió.

```bash
# Una sola vez, al adoptar esta convención
git checkout master
git checkout -b dev
git push -u origin dev

# Al empezar a trabajar en algo nuevo
git checkout dev
git pull
git checkout -b feature/nombre-corto    # o fix/nombre-corto

# Al terminar, mergear de vuelta (o abrir PR, según cómo trabaje el equipo)
git checkout dev
git merge feature/nombre-corto
git push
```

**El merge nunca es automático — es un punto de parada explícito, no el último paso de una cadena.** Después de commitear y pushear la rama `feature/*`/`fix/*` (o de dejar lista una rama `dev` para un release), parar ahí y mostrar al usuario un resumen del cambio: qué se hizo, qué archivos se tocaron, resultado de tests/checks relevantes. Recién con confirmación explícita ejecutar `git merge` — pedida con `AskUserQuestion`, igual que el push, y no con un "dale" suelto en el chat: una frase libre no distingue entre aprobar el merge y aprobar además el tag y el push que suelen venir detrás. Nunca encadenar commit → push → merge sin que el usuario vea qué se está por integrar a `dev` o `master`. Esto aplica igual a ambos sentidos del merge: `feature/*`/`fix/*` → `dev`, y `dev` → `master` en un release.

**La misma pausa aplica antes del `push`, no solo antes del merge — siempre, sin importar el impacto del cambio.** Commitear localmente, parar, mostrar el mismo resumen que se usaría antes del merge, y esperar confirmación explícita antes de `git push`, usando `AskUserQuestion` (nombre de la rama + resumen corto en la descripción, opciones Sí/No) — no una confirmación en texto libre. Si en un mismo momento hay más de una rama lista para pushear, una pregunta por rama, para capturar la decisión de cada una por separado.

**Esto es insistente a propósito** — es común que esta convención quede escrita pero en la práctica todo se siga commiteando directo a `master`/`dev`. Por eso el Branch Discipline Check (paso 0-ter del Workflow de Git, arriba) no es solo una mención pasiva: antes de cada commit no trivial, si la rama actual es `master` o `dev`, avisar explícitamente y ofrecer crear la rama correspondiente ahí mismo — no asumir que "ya se sabe" y dejarlo pasar.

**Sugerencia de versión al mergear `feature/*`/`fix/*` → `dev`** (o `fix/*` → `master` en un hotfix — ver `.rocky-spec/reference/versioning.md` de la skill para el detalle completo): antes de ese merge, correr `rocky check version .` — calcula el bump exacto a partir de los commits reales desde el último tag (Conventional Commits, regla "el más alto gana": MAJOR > MINOR > PATCH, nunca se apilan varios bumps), en vez de que el agente tenga que "acordarse" en prosa. Mostrar el resultado al usuario y preguntar si se taguea ahora o se deja para cuando se junten más cambios — **nunca taguear solo**, es una decisión del usuario.

**Esto NO se dispara al mergear `dev` → `master` para hacer un release.** Ahí `master` simplemente hereda la versión que `dev` ya trae acumulada de sus merges anteriores — no se vuelve a calcular ni a bumpear un número distinto. El cálculo pasa una sola vez, en el merge hacia `dev` (o en el hotfix directo a `master`), nunca en el merge de integración `dev` → `master`.

`rocky check version` también avisa si una rama `feature/*` acumuló demasiados `fix` además del feature en sí (comparado contra `dev`) — mismo patrón de umbrales escalonados que el TODO Size Check: 3-5 fixes es una señal 🟡 de que el plan (RF-N/US-N) subestimó la complejidad, 6+ es 🔴 y sugiere partir la feature en dos.

## Versionado y releases — Semantic Versioning

Este proyecto sigue [SemVer](https://semver.org/lang/es/) (`MAJOR.MINOR.PATCH`) y mantiene `CHANGELOG.md` en formato [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) — ver `.rocky-spec/reference/versioning.md` de la skill para el detalle completo. Resumen operativo:

- **`[Unreleased]` de `CHANGELOG.md`** se va llenando commit a commit (paso 1-bis del Workflow de Git de arriba) — no es una tarea aparte, ya está integrada al flujo normal.
- **No se taguea en cada commit.** Un release es una decisión explícita, en un hito real: primer deploy a producción, antes de un cambio grande, o cuando el usuario lo pide.
- **Cómo hacer un release** cuando corresponda:
  1. Mover `[Unreleased]` a `## [X.Y.Z] - {{fecha}}` en `CHANGELOG.md`, dejando un `[Unreleased]` vacío arriba.
  2. `git commit -m "chore(release): vX.Y.Z"`
  3. `git tag -a vX.Y.Z -m "Release vX.Y.Z"` y `git push origin vX.Y.Z`
  4. Después de mergear a la rama principal: listar `git branch --merged dev` (menos `dev`/`master`) y preguntarle al usuario cuáles borrar (local + remoto) **con `AskUserQuestion`** — nunca borrar sin confirmar, y nunca ofrecer una rama que no esté 100% mergeada. Usar `git branch -d` y no `-D`: si la rama no estuviera mergeada, `-d` se niega y actúa como red de seguridad además de la verificación previa.
- **Qué bump corresponde**: `fix` → PATCH · `feat` → MINOR · breaking change → MAJOR. Mientras el proyecto está en `0.x.y` (antes del primer release estable), un breaking change puede seguir bumpeando MINOR en vez de saltar a `1.0.0` — pasar a `1.0.0` es decisión del usuario, no automática.
- **Decisión de este proyecto (2026-09-04)**: `rocky-spec` se queda en `0.x.y` por ahora — todavía en `Development Status :: 3 - Alpha`, sin publicación en PyPI (RF-6) ni usuarios externos conocidos que fijen la versión como dependencia. Próximos breaking changes (como el rename `charless` → `rocky` de `v0.7.0`) siguen bumpeando MINOR, no `1.0.0`. Revisar esta decisión cuando aparezca cualquiera de esas dos señales.
- **Nivel de exigencia**: un prototipo descartable no necesita nada de esto. Si este proyecto es una librería o paquete publicado (npm, PyPI), el versionado es estricto y romper compatibilidad es siempre MAJOR — ver `.rocky-spec/reference/versioning.md` sección "Nivel de exigencia" para el detalle completo.

## Gestión de dependencias

El escaneo de vulnerabilidades ya está en `SECURITY.md`. Acá va la política de **mantenimiento** — ver `.rocky-spec/reference/dependencies.md` de la skill para el detalle completo:

- **Pinning**: dependencias de aplicación con rango caret (`^1.2.3`), herramientas de build críticas con versión exacta. El lockfile (no aplica todavía — pyproject.toml declara rangos, sin lockfile) siempre commiteado — nunca en `.gitignore`.
- **Cadencia**: "Dependabot semanal — patches se auto-mergean si CI pasa, minors se revisan agrupados, majors se revisan uno por uno".
- **Antes de un release grande**: correr auditoría de dependencias sin usar (`depcheck`/`pip-check`/`cargo-udeps` según el stack) — no es un chequeo de cada commit.
- **Licencias de terceros**: "no aplica — proyecto privado, no se redistribuye" <!-- si el proyecto es open source o se redistribuye, cambiar a "sí — correr license-checker antes de cada release" -->

## Próximas decisiones pendientes

Ver `TODO.md` para el detalle.
