# Constitution — rocky-spec

> Concepto tomado de GitHub Spec Kit: la constitution es el conjunto de principios **inmutables** que gobiernan cómo las specs se convierten en código — la diferencia con `SPEC.md` es la frecuencia de cambio. `SPEC.md` cambia con cada feature (Spec-Anchored, vivo). Esta Constitution casi no cambia — enmendarla es un acto deliberado y explícito, nunca un efecto colateral de resolver una tarea.
>
> Relación con los demás documentos: `SPEC.md` dice **qué** se construye. `AGENTS.md` dice **cómo operar** el día a día (comandos, stack, workflow). Esta Constitution dice **qué reglas nunca se negocian** mientras se construye cualquiera de las dos cosas anteriores.

## Gobernanza

- **Versión de esta Constitution**: 1.5.0
- **Fecha de ratificación**: 2026-08-31
- **Última enmienda**: 2026-09-06

**Regla de enmienda** (versionado propio, independiente del SemVer del software — ver `.rocky-spec/reference/versioning.md` de la skill):
- **MAJOR**: se elimina o redefine un artículo existente (ej. dejar de aplicar SOLID).
- **MINOR**: se agrega un artículo nuevo (ej. sumar un requisito de accesibilidad que antes no estaba).
- **PATCH**: aclaración de redacción sin cambio de fondo.

**Cómo enmendar**: nunca en silencio dentro de un commit de feature. Si una tarea hace evidente que un artículo ya no tiene sentido para este proyecto, es señal de pausar y conversarlo explícitamente con el humano — no de bandear la regla y seguir. Una vez acordado el cambio, actualizar este archivo, subir la **Versión de esta Constitution** según la regla de arriba, y agregar la línea correspondiente al Historial de enmiendas al final.

## Artículo 1 — Principios de código

| Principio | Qué significa en la práctica |
|---|---|
| **SOLID** | Cada módulo tiene una sola razón para cambiar (SRP). Extender sin modificar lo existente (OCP). Interfaces pequeñas y específicas (ISP). Depender de abstracciones, no de implementaciones concretas (DIP). |
| **DRY** | Si una lógica aparece dos veces, extraerla a una función, hook o constante. |
| **KISS** | La solución más simple que resuelve el problema es la correcta. |
| **YAGNI** | No implementar lo que no se necesita hoy. |
| **Clean Code** | Nombres que se explican solos. Funciones < 30 líneas. Early returns. Logs estructurados, nunca `console.log("texto")` — ver `OBSERVABILITY.md` para la librería y el formato exacto de este proyecto. |

Detalle completo, ejemplos y contraejemplos en `.rocky-spec/reference/coding-principles.md`.

## Artículo 2 — Tamaño y estructura de archivos

- **Límite de tamaño de archivo** — cualquier proyecto de código. Componente UI < 150 líneas (dividir en 400). Servicio/hook < 200 (dividir en 400). **1000 líneas es techo duro sin excepción de tipo de archivo.**
- **Code smells a evitar**: God File, Long Method, Duplicate Code, Primitive Obsession, Long Parameter List — catálogo completo en `coding-principles.md`.
- **Separación de tipos/interfaces**: si un tipo se usa en 2+ archivos o el archivo ya tiene 3+ declaraciones, va en `<entidad>.types.ts` / `types/` propio.
- **Sin estilos inline** (solo proyectos con interfaz visual): `no aplica — sin interfaz visual` — clases del framework, nunca `style="..."` ni `style={{}}` salvo valores calculados en runtime.
- **Etiquetas semánticas HTML** (solo proyectos con interfaz visual): `<header>`/`<nav>`/`<main>`/`<article>`/`<section>`/`<aside>`/`<footer>` en vez de `<div>` genérico.

## Artículo 3 — Seguridad

- Nunca secrets en el repo — `.env` en `.gitignore` desde el primer commit.
- Passwords siempre hasheados (bcrypt/argon2), nunca en texto plano.
- Validación de input en el borde antes de que llegue a la lógica de negocio.
- HTTPS obligatorio en producción.
- Dependency scanning configurado en CI.

Checklist completo (OWASP adaptado) y decisiones específicas de este proyecto en `SECURITY.md`.

## Artículo 4 — Especificación viva (SDD Spec-Anchored)

`SPEC.md` es la fuente de verdad de qué se construye, y se actualiza **antes** de escribir código para cualquier cambio de alcance — nunca después, nunca "cuando haya tiempo". Este principio no se negocia por apuro: un cambio de alcance sin su línea correspondiente en `SPEC.md` es una violación de esta Constitution, no un atajo válido. Mecanismo completo en `AGENTS.md` sección "Agregar o modificar features".

## Artículo 5 — Patrones de arquitectura de este proyecto

- **Arquitectura elegida**: Plugin registry (Mediano — feature-based)
- **Patrones activos**: Registry / Plugin, Adapter (cada integración adapta el mismo conocimiento a su formato) <!-- ej. Repository, Factory, Observer, Strategy -->

Estos patrones son la forma concreta en que este proyecto aplica el Artículo 1 (SOLID en particular) — no son una capa aparte, son su implementación.

## Artículo 6 — Boundaries

**Preguntar primero** (no asumir, confirmar con el humano antes de aplicar):
- Cualquier feature nueva o corrección: mostrar el plan (con o sin cambio de `SPEC.md`, según corresponda) y esperar confirmación explícita antes de tocar código — ver `AGENTS.md` sección "Agregar o modificar código (Plan → Confirmar → Implementar)". Esta regla es la base de todas las demás de este artículo.
- Cambios de arquitectura que tocan 3+ módulos.
- Agregar una dependencia nueva no trivial (más de un wrapper chico).
- Desactivar alguno de los artículos de esta Constitution para este proyecto puntual.
- Cambiar el mecanismo de auth o el alcance de CORS/rate limiting.

**Nunca:**
- Commitear secrets, API keys o `.env` con valores reales.
- Saltarse el Artículo 4 (Spec-Anchored) para cambios de dominio o alcance.
- Marcar una tarea del `TODO.md` como hecha sin el commit correspondiente.
- Enmendar esta Constitution como efecto colateral de una tarea (ver "Cómo enmendar" arriba).

## Artículo 7 — Versionado y releases

- Los commits siguen **Conventional Commits** — el tipo (`feat`/`fix`/`feat!`) no es una etiqueta libre, determina el bump de SemVer y si entra al `CHANGELOG.md`.
- La versión del proyecto sigue **SemVer** (`MAJOR.MINOR.PATCH`) — romper compatibilidad es siempre MAJOR, sin excepción, incluso si el cambio fue chico de programar.
- Un release (tag de versión) es una decisión explícita, nunca automática por acumulación de commits.
- El trabajo del día a día se hace en `feature/*`/`fix/*`, nunca directo sobre `master`/`dev` — ver `AGENTS.md` sección "Branching". Al mergear a `dev` o `master`, recordar (no ejecutar solo) si corresponde bumpear versión.
- **Ninguna acción que publique, integre o destruya se ejecuta sola.** Antes de cada una: parar, mostrar un resumen de lo que se está por hacer, y esperar la confirmación **por el mecanismo que fija esta tabla**. Nunca encadenar commit → push → merge, ni inferir un permiso de una frase suelta del chat.

  | Acción | Mecanismo de confirmación |
  |---|---|
  | `git push` — cualquier rama, cualquier tamaño de cambio | `AskUserQuestion`, una pregunta **por rama** |
  | `git merge` — en ambos sentidos (`feature/*`→`dev`, `dev`→`master`) | `AskUserQuestion` |
  | `git tag` / publicar un release | `AskUserQuestion` — nunca taguear por acumulación de commits |
  | Borrar ramas (local o remoto) | `AskUserQuestion` — y solo ramas 100% mergeadas, salvo decisión explícita del humano |
  | Elegir entre alternativas de diseño o implementación | `AskUserQuestion` con las opciones reales |
  | Avisos que **no** piden decisión (Spec Drift, TODO Size) | Texto en la respuesta, sin bloquear |

  **Por qué el mecanismo es parte de la regla y no un detalle**: una confirmación en texto libre ("dale", "ok") es ambigua en su alcance — no distingue entre aprobar un push y aprobar además el merge y el tag que vienen después. `AskUserQuestion` obliga a enumerar las opciones reales antes de preguntar, y deja la decisión registrada como decisión. Cuando la tabla no cubra una acción irreversible o de cara al exterior, el default es preguntar, no asumir.

Detalle completo, ejemplos y la relación con los snapshots de `specs/` en `.rocky-spec/reference/versioning.md` de la skill.

## Artículo 8 — Gestión de dependencias

- El lockfile (`no aplica todavía (sin dependencias fijadas por lockfile — pyproject.toml declara rangos)`) se commitea **siempre** — nunca en `.gitignore`. Es lo único que garantiza que todos instalen exactamente la misma versión.
- Dependency scanning corre en CI (Dependabot u equivalente, ver Artículo 3) — esto es seguridad. Mantener las dependencias actualizadas en el tiempo (no solo parchear vulnerabilidades) es mantenimiento — ver `.rocky-spec/reference/dependencies.md` para pinning, cadencia de actualización, y compliance de licencias de terceros.
- Si este proyecto se redistribuye o es open source: compliance de licencias de terceros es obligatorio, no opcional — una sola dependencia con licencia copyleft fuerte (GPL/AGPL) mal usada puede obligar a relicenciar el proyecto completo.

## Overrides ratificados

Excepciones explícitas a algún artículo de arriba, acordadas para este proyecto en particular — no vale desviarse de un artículo sin que quede escrito acá:

- Artículo 2 (tamaño de archivo): sin excepciones vigentes — todos los módulos están bajo 200 líneas. <!-- ej. "Artículo 1 (KISS) relajado en el módulo de pricing: la complejidad ahí es inherente al dominio, no accidental" -->
- —

---

## Historial de enmiendas

| Fecha | Versión | Cambio | Motivo |
|-------|---------|--------|--------|
| 2026-08-31 | 1.0.0 | Ratificación inicial | Setup del proyecto (P6) |
| 2026-08-31 | 1.1.0 | Artículo 6: regla de Plan → Confirmar → Implementar. Artículo 7: adopción de branching GitFlow simplificado (`master`/`dev`/`feature`/`fix`) | Pedido explícito del usuario de empezar a aplicar la metodología GitFlow de ahora en adelante |
| 2026-08-31 | 1.2.0 | Artículo 7: el merge nunca es automático — parar y mostrar un resumen antes de ejecutar `git merge`, esperar confirmación explícita | Pedido explícito del usuario tras notar que los merges a `dev`/`master` se venían ejecutando en cadena sin pausa |
| 2026-09-04 | 1.3.0 | Artículo 7: el push tampoco es automático para cambios breaking o de alcance grande — pausa y resumen antes de `git push`, igual que ya regía para `git merge`. Con varias ramas listas, usar `AskUserQuestion` (una pregunta por rama, Sí/No) para capturar cuáles pushear | Pedido explícito del usuario tras notar que la rama `refactor/rename-to-rocky-spec` (un rename completo del framework, marcado `BREAKING CHANGE:`) se pusheó sin pedir su aprobación primero |
| 2026-09-04 | 1.4.0 | Artículo 7: la pausa antes de `git push` deja de depender del impacto del cambio — aplica siempre, para cualquier commit, vía `AskUserQuestion` | Pedido explícito del usuario para simplificar la regla de 1.3.0: en vez de juzgar caso a caso si un cambio es "breaking o de alcance grande", preguntar siempre |
| 2026-09-06 | 1.5.0 | Artículo 7: los dos bullets sueltos de `merge` y `push` se reemplazan por una **tabla acción → mecanismo** que cierra el alcance (push, merge, tag, borrado de ramas, elección entre alternativas) y separa las confirmaciones de los avisos que no piden decisión | Pedido explícito del usuario de validar si el uso de `AskUserQuestion` estaba definido "y no en prosa". No lo estaba: solo regía para `push`, `merge` seguía aceptando texto libre, y ni el borrado de ramas ni el tag fijaban mecanismo. La revisión además destapó que `AGENTS.md` se contradecía a sí mismo ("hacer `git push` inmediatamente" en el paso 4 del workflow vs. la pausa obligatoria 80 líneas después) y que los templates distribuidos no llevaban nada de esto |
