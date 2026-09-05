# Project Patterns — Templates opinados para casos específicos

Esta carpeta contiene **patrones de proyecto**: recetas completas y opinadas para casos de uso concretos donde tiene sentido saltarse las preguntas de stack/arquitectura porque ya está todo decidido.

La skill `/rocky-spec` los consulta en el Paso 1 (descripción del proyecto). Si la descripción matchea las criterias de algún patrón → ofrece usarlo. Si no, sigue el flujo genérico.

## Cómo se usa este archivo

Claude lee este README al final de P1. Para cada patrón listado abajo, evalúa los **match criteria** contra la descripción del usuario:

- Si **2 o más señales** matchean → ofrecer el patrón como aceleración.
- Si **0 o 1** señales matchean → no ofrecer, seguir flujo genérico.

El usuario siempre puede aceptar o rechazar. Si rechaza, vuelve al flujo genérico de P2.

## Cuando un patrón se acepta

- Cargar el archivo completo del patrón (`<pattern-id>.md`).
- Los pasos **P2 (sugiere stack)**, **P3 (confirma/edita)** y **P4 (sugiere arquitectura)** se **resumen**: la skill anuncia el stack y la arquitectura del patrón y pregunta *"¿Querés modificar algo o vamos así?"*.
- **P5 (comandos)** sigue normal, pero los comandos vienen del patrón.
- **P6 (genera archivos base)** usa los templates derivados del patrón en vez de los genéricos (ej. `BRIEF.md` específico del patrón).
- **P7 (TODO)** usa la lista base del patrón como semilla.

## Patrones disponibles

### `cinematic-product-landing`

Single-page parallax para marca de producto físico (bebida, snack, gadget, perfume, sneaker). Hero con WebP sequence mapeado al scroll, variantes navegables, dark mode default.

**Match criteria** (necesita 2+ señales en la descripción del usuario):

- **Tipo de página**: "single-page", "landing", "one-pager", "página de producto", "sitio de marca"
- **Producto físico**: "bebida", "lata", "botella", "snack", "perfume", "gadget", "sneaker", "auriculares", "electrónica", "consumo", "packaging", "DTC", nombre de marca de producto consumo
- **Aesthetic / animación**: "parallax", "scroll-driven", "cinematográfica", "cinematic", "inmersiva", "immersive", "WebP sequence", "scroll animation", "video-like", "premium"
- **Variantes a mostrar**: "varios sabores", "variantes", "flavors", "colores", "modelos", "PREV/NEXT", "navegación de productos"

Archivo: `cinematic-product-landing.md`

---

## Patrones generados por el usuario (auto)

Cuando el usuario termina un proyecto con `/rocky-spec` y queda conforme, en **P8.5** la skill ofrece generar un `SYSTEM_PROMPT.md` del proyecto y opcionalmente guardarlo acá como pattern reusable. Esos patterns aparecen abajo bajo "User-generated" y son indistinguibles funcionalmente de los que vienen con la skill: pasan por el mismo matching en P1.5.

### User-generated

> Esta lista la edita la skill automáticamente cuando se guardan nuevos patterns.
> Formato: `### <slug>` + descripción 1-línea + match criteria + metadata (origen, fecha, proyecto fuente).

<!-- AUTO-GENERATED ENTRIES BELOW — la skill inserta acá -->

### `fullstack-twitter-clone-express-react`

Clon de red social tipo Twitter/X. Fullstack completo: API REST con auth JWT custom, timeline, follows, likes, SSE real-time. SPA React autenticada.

**Match criteria** (necesita 2+ señales):
- `twitter clone` / `red social` / `microblogging` / `social network`
- `tweets` / `feed` / `timeline` / `seguir usuarios`
- `likes` / `follows` / `interacciones sociales`
- `REST API` + `PostgreSQL` + `JWT` / `auth custom`
- `fullstack` + `React` + `Express` / `Node.js`

**Stack**: Vite + React 19 + TypeScript · Express v5 + TypeScript · PostgreSQL + Prisma 7 · JWT (jose + bcryptjs) · Tailwind v4 + shadcn/ui · TanStack Query · Framer Motion · Vitest + Supertest · Docker Compose

**Origen**: user-generated · 2026-06-04 · `C:\Users\charly\Desktop\workspace\twitter-clone`
Archivo: `fullstack-twitter-clone-express-react.md`

---

<!-- /AUTO-GENERATED ENTRIES -->

## Default si no hay match exacto

Si en P1.5 ningún pattern alcanza 2+ matches pero **el usuario deja a la imaginación** (ej. "hace algo lindo", "no estoy seguro"), la skill ofrece el **último pattern user-generated** como semilla:

> *"No tengo match exacto con tu descripción, pero tu último proyecto fue `<slug>`. ¿Lo usamos de base o arrancamos genérico?"*

---

## Cómo agregar un patrón a mano

1. Crear archivo `<id>.md` en esta carpeta.
2. Incluir secciones obligatorias:
   - `## Match criteria` con señales detectables en lenguaje natural
   - `## Stack recomendado` (con justificación)
   - `## Arquitectura de carpetas`
   - `## Templates derivados` (BRIEF, prompts, README, TODO base)
   - `## Comandos de setup` (para P5)
   - `## Prompt original / referencia` (si aplica)
3. Agregar entrada acá en este README con sus match criteria.

Para patterns generados por la skill al cierre del proyecto, ya viene rellenado con el formato del `SYSTEM_PROMPT.md.template`.

Ideas de patrones que valdría la pena agregar a mano:
- `dashboard-saas` (Next.js + shadcn + Drizzle + Better Auth)
- `portfolio-3d` (R3F + GSAP + drei)
- `ecommerce-mvp` (Next.js + Stripe + shadcn)
- `mobile-tabs-app` (Expo + NativeWind)
- `video-ad-campaign` (creativo puro — ya cubierto en architectures.md)
