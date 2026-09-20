# Principios de código — referencia canónica

> Este archivo es la fuente de verdad para las **reglas concretas y medibles** de código que la skill `/rocky-spec` aplica al generar y al adoptar proyectos: code smells, tamaño de archivo, separación de tipos, reglas de estilo y reglas base. Los **principios** (SOLID, DRY, KISS, YAGNI, Clean Code), los **patrones de diseño** y las **buenas prácticas por capa** viven en archivos propios — ver "Dónde está lo que se movió" más abajo.
>
> El usuario puede activar/desactivar cada uno en su `~/.claude/profile.md` sección "Principios de código".
> Cada proyecto hereda esa configuración y la guarda en su `AGENTS.md` (importado automáticamente por `CLAUDE.md` en Claude Code).

## Índice

- [Cómo se usa este archivo](#cómo-se-usa-este-archivo)
- [Dónde está lo que se movió](#dónde-está-lo-que-se-movió) — SOLID, principios generales, patrones de diseño
- [Code smells](#code-smells--catálogo-y-señales-de-alerta) — catálogo y señales de alerta
- [Tamaño de archivo](#tamaño-de-archivo--límites-y-cuándo-dividir) — límites y cuándo dividir
- [Separación de tipos e interfaces](#separación-de-tipos-interfaces-y-responsabilidades-por-archivo)
- [Reglas de estilo de código](#reglas-de-estilo-de-código) — estilos inline, HTML semántico, funciones cortas, early returns, etc.
- [Reglas por tipo de proyecto](#reglas-específicas-por-tipo-de-proyecto) — backend, frontend, scripts/CLI
- [Cómo el usuario activa/desactiva](#cómo-el-usuario-activa--desactiva) + [reglas base no-opt-in](#reglas-base--no-son-opt-in)

## Cómo se usa este archivo

- **P4 (Sugiere arquitectura)**: la skill consulta los principios y patrones activos (`solid.md`, `general-principles.md`, `design-patterns.md`) y propone una arquitectura coherente con ellos. Ej. si Repository está activo y el proyecto tiene DB, las carpetas separan `domain/`, `application/`, `infrastructure/`.
- **P6 (Genera archivos base)**: cuando la skill genera código de scaffolding (componentes, configs, etc.), respeta las reglas de estilo activas. Ej. si "no estilos inline" está activo y el stack es React+Tailwind, los componentes ejemplo usan clases Tailwind, no `style={{}}`.
- **Modo Adopción (MA-1.5)**: al adoptar un proyecto existente, la skill corre un health-check rápido contra los límites de tamaño de archivo y los code smells de este documento, y reporta lo que encuentra.
- **AGENTS.md del proyecto** (importado por `CLAUDE.md`): hereda los principios para que cualquier agente futuro en ese proyecto — Claude Code u otro — los respete también.

---

## Dónde está lo que se movió

SOLID, los principios generales y los patrones de diseño tenían su sección acá. Ahora cada uno vive en su propio archivo, con la misma plantilla (qué es, cuándo sí, cuándo no, señal en el código, ejemplo mínimo, cómo lo aplica la skill):

| Antes en este archivo | Ahora en |
|---|---|
| SOLID | `.rocky-spec/reference/solid.md` |
| DRY, KISS, YAGNI, Clean Code | `.rocky-spec/reference/general-principles.md` |
| Repository, Factory, Strategy, Observer, Singleton (y el resto de GoF) | `.rocky-spec/reference/design-patterns.md` |
| MVC / MVVM | `.rocky-spec/reference/architectures.md` — son arquitecturas de UI, no patrones de clases |
| Reglas de Backend/API y Frontend/React | `.rocky-spec/reference/best-practices-backend.md` y `best-practices-frontend.md` |

Este archivo conserva lo que se **mide o se verifica**: los umbrales de tamaño, el catálogo de smells, las reglas de estilo y las reglas base.

---

## Code smells — catálogo y señales de alerta

Un "code smell" no es un bug: el código funciona, pero algo en su forma anticipa problemas de mantenimiento. La skill los usa como señal para sugerir un refactor — nunca los bloquea, siempre los conversa con el usuario primero.

| Smell | Señal concreta | Qué sugerir |
|---|---|---|
| **God File / God Object** | Un archivo hace de todo: UI + lógica + tipos + llamadas a API. Ver umbrales en "Tamaño de archivo" abajo. | Partir por responsabilidad: extraer tipos, extraer lógica pura, extraer subcomponentes. |
| **Long Method** | Una función no entra en pantalla (> 30 líneas, ver Clean Code en `general-principles.md`) o tiene más de 3-4 niveles de anidamiento. | Extraer sub-funciones con nombres descriptivos; aplicar early returns. |
| **Duplicate Code** | El mismo bloque (o casi) aparece en 3+ lugares. | Extraer a función/módulo compartido (DRY) — pero solo si es duplicación real, no accidental (ver la nota de DRY en `general-principles.md`). |
| **Feature Envy** | Una función usa más datos/métodos de OTRO módulo que de los suyos propios. | Mover la función al módulo cuyos datos usa. |
| **Shotgun Surgery** | Un solo cambio de negocio obliga a tocar 5+ archivos distintos. | Señal de que la responsabilidad está mal repartida; consolidar en un solo lugar (a veces es DRY al revés: falta abstracción). |
| **Primitive Obsession** | Usar `string`/`number` sueltos para conceptos con reglas propias (email, dinero, IDs). | Crear un tipo/value object (`type Email = string` con validación, o una clase `Money`). |
| **Long Parameter List** | Una función recibe 4+ parámetros posicionales. | Agrupar en un objeto de opciones (`{ userId, email, role }`) o usar builder. |
| **Data Clumps** | Los mismos 3-4 campos viajan juntos por todos lados como parámetros sueltos (`street, city, zip` repetido). | Agruparlos en un tipo/struct propio (`Address`). |
| **Speculative Generality** | Abstracciones, flags o parámetros "por si en el futuro..." que nadie usa hoy. | Aplicar YAGNI (`general-principles.md`) — eliminar hasta que haga falta de verdad. |
| **Comments as Deodorant** | Un comentario largo explicando qué hace un bloque confuso, en vez de renombrar/reestructurar. | Reescribir con nombres claros; el comentario debería explicar el "por qué", no el "qué" (ver Clean Code en `general-principles.md`). |
| **Dead Code** | Funciones, imports o ramas de `if` que ya nadie ejecuta. | Borrar. Git guarda el historial; no hace falta comentarlo "por las dudas". |

**Cómo lo aplica la skill**: en **P6** evita introducir estos smells al generar código nuevo. En **Modo Adopción (MA-1.5)** los busca en el código existente y los reporta — sin refactorizar nada sin permiso explícito del usuario.

## Tamaño de archivo — límites y cuándo dividir

Esto es una extensión natural de "Funciones < 30 líneas": el mismo principio aplica un nivel más arriba, al archivo completo. Un archivo enorme es casi siempre un God File — mezcla responsabilidades que deberían vivir separadas.

| Tipo de archivo | Ideal | Revisar si supera | Dividir sí o sí si supera |
|---|---|---|---|
| Componente UI (React/Vue/Svelte) | < 150 líneas | 250 | 400 |
| Función / método individual | < 30 líneas | 30 | 60 |
| Servicio / hook / composable | < 200 líneas | 300 | 400 |
| Archivo de tipos/interfaces | sin límite estricto (son declaraciones, no lógica) | 300 | 500 — pero dividir por **dominio**, no por tamaño a secas (ver sección siguiente) |
| Config / constantes | sin límite práctico (son datos, no lógica) | — | — |
| Tests | pueden ser más largos que el código que testean | 500 | dividir por `describe`/escenario |
| Markdown / docs | < 500 líneas | 500 | aplicar progressive disclosure: índice liviano + archivos de referencia (exactamente lo que se hizo con el `SKILL.md` de esta misma skill) |

**Qué hacer cuando un archivo crece de más:**

1. **Separar tipos/interfaces** a su propio archivo (ver sección siguiente) — suele ser el primer aire que gana un archivo grande.
2. **Extraer subcomponentes** (UI) con su propia responsabilidad visual.
3. **Extraer hooks/composables custom** — lógica de estado que no es puramente visual.
4. **Extraer funciones puras** (sin side-effects) a un módulo de utils/helpers del dominio, no a un `utils.ts` genérico de toda la app.
5. **Separar constantes/config** que no cambian en runtime.

**Cómo lo aplica la skill**: en **P6**, si el scaffolding generado para un paso ya anticipa que un archivo va a crecer (ej. un componente de formulario complejo), lo genera ya dividido desde el principio en vez de esperar a que sea grande. En **Modo Adopción (MA-1.5)**, mide los archivos existentes contra esta tabla y reporta los que están en zona "revisar" o "dividir".

**Regla dura, no negociable**: si un archivo supera las **1000 líneas**, sin importar el tipo, la skill lo marca 🔴 en cualquier reporte (P8 o MA-2) y lo prioriza como primer ítem de deuda técnica en el TODO — no hay "tipo de archivo" que lo justifique.

## Separación de tipos, interfaces y responsabilidades por archivo

**Regla base**: cuando un archivo mezcla declaraciones de tipos con lógica de implementación, y el archivo ya está en zona "revisar" (ver tabla arriba) o el tipo se usa en 2+ archivos, separar los tipos a su propio archivo.

**TypeScript:**
- Un tipo/interface usado en un solo archivo y simple (< 10 líneas) puede quedar inline arriba del archivo que lo usa.
- Un tipo/interface usado en 2+ archivos, o un archivo con 3+ declaraciones de tipo → sacarlas a `<entidad>.types.ts` (co-ubicado junto a la entidad) o a `types/` si son transversales a todo el proyecto.
- Convención sugerida por default: `types/` por dominio (`types/user.ts`, `types/order.ts`) en vez de un único `types.ts` gigante — el mismo principio de "dividir por dominio, no por tamaño a secas" de la tabla anterior.
- Barrel file opcional (`types/index.ts`) re-exportando, solo si el proyecto ya usa el patrón de barrels en otros lados (no introducirlo si no es la convención del proyecto).

**Equivalentes en otros lenguajes del stack:**
- **Python**: modelos/schemas (Pydantic, dataclasses) en `schemas.py` o `models/`, separados de la lógica de negocio y de los handlers/routers.
- **Go**: structs y interfaces en `types.go` o un package `types` propio, separados de la lógica que los usa.
- **Rust**: `struct`/`trait`/`enum` en un módulo dedicado (`types.rs` o `domain/`) separado de la implementación.

**Por qué importa:**
- Un archivo de tipos se puede importar desde cualquier lado sin arrastrar lógica de implementación (evita dependencias circulares).
- Cambiar la forma de un dato no obliga a tocar el archivo que además tiene la lógica — reduce el blast radius de un cambio (ver Shotgun Surgery arriba).
- Hace el archivo de implementación más corto y enfocado en UNA cosa (Single Responsibility, ver `solid.md`).

**Cómo lo aplica la skill**: en **P6**, si el stack elegido es TypeScript (u otro lenguaje tipado) y la entidad del dominio (definida en P1.7) tiene 2+ campos o se comparte entre capas, genera el archivo de tipos separado desde el arranque en vez de esperar a que el archivo crezca.

---

## Reglas de estilo de código

### NO usar estilos inline — regla base, siempre activa

> Esta regla NO es opt-in del perfil: aplica por default a **todo** proyecto con interfaz visual generado por `/rocky-spec`, independientemente de lo que diga `profile.md`. Salvo correcciones puntuales muy menores (un margin específico de 3px, un color override en un caso edge).

**Orden de prioridad para resolver estilos:**

1. **Clases del framework/librería del stack elegido** — si el proyecto usa Tailwind, Bootstrap, Bulma, etc., usar esas clases.
2. **Sistema de estilos del framework** — CSS Modules, styled-components, Emotion, Sass si el stack los incluye.
3. **Archivo `.css` propio** — si el stack es HTML/CSS/JS vanilla o no tiene sistema de clases, crear un archivo `styles.css` (o uno por componente) y enlazarlo. Nunca dejar el estilo flotando inline porque "no hay framework".

**Anti-patrón en React/JSX**:
```jsx
<div style={{ display: 'flex', padding: '20px', backgroundColor: '#fff' }}>
```

**Correcto (Tailwind)**:
```jsx
<div className="flex p-5 bg-white">
```

**Correcto (CSS Modules / styled-components / Sass)**:
```jsx
<div className={styles.container}>
```

**Correcto (HTML/CSS/JS vanilla — sin framework)**:
```html
<!-- index.html -->
<link rel="stylesheet" href="styles.css">
<div class="card">...</div>
```
```css
/* styles.css */
.card {
  display: flex;
  padding: 20px;
  background-color: #fff;
}
```

**Por qué**:
- Los inline styles ignoran el sistema de tokens del proyecto (no respetan dark mode, no usan paleta).
- No se puede reutilizar.
- Mata el caché de CSS del navegador.
- Más pesados que clases.

**Excepción aceptable**: valores dinámicos calculados en runtime (ej. `style={{ width: progress + '%' }}` en una barra de progreso). Para esos casos sí, inline está bien.

### Etiquetas semánticas HTML — regla base, siempre activa (SEO + accesibilidad)

> Tampoco es opt-in: aplica a todo proyecto con HTML generado, sea React/Vue/Astro o HTML plano.

Priorizar etiquetas semánticas sobre `<div>` genérico cuando la semántica del contenido lo permite:

| Usar                | En vez de                          | Para                                  |
|---------------------|-------------------------------------|----------------------------------------|
| `<header>`          | `<div class="header">`              | Cabecera de página o sección          |
| `<nav>`              | `<div class="nav">`                 | Bloques de navegación / menús         |
| `<main>`             | `<div id="main">`                   | Contenido principal (uno por página)  |
| `<article>`          | `<div class="post">`                | Contenido autocontenido (post, card de producto) |
| `<section>`          | `<div class="section">`             | Agrupación temática de contenido      |
| `<aside>`            | `<div class="sidebar">`             | Contenido relacionado/secundario      |
| `<footer>`           | `<div class="footer">`              | Pie de página o sección               |
| `<figure>`+`<figcaption>` | `<div>` con `<img>` + `<span>` | Imágenes con leyenda                  |
| `<button>`           | `<div onClick>`                    | Cualquier elemento clickeable de acción |
| `<a href>`           | `<div onClick>` con navegación      | Cualquier elemento que navega         |

**Por qué importa para SEO:**
- Los motores de búsqueda usan la estructura semántica para entender jerarquía y relevancia del contenido (qué es navegación vs contenido principal vs relleno).
- `<h1>`–`<h6>` deben seguir orden jerárquico sin saltos (no pasar de `<h1>` a `<h3>` sin `<h2>`).
- Listas reales (`<ul>`/`<ol>`/`<li>`) en vez de `<div>` repetidos para contenido tipo lista.

**Por qué importa para accesibilidad:**
- Lectores de pantalla anuncian la estructura semántica (landmarks) — un usuario con screen reader puede saltar directo a `<nav>` o `<main>` con un atajo de teclado.
- `<div onClick>` no es focuseable ni anunciado como interactivo sin trabajo extra de ARIA — `<button>` y `<a>` lo traen gratis.

**Excepción aceptable**: `<div>` y `<span>` siguen siendo correctos para agrupar elementos puramente visuales sin significado semántico propio (un wrapper de flexbox, un ícono decorativo).

### Funciones < 30 líneas

Guideline, no regla dura. Si pasa de 30, preguntarse si está haciendo más de una cosa.

### Nombres > Comentarios

Si necesitás un comentario para explicar QUÉ hace el código, probablemente el nombre de la función/variable está mal elegido.

### Early returns

Salir temprano cuando hay condiciones inválidas, en vez de anidar.

```ts
// Anti-patrón
function process(user) {
  if (user) {
    if (user.active) {
      if (user.permissions.includes('read')) {
        // hacer cosas
      }
    }
  }
}

// Correcto
function process(user) {
  if (!user) return;
  if (!user.active) return;
  if (!user.permissions.includes('read')) return;
  // hacer cosas
}
```

### Magic numbers / strings → constantes nombradas

```ts
// Anti-patrón
if (user.age >= 18) { ... }

// Correcto
const LEGAL_AGE = 18;
if (user.age >= LEGAL_AGE) { ... }
```

### Imports ordenados

Por convención: externos → internos → relativos. Configurable con ESLint plugin `import/order` o Biome equivalente.

### Tipado siempre que se pueda

En TS, evitar `any`. Preferir tipos explícitos sobre `unknown` cuando se sabe la forma.

---

## Reglas específicas por tipo de proyecto

- **Backend / API** y **Frontend**: sus reglas (validación en el borde, errores centralizados, logs estructurados; componentes funcionales, estado local primero, memoización solo con problema medido, props tipadas) viven ahora en `best-practices-backend.md` y `best-practices-frontend.md`, con su señal de falla y su "cuándo NO".

### Scripts / CLI

- Argumentos parseados con librería (clap en Rust, yargs/commander en Node, click en Python), no slicing manual de `process.argv`.
- Mensajes de error útiles con código de salida distinto de 0.

---

## Cómo el usuario activa / desactiva

En `~/.claude/profile.md` sección "Principios de código", marcar los checkboxes. Default sugerido para perfiles que no especifican: SOLID, Repository, DRY, KISS, YAGNI, Clean Code, "no inline styles", "early returns", "tipado explícito" → todos activos.

Para proyectos individuales, el usuario puede sobrescribir en el `AGENTS.md` del proyecto:

```markdown
## Principios aplicados a este proyecto
Heredados del perfil global, con esta excepción:
- KISS desactivado para este proyecto: necesito una arquitectura compleja porque es enterprise.
```

### Reglas base — no son opt-in

A diferencia de los principios (SOLID, DRY, etc. — ver `solid.md` y `general-principles.md` — configurables por perfil), estas **siempre se aplican**, sin importar lo que diga `profile.md`:

- **NO usar estilos inline** (clases del framework → sistema de estilos del framework → archivo `.css` propio, en ese orden de prioridad) — solo proyectos con interfaz visual.
- **Etiquetas semánticas HTML** (header/nav/main/article/section/aside/footer en vez de div genérico) — solo proyectos con interfaz visual.
- **Límite de tamaño de archivo** — cualquier proyecto de código. Ver tabla en "Tamaño de archivo — límites y cuándo dividir". El umbral de 1000 líneas es regla dura sin excepción de tipo de archivo.
- **Separar tipos/interfaces cuando corresponda** — cualquier proyecto con lenguaje tipado (TypeScript, Python con type hints, Go, Rust). Ver "Separación de tipos, interfaces y responsabilidades por archivo".

Si el usuario pide explícitamente desactivarlas para un proyecto puntual, se puede, pero hay que confirmarlo antes:
> "Por default este proyecto va a usar HTML semántico, cero estilos inline, y límites de tamaño de archivo (reglas base de la skill, no del perfil). ¿Querés que desactive alguna para este proyecto en particular?"
