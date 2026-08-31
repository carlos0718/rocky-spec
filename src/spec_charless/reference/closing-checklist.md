> Referencia de **charless-ia** — Checklist de cierre. Se ejecuta al terminar tanto el flujo de creación (P8) como el Modo Adopción (MA-8): appendea al activity log y actualiza `profile.md`.

### Cierre

#### 1) Appendear al activity log

```json
{"date":"YYYY-MM-DD","skill":"charless-ia","name":"<nombre>","type":"<tipo>","stack":{...},"architecture":"<arq>","path":"<absolute path>"}
```

#### 2) Actualizar `profile.md` (auto-update orgánico)

**Para CADA tecnología del stack final del proyecto** (frontend, backend, estilos, UI primitives, animación, state, data fetching, forms, auth, ORM, testing, etc., incluyendo los items "Extra" agregados en P3 opción 3 y los comandos libres de P3 opción 4):

1. **Detectar la categoría correcta** del profile.md según el tipo de herramienta:

   | Tecnología | Sección de profile.md |
   |---|---|
   | React, Vue, Svelte, Angular, Astro, Next, Nuxt, vanilla | Frontend (frameworks / libs base) |
   | Express, NestJS, Fastify, FastAPI, Django, etc. | Backend |
   | TypeScript, JavaScript, Python, Go, Rust | Lenguaje default |
   | Tailwind, Sass, CSS Modules, styled-components, Emotion | Estilos |
   | shadcn/ui, Radix, Headless UI, MUI, Chakra, Mantine, Ant Design | UI primitives |
   | Framer Motion, GSAP, Anime.js, Lottie, Auto-Animate | Animación / motion |
   | Zustand, Redux Toolkit, Jotai, Valtio, Context API, Pinia | State management |
   | TanStack Query, SWR, axios, ky, RTK Query | Data fetching / HTTP client |
   | React Hook Form, Formik, Zod, Yup, TanStack Form | Forms / validación |
   | Better Auth, NextAuth, Clerk, Lucia, Supabase Auth | Auth |
   | Prisma, Drizzle, Mongoose, TypeORM, Knex | ORM / DB clients |
   | Vitest, Jest, Playwright, Cypress, Testing Library | Testing |
   | Vercel, Netlify, Fly.io, Railway, AWS | Infra / Deploy |
   | otras (date-fns, lodash, lucide-react, etc.) | Otros / utilidades |

   Si la tecnología no encaja en ninguna categoría conocida → preguntar al usuario en qué sección guardarla, o crear sección nueva si no existe.

2. **Para cada tech**, chequear si YA está en su sección del perfil:
   - **Si ya está** → incrementar el contador y actualizar `último uso` a la fecha de hoy.
   - **Si NO está** → agregar como línea nueva: `- <nombre>: 1 proyecto, último uso YYYY-MM-DD`.

3. **Mostrar el diff al usuario antes de escribir** el `profile.md`:

   ```
   Actualizaciones al perfil:
     • Frontend          React: 12 → 13 proyectos
     • Estilos           Tailwind: 9 → 10 proyectos
     • UI primitives     shadcn/ui: + agregar (primera vez)
     • State management  Zustand: + agregar (primera vez)
     • Data fetching     TanStack Query: 2 → 3 proyectos
     • Forms             Zod: + agregar (primera vez)

   ¿Confirmás? (S/n)
   ```

4. Si el usuario confirma → escribir `profile.md`. Si rechaza → no escribir (solo se appendea al log).

5. **Actualizar también la fecha** `last_scan_date` en la sección Configuración si tiene sentido (solo si hubo cambios significativos, no para cada proyecto).

#### Notas

- **No tocar las secciones Configuración, Principios de código, ni Convenciones** salvo que el usuario lo pida explícitamente. Esas son del usuario.
- **No remover tecnologías del perfil** automáticamente — solo agregar e incrementar. La poda manual la hace el usuario.
- **Para proyectos creativos** (no código), actualizar las secciones "Stacks dominantes — Creativo" con la misma lógica (AI image gen, AI video gen, editor, etc.).
- Si el usuario eligió un **patrón** en P1.5 (ej. `cinematic-product-landing`), también registrar el `pattern_used` en la línea del activity-log.

