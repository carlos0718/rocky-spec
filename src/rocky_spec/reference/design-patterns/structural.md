> Referencia de **rocky-spec** — patrones **estructurales** de GoF (7): cómo se componen clases y objetos. Índice y criterios generales en `.rocky-spec/reference/design-patterns.md`.

# Patrones estructurales

Resuelven cómo se combinan las piezas: envolver, traducir, agrupar o compartir, sin que los cambios en una se propaguen a las otras.

---

### Adapter

**Frecuencia:** frecuente

**Qué es**: traduce la interfaz de una cosa a la que tu código espera. Aísla lo externo para que su forma no se filtre al dominio. Es la base de la arquitectura Hexagonal (los "adapters").

**Cuándo sí**: integrar una librería o API de terceros (pagos, email, storage) sin que sus tipos y errores lleguen a la lógica de negocio.

**Cuándo no**: si la librería ya tiene la interfaz que necesitás, o si es código propio y podés cambiarlo directamente.

**Señal en el código**: la lógica de negocio maneja tipos o errores del proveedor (`StripeError`); cambiar de proveedor implica tocar veinte archivos.

```ts
interface PaymentGateway { charge(amount: number): Promise<void> }

class StripeAdapter implements PaymentGateway {
  async charge(amount: number) {
    await stripe.paymentIntents.create({ amount });
  }
}
```

**Cómo lo aplica la skill**: cada servicio externo que P3 registra (email, pagos, storage) se envuelve tras un adapter. Este mismo kit lo usa: cada agente soportado es un adapter detrás de `IntegrationBase`.

---

### Bridge

**Frecuencia:** raro

**Qué es**: separa una abstracción de su implementación para que varíen por separado, evitando la explosión de subclases.

**Cuándo sí**: hay **dos dimensiones** independientes de variación (tipo de notificación × canal de envío).

**Cuándo no**: con una sola dimensión, o cuando las combinaciones son pocas y fijas.

**Señal en el código**: clases como `EmailUrgentNotification`, `SmsUrgentNotification`, `EmailInfoNotification`… el producto cartesiano.

```ts
class Notification {
  constructor(private channel: Channel, private level: 'urgent' | 'info') {}
  send(text: string) { this.channel.deliver(`[${this.level}] ${text}`); }
}
```

**Cómo lo aplica la skill**: resuelve primero con composición simple; Bridge solo si aparecen de verdad las dos dimensiones.

---

### Composite

**Frecuencia:** ocasional

**Qué es**: tratar de la misma forma a un objeto individual y a un grupo de objetos (una estructura en árbol).

**Cuándo sí**: árboles donde la misma operación aplica a hoja y a rama: menús anidados, carpetas y archivos, árboles de componentes UI (React ya lo es), permisos jerárquicos.

**Cuándo no**: si no hay jerarquía real.

**Señal en el código**: `if (node.children)` repetido para tratar distinto una hoja y una rama.

```ts
interface Node { size(): number }
class File implements Node { constructor(private bytes: number) {} size() { return this.bytes; } }
class Folder implements Node {
  constructor(private items: Node[]) {}
  size() { return this.items.reduce((sum, n) => sum + n.size(), 0); }
}
```

**Cómo lo aplica la skill**: no lo introduce; lo reconoce cuando el dominio (P1.7) es un árbol.

---

### Decorator

**Frecuencia:** frecuente

**Qué es**: agregar comportamiento a un objeto **envolviéndolo**, sin modificarlo ni heredar de él. El envoltorio tiene la misma interfaz.

**Cuándo sí**: capas opcionales y combinables alrededor de un servicio: cache, logging, reintentos, autorización. Middlewares y decoradores de Python/TS son variantes.

**Cuándo no**: si el comportamiento extra es siempre el mismo y pertenece a la clase.

**Señal en el código**: subclases del estilo `CachedLoggedUserRepository`; flags `if (useCache)` dentro de la clase.

```ts
class CachedUserRepo implements UserRepo {
  constructor(private inner: UserRepo, private cache: Cache) {}
  async find(id: string) {
    return (await this.cache.get(id)) ?? this.inner.find(id);
  }
}
```

**Cómo lo aplica la skill**: prefiere componer capas con decorators antes que crear subclases combinadas (composición sobre herencia).

---

### Facade

**Frecuencia:** frecuente

**Qué es**: una interfaz simple al frente de un subsistema complejo.

**Cuándo sí**: el cliente tendría que coordinar 4 o 5 llamadas a piezas distintas para una operación común (un checkout: reservar stock, cobrar, agendar envío).

**Cuándo no**: si solo reenvía una llamada sin simplificar nada, o si esconde algo que el cliente necesita controlar.

**Señal en el código**: el mismo bloque de cinco llamadas repetido en varios controladores.

```ts
class CheckoutService {
  placeOrder(cart: Cart) {
    this.inventory.reserve(cart);
    this.payment.charge(cart);
    this.shipping.schedule(cart);
  }
}
```

**Cómo lo aplica la skill**: la capa de servicios o casos de uso que P4 arma en Clean/Hexagonal/Onion cumple exactamente este papel.

---

### Flyweight

**Frecuencia:** raro

**Qué es**: compartir el estado común de muchos objetos casi idénticos para ahorrar memoria.

**Cuándo sí**: miles o millones de objetos con datos repetidos (partículas, glifos de texto, tiles de un mapa) **y** un problema de memoria medido.

**Cuándo no**: casi siempre; es optimización prematura.

**Señal en el código**: un profiler que muestra memoria dominada por instancias con los mismos datos duplicados.

```ts
const glyphs = new Map<string, Glyph>();
const glyph = (ch: string) => glyphs.get(ch) ?? glyphs.set(ch, new Glyph(ch)).get(ch)!;
```

**Cómo lo aplica la skill**: no lo propone sin una medición que lo justifique.

---

### Proxy

**Frecuencia:** ocasional

**Qué es**: un sustituto con la misma interfaz que **controla el acceso** al objeto real: carga diferida, cache, permisos, log o acceso remoto.

**Cuándo sí**: cargar algo caro recién al usarlo, controlar quién puede llamar, o un cliente de un servicio remoto que se ve como un objeto local.

**Cuándo no**: si alcanza un Decorator. La diferencia es la intención: Decorator *agrega* comportamiento, Proxy *controla el acceso*.

**Señal en el código**: chequeos de permisos o de "ya se cargó" desparramados por el código que usa el objeto.

```ts
class LazyImage implements Image {
  private real?: RealImage;
  constructor(private path: string) {}
  draw() { (this.real ??= new RealImage(this.path)).draw(); }
}
```

**Cómo lo aplica la skill**: no lo introduce por su cuenta; lo usa cuando el SPEC pide carga diferida o control de acceso explícito.
