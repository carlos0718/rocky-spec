> Referencia de **rocky-spec** — buenas prácticas de frontend, agnósticas de framework: estructura, estado, rendimiento, datos, errores, seguridad del cliente y testing. P5.9 las usa para derivar el `PRACTICES.md` de un proyecto con interfaz. No repite lo que ya cubren `coding-principles.md` (estilos inline, HTML semántico, tamaño de archivo), `ui-design-guidelines.md` (paletas, espaciado, accesibilidad visual) y `security.md`.

# Buenas prácticas — frontend

Cada sección trae qué hacer, la **señal** de que algo anda mal y **cuándo no aplicarla**. Son guías para decidir, no una lista de verificación para tildar entera: el tamaño del proyecto (P4) decide cuáles pesan. Una landing no necesita una capa de datos con cache; una SPA con un año de vida, sí.

---

## 1 · Componentes y estructura

**Qué hacer**
- Componentes chicos con **una responsabilidad**. Separar lo que dibuja de lo que decide: la lógica de estado y datos va a un hook o composable propio, el componente queda casi puro.
- Preferir **composición** (children, slots, render props) antes que un componente con 15 props de configuración.
- Props **tipadas** explícitamente; no pasar objetos enteros cuando el componente usa dos campos.
- Organizar por feature, no por tipo de archivo, cuando el proyecto pasa de un par de pantallas (ver `architecture-styles/` y `architectures.md`).
- Componentes funcionales con hooks, no clases (salvo código legacy).

**Señal de que falla**: un componente de 400 líneas que hace fetch, transforma datos y renderiza; props que son un `config` con 12 campos opcionales; un cambio de una pantalla que obliga a editar tres carpetas distintas.

**Cuándo NO**: en un Mini/Chico no separar en hooks y capas lo que cabe en un archivo legible. Los límites de tamaño están en `coding-principles.md`.

## 2 · Estado

**Qué hacer**
- **Estado local primero.** Subirlo o volverlo global solo cuando dos componentes lejanos lo necesitan de verdad.
- Distinguir **estado de servidor** (datos que vienen de una API: usar una librería de cache como TanStack Query o SWR) de **estado de cliente** (un modal abierto, un input). Mezclarlos en un mismo store global es la causa más común de estado desincronizado.
- **Derivar, no duplicar**: lo que se puede calcular a partir de otro estado no se guarda como estado aparte.
- Poner en la **URL** el estado que el usuario querría compartir o recargar: filtros, orden, paginación, pestaña activa.

**Señal de que falla**: `useEffect` que copia una prop a un estado; un store global con datos de la API y banderas de UI mezclados; "lo arreglé recargando".

**Cuándo NO**: para una app con dos o tres pantallas, el estado de React/Vue basta; no sumar Redux "por si acaso" (ver YAGNI en `general-principles.md`).

## 3 · Rendimiento

**Qué hacer**
- **Medir antes de optimizar.** Memoización (`useMemo`, `useCallback`, `memo`) solo cuando hay un problema medido, no preventivamente.
- Cargar lo justo: **code splitting por ruta**, imágenes con carga diferida y tamaños declarados (`width`/`height`) para evitar saltos de layout.
- Listas con **keys estables** (un id, no el índice si la lista se reordena).
- Vigilar los Core Web Vitals: **LCP** (carga), **INP** (respuesta a la interacción) y **CLS** (estabilidad visual).
- Poner un **presupuesto de bundle** y revisarlo cuando se suma una dependencia.

**Señal de que falla**: una librería de 200 KB para formatear una fecha; imágenes sin dimensiones; re-renders de toda la pantalla por un cambio en un input.

**Cuándo NO**: no optimizar el rendimiento de algo que nadie notó lento. El costo de una optimización prematura es complejidad que se paga para siempre.

## 4 · Datos y red

**Qué hacer**
- Modelar siempre los **cuatro estados**: cargando, con datos, vacío y error. Una pantalla que solo contempla "con datos" se rompe en producción.
- Manejar **condiciones de carrera**: cancelar o ignorar la respuesta de una request vieja cuando ya hay una más nueva (búsqueda mientras se tipea).
- **Validar la forma de la respuesta** en el borde (un schema como Zod) si el backend no da tipos generados; no asumir que la API cumple el contrato.
- **Optimistic updates** solo con *rollback* si falla, y solo donde el resultado casi siempre es exitoso.
- Nunca poner un `fetch` suelto en un `useEffect` cuando el stack ya trae una librería de datos.

**Señal de que falla**: spinner infinito cuando la request falla; la lista muestra resultados de una búsqueda anterior; `undefined is not a function` porque el backend cambió un campo.

## 5 · Errores

**Qué hacer**
- Un **error boundary** (o el equivalente del framework) por zona de la pantalla, para que un fallo en un widget no tumbe toda la página.
- Mensajes al usuario que digan **qué pasó y qué puede hacer**, no un código interno.
- **Nunca tragar un error** con un `catch` vacío: registrarlo (ver `observability.md`) o mostrarlo.

**Señal de que falla**: pantalla en blanco ante cualquier excepción; `catch (e) {}`; errores que solo aparecen en la consola del usuario.

## 6 · Accesibilidad y estilos

No se duplica acá; se aplican estas reglas ya escritas:
- HTML semántico, cero estilos inline, orden de resolución de estilos → `coding-principles.md`, sección "Reglas de estilo de código".
- Contraste, touch targets, foco visible, breakpoints → `ui-design-guidelines.md`.
- Si el proyecto tiene `ACCESSIBILITY.md` (P5.8), ese checklist manda; `rocky check accessibility` lo audita.

Sumar acá un punto que las otras no cubren: **todo lo que se puede hacer con el mouse se puede hacer con el teclado**, y el foco se mueve de forma predecible al abrir y cerrar un modal.

## 7 · Seguridad en el cliente

**Qué hacer**
- **El cliente no es un límite de confianza.** Cualquier validación o control de acceso hecho solo en el frontend se puede saltear; el backend repite lo importante.
- **Nada secreto en el bundle.** Las variables con prefijo público (`VITE_*`, `NEXT_PUBLIC_*`) terminan en el JavaScript que descarga cualquiera: ahí van URLs y claves *públicas*, nunca una API key privada.
- **XSS**: no insertar HTML de origen externo con `dangerouslySetInnerHTML`, `v-html` o `innerHTML` sin sanitizarlo.
- Guardar tokens de sesión en **cookies `httpOnly`** antes que en `localStorage`, que cualquier script de la página puede leer.

Detalle completo y checklist en `security.md`.

## 8 · Testing

**Qué hacer**
- Testear **comportamiento visible**, no implementación: buscar elementos por rol y texto (Testing Library), no por clase CSS ni por estado interno.
- Muchos tests unitarios de lógica pura (utilidades, hooks), algunos de componentes, y **pocos E2E** para los flujos críticos (login, checkout).
- Un test que se rompe al refactorizar sin cambiar el comportamiento está mal escrito.

**Cuándo NO**: en un prototipo descartable alcanza con probar a mano; ver la decisión de TDD del proyecto en `AGENTS.md`.

## 9 · Tipado

**Qué hacer**: TypeScript en modo estricto, sin `any` (preferir `unknown` y estrechar). Si hay OpenAPI o un schema, **generar los tipos** del contrato en vez de escribirlos a mano.

---

## Herramientas típicas — insumo de `PRACTICES.md`

Se listan como **recomendación**; la skill no instala nada por su cuenta.

| Objetivo | Opciones habituales |
|---|---|
| Linter + formatter | ESLint + Prettier, o Biome (una sola herramienta) |
| Tipos | TypeScript `strict` |
| Tests de componentes | Vitest o Jest + Testing Library |
| E2E | Playwright o Cypress |
| Accesibilidad | `rocky check accessibility`, axe, Lighthouse |
| Rendimiento | Lighthouse, análisis del bundle del build tool |
| Cache de datos | TanStack Query o SWR |
| Validación de respuestas | Zod |

## Cómo lo aplica la skill

- **P4/P6**: usa las secciones 1–3 para decidir cuánta estructura darle al scaffolding según la escala del proyecto.
- **P5.9**: cruza este archivo con el stack (P3) para derivar las prácticas y herramientas de `PRACTICES.md`. Una práctica solo entra si el stack y el SPEC del proyecto la justifican.
