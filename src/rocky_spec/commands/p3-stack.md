> Referencia de **rocky-spec** — Paso P3 del flujo de creación: loop interactivo para confirmar o editar el stack sugerido en P2.

### P3 · Confirma, edita o ampliá el stack (loop interactivo)

Mostrar la sugerencia como tabla:

```
Stack sugerido para tu proyecto:

  Capa       | Elección
  -----------+----------------------------
  Frontend   | React + Vite (TS)
  Backend    | Express
  Estilos    | Tailwind
  Testing    | Vitest
```

Después ofrecer el menú principal:

```
¿Qué hacés con este stack?
> 1) Acepto todo — seguimos a P4
  2) Cambiar una capa
  3) Agregar una herramienta extra (animación, ORM, auth, state, etc.)
  4) Usar un comando libre (algo no listado)
  5) Ver alternativas para todo el stack

(Tipeá el número, o respondé "acepto" / "cambiar X" / "agregar Y" en lenguaje natural)
```

**Loop**: ejecutar la opción elegida, mostrar la tabla actualizada, y volver al menú hasta que el usuario elija 1.

#### Al confirmar (opción 1) — servicios externos

**Antes de la pregunta de TDD**, capturar los servicios de terceros. Preguntar una sola vez:

```
¿El proyecto va a usar algún servicio externo? (email, pagos, storage,
auth, SMS, IA...)

Ejemplos: Resend / SendGrid (email) · Stripe / MercadoPago (pagos) ·
S3 / Cloudinary (archivos) · Clerk / Auth0 (auth) · Twilio (SMS) ·
OpenAI / Anthropic (IA)

(Nombralos, o "ninguno por ahora")
```

Por **cada** servicio mencionado, registrar cuatro datos: **nombre**, **para qué se usa**, **variables de entorno que necesita**, y **estado** (arranca siempre en `pendiente`). Van a la tabla "Servicios externos" de `AGENTS.md` y generan su bloque de tareas en el `TODO.md` (ambos se escriben en P6/P7).

**Por qué se pregunta acá y no se deja para después**: un servicio externo se menciona al pasar en la conversación del stack ("los mails los mando con Resend") y después no queda registrado en ningún lado — no es una feature del `SPEC.md` ni una capa del stack. Sin este paso, la implementación se olvida hasta que alguien nota que la app no manda emails.

**No confundir con la opción 3 del menú** (herramienta extra): una librería que se instala con el gestor de paquetes y vive en el repo es stack; un servicio que necesita cuenta, credenciales y corre fuera del proyecto es servicio externo. Si el usuario nombra un servicio externo dentro de la opción 3, registrarlo acá igual.

**Si alguno de los servicios registrados es de categoría IA** (OpenAI/Anthropic/etc. — no una librería como LangChain o Vercel AI SDK, esas son stack): agregar filas de RNF específicas al `SPEC.md` que ya se aprobó en P1.7 (contenido guardado en `.skill-state.json`, todavía sin escribir a disco — se patchea ahí mismo, se escribe recién en P6 como el resto). Usar el próximo `RNF-N` disponible, tres filas:

| ID | Categoría | Alcance | Requisito | Detalle |
|---|---|---|---|---|
| RNF-N | Costo de IA | Global | costo objetivo por request o por mes (preguntar si no se mencionó, default "sin tope definido — monitorear con el proveedor") | ej. "<$0.01 por request", "<$50/mes en fase MVP" |
| RNF-N+1 | Latencia de IA | Global | latencia p95 objetivo para la respuesta del modelo (default "sin objetivo estricto — depende del proveedor") | ej. "<3s p95 para el endpoint de chat" |
| RNF-N+2 | Fallback de IA | Global | comportamiento si el proveedor no responde o tira error (default "sin fallback definido — el request falla") | ej. "reintentar 1 vez, después degradar a respuesta cacheada/genérica" |

Esto también dispara el checklist OWASP LLM Top 10 de `SECURITY.md` (ver `p5.6-security.md`) — mismo trigger, no hace falta repetir la detección ahí.

Si el usuario dice "ninguno", seguir sin insistir — la tabla queda vacía y se puede sumar después con `/rocky-stack`.

#### Al confirmar (opción 1) — TDD sí o no

Antes de pasar a P4, una sola pregunta binaria — **no asumir que se hace TDD solo porque hay un framework de testing elegido**, son cosas distintas (tener Vitest no implica escribir el test antes del código):

```
Una más antes de seguir: ¿querés hacer TDD en este proyecto?

TDD = escribir el test primero (que falla), después el código mínimo
para que pase, después refactorizar. Fuerza diseño testeable desde el
arranque, pero es más lento al principio.

Si decís que no, se testea después de implementar (o no se testea todo,
según lo que confirmes en Calidad/TODO) — igual de válido, distinto
approach.

1) Sí, TDD                    2) No, testear después / no estricto
```

Guardar la respuesta — determina si `AGENTS.md` incluye el ciclo Red→Green→Refactor como parte del workflow de este proyecto (ver `.rocky-spec/reference/methodologies.md` sección TDD) o no. Si el `profile.md` tiene `default_tdd` seteado, usarlo sin preguntar (con opción de cambiarlo para este proyecto puntual si el usuario lo pide).

#### Opción 2 — Cambiar una capa

```
¿Qué capa querés cambiar?
> 1) Frontend  (actual: React + Vite TS)
  2) Backend   (actual: Express)
  3) Estilos   (actual: Tailwind)
  4) Testing   (actual: Vitest)
  5) Lenguaje  (actual: TypeScript)
```

Cuando elige una capa, mostrar el listado completo de esa capa desde `.rocky-spec/reference/stacks-code.md`. Por ejemplo si elige "Estilos":

```
Opciones de estilos:
> 1) Tailwind CSS         (actual)
  2) shadcn/ui            (Tailwind + componentes prearmados)
  3) MUI (Material UI)
  4) Bootstrap (CSS puro)
  5) React-Bootstrap
  6) Chakra UI
  7) Mantine
  8) Ant Design
  9) styled-components
  10) Emotion
  11) Sass / SCSS
  12) CSS Modules
  13) Otra (la indico)
```

Aceptar número o nombre. Volver a la tabla y al menú principal.

#### Opción 3 — Agregar herramienta extra

Pedir la categoría:

```
¿Qué tipo de herramienta agregamos?
> 1) Animación / motion (Framer Motion, GSAP, Lottie, Three.js, R3F)
  2) State management (Zustand, Redux Toolkit, Jotai, TanStack Query)
  3) Forms + validación (React Hook Form, Zod, Yup)
  4) ORM / DB (Prisma, Drizzle, Mongoose)
  5) Auth (Better Auth, Auth.js, Clerk, Lucia)
  6) i18n
  7) Otra
```

Mostrar opciones de esa categoría desde `.rocky-spec/reference/stacks-code.md` o `stacks-web-animation.md`, agregar al stack. La tabla muestra ahora la fila nueva como "Extra: animación / Framer Motion".

#### Opción 4 — Comando libre

```
¿Qué herramienta querés agregar que no esté en la lista?
- Nombre: <input>
- Comando exacto de instalación: <input>
```

Se agrega al stack como ítem custom. La skill confía en el comando que pegues sin validarlo.

#### Opción 5 — Ver alternativas para todo el stack

Útil cuando el usuario quiere comparar antes de elegir. Mostrar un combo alternativo basado en otro perfil común (ej. si la sugerencia era React+Tailwind, mostrar Vue+Pinia como alternativa).

#### Caso especial: Vite

Cuando el frontend elegido es Vite-based (React, Vue, Svelte, Solid, vanilla), preguntar explícitamente:

```
¿Versión del template?
> 1) TypeScript  (recomendado, default de tu perfil)
  2) JavaScript
```

Y elegir el template correcto: `react` vs `react-ts`, `vue` vs `vue-ts`, etc. Ver `.rocky-spec/reference/stacks-code.md` sección "Vite templates".

