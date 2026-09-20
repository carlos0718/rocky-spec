> Referencia de **rocky-spec** — los 5 principios SOLID: qué dicen, cuándo aplicarlos, cuándo no, cómo se ve el código que los viola y cómo los usa la skill. Es a SOLID lo que `design-patterns.md` es a los patrones y `general-principles.md` a DRY/KISS/YAGNI.

# SOLID

Cinco principios para que el código orientado a objetos sea barato de cambiar (con adaptación, valen también en otros paradigmas). No son reglas para cumplir siempre: son **señales** de que un cambio futuro va a costar más de lo que debería.

| Letra | Principio | Idea en una frase |
|---|---|---|
| **S** | Single Responsibility | Un módulo tiene una sola razón para cambiar. |
| **O** | Open/Closed | Agregar un caso nuevo no obliga a editar código que ya funciona. |
| **L** | Liskov Substitution | Donde va la clase base tiene que poder ir cualquier subclase sin sorpresas. |
| **I** | Interface Segregation | Ningún cliente depende de métodos que no usa. |
| **D** | Dependency Inversion | El negocio define la interfaz; la infraestructura la implementa. |

**Cuándo aplicarlo en general**: proyectos medianos a grandes. En un script de 50 líneas o un Mini/Chico, cumplir los cinco a rajatabla agrega interfaces y archivos que nadie va a necesitar (ver YAGNI en `general-principles.md`). La escala del proyecto (P4) decide cuántos de estos pesan.

---

## S — Single Responsibility

**Qué dice**: una clase o módulo tiene una sola razón para cambiar — un solo motivo de negocio que obligue a tocarlo. La responsabilidad no es "un método", es "un motivo de cambio".

**Cuándo sí**: cuando un archivo mezcla cosas que cambian por motivos distintos (calcular un total y darle formato de PDF).

**Cuándo no**: no partir una clase cohesiva en cinco clases de un método cada una "porque SRP". Si todo lo que hay adentro cambia junto y por lo mismo, está bien donde está.

**Señal en el código**: nombres con `And`, `Manager`, `Helper` que hacen de todo; un cambio de regla de negocio y un cambio de formato tocan el mismo archivo; un God File (ver code smells en `coding-principles.md`).

```ts
// Anti-patrón: calcula, persiste y formatea
class Invoice { total() {} save() {} toPdf() {} }

// Correcto: cada pieza cambia por un motivo distinto
class Invoice { total() {} }
class InvoiceRepository { save(invoice: Invoice) {} }
class InvoicePdfRenderer { render(invoice: Invoice) {} }
```

**Cómo lo aplica la skill**: en P6 genera el scaffolding ya separado por motivo de cambio (tipos, lógica, UI) — es el mismo criterio detrás de los límites de tamaño de archivo.

## O — Open/Closed

**Qué dice**: el código está abierto a extensión y cerrado a modificación — sumar una variante nueva es agregar código, no editar el que ya anda.

**Cuándo sí**: cuando el mismo `if`/`switch` sobre un "tipo" se repite y crece con cada caso nuevo (métodos de pago, formatos de export, canales de notificación).

**Cuándo no**: con una sola variante hoy, no abstraer "por si viene otra". Esperar a la segunda o tercera; abstraer antes es Speculative Generality.

**Señal en el código**: `switch (type)` repetido en varios archivos; agregar una variante obliga a tocar cuatro lugares (Shotgun Surgery).

```ts
// Anti-patrón: cada método nuevo edita esta función
function fee(method: string, amount: number) {
  if (method === 'card') return amount * 0.03;
  if (method === 'paypal') return amount * 0.05;
}

// Correcto: un método nuevo es una clase nueva
interface PaymentMethod { fee(amount: number): number }
class Card implements PaymentMethod { fee(a: number) { return a * 0.03; } }
```

**Cómo lo aplica la skill**: cuando detecta el `switch` repetido sobre un tipo, propone Strategy (ver `design-patterns.md`). Si hay una sola variante, no lo introduce.

## L — Liskov Substitution

**Qué dice**: una subclase (o cualquier implementación de una interfaz) tiene que poder usarse donde se espera la base sin romper nada ni obligar al llamador a saber cuál es.

**Cuándo sí**: siempre que haya herencia o implementaciones intercambiables de una misma interfaz.

**Cuándo no**: sin herencia ni polimorfismo no aplica, y en código funcional o de composición casi no aparece. Es un argumento a favor de preferir composición sobre herencia (ver `general-principles.md`).

**Señal en el código**: una subclase que lanza `NotImplemented` en un método heredado; un `instanceof` para tratar distinto a una subclase; una subclase que rechaza entradas que la base aceptaba.

```ts
// Anti-patrón: el "repositorio de solo lectura" rompe el contrato de Repository
class ReadOnlyRepository extends Repository {
  save() { throw new Error('no soportado'); }
}

// Correcto: interfaces separadas, cada una cumple lo que promete
interface Reader { find(id: string): Promise<User> }
interface Writer { save(user: User): Promise<void> }
```

**Cómo lo aplica la skill**: al sugerir jerarquías en P4/P6 prefiere composición o interfaces chicas; si una subclase tiene que romper el contrato de su base, lo señala como violación en vez de taparlo.

## I — Interface Segregation

**Qué dice**: mejor varias interfaces específicas que una grande. Ningún cliente debería depender de métodos que no usa.

**Cuándo sí**: interfaces con seis o más métodos donde cada implementador usa la mitad; o cuando testear una función obliga a mockear diez métodos.

**Cuándo no**: no fragmentar en interfaces de un método por reflejo. Si todos los clientes usan todo, una interfaz cohesiva está bien.

**Señal en el código**: implementaciones con métodos vacíos o que lanzan error; mocks de tests enormes para probar una sola cosa.

```ts
// Anti-patrón: el robot no come
interface Worker { work(): void; eat(): void }

// Correcto
interface Workable { work(): void }
interface Feedable { eat(): void }
```

**Cómo lo aplica la skill**: en P6 genera las interfaces de servicios y repositorios por caso de uso, no una interfaz monolítica que lo expone todo.

## D — Dependency Inversion

**Qué dice**: los módulos de alto nivel (el negocio) no dependen de los de bajo nivel (DB, HTTP, email); los dos dependen de abstracciones. **El dominio define la interfaz, la infraestructura la implementa** — la flecha de dependencia apunta hacia el dominio. Es la base de Clean, Hexagonal y Onion (ver `architecture-styles/`).

**Cuándo sí**: cuando la lógica de negocio hay que testearla sin DB ni red, o cuando el detalle técnico puede cambiar (otro proveedor de email, otra base).

**Cuándo no**: para dependencias estables que nunca vas a cambiar ni mockear (`Math`, la librería estándar). Envolver todo en interfaces "por las dudas" es ruido.

**Señal en el código**: el servicio de negocio hace `import { PrismaClient }` o `new SmtpClient()` adentro; los tests necesitan una DB real para probar una regla.

```ts
// Anti-patrón: el negocio conoce el detalle técnico
class Checkout { private mailer = new SmtpMailer(); }

// Correcto: depende de la abstracción, se inyecta desde afuera
interface Mailer { send(to: string, body: string): Promise<void> }
class Checkout { constructor(private mailer: Mailer) {} }
```

> **Inversión ≠ inyección.** Dependency Inversion es el *principio* (quién define la interfaz); Dependency Injection es el *mecanismo* para pasar la implementación (ver `design-patterns.md`). Se puede invertir sin un contenedor de DI.

**Cómo lo aplica la skill**: si SOLID está activo y el proyecto es mediano o más, P4 separa interfaces de implementaciones (`domain/repositories/UserRepository.ts` como interface, `infrastructure/persistence/UserRepositoryPg.ts` como implementación).

---

## Cómo se conectan con el resto

- **S** es el mismo criterio que los límites de tamaño de archivo y el smell *God File* (`coding-principles.md`).
- **O** se implementa casi siempre con Strategy (`design-patterns.md`).
- **D** es la regla de dependencia de las arquitecturas de núcleo protegido (`architecture-styles/onion.md`, `hexagonal.md`).
- **YAGNI** (`general-principles.md`) es el freno: SOLID sin YAGNI produce interfaces y capas que nadie usa.
