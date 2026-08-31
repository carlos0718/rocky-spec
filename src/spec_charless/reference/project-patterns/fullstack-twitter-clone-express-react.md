# System Prompt — The Flock (Twitter Clone)

> Contexto completo del proyecto para cualquier agente de IA que trabaje en este codebase.
> Cubre decisiones de arquitectura, stack, testing, UI/UX y gotchas aprendidos.
> **Generado al cierre del challenge** con `/charless-ia` (P8.5).
> Reusable como base para cualquier proyecto fullstack con API REST + SPA autenticada.

---

## Identidad del proyecto

**The Flock** es un clon funcional de Twitter/X desarrollado como challenge técnico full-stack de 72 horas.
Permite registro/login, publicar tweets (280 chars), seguir usuarios, dar likes, ver un timeline personalizado, buscar usuarios y recibir actualizaciones en tiempo real vía SSE.
Tono: producto real, código limpio, buenas prácticas — no un prototipo descartable.

---

## Stack técnico

| Capa | Tecnología | Notas |
|---|---|---|
| Framework frontend | Vite + React 19 + TypeScript | SPA pura — no SSR (app totalmente autenticada, SSR no aporta) |
| Framework backend | Express.js v5 + TypeScript | v5 maneja async/await nativo sin express-async-errors |
| Lenguaje | TypeScript estricto | Ambas apps. Sin `any`. |
| Estilos | Tailwind CSS v4 + shadcn/ui | v4 usa `@tailwindcss/vite`, sin `tailwind.config.js`. Preset Nova con Geist. |
| Animaciones | Framer Motion | Like button (spring), contador de tweets (AnimatePresence) |
| Estado server | TanStack Query v5 | Cache, invalidación, optimistic updates en likes y follows |
| Forms / validación | React Hook Form + Zod | Mismo schema Zod compartible entre frontend y backend |
| Auth | Custom JWT — bcryptjs + jose | `jose` es la implementación moderna del estándar JWT (Web Crypto API) |
| Backend / API | Express.js REST API | 7 features: auth, tweets, timeline, follows, likes, users, search + SSE |
| DB / ORM | PostgreSQL 16 + Prisma 7 | Prisma genera tipos TypeScript desde el schema |
| Real-time | SSE (Server-Sent Events) | Unidireccional server→client — más simple que WebSockets para este caso |
| Testing backend | Vitest + Supertest | 79 tests. Unit (mocks) + Integration (test DB real). Coverage 84%+ branches |
| Testing frontend | Vitest + Testing Library | 17 tests. Login, TweetComposer, TweetCard, FollowButton |
| Deploy | Docker Compose | PostgreSQL + API + Frontend (nginx multi-stage) |

### Comandos

```bash
# Backend
cd backend
npm run dev          # tsx watch src/server.ts → http://localhost:3000
npm run build        # tsc → dist/
npm test             # vitest run (79 tests)
npm run test:coverage # coverage report (threshold 80%)
npm run db:migrate   # prisma migrate dev
npm run db:seed      # tsx prisma/seed.ts (10 users, 20 tweets)

# Frontend
cd frontend
npm run dev          # Vite → http://localhost:5173
npm run build        # tsc -b && vite build
npm test             # vitest run (17 tests)
npm run lint         # eslint

# Todo el stack
docker compose up --build
```

---

## Arquitectura de carpetas

```
twitter-clone/
├── backend/
│   ├── prisma/
│   │   ├── schema.prisma          # Modelos: User, Tweet, Follow, Like
│   │   ├── migrations/
│   │   └── seed.ts                # 10 users, 20 tweets, follows, likes
│   ├── src/
│   │   ├── app.ts                 # Express app + rutas montadas
│   │   ├── server.ts              # Entry point (dotenv + listen)
│   │   ├── features/
│   │   │   ├── auth/              # register, login, logout, me
│   │   │   ├── tweets/            # POST, DELETE, GET /:id
│   │   │   ├── timeline/          # GET con paginación
│   │   │   ├── follows/           # follow, unfollow, followers, following
│   │   │   ├── likes/             # like, unlike
│   │   │   ├── users/             # perfil público, PUT /me
│   │   │   ├── search/            # GET /users?q=
│   │   │   └── stream/            # SSE — GET /stream
│   │   └── shared/
│   │       ├── middlewares/auth.middleware.ts   # requireAuth (Bearer + ?token=)
│   │       ├── types/index.ts                  # AuthRequest
│   │       └── utils/prisma.ts                 # PrismaClient singleton con PrismaPg adapter
│   └── tests/
│       ├── setup.ts               # Apunta DATABASE_URL a test DB
│       ├── helpers.ts             # createTestPrisma, signTestToken, createTestUser, cleanDatabase
│       └── integration/           # auth, tweets, social, users integration tests
├── frontend/
│   └── src/
│       ├── app/                   # Layout, ProtectedRoute, RightSidebar
│       ├── features/
│       │   ├── auth/              # LoginPage, RegisterPage, AuthContext, auth.api
│       │   ├── tweets/            # TweetCard, TweetComposer, tweet.api, tweet.types
│       │   ├── timeline/          # TimelinePage, timeline.api, useTimelineStream (SSE)
│       │   ├── users/             # ProfilePage (tabs), user.api
│       │   └── search/            # SearchPage con debounce
│       └── lib/                   # api.ts (axios), date.ts, useDebounce, useTheme
├── docker-compose.yml
├── CLAUDE.md
├── README.md
├── TECH_DECISIONS.md
└── TODO.md
```

**Decisiones clave de estructura**:
- Feature-based en ambas apps — cada feature es un módulo autocontenido (controller + service + routes + test en backend; page + api + types en frontend).
- En backend: controllers son thin wrappers (solo HTTP), services tienen la lógica de negocio.
- En frontend: TanStack Query gestiona todo el server state; no hay Redux ni Zustand.

---

## Sistema de diseño

### Paleta de colores

El proyecto usa los tokens CSS de shadcn/ui en oklch. Dark mode via clase `.dark` en `<html>`.

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--background` | `oklch(1 0 0)` | `oklch(0.145 0 0)` | Fondo base |
| `--foreground` | `oklch(0.145 0 0)` | `oklch(0.985 0 0)` | Texto principal |
| `--primary` | `oklch(0.205 0 0)` | `oklch(0.922 0 0)` | Botones, nav activo |
| `--muted-foreground` | `oklch(0.556 0 0)` | `oklch(0.708 0 0)` | Timestamps, labels secundarios |
| `--border` | `oklch(0.922 0 0)` | `oklch(1 0 0 / 10%)` | Bordes de tweet, sidebar |
| `--accent` | `oklch(0.97 0 0)` | `oklch(0.269 0 0)` | Hover states |
| `--destructive` | `oklch(0.577 0.245 27.325)` | `oklch(0.704 0.191 22.216)` | Eliminar tweet, errores |

> **Gotcha**: Tailwind v4 no usa `tailwind.config.js`. La config es via `@theme inline` en `index.css`. Los colores se definen como variables CSS (`--color-primary: var(--primary)`) y se consumen como clases Tailwind (`bg-primary`, `text-foreground`).

### Tipografía

- **Fuente**: `Geist Variable` (@fontsource-variable/geist), fallback: `sans-serif`
- **Definida en**: `--font-sans` en `@theme inline` de `index.css`
- **Body**: `text-sm` (tweets, labels), `text-base` (headers de página)
- **Bold**: `font-semibold` en headers, `font-bold` en usernames y contadores

### Jerarquía de botones (shadcn/ui Button)

| Nivel | Variant | Uso |
|---|---|---|
| Acción principal | `default` | Publicar tweet, Seguir, Crear cuenta |
| Acción secundaria | `outline` | Editar perfil, Siguiendo (toggle), Cancelar |
| Acción destructiva | texto rojo inline | Confirmar eliminar tweet (sin botón formal) |
| Ghost / nav | `ghost` | Logout en sidebar |

### Espaciado y layout

- Max-width del layout: `1280px` centrado.
- Columna principal (tweets): `max-w-[600px]`.
- Sidebar izquierda: `w-20` (collapsed, tablet) / `w-64` (expanded, desktop).
- Sidebar derecha: `w-80 xl:w-96` (solo desktop `lg+`).
- Bottom nav móvil: fija, `h-16`, `z-50` — requiere `pb-16 sm:pb-0` en el main.
- Headers de página: `sticky top-0`, `pr-12 sm:pr-4` para dejar espacio al toggle de tema en mobile.

---

## Autenticación

- JWT stateless firmado con `jose` (HS256), expira en 7 días.
- Token se guarda en `localStorage` y se envía como `Authorization: Bearer <token>`.
- Interceptor en axios lee el token automáticamente. En 401 → limpia localStorage + redirect a `/login`.
- El middleware `requireAuth` acepta el token también via query string `?token=` para compatibilidad con SSE/EventSource (que no soporta custom headers).
- No hay refresh tokens — si expira, el usuario vuelve a hacer login.

---

## Real-time (SSE)

- Endpoint: `GET /api/stream` (requiere auth via `?token=`).
- Registro de clientes en memoria (`stream.service.ts`).
- Cuando se crea un tweet, `notifyFollowers(authorId, payload)` emite a todos los clientes conectados excepto el autor.
- Frontend: hook `useTimelineStream` abre EventSource, cuenta nuevos tweets y muestra banner "X nuevos tweets — ver".
- Al clickear el banner: reset del contador + invalidación del cache de timeline.
- **Decisión UX**: no auto-insertar tweets (como hace Twitter) — mostrar el banner primero.

---

## Testing — estrategia

### Backend (Vitest + Supertest)

- **Unit tests**: mockean `prisma` con `vi.mock`. Testean services en aislamiento.
- **Integration tests**: usan `TEST_DATABASE_URL` (DB separada `twitter_clone_test`). Setup en `tests/setup.ts` que sobreescribe `DATABASE_URL`.
- **`fileParallelism: false`** en `vitest.config.ts` — obligatorio para integration tests que comparten la misma DB y se limpian entre tests. Sin esto, los `beforeEach(cleanDatabase)` de distintos archivos se pisaban.
- **Controller tests**: testean que los catch blocks retornan 500 cuando el service tira sin `statusCode`. Esto fue necesario para alcanzar 80%+ de branch coverage (el branch `?? 500` no se cubría de otra forma).

### Frontend (Vitest + Testing Library)

- `vitest.config.ts` independiente del de Vite (no puede importar plugin de tailwindcss).
- Los mocks de `framer-motion` son necesarios porque jsdom no soporta Web Animations API.

---

## Gotchas y decisiones no obvias

1. **Prisma 7 requiere el adapter siempre**: `new PrismaClient()` sin `{ adapter }` tira `PrismaClientInitializationError`. Esto afectó al `seed.ts` que se olvidó de pasar el `PrismaPg adapter`. El singleton en `shared/utils/prisma.ts` es el patrón correcto a seguir.

2. **Express 5 tipea `req.params` como `string | string[]`**: al pasar `req.params.userId` a funciones que esperan `string`, TypeScript tira error. Solución: cast explícito `req.params.userId as string` en todos los controllers.

3. **Desincronización de validaciones frontend/backend**: el frontend tenía `password.min(6)` y el backend `min(8)`. El usuario podía enviar una contraseña de 6 chars que pasaba el form pero el backend rechazaba con 400, mostrando un error genérico. Regla: siempre alinear los schemas Zod entre ambas apps.

4. **Búsqueda con `@` prefix**: los usuarios naturalmente escriben `@alice` para buscar. El frontend debe strip el `@` antes de enviar la query, porque los usernames en DB no tienen `@`.

5. **Dark mode toggle en mobile sobre el header**: el botón `fixed top-3 right-3 h-9` tenía su borde inferior exactamente en el límite del header sticky (`py-3` + 24px texto = ~49px). Solución: `h-8 top-2.5` + `pr-12 sm:pr-4` en los headers.

6. **EventSource no soporta headers custom**: para el SSE el token no puede ir en `Authorization: Bearer`. Se acepta también via `?token=` en el middleware `requireAuth`.

7. **TweetCard follow state es local**: el unfollow en el timeline NO invalida el cache (el tweet no desaparece). El estado `following` vive en el componente con `useState(initialIsFollowing)`. Esto es intencional por UX — no se borra el contenido que ya estabas viendo.

---

## Roles del agente para este proyecto

- **Backend**: arquitectura feature-based, Express 5 async, Prisma 7 con adapter, Zod en controllers, errores con `statusCode` en el objeto Error.
- **Frontend**: React 19, TanStack Query para server state, optimistic updates, no Redux/Zustand.
- **UI / UX**: Tailwind v4 (sin config file), shadcn/ui variants, dark mode via clase `.dark`, mobile-first con breakpoints `sm:` y `lg:`.
- **Testing**: unit tests con `vi.mock` en services, integration tests con test DB real + `fileParallelism: false`.
- **Auth**: JWT stateless, token en localStorage, interceptor axios, `requireAuth` middleware + query param fallback para SSE.

---

## Principios de código aplicados

- **NO estilos inline** — solo clases Tailwind en todos los componentes React.
- **Early returns** — controllers y services usan early return en lugar de pirámides de if/else.
- **Tipado explícito** — props tipadas, sin `any`. Express 5 params requieren cast explícito.
- **Funciones cortas** — services tienen funciones de ≤30 líneas. Helpers de formato separados.
- **Commits atómicos** — un commit por feature + push inmediato. El historial refleja el progreso como historias de usuario.

---

## Personalización rápida (al reusar este template)

| Qué cambiar | Dónde |
|---|---|
| Nombre de la app | `frontend/src/app/Layout.tsx`, `frontend/src/app/RightSidebar.tsx`, `README.md` |
| Trending topics / sugeridos | `frontend/src/app/RightSidebar.tsx` (datos fake hardcodeados) |
| Credenciales seed | `backend/prisma/seed.ts` |
| Puerto de la API | `backend/.env` + `frontend/vite.config.ts` (proxy target) |
| JWT secret | `backend/.env` — nunca commitear el valor real |
| Colores de marca | `frontend/src/index.css` — variables CSS en `:root` y `.dark` |

---

## Match criteria para reuso

Este pattern se ofrece automáticamente en `/charless-ia` cuando la descripción incluye:

- `twitter clone` / `red social` / `microblogging`
- `tweets` / `feed` / `timeline`
- `follows` / `likes` / `social`
- `fullstack` + `React` + `Express` / `Node`
- `REST API` + `PostgreSQL` + `JWT`

Si matchea 2+ señales, la skill ofrece este patrón.

---

## Generado por

- **Fecha**: 2026-06-04
- **Proyecto fuente**: `C:\Users\charly\Desktop\workspace\twitter-clone`
- **Autor**: Carlos Jesus — [portfolio-master-carlos-jesus.vercel.app](https://portfolio-master-carlos-jesus.vercel.app/)
- **Skill**: `/charless-ia` P8.5
