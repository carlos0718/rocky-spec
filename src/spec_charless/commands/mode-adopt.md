> Referencia de **charless-ia** — Modo Adopción. Se carga cuando el directorio tiene código pre-existente pero SIN `.skill-state.json` (proyecto no creado con esta skill).

## Modo Adopción — proyecto existente sin `.skill-state.json`

> Los pasos de este modo se numeran con el prefijo **MA** (**M**odo **A**dopción) — MA-1, MA-2, etc. — para no confundirlos con los pasos P0–P8 del flujo de creación normal.

Este modo se activa cuando el directorio tiene código ya escrito pero NO fue creado con esta skill. El objetivo no es empezar de cero: es **retro-aplicar** las convenciones de la skill sobre lo que ya existe.

**Regla principal:** nunca sobreescribir archivos que ya existen salvo confirmación explícita del usuario. Todo lo que ya está se respeta; solo se genera lo que falta.

### MA-1 · Scan automático del proyecto

Leer el estado actual del proyecto con una combinación de herramientas disponibles:

```bash
# Detectar tipo de proyecto y stack
cat package.json          # dependencies, scripts, devDependencies
ls -la                    # archivos en raíz (README.md, SPEC.md, CLAUDE.md, TODO.md, etc.)
find . -maxdepth 3 -type d  # estructura de carpetas (arquitectura actual)
```

Procesar los resultados para detectar:

| Aspecto | Qué buscar |
|---|---|
| **Runtime / lenguaje** | `package.json` → Node/TS/JS; `requirements.txt` → Python; `Cargo.toml` → Rust; `go.mod` → Go |
| **Framework frontend** | deps: `react`, `vue`, `svelte`, `angular`, `astro`, `next`, `nuxt` |
| **Framework backend** | deps: `express`, `fastify`, `nestjs`, `hono`, `fastapi`, `django` |
| **Estilos** | deps: `tailwindcss`, `@mui/material`, `bootstrap`, `styled-components`, `sass` |
| **Testing** | deps: `vitest`, `jest`, `playwright`, `cypress` |
| **ORM / DB** | deps: `prisma`, `drizzle-orm`, `mongoose`, `typeorm` |
| **Arquitectura** | carpetas en `src/`: `features/`, `components/`, `domain/`, `pages/`, `api/`, `routes/` |
| **Branching** | `git branch -a` → ¿existe `dev`? `git log --oneline -20` → ¿los commits recientes son directo sobre `main`/`dev`, o vienen de ramas `feature/*`/`fix/*` mergeadas? |
| **Archivos de skill** | `AGENTS.md`, `CLAUDE.md`, `SPEC.md`, `TODO.md`, `design-system/MASTER.md` — qué ya existe |

Si no existe `dev`, se crea en MA-6 al generar `AGENTS.md` (queda como tarea en el TODO si el usuario prefiere hacerlo después). Si los commits recientes son mayormente directo sobre ramas principales, es un hallazgo 🟡 — se reporta en MA-2 igual que salud del código/seguridad/observabilidad, no se fuerza un cambio de hábito sin avisar primero.

### MA-1.5 · Health check — tamaño de archivos y code smells

Correr un chequeo rápido de salud del código existente, sobre los archivos de código (ignorando `node_modules/`, `dist/`, `build/`, `.git/`):

```bash
# Top 15 archivos más largos del proyecto
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" \) \
  -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/build/*" -not -path "*/.git/*" \
  -exec wc -l {} \; | sort -rn | head -15
```

Clasificar cada archivo del top 15 contra la tabla de `.charless/reference/coding-principles.md` sección "Tamaño de archivo — límites y cuándo dividir":
- 🔴 **Dividir sí o sí** — supera el umbral duro de su tipo (o las 1000 líneas, regla dura sin excepción).
- 🟡 **Revisar** — está en la zona intermedia.
- Sin flag — dentro de lo ideal.

Además, un grep rápido (no exhaustivo — esto es un chequeo conversacional, no una auditoría completa) para detectar candidatos a separar tipos de implementación: archivos con 3+ declaraciones `interface`/`type` (TS) o `class`/`@dataclass` (Python) mezcladas con funciones no triviales en el mismo archivo.

Guardar la lista de archivos flaggeados — se muestra en MA-2 y se usa como semilla de deuda técnica en MA-7.

### MA-1.6 · Health check — seguridad

Correr un chequeo rápido de seguridad sobre el código existente (heurístico, no reemplaza una auditoría — ver `.charless/reference/security.md`):

```bash
# .env commiteado por error (no debería aparecer en git)
git ls-files | grep -E "^\.env$|^\.env\.[a-z]+$" | grep -v "\.env\.example"

# .gitignore no tiene .env
grep -q "^\.env$" .gitignore 2>/dev/null || echo "⚠️  .env no está en .gitignore"

# Candidatos a secret hardcodeado (heurístico — falsos positivos posibles, no reemplaza revisión manual)
grep -rEn "(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]" \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.go" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build .

# Dependencias con vulnerabilidades conocidas (según el ecosistema detectado en MA-1)
npm audit --audit-level=high 2>/dev/null || pip-audit 2>/dev/null || echo "Correr el audit del ecosistema correspondiente manualmente"

# Extensión — gestión de dependencias (.charless/reference/dependencies.md), no solo seguridad:
# Dependencias declaradas pero nunca importadas
npx depcheck 2>/dev/null || pip-check 2>/dev/null || echo "Correr depcheck/pip-check/cargo-udeps del ecosistema correspondiente manualmente"

# Licencias de terceros incompatibles (solo relevante si el proyecto se redistribuye)
npx license-checker --summary 2>/dev/null || pip-licenses 2>/dev/null || echo "Correr license-checker/pip-licenses manualmente si el proyecto es open source"
```

Clasificar hallazgos:
- 🔴 **Crítico** — `.env` commiteado, o un match de secret hardcodeado que parece real (no un placeholder tipo `xxx` o `your-key-here`).
- 🟡 **Revisar** — `.gitignore` sin `.env`, vulnerabilidades `high`/`critical` en `npm audit`, dependencias sin usar acumuladas, o una licencia GPL/AGPL colada en un proyecto que se redistribuye (ver `.charless/reference/dependencies.md` "Compliance de licencias de terceros" — no aplica si el proyecto es privado).

Guardar la lista de hallazgos — se muestra en MA-2 junto a la salud del código, y alimenta el checklist OWASP de `SECURITY.md` en MA-6 (los ítems con hallazgo 🔴/🟡 arrancan sin marcar en vez de asumidos como resueltos).

**Nunca mostrar el valor del secret encontrado** en el reporte — solo el archivo y la línea. Mostrar el valor sería repetir el problema de seguridad que se está reportando.

### MA-1.7 · Health check — observabilidad

Correr un chequeo rápido de observabilidad sobre el proyecto existente (heurístico — ver `.charless/reference/observability.md`):

```bash
# Error tracking configurado (Sentry u otro)
grep -rEl "Sentry\.init|@sentry/|bugsnag|rollbar" --include="*.ts" --include="*.js" --include="*.py" \
  --exclude-dir=node_modules --exclude-dir=.git . | head -1

# Endpoint de health check
grep -rEln "['\"](\/health|\/healthz|\/status)['\"]" --include="*.ts" --include="*.js" --include="*.py" \
  --exclude-dir=node_modules --exclude-dir=.git . | head -1

# Logging estructurado vs console.log suelto
grep -rc "console\.log(" --include="*.ts" --include="*.js" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist . | awk -F: '{sum+=$2} END {print sum " apariciones de console.log"}'
```

Clasificar hallazgos:
- 🟡 **Revisar** — no hay error tracking configurado, no hay endpoint de health check, o hay un número alto de `console.log` sueltos (más de ~15-20, según el tamaño del proyecto) en vez de logging estructurado.
- Sin flag — el proyecto ya tiene error tracking y/o health check configurados; no forzar un reemplazo si ya funciona, solo completar lo que falte.

Guardar la lista de hallazgos — se muestra en MA-2 junto a los de seguridad, y alimenta las tareas pendientes de `OBSERVABILITY.md` en MA-6.

### MA-2 · Presentar hallazgos + pedir descripción

Mostrar al usuario lo encontrado y pedir los datos que no se pueden inferir del código:

```
Encontré un proyecto existente con:

  Runtime:    Node.js / TypeScript
  Frontend:   React (Vite)
  Estilos:    Tailwind CSS
  Testing:    Vitest
  Arquitectura actual: src/components/, src/pages/, src/hooks/

Salud del código (archivos más largos):
  🔴 src/pages/Dashboard.tsx        842 líneas — dividir sí o sí
  🟡 src/components/OrderForm.tsx   280 líneas — revisar (mezcla tipos + UI + fetch)
  ..resto sin flag..

Seguridad:
  🔴 backend/.env está commiteado en el repo — hay que sacarlo del historial y rotar cualquier secret que contenga
  🟡 backend/.gitignore no incluye .env
  🟡 3 vulnerabilidades "high" en dependencias (npm audit)

Observabilidad:
  🟡 No encontré error tracking configurado (Sentry u otro)
  🟡 No encontré un endpoint de health check
  🟡 47 apariciones de console.log — sin logging estructurado

Archivos de la skill que ya existen:
  [v] README.md
  [x] CONSTITUTION.md    ← lo generamos
  [x] AGENTS.md          ← lo generamos
  [x] CLAUDE.md          ← lo generamos
  [x] SPEC.md            ← lo generamos
  [x] SECURITY.md        ← lo generamos
  [x] OBSERVABILITY.md   ← lo generamos
  [x] CHANGELOG.md       ← lo generamos (o mergeamos si ya existe)
  [x] LICENSE            ← preguntamos si no existe, nunca la inventamos sola
  [x] TODO.md            ← lo generamos
  [x] design-system/     ← lo generamos

Para adaptar la skill a este proyecto necesito que me cuentes:

  1. ¿De qué trata el proyecto? (descripción breve del objetivo)
  2. ¿Qué tipo es? (web app, API, fullstack, landing, otra)
  3. ¿Está solo el frontend o también tiene backend/DB?

(Si ya hay un README.md con descripción, lo leo y lo uso como base — confirmame si está actualizado)
```

Si MA-1.5 no encontró ningún archivo en zona 🔴 o 🟡, omitir el bloque "Salud del código" entero — no mostrar una sección vacía. Mismo criterio para MA-1.6/MA-1.7 y los bloques "Seguridad"/"Observabilidad": si no hay hallazgos, omitirlos. Si MA-1.6 encontró un secret hardcodeado real (🔴), priorizar avisarlo de forma bien visible — no dejarlo mezclado entre el resto de hallazgos menores.

### MA-3 · Análisis SDD + DDD (adaptado a código existente)

**Paso A — Determinar si aplica DDD:**
Usar la misma tabla de decisión de P1.7 (fullstack/backend → sí; frontend puro → no) — ver `.charless/commands/p1-spec-ddd.md`, Paso A.

**Paso B — Análisis de dominio (si aplica):**
En vez de preguntar desde cero, primero intentar inferir las entidades del código existente:
- Leer archivos en `src/domain/`, `src/models/`, `src/entities/`, `prisma/schema.prisma`, `src/types/` si existen
- Si se encuentra un schema o modelos → mostrarlos al usuario y preguntar *"¿Esto refleja bien tu dominio o hay cambios?"*
- Si no hay nada que inferir → hacer las 3 preguntas del Paso B de P1.7 igual que en el flujo normal (ver `.charless/commands/p1-spec-ddd.md`, Paso B)

**Paso C — Generar SPEC.md:**
Generar el SPEC.md igual que en P1.7 (ver `.charless/commands/p1-spec-ddd.md`, Paso C), pero:
- En la sección "Features MVP" → marcar como ✅ las features que claramente ya existen en el código (inferido de las rutas, componentes, o README existente)
- En "Criterios de aceptación" → dejar los pendientes como `- [ ]` y los ya resueltos como `- [x]`
- Mostrar al usuario antes de guardar:
  > "Generé el SPEC.md del proyecto. Revisá especialmente qué marqué como ✅ (ya hecho) y qué quedó como pendiente — quiero que quede con el estado real del proyecto."

### MA-4 · Documentar arquitectura (adaptado a código existente)

En vez de correr el flujo completo de P4 desde cero, leer la estructura actual de carpetas e inferir la arquitectura que ya se está usando:

```
La estructura que encontré en src/ sugiere una arquitectura Feature-based:
  src/features/auth/
  src/features/dashboard/
  src/shared/components/

¿Es eso lo que usás, o fue evolucionando sin un patrón intencional?
> 1) Sí, es Feature-based intencional
  2) No tiene estructura clara todavía — ayudame a definir una
  3) Es otra arquitectura (la describo)
```

Si el usuario elige **1**: documentar la arquitectura detectada directamente en el CLAUDE.md generado, con su descripción, beneficios y trade-offs según `.charless/reference/architectures.md` (tipos) y `.charless/reference/architectures/codigo.md` (árbol de carpetas de referencia para comparar contra lo detectado).

Si el usuario elige **2**: ejecutar el flujo completo de P4 (scoring + recomendación educativa — ver `.charless/commands/p4-architecture.md`) igual que en proyectos nuevos, pero aclarando: *"La estructura actual es libre. Te propongo una arquitectura para que la adoptemos de acá en adelante — no hace falta refactorear lo que ya existe, sino seguir el patrón en el código nuevo."*

Si el usuario elige **3**: el usuario describe, se documenta su elección.

### MA-5 · Design System (si tiene interfaz visual)

Si el proyecto tiene frontend, ejecutar P4.5 normalmente (ver `.charless/commands/p4.5-design-system.md`), usando el mismo `.charless/templates/MASTER.md.template`. Pero antes:
- Verificar si ya hay un `tailwind.config.js`, `theme.ts`, variables CSS, o sistema de tokens definido
- Si hay tokens o colores definidos → leerlos y usarlos como base para completar el template en vez de generarlo desde cero
- Mostrar: *"Encontré estos tokens de color en tu proyecto. ¿Los uso como base del design system o querés definirlo desde cero?"*
- Los campos de identidad (`{{PRODUCT_TYPE}}`, `{{TARGET_USERS}}`) se completan con lo ya inferido/confirmado en MA-3 — no preguntar de nuevo.

### MA-6 · Generar archivos faltantes

Para cada archivo que el audit de MA-1 marcó con `[x]` (no existe), generarlo usando los templates y la información recolectada:

| Archivo | Template base | Datos usados |
|---|---|---|
| `CONSTITUTION.md` | `.charless/templates/CONSTITUTION.md.template` | Arquitectura y patrones detectados en MA-1, principios del perfil, reglas base de `coding-principles.md`/`security.md` |
| `AGENTS.md` | `.charless/templates/AGENTS.md.template` | Stack detectado, arquitectura documentada, principios del perfil, comandos reales del proyecto — incluyendo el Spec Drift Check (mismo criterio que P6: buscar el backend/ORM detectado en MA-1 dentro de `.charless/reference/stacks-code.md`; si no está en la tabla, derivarlo del conocimiento del framework y ofrecer agregarlo a la tabla; solo deshabilitar si no hay confianza real en la sintaxis) |
| `CLAUDE.md` | `.charless/templates/CLAUDE.md.template` | Importa `AGENTS.md` + roles del asistente |
| `SECURITY.md` | `.charless/templates/SECURITY.md.template` | Stack y auth detectados en MA-1, hallazgos de MA-1.6 (los ítems OWASP con hallazgo 🔴/🟡 arrancan sin marcar, no asumidos como resueltos) |
| `OBSERVABILITY.md` | `.charless/templates/OBSERVABILITY.md.template` | Stack detectado en MA-1, hallazgos de MA-1.7 (si ya hay error tracking/health check, documentarlos tal cual están en vez de asumir que no existen) |
| `CHANGELOG.md` | `.charless/templates/CHANGELOG.md.template` | Si hay tags de git existentes, usarlos para reconstruir versiones pasadas (ver caso especial abajo); si no hay historial de versiones, arranca en `[Unreleased]` |
| `LICENSE` | `.charless/templates/LICENSE-*.template` | Solo si no existe ya (ver caso especial abajo) — nunca inventar una licencia sin preguntar |
| `TODO.md` | `.charless/templates/TODO.md.template` | Features del SPEC.md (las ✅ ya marcadas como hecho, las pendientes como `- [ ]`) |
| `design-system/MASTER.md` | `.charless/templates/MASTER.md.template` | Resultado de MA-5 (tokens detectados o generados desde cero) |

**Regla de no sobreescritura:** si alguno ya existe, preguntar:
> "`CLAUDE.md` ya existe en este proyecto. ¿Lo reemplazo con la versión de la skill, lo mergeo, o lo dejo como está?"
> 1) Reemplazar (se pierde el actual)
> 2) Mergear (te muestro las secciones nuevas que agregaría)
> 3) Dejar como está

Para la opción **2 (mergear)**: mostrar solo las secciones que NO están en el archivo actual (por ejemplo, si le falta la sección "Agregar o modificar features — flujo de iteración", agregar esa sección al final del existente).

**Caso especial — `CONSTITUTION.md` no existe pero hay convenciones equivalentes escritas en otro lado** (`CONTRIBUTING.md`, un wiki interno, un `.eslintrc` muy opinado): no ignorarlas — extraer lo que ya está decidido (estilo, principios, reglas de PR) y usarlo como base de los Artículos, en vez de imponer los defaults de la skill sobre convenciones que el equipo ya venía siguiendo. Preguntar si hay dudas sobre cuál gana en caso de conflicto.

**Caso especial — `AGENTS.md` ya existe:** es el escenario más probable de todos, porque es un estándar abierto y muchos proyectos ya lo tienen sin haber usado esta skill (a veces generado por Codex, Cursor, o a mano). Nunca reemplazar sin mostrar antes qué se perdería — casi siempre conviene **mergear**: conservar los comandos/convenciones reales que ya documentaron y sumar las secciones propias de la skill que falten (boundaries, flujo Spec-Anchored, workflow de Git de 1 tarea = 1 commit).

**Caso especial — `SECURITY.md` ya existe:** también es un archivo estándar de GitHub (política de reporte de vulnerabilidades) — muchos proyectos lo tienen aunque sea solo con esa sección. **Mergear**, no reemplazar: conservar el contacto de reporte y cualquier decisión ya documentada, y sumar el checklist OWASP + el "Historial de cambios" que trae el template de la skill si no los tiene.

**Caso especial — `CHANGELOG.md` ya existe:** nunca reemplazar — es historial real del proyecto, perderlo sería peor que no generarlo. Si ya sigue el formato Keep a Changelog, dejarlo intacto y solo agregar `[Unreleased]` arriba si no la tiene. Si tiene otro formato (texto libre, por fecha sin SemVer), preguntar antes de tocarlo:
> "Encontré un `CHANGELOG.md` con [formato detectado]. ¿Lo dejo como está y arranco a mantenerlo igual, o lo migro a formato Keep a Changelog (categorías + versiones SemVer)?"

**Caso especial — no hay `CHANGELOG.md` pero sí hay tags de git**: antes de generar uno vacío, correr `git tag --sort=-creatordate` y `git log --oneline <tag_anterior>..<tag>` para cada tag, y usarlo para reconstruir al menos las versiones ya releaseadas (mejor un changelog retroactivo aproximado que uno vacío que ignora todo un historial de releases real).

**Caso especial — `LICENSE` ya existe:** nunca tocarlo — es una decisión legal ya tomada, no una convención de documentación como las demás. Ni sugerir cambiarla.

**Caso especial — no hay `LICENSE`:** no asumir ninguna por default (a diferencia de `AGENTS.md`/`SECURITY.md`, acá no hay un valor "seguro" para inventar sin preguntar). Preguntar igual que en P6: *"Este proyecto no tiene `LICENSE`. ¿Querés que agregue una (MIT / Apache 2.0 / Propietaria), o lo dejamos así por ahora?"*

### MA-7 · TODO desde estado actual

Generar el TODO adaptado al estado real del proyecto. Antes de generarlo preguntar:

```
Para armar el TODO desde el estado actual del proyecto, necesito saber:

  1. ¿Qué está terminado?
     (te muestro las features del SPEC y me decís cuáles ya están listas)
  2. ¿Qué está en progreso ahora?
  3. ¿Qué es lo próximo que querés hacer?
```

Generar el TODO con:
- Sección `Setup` marcada completamente como `[x]` (si el proyecto ya tiene deps instaladas y dev server andando)
- Features ya terminadas marcadas como `[x]`
- Features en progreso como `[ ]` con nota `<!-- en progreso -->`
- Features pendientes como `[ ]`
- Conservar las secciones DDD si el proyecto es fullstack (Dominio/DB, API/Backend, Frontend/UI) — o reorganizar por feature si el usuario prefiere ese modo (ver siguiente punto)
- Si `SPEC.md` (generado en MA-3) tiene historias de usuario con ID, taguear cada tarea con su `US-N` correspondiente (ver `AGENTS.md` sección "Trazabilidad de requisitos")

**Preguntar por capas o por features** (mismo criterio que P7, ver `.charless/commands/p6-p7-files-todo.md` sección "Organización de 'Features iniciales'") si el proyecto es fullstack o backend con DDD — no asumir por capas solo porque es lo que había antes, si el proyecto es de una sola persona full-stack puede convenirle más por features.

**Mismo criterio de único vs. orquestador que P7** (ver `.charless/commands/p6-p7-files-todo.md` sección "¿TODO único o dividido — y por qué eje?"): si el proyecto detectado en MA-1 es fullstack o de arquitectura Grande, generar directamente en modo orquestador (`todos/` con un archivo por grupo) en vez de un `TODO.md` único — no tiene sentido reconstruir un TODO que va a necesitar dividirse enseguida. Si ya existe un `TODO.md` grande de antes (proyecto adoptado con mucho historial), es el momento natural de hacer la migración, no después.

**Sección `Deuda técnica`** (solo si MA-1.5 flaggeó archivos 🔴 o 🟡): agregar una sección separada, no mezclada con las features — en modo único, al final de `TODO.md`; en modo orquestador, en su propio `todos/deuda-tecnica.md` (referenciado en la tabla "Estado por grupo" del orquestador):

```markdown
## Deuda técnica (detectada al adoptar el proyecto)
- [ ] 🔴 Dividir `src/pages/Dashboard.tsx` (842 líneas) — ver `.charless/reference/coding-principles.md` sección "Tamaño de archivo"
- [ ] 🟡 Revisar `src/components/OrderForm.tsx` (280 líneas, mezcla tipos + UI + fetch)
```

Estos ítems no bloquean el desarrollo normal — son backlog. El usuario decide cuándo atacarlos.

### MA-7.5 · Revisión funcional y de QA

Mismo mecanismo que P7.5 (ver `.charless/commands/p7.5-qa-review.md`), aplicado al `SPEC.md` reconstruido en MA-3 y al TODO de MA-7 — con un foco extra: como el spec se reconstruyó a partir de código existente (no de una conversación con el usuario), es más probable que falten user stories o que los criterios de aceptación sean inferidos y no confirmados. Marcar como pendiente de confirmar lo que se infirió sin que el usuario lo dijera explícitamente, en vez de darlo por hecho.

### MA-8 · Reporte de adopción

Al terminar, mostrar un resumen de lo que se hizo:

```
=== Adopción completada ===
Proyecto: <nombre>
Stack detectado: <resumen>
Arquitectura: <nombre>

Archivos generados:
  [v] CONSTITUTION.md   (principios inmutables: código, seguridad, arquitectura, boundaries)
  [v] SPEC.md           (estado actual del proyecto documentado, nivel Spec-Anchored)
  [v] AGENTS.md         (instrucciones universales — stack, comandos, convenciones, git workflow)
  [v] CLAUDE.md         (importa AGENTS.md + roles del asistente)
  [v] SECURITY.md       (checklist OWASP adaptado + hallazgos de MA-1.6)
  [v] OBSERVABILITY.md  (error tracking, logging, health check + hallazgos de MA-1.7)
  [v] CHANGELOG.md      (formato Keep a Changelog + SemVer)
  [v] LICENSE           ({{LICENSE_TYPE}} — o "sin definir" si el usuario prefirió no agregarla)
  [v] TODO.md           (estado real: X hechas, Y pendientes)
  [v] design-system/MASTER.md

A partir de ahora:
  • Usá las frases "continuemos", "qué sigue", "próxima tarea" para que
    la skill retome desde el TODO.
  • Cuando agregues features, la skill aplica el flujo Spec-Anchored
    (actualiza SPEC.md antes de escribir código).
  • Cada tarea completada = 1 commit + push (ver sección en AGENTS.md).
```

**Si MA-1.6 encontró algo 🔴 (secret hardcodeado o `.env` commiteado)**, este reporte no es el lugar para que pase desapercibido — repetirlo como línea aparte antes de cerrar, fuera del bloque de código:
> "⚠️ Antes de seguir: encontré [hallazgo] en `<archivo>`. Te recomiendo atenderlo ahora — sacarlo del código y, si es un secret real, rotarlo — antes de seguir desarrollando sobre este proyecto."

### Nota sobre `.skill-state.json` en Modo Adopción

Al finalizar la adopción, crear un `.skill-state.json` mínimo que marque el proyecto como adoptado:

```json
{
  "mode": "adopted",
  "timestamp": "<ISO date>",
  "step": "adoption_complete",
  "decisions": {
    "stack_detected": true,
    "spec_generated": true,
    "claude_md_generated": true,
    "todo_generated": true
  }
}
```

Esto evita que la skill vuelva a ofrecer el Modo Adopción en sesiones futuras, y en cambio usa el flujo normal de Reanudación.

---
