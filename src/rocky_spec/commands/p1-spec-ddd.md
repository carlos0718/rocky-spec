> Referencia de **rocky-spec** — Paso P1 del flujo de creación: descripción del proyecto, pattern matching (P1.5) y generación de `SPEC.md` con SDD+DDD (P1.7).

### P1 · Describe el proyecto

Pregunta libre: "¿De qué trata el proyecto?". Después, una pregunta cerrada de tipo:

- **Código** → web app, API, fullstack, script/CLI, mobile, librería
- **Creativo** → video ad, motion piece, social content (Reels/TikTok/Shorts), storyboard, branding visual
- **Híbrido** → landing con 3D, web inmersiva, portfolio con motion, instalación interactiva

Si el usuario duda, hacer 2–3 preguntas para inferir el tipo. Guardar tipo en `.skill-state.json`.

#### P1.5 · Pattern matching (chequeo automático)

**Después de capturar la descripción y el tipo**, antes de pasar a P2, evaluar si la descripción matchea algún patrón pre-armado:

1. Leer `.rocky-spec/reference/project-patterns/README.md`.
2. Para cada patrón listado, contar cuántas **match criteria** matchean contra la descripción del usuario (palabras clave o sinónimos cercanos).
3. Si **2 o más señales** matchean para algún patrón → ofrecerlo:

   ```
   Tu descripción matchea con el patrón **<nombre del patrón>**.
   Este patrón ya tiene stack, arquitectura, templates y prompts pre-armados específicos
   para este caso de uso, así te ahorrás varias decisiones.

   ¿Lo usamos?
   > 1) Sí, cargá el patrón
     2) No, seguimos con el flujo genérico (yo decido stack y arquitectura)
     3) Mostrame qué incluye el patrón antes de decidir
   ```

4. Si el usuario elige **1**: cargar el archivo del patrón completo (`<pattern-id>.md`) y seguir las "Notas para Claude al cargar este patrón" del propio archivo. Eso típicamente significa:
   - P2 → anuncio del stack del patrón, no pregunta abierta.
   - P3 → confirmá *"¿OK o cambiamos algo?"* pero con la tabla del patrón pre-llenada.
   - P4 → arquitectura del patrón directamente.
   - P5 → comandos del patrón.
   - P6 → templates del patrón.
   - P7 → TODO base del patrón como semilla del modo C.

5. Si el usuario elige **2**: seguir flujo genérico P2 normal.

6. Si el usuario elige **3**: mostrar el resumen del patrón (su sección "Stack recomendado" + "Arquitectura de carpetas" + qué templates incluye), después volver a preguntar 1/2.

**Si 0 o 1 señales matchean** para todos los patrones → no ofrecer nada, pasar directo a P1.7.

**Si más de un patrón matchea con 2+ señales** → ofrecer los dos con sus scores y dejar elegir.

**Si el usuario cargó un patrón y después en P3 decide cambiar algo fundamental** (ej. pide otro framework distinto al del patrón) → avisar *"Eso sale del patrón. ¿Querés salir del patrón y volver al flujo genérico, o ajustamos solo esa pieza?"*.

### P1.7 · SDD + DDD — Generar Project Spec

**Metodologías combinadas:**
- **SDD (Specification-Driven Development)**: definir qué se va a construir antes de tocar código. Genera `SPEC.md` como contrato del proyecto.
- **DDD (Domain-Driven Design)**: para proyectos con lógica de negocio (fullstack, backend, API), pensar desde el dominio hacia afuera — primero las entidades y reglas, luego la DB, luego la API, luego el frontend. El orden importa porque todo lo demás se deriva del dominio.

Ver referencia completa de ambas metodologías en `.rocky-spec/reference/methodologies.md`.

#### Paso A — Determinar si aplica DDD

DDD aplica cuando el proyecto tiene **lógica de negocio + persistencia**:

| Tipo de proyecto           | ¿DDD aplica? | Qué analizar                        |
|----------------------------|:------------:|-------------------------------------|
| Fullstack (frontend + API + DB) | ✅ Sí    | Dominio → DB → API → Frontend       |
| Backend / API pura          | ✅ Sí        | Dominio → DB → API                  |
| Frontend puro (SPA/landing) | ❌ No        | Solo features + user stories        |
| Script / CLI                | ❌ No        | Solo features + flujo de uso        |
| Creativo / motion           | ❌ No        | Solo brief + deliverables           |

Si DDD aplica → ejecutar el análisis de dominio **antes** de generar el SPEC.md completo.

#### Paso B — Análisis de dominio (solo si DDD aplica)

Guiar al usuario con preguntas breves para identificar las entidades del dominio:

> "Antes de armar el spec completo, necesito entender el dominio del negocio. Voy a hacerte 3 preguntas rápidas."

**Pregunta 1 — Entidades principales:**
> "¿Cuáles son los 'objetos' principales de tu app? Por ejemplo para un e-commerce serían Producto, Pedido, Usuario, Carrito. Para un blog: Post, Autor, Categoría, Comentario. ¿Cuáles son los tuyos?"

**Pregunta 2 — Relaciones:**
> "¿Cómo se relacionan? Por ejemplo: 'un Usuario tiene muchos Pedidos', 'un Pedido tiene muchos Productos'. Dame las relaciones más importantes."

**Pregunta 3 — Reglas de negocio críticas:**
> "¿Hay alguna regla de negocio importante? Por ejemplo: 'un Pedido no puede tener stock negativo', 'solo usuarios verificados pueden comprar', 'los Posts necesitan aprobación antes de publicarse'."

Con esas 3 respuestas, generar automáticamente:

**Diagrama de entidades (formato texto):**
```
[Usuario] 1 ──── N [Pedido] N ──── N [Producto]
   |                  |
   └── tiene roles     └── tiene estados (pendiente/pagado/enviado)
```

**Schema de DB inferido:**
```sql
-- users
id, email, password_hash, role, created_at, verified_at

-- products
id, name, description, price, stock, category_id, created_at

-- orders
id, user_id, status, total, created_at, updated_at

-- order_items
id, order_id, product_id, quantity, unit_price
```

Mostrar el diagrama + schema al usuario:
> "Basado en lo que me dijiste, este sería el modelo de dominio y el schema de DB inicial. ¿Lo ajustamos o seguimos?"

Si el usuario aprueba → guardar en SPEC.md. Si pide ajustes → incorporarlos.

#### Paso C — Generar SPEC.md

Basado en la descripción del usuario (P1) + el análisis de dominio (si aplica), generar automáticamente un borrador de `SPEC.md` usando **`.rocky-spec/templates/SPEC.md.template`** (nivel SDD: **Spec-Anchored** — ver `.rocky-spec/reference/methodologies.md` para la definición completa de los niveles de SDD). El template ya trae el header que marca el documento como vivo y la sección de Historial de cambios.

Rellenar sus placeholders con:
- `{{PROJECT_DESCRIPTION}}`: 2-3 líneas del objetivo principal
- `{{TARGET_USERS}}`: quién lo usa y para qué
- Tabla de features P0/P1/P2 con descripción breve de cada una — cada fila es un **`RF-N`** (Requisito Funcional), numerados en el orden que aparecen
- 3-5 user stories críticas del MVP — cada una anota qué `RF-N` implementa (una feature puede desglosarse en varias historias; ver "Impacto en el TODO.md" más abajo para cómo se traduce esto al orden de trabajo)
- Si DDD aplica: entidades y relaciones, schema de DB, API contracts (del análisis del Paso A/B de arriba) — si no aplica, borrar esas tres secciones del archivo generado
- Criterios de aceptación del MVP
- Qué queda fuera de alcance en v1
- **Requisitos no funcionales**: usar los defaults del template (performance/escalabilidad/compatibilidad/i18n/retención "sin objetivo estricto") sin preguntar, salvo que la descripción del usuario en P1 ya haya mencionado algo puntual (ej. "tiene que aguantar mucho tráfico el día del lanzamiento", "necesita estar en inglés y español desde el día 1") — en ese caso, completar ese campo específico con lo mencionado y dejar el resto en default. No convertir esto en un cuestionario de 5 preguntas nuevas; si nada se mencionó, los defaults son la respuesta correcta para un MVP. Cada fila ya viene numerada `RNF-N` en el template; si un NFR aplica a una feature puntual y no a todo el proyecto (ej. "el buscador debe responder rápido" es de una sola feature), completar la columna "Alcance" con el `RF-N`/`US-N` correspondiente en vez de dejarla en "Global".
- Primera línea del Historial de cambios: fecha de hoy, "Spec inicial (P1.7)", y el commit donde se guardó

**Trazabilidad completa**: al terminar este paso, la cadena `RF-N → US-N → (tarea del TODO en P7)` y `RNF-N → (tarea del TODO si tiene objetivo concreto)` debe poder seguirse de punta a punta — ver `AGENTS.md` sección "Trazabilidad de requisitos" para el mecanismo completo (se termina de completar en P7).

**Nota para P4 (arquitectura):** si algún NFR de escalabilidad quedó con un valor real (no el default), es una señal a tener en cuenta al recomendar arquitectura — un objetivo de "5000 usuarios concurrentes desde el lanzamiento" no encaja con una arquitectura Mini/Chico.

**Mostrar el SPEC al usuario antes de guardar:**
> "Generé el spec del proyecto siguiendo SDD + DDD. Revisalo — si querés ajustar entidades, schema, features o alcance, decime antes de arrancar."

Si el usuario aprueba, guardar como `SPEC.md` en el directorio del proyecto (se creará en P6 junto con `AGENTS.md` y el resto de archivos base). Guardar el contenido aprobado en `.skill-state.json` para usarlo en P6.

Si el usuario pide cambios, incorporarlos y mostrar la versión actualizada una vez. No entrar en loop — si pide una segunda ronda, aplicarla y seguir.

#### Impacto en el TODO.md — orden de desarrollo para fullstack

Si el proyecto es fullstack o backend con DDD, en P7 se pregunta explícitamente **por capas o por features** (ver `.rocky-spec/commands/p6-p7-files-todo.md` sección "Organización de 'Features iniciales'") — no es automático, depende de cómo va a trabajar el equipo. Lo que sigue acá es el razonamiento de **por qué** el orden por capas es dominio-primero cuando se elige esa opción; para el detalle de ambos modos y cómo se preguntan, ver P7.

**Modo "por capas"** — dominio primero, presentación al final. El TODO tendrá una sección extra entre Setup y Features:

```markdown
## Dominio / Base de datos
<!-- 📄 README sync → agregar sección de arquitectura/schema cuando se complete -->
- [ ] Crear migraciones de DB (tablas definidas en SPEC.md) (US-1)
- [ ] Implementar modelos / entidades del dominio (US-1)
- [ ] Configurar conexión a DB y ORM
- [ ] Seed de datos básicos para desarrollo

## API / Backend
<!-- 📄 README sync → actualizar sección de API con endpoints reales -->
- [ ] Implementar repositorios / data access layer (US-1)
- [ ] Implementar servicios / lógica de negocio (US-1)
- [ ] Implementar endpoints (según API Contracts del SPEC.md) (US-1)
- [ ] Tests de integración de endpoints críticos

## Frontend / UI
<!-- 📄 README sync → agregar capturas o descripción de pantallas -->
- [ ] Configurar routing
- [ ] Implementar páginas/vistas principales (US-1)
- [ ] Conectar con la API (US-1)
- [ ] Estados de loading, error y empty
```

**Modo "por features"** — cada historia de usuario es su propio grupo, con lo que haga falta de cada capa adentro:

```markdown
## Login (US-1)
- [ ] Migración de tabla users
- [ ] Endpoint POST /login
- [ ] Formulario de login + validación
- [ ] Estados de loading y error

## Checkout (US-2, US-3)
- [ ] Migración de tabla orders
- [ ] Endpoint POST /checkout
- [ ] Flujo de carrito → confirmación
```

Los IDs `(US-N)` de arriba salen de `SPEC.md` sección "User Stories clave" (ver Paso C más abajo) — asignarlos al escribir cada tarea, no como paso aparte al final. No hace falta repetir el `RF-N` en la tarea (ya está implícito en el `US-N`, que declara de qué `RF-N` sale). Si una tarea existe específicamente para cumplir un requisito no funcional con objetivo concreto (ej. una tarea de caché para cumplir un `RNF-1` de performance), sumar también ese ID: `(US-4, RNF-1)`.

Para **frontend puro**: el TODO mantiene solo `Setup → Features iniciales → Calidad → Documentación → Deploy` (sin las secciones de dominio/API) — la pregunta de por capas/por features no aplica, no hay más de una capa para ordenar.

Continuar a P2.

