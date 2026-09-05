# Development Methodologies

Este archivo documenta las metodologías de desarrollo que usa la skill `/rocky-spec` al crear proyectos. Cada proyecto generado aplica **SDD** para definir el alcance, **DDD** para modelar el dominio (proyectos con backend/DB), **TDD** durante el desarrollo de cada feature, y **BDD** para documentar comportamientos en iteraciones futuras.

---

## Specification-Driven Development (SDD)

**Cuándo:** Antes de escribir cualquier línea de código.

SDD establece que toda feature debe tener una spec antes de ser implementada. El código existe para satisfacer la spec, no al revés.

### SDD no es una sola cosa — 3 niveles

SDD es una familia de enfoques, no un estándar único. La terminología más citada (Birgitta Böckeler, ThoughtWorks) distingue tres niveles de madurez:

| Nivel | Qué significa | Quién lo implementa |
|---|---|---|
| **Spec-First** | La spec genera el plan y el código una vez. Después de implementar, nada obliga a mantenerla sincronizada — con el tiempo queda desactualizada. | Flujo básico de GitHub Spec Kit, Amazon Kiro |
| **Spec-Anchored** | La spec es un documento **vivo**: evoluciona junto con el código en cada cambio de alcance. Es el balance más práctico para la mayoría de los equipos. | Spec Kit y Kiro usados con disciplina, BMad |
| **Spec-as-Source** | La spec es el **único** artefacto editado por humanos; el código se regenera a partir de ella (más parecido a un compilador que a "escribir código"). | Tessl, OpenSpec |

**`rocky-spec` implementa SDD en el nivel Spec-Anchored.** `SPEC.md` se genera en P1.7 (o MA-3 en Modo Adopción) y se actualiza — no se re-escribe desde cero — cada vez que el alcance cambia. Ver `.rocky-spec/templates/SPEC.md.template` (incluye una sección de Historial de cambios) y `AGENTS.md` del proyecto generado, sección "Agregar o modificar features (Spec-Anchored)", para el mecanismo exacto.

### ¿SDD es un framework o una skill?

Depende de la implementación, y vale la pena tener claro en cuál estamos parados:

- **Como framework standalone**: herramientas como **GitHub Spec Kit** (CLI en Python, comando `specify init`, workflow propio Constitution → Specify → Plan → Tasks → Implement) o **Amazon Kiro** son productos separados que instalás en el proyecto. Traen su propia estructura de carpetas, sus propios comandos, y funcionan con cualquier agente de código (Claude Code, Copilot, Cursor, etc.) porque son agnósticos de agente — el framework le da instrucciones al agente, no al revés.
- **Como skill (lo que hace `rocky-spec`)**: acá no hay una herramienta separada que instalar. La disciplina de SDD está **encodeada directamente en el comportamiento de la skill** — es la skill la que sabe cuándo generar el spec, cuándo actualizarlo, y en qué archivo. No hay un `specify init` porque no hace falta: el flujo P1→P8 ya cubre ese rol, y Modo Resume/Adopción cubren el mantenimiento continuo del spec en vez de un comando aparte.
- **Trade-off**: un framework standalone (Spec Kit) funciona igual sin importar qué agente uses. Nuestra skill es más liviana (no hay nada que instalar en el proyecto, todo vive en `~/.claude/skills/`) pero está atada a que el agente use esta skill — si mañana el usuario abre el proyecto con otro agente sin la skill instalada, ese agente no sabe que existe el mecanismo de Spec-Anchored, aunque sí va a poder leer `SPEC.md` y `AGENTS.md` como texto plano (son solo Markdown). Por eso el proyecto generado siempre incluye `AGENTS.md`: cualquier agente, tenga o no la skill, puede seguir las reglas ahí escritas.

### Otras herramientas del ecosistema (no son SDD, pero son relevantes)

- **OpenCode**: no es un framework de SDD — es un agente de código alternativo (como Claude Code, pero open-source y agnóstico de proveedor de modelo). No compite con SDD, compite con la herramienta que ejecuta el flujo. Es relevante acá solo porque, si el usuario o su equipo lo usan en el mismo proyecto, van a depender de `AGENTS.md` (no de esta skill ni de `CLAUDE.md`) para conocer las convenciones — otra razón para que `AGENTS.md` sea siempre el archivo completo y actualizado.
- Este panorama cambia rápido — si en el momento de leer esto ya hay novedades sobre Spec Kit, Kiro, Tessl u OpenCode, vale la pena confirmarlo con una búsqueda antes de asumir que este resumen sigue vigente.

### En la práctica

Al crear un proyecto con `/rocky-spec`, se genera un `SPEC.md` en la raíz que define:
- El objetivo del proyecto en 2-3 líneas
- Las features del MVP ordenadas por prioridad (P0/P1/P2)
- User stories clave
- Modelos de datos y API contracts (si aplica)
- Criterios de aceptación del MVP
- Qué queda **fuera** del alcance v1 (evitar scope creep)

### Flujo SDD

```
Descripción del proyecto
        ↓
    SPEC.md aprobado
        ↓
   Diseño del sistema (stack, arquitectura, design system)
        ↓
   Implementación (el código satisface el spec)
        ↓
   Criterios de aceptación verificados
```

### Mantener el spec actualizado (el mecanismo de Spec-Anchored)

Cada vez que se agrega una feature nueva o se cambia el alcance:
1. Actualizar `SPEC.md` primero — incluyendo una línea nueva en su sección "Historial de cambios"
2. Mover features completadas a la sección ✅
3. Documentar qué quedó fuera de alcance y por qué

Este mecanismo está documentado también en el `AGENTS.md` de cada proyecto generado (sección "Agregar o modificar features"), para que cualquier agente que trabaje en el proyecto lo respete, no solo Claude Code.

**El límite de este mecanismo:** depende de que alguien *anuncie* la feature nueva en la conversación antes de escribir código. Si el código cambia sin ese anuncio (una tarea "se estira" un poco de más, un fix termina agregando algo nuevo), nada lo detecta solo. Para cubrir ese caso, `AGENTS.md` incluye un **Spec Drift Check** heurístico (paso 0 del Workflow de Git, sección "Spec Drift Check — el paso 0 en detalle"): antes de cada commit, greppea el diff en busca de rutas, tablas de DB o entidades de dominio nuevas que no estén mencionadas en `SPEC.md`, y si encuentra alguna, pregunta antes de commitear. Es un heurístico estructural, no semántico — no reemplaza el anuncio conversacional, lo complementa para los casos que se cuelan.

### Snapshots de fase — carpeta `specs/`

`SPEC.md` en la raíz es siempre el vivo — el de "ahora". Pero un proyecto real pasa por fases (MVP, v2, la versión que agregó pagos, etc.), y cuando una fase se cierra, tiene sentido congelar una foto de "qué decíamos que era el alcance en ese momento" antes de seguir editando el spec para lo que viene. Para eso existe `specs/<fase>/SPEC.md` — no reemplaza el spec vivo, lo complementa como archivo histórico.

**Cuándo se dispara**: nunca automático — es una decisión explícita del usuario. Frases típicas: "el MVP está listo", "cerremos esta fase", "arranquemos la v2", "quiero congelar el spec como está ahora".

**Mecanismo**:
1. Preguntar el nombre de la fase si no es obvio por el contexto: *"¿Cómo le decimos a esta fase? (ej. `mvp`, `v2-marketplace`, `beta-publica`)"*
2. Crear `specs/<nombre-slug>/` (slug: minúsculas, guiones, sin espacios).
3. Copiar el `SPEC.md` actual, tal cual está, a `specs/<nombre-slug>/SPEC.md` — es una foto congelada, no se vuelve a editar después.
4. Agregar una línea en el "Historial de cambios" del `SPEC.md` de la raíz: `{{fecha}} | Fase "<nombre>" cerrada — snapshot en specs/<nombre-slug>/SPEC.md | {{commit}}`.
5. El `SPEC.md` de la raíz sigue vivo y se sigue editando normalmente para lo que sigue — este mecanismo no lo pausa ni lo reemplaza.

**Relación con `CHANGELOG.md`/tags** (ver `.rocky-spec/reference/versioning.md`): son mecanismos parecidos pero no son lo mismo. Un release (tag `vX.Y.Z`) marca un punto exacto del código. Un snapshot de fase marca un punto del **alcance acordado**, con el nombre que el equipo le puso a esa etapa — pueden coincidir en el tiempo (cerrar el MVP y taguear `v1.0.0` el mismo día) pero no tienen por qué: se puede cerrar una fase de spec sin hacer un release de código todavía, o al revés.

**No reemplaza Spec Kit ni sus specs por feature**: Spec Kit organiza `specs/` por feature individual (`specs/001-user-auth/`), pensado para equipos que corren un ciclo specify→plan→tasks→implement por cada capacidad nueva. Acá elegimos organizarlo por fase del producto porque encaja mejor con el modelo Spec-Anchored (un spec vivo, no uno por feature) — si en algún momento hace falta trackear specs por feature individual en vez de por fase, es una extensión de este mismo mecanismo, no un reemplazo.

---

## Test-Driven Development (TDD)

**Cuándo:** Solo si el usuario eligió TDD explícitamente en P3 (pregunta "¿querés hacer TDD en este proyecto?") — no es un default silencioso. Tener un framework de testing elegido (Vitest, Jest, pytest) no implica TDD; son decisiones independientes: una es *con qué* se testea, la otra es *cuándo* se escribe el test respecto al código.

Si el usuario no eligió TDD, el proyecto igual tiene tests (ver "Calidad" en `TODO.md`) — solo que se escriben después de implementar, no antes. Ninguno de los dos caminos es "el correcto"; TDD fuerza diseño testeable desde el arranque a cambio de ser más lento al principio.

TDD garantiza que el código hace exactamente lo que el spec dice, y que los cambios futuros no rompen funcionalidad existente.

### Ciclo Red → Green → Refactor

```
1. RED    → Escribir un test que falla para la funcionalidad a implementar
2. GREEN  → Escribir el mínimo código necesario para que el test pase
3. REFACTOR → Mejorar el código sin romper los tests
```

### En la práctica

```typescript
// 1. RED — el test falla porque la función no existe todavía
it("should calculate total with tax", () => {
  expect(calculateTotal(100, 0.21)).toBe(121);
});

// 2. GREEN — implementación mínima
function calculateTotal(amount: number, tax: number): number {
  return amount + amount * tax;
}

// 3. REFACTOR — mejorar sin romper
function calculateTotal(amount: number, taxRate: number): number {
  return parseFloat((amount * (1 + taxRate)).toFixed(2));
}
```

### Comandos del proyecto

```bash
npm test              # corre todos los tests
npm test -- --watch   # modo watch (ideal para TDD activo)
npm run test:coverage # coverage report
```

### Qué testear con TDD

- Funciones de negocio puras (cálculos, transformaciones, validaciones)
- Handlers de API (request → response)
- Componentes con lógica compleja
- Casos edge: null, undefined, strings vacíos, arrays vacíos, números negativos

### Qué NO necesita TDD estricto

- Componentes puramente visuales sin lógica
- Configuración de herramientas (tailwind.config, vite.config)
- Migraciones de base de datos

---

## Behavior-Driven Development (BDD)

**Cuándo:** Para definir y documentar el comportamiento de features nuevas, especialmente en iteraciones futuras del proyecto.

BDD conecta el lenguaje de negocio con los tests técnicos usando Given/When/Then, haciendo que los criterios de aceptación sean directamente ejecutables.

> **Three Amigos:** la práctica de revisar una historia entre quien la define (negocio/Analista Funcional), quien la prueba (QA) y quien la programa, antes de escribir código — el origen del formato Given/When/Then es justamente hacer que esa conversación produzca algo directamente testeable. La skill aplica esta misma idea al cierre de la planificación, en **P7.5 (Revisión funcional y de QA)** — ver `.rocky-spec/commands/p7.5-qa-review.md`.

### Sintaxis Gherkin

```gherkin
Feature: [nombre de la feature]

  Scenario: [caso de uso específico]
    Given [el estado inicial del sistema]
    When  [la acción que realiza el usuario]
    And   [acción adicional si necesario]
    Then  [el resultado esperado]
    And   [resultado adicional si necesario]
```

### Ejemplo real

```gherkin
Feature: Autenticación de usuarios

  Scenario: Login exitoso con credenciales válidas
    Given el usuario está en la página de login
    When ingresa el email "user@example.com" y la contraseña correcta
    And hace click en "Ingresar"
    Then es redirigido al dashboard
    And ve su nombre en el header

  Scenario: Credenciales incorrectas
    Given el usuario está en la página de login
    When ingresa una contraseña incorrecta
    Then ve el mensaje "Email o contraseña incorrectos"
    And permanece en la página de login
    And el campo de contraseña se limpia

  Scenario: Intentos fallidos repetidos
    Given el usuario falló el login 3 veces consecutivas
    When intenta ingresar de nuevo
    Then ve el mensaje "Cuenta bloqueada temporalmente"
    And recibe un email de recuperación
```

### BDD con Vitest (sin Cucumber)

Si no querés instalar Cucumber, podés escribir BDD-style en Vitest:

```typescript
describe("Feature: User Authentication", () => {
  describe("Scenario: Successful login with valid credentials", () => {
    it("Given user is on login page, When they enter valid credentials, Then they are redirected to dashboard", async () => {
      // arrange
      renderLoginPage();
      // act
      await userEvent.type(screen.getByLabelText("Email"), "user@example.com");
      await userEvent.type(screen.getByLabelText("Password"), "validPass123");
      await userEvent.click(screen.getByRole("button", { name: "Ingresar" }));
      // assert
      expect(window.location.pathname).toBe("/dashboard");
    });
  });
});
```

### BDD con Playwright (E2E)

```typescript
test.describe("Feature: Checkout flow", () => {
  test("Scenario: Complete purchase with valid card", async ({ page }) => {
    // Given
    await page.goto("/cart");
    await expect(page.getByText("2 items")).toBeVisible();
    // When
    await page.getByRole("button", { name: "Proceed to checkout" }).click();
    await page.getByLabel("Card number").fill("4242 4242 4242 4242");
    await page.getByRole("button", { name: "Pay now" }).click();
    // Then
    await expect(page.getByText("Order confirmed")).toBeVisible();
  });
});
```

### Cómo usar BDD en iteraciones futuras

Antes de implementar una feature nueva en este proyecto:

1. **Escribir los scenarios BDD** en lenguaje natural (con el equipo o el cliente si aplica)
2. **Convertirlos en tests** (Playwright para E2E, Vitest para unitarios)
3. **Confirmar que los tests fallan** (Red)
4. **Implementar la feature** hasta que los tests pasen (Green)
5. **Refactorizar** sin romper los tests

Los scenarios BDD también sirven como documentación viva — cualquiera puede leer `login.feature` y entender exactamente cómo funciona el login sin leer el código.

---

---

## Domain-Driven Design (DDD)

**Cuándo:** Junto con SDD, antes de codear. Solo para proyectos con lógica de negocio y persistencia (fullstack, backend, API). Para frontend puro o scripts: omitir.

DDD propone pensar el software desde las **entidades y reglas del negocio** hacia afuera, en vez de arrancar desde la interfaz o desde la tecnología. La idea central: el código debe hablar el mismo idioma que el negocio (ubiquitous language).

### Por qué importa el orden

En un proyecto fullstack, todo se deriva del dominio:

```
Entidades del dominio (qué existe en el negocio)
        ↓
Schema de DB (cómo se persisten esas entidades)
        ↓
Repositorios (cómo se accede a los datos — abstracción)
        ↓
Servicios / lógica de negocio (las reglas que operan sobre las entidades)
        ↓
API / endpoints (cómo el mundo exterior accede a los servicios)
        ↓
Frontend / UI (cómo el usuario interactúa con la API)
```

Si arrancás al revés (primero los componentes, después ves qué datos necesitan), terminás con una DB que sigue la forma de tu UI en vez de la forma de tu negocio — y eso genera deuda técnica difícil de corregir.

### Conceptos clave de DDD aplicados

| Concepto | Qué es | Ejemplo |
|---|---|---|
| **Entity** | Objeto con identidad propia que persiste | `User`, `Order`, `Product` |
| **Value Object** | Dato inmutable sin identidad propia | `Money`, `Address`, `Email` |
| **Aggregate** | Grupo de entidades que se tratan como unidad | `Order` + `OrderItems` |
| **Repository** | Abstracción del acceso a datos | `OrderRepository.findById()` |
| **Service** | Lógica que no pertenece a ninguna entidad | `PaymentService.charge()` |
| **Ubiquitous Language** | Nombres del dominio que se usan igual en el código y en las conversaciones | Si el negocio dice "Pedido", el código dice `Order` — no `Cart`, no `Transaction` |

### Flujo de análisis de dominio en P1.7

Antes de generar el SPEC.md, la skill hace 3 preguntas para extraer el modelo de dominio:

1. **¿Cuáles son las entidades principales?** → `User`, `Product`, `Order`, `Post`, etc.
2. **¿Cómo se relacionan?** → "un User tiene muchos Orders", "un Order tiene muchos Products"
3. **¿Cuáles son las reglas de negocio críticas?** → "el stock no puede ser negativo", "solo admins pueden publicar"

Con esas respuestas se genera el diagrama de entidades y el schema de DB inferido, que quedan en el SPEC.md como punto de partida.

### Estructura de carpetas que refleja DDD

Para proyectos donde DDD aplica, la arquitectura de P4 separa las capas:

```
src/
  domain/              # entidades, value objects, interfaces de repositorio
    entities/
      User.ts
      Order.ts
    repositories/
      UserRepository.ts     ← interface (contrato)
      OrderRepository.ts
  application/         # servicios con lógica de negocio
    UserService.ts
    OrderService.ts
  infrastructure/      # implementaciones concretas (DB, HTTP, etc.)
    persistence/
      UserRepositoryImpl.ts  ← implementación real con Prisma/Drizzle
      OrderRepositoryImpl.ts
    http/
      routes/
  presentation/        # controllers, handlers, response mappers
    api/
      userController.ts
```

### DDD + TDD — la combinación ideal

Una vez definido el dominio:
1. Los **repositorios son interfaces** → se pueden mockear fácilmente en tests
2. Los **servicios reciben interfaces** → la lógica de negocio es testeable sin DB
3. Los tests de dominio son los más rápidos y los más estables

```typescript
// domain/repositories/OrderRepository.ts
export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

// application/OrderService.ts
export class OrderService {
  constructor(private repo: OrderRepository) {}

  async placeOrder(userId: string, items: OrderItem[]): Promise<Order> {
    // lógica de negocio pura, sin imports de Prisma ni DB
  }
}

// tests/OrderService.test.ts
const mockRepo: OrderRepository = {
  findById: vi.fn(),
  save: vi.fn(),
};
const service = new OrderService(mockRepo);
// → test rápido, sin DB, sin red
```

---

## Resumen — cuándo usar cada una

| Metodología | Momento                          | Artefacto                            | ¿Aplica a qué proyectos?          |
|-------------|----------------------------------|--------------------------------------|-----------------------------------|
| SDD         | Antes de codear                  | `SPEC.md`                            | Todos                             |
| DDD         | Junto con SDD (análisis previo)  | Diagrama de entidades + schema de DB | Fullstack, backend, API           |
| TDD         | Durante el desarrollo            | Tests unitarios / integración        | Todos con lógica testeable        |
| BDD         | Iteraciones futuras              | Scenarios Gherkin / E2E tests        | Todos con flujos de usuario       |
