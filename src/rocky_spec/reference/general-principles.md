> Referencia de **rocky-spec** — principios generales de código, activos por default: DRY, KISS, YAGNI, Clean Code y composición sobre herencia. Cada uno con cuándo aplicarlo, cuándo no y cómo se ve cuando se viola. Complementa a `solid.md` y frena su exceso.

# Principios generales

Son heurísticas, no leyes. Varias **se contradicen entre sí** según el caso (DRY quiere abstraer, YAGNI quiere esperar) — por eso cada una trae su "cuándo NO". Al final hay una tabla de tensiones para decidir cuál pesa más.

El usuario puede desactivar cada una en su `profile.md` (sección "Principios de código"); el proyecto hereda esa configuración en su `AGENTS.md`.

---

## DRY — Don't Repeat Yourself

**Qué dice**: no duplicar **conocimiento**, no necesariamente código. Si la misma regla de negocio vive en tres lugares, cambiarla exige tocar los tres — y te vas a olvidar de uno.

**Cuándo sí**: la misma regla (validación, cálculo, formato, constante de negocio) aparece en 3+ lugares y **cambiaría por el mismo motivo**.

**Cuándo no**: la duplicación accidental no es duplicación real. Dos funciones que se parecen pero modelan cosas distintas (el descuento de un cupón y el de un mayorista) no se unen: si cambian por motivos distintos, unirlas las acopla sin razón. Con dos ocurrencias, esperar a la tercera (regla de tres).

**Señal en el código**: copy-paste entre archivos; un bug arreglado en un lugar que reaparece en otro; el mismo literal (`0.21`, `'admin'`) repetido.

```ts
// Anti-patrón: la regla del IVA duplicada
const totalA = price * 1.21;
const totalB = subtotal * 1.21;

// Correcto: el conocimiento vive en un solo lugar
const VAT_RATE = 0.21;
const withVat = (amount: number) => amount * (1 + VAT_RATE);
```

**Cómo lo aplica la skill**: en P6 evita duplicar reglas al generar scaffolding. En Modo Adopción (MA-1.5) reporta el smell *Duplicate Code*, pero distingue duplicación real de accidental antes de sugerir extraer nada.

## KISS — Keep It Simple

**Qué dice**: gana la solución más simple que resuelve el problema. La complejidad es deuda que se paga en cada lectura.

**Cuándo sí**: siempre como punto de partida. Si dos soluciones resuelven lo mismo, elegir la que un compañero entiende sin explicación.

**Cuándo no**: simple no es "el menor número de líneas" ni "lo más rápido de escribir". Una solución ingeniosa y corta suele ser más difícil de leer que una de diez líneas obvias. Y simple no justifica saltear cosas que el problema sí exige (validar input, manejar errores).

**Señal en el código**: capas de indirección para una sola llamada; una clase donde una función alcanzaba; un one-liner que necesita un comentario para descifrarse; una librería de 5 MB para resolver algo que son tres líneas.

```ts
// Anti-patrón: una clase, un método, sin estado
class TaxCalculator { calculate(amount: number) { return amount * 0.21; } }

// Correcto
const withTax = (amount: number) => amount * 1.21;
```

**Cómo lo aplica la skill**: prefiere funciones planas sobre clases si no hay estado ni herencia, y evita abstracciones especulativas. La escala del proyecto (P4) fija cuánta estructura es "simple" para ese caso: una landing no lleva Clean Architecture.

## YAGNI — You Aren't Gonna Need It

**Qué dice**: no programes para necesidades futuras hipotéticas; programá lo que se necesita hoy. Cuando el futuro llega (si llega), se refactoriza con información real.

**Cuándo sí**: flags, parámetros, capas o "puntos de extensión" que nadie usa hoy.

**Cuándo no**: lo que es **muy caro de cambiar después** sí merece pensarse de antemano — el esquema de la DB, el contrato de una API pública, los IDs, la identidad visual de una marca. YAGNI se aplica a código, no a decisiones irreversibles.

**Señal en el código**: `// por si en el futuro queremos...`; configuración que nadie configura; interfaces con una sola implementación y sin motivo de test; el smell *Speculative Generality*.

```ts
// Anti-patrón: configurable "por si acaso"
function send(msg: string, { retries = 3, backoff = 'exp', transport = 'smtp' } = {}) {}

// Correcto: lo que hace falta hoy
function send(msg: string) {}
```

**Cómo lo aplica la skill**: no genera abstracciones que el SPEC no pide. Es también la regla detrás de `PRACTICES.md`: un patrón entra solo si un requisito del SPEC lo necesita.

## Clean Code

**Qué dice**: un conjunto de hábitos para que el código se lea como prosa. Los cinco que más rinden:

- **Nombres que dicen qué es**: `getUserByEmail(email)` > `getUser(e)` > `getU(e)`.
- **Una función, una cosa**: si necesitás la palabra "y" para describirla, son dos funciones.
- **Comentarios para el "por qué", no el "qué"**: el qué lo dice el nombre; el porqué (una decisión no obvia, un workaround) no se puede deducir del código.
- **Sin estado global mutable**: cualquiera lo cambia desde cualquier lado, y razonar sobre el código se vuelve imposible.
- **Salir temprano** (early returns) en vez de pirámides de `if`.

**Cuándo sí**: siempre; es barato y se paga solo en cada lectura.

**Cuándo no**: no convertirlo en dogma. Dividir una función clara de 35 líneas en siete de cinco líneas con nombres forzados la vuelve *más* difícil de seguir. Los números concretos (funciones < 30 líneas, límites de archivo) son guías, no paredes.

**Señal en el código**: nombres como `data`, `tmp`, `handle2`; un comentario largo explicando un bloque confuso en vez de renombrarlo (*Comments as Deodorant*); funciones de 80 líneas con cuatro niveles de anidamiento.

**Cómo lo aplica la skill**: las reglas concretas y medibles (tamaño de funciones y archivos, early returns, magic numbers, imports) viven en `coding-principles.md`, sección "Reglas de estilo de código". Acá está el criterio; allá, el umbral.

## Composición sobre herencia

**Qué dice**: para reutilizar comportamiento, preferir **componer objetos** (una pieza *tiene* otra) antes que **heredar** (una pieza *es* otra). La herencia acopla la subclase a los detalles internos de la base y se rompe con Liskov (ver `solid.md`); la composición se cambia en runtime y se testea por partes.

**Cuándo sí**: casi siempre que la relación sea "usa/tiene" y no una taxonomía real. Es lo que ya hacen los hooks de React, los middlewares, Strategy y Decorator.

**Cuándo no**: la herencia sigue siendo correcta cuando hay una relación "es un" genuina y estable, y el framework la espera (clases de Django, controladores de Rails, `Error` personalizados). No evitarla donde el ecosistema la usa por convención.

**Señal en el código**: jerarquías de tres o más niveles; subclases que sobreescriben casi todo; una subclase creada solo para reusar un método; `super.metodo()` encadenado que nadie puede seguir.

```ts
// Anti-patrón: heredar solo para reusar logging
class UserService extends Logger { }

// Correcto: el servicio tiene un logger, y se puede reemplazar en un test
class UserService { constructor(private logger: Logger) {} }
```

**Cómo lo aplica la skill**: al proponer estructura en P4/P6 arma piezas que se inyectan y combinan en vez de jerarquías; respeta la herencia cuando el framework elegido en P3 la exige.

---

## Tensiones — cuál pesa más

| Choque | Regla práctica |
|---|---|
| **DRY vs YAGNI/KISS** | Con dos ocurrencias, tolerar la duplicación. Abstraer en la tercera, cuando ya se ve qué es lo común de verdad. |
| **SOLID vs YAGNI** | Cada interfaz o capa nueva necesita un motivo hoy (un test, una segunda implementación). "Podría hacer falta" no alcanza. |
| **Clean Code vs KISS** | Si dividir una función la hace más difícil de seguir, no dividirla. La meta es legibilidad, no cantidad de funciones. |
| **DRY vs desacople** | Si unificar código obliga a dos módulos independientes a depender del mismo helper, preferir un poco de duplicación. |
| **YAGNI vs decisiones caras** | Lo irreversible (esquema, API pública) se diseña de antemano; lo reversible (una función interna) no. |

Ante la duda, elegir la opción **más fácil de deshacer**.
