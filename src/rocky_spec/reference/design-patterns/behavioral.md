> Referencia de **rocky-spec** — patrones de **comportamiento** de GoF (11): cómo se reparten responsabilidades y se comunican los objetos. Índice y criterios generales en `.rocky-spec/reference/design-patterns.md`.

# Patrones de comportamiento

Resuelven cómo colaboran los objetos y quién decide qué. Es la categoría donde más patrones "desaparecen" en lenguajes con funciones de primera clase: Strategy, Command e Iterator suelen ser una función, un closure y un generador.

---

### Chain of Responsibility

**Frecuencia:** frecuente

**Qué es**: una petición pasa por una cadena de handlers; cada uno la procesa o se la pasa al siguiente.

**Cuándo sí**: pipelines de validación o middlewares (Express, Koa): autenticación → autorización → rate limit → handler. El manejo de errores centralizado de un backend también es una cadena.

**Cuándo no**: si siempre hay un único handler conocido de antemano.

**Señal en el código**: una función con ocho `if` en secuencia que validan o transforman cosas distintas.

```ts
app.use(authenticate);
app.use(rateLimit);
app.use(handler);
```

**Cómo lo aplica la skill**: en backends con middleware ya lo respeta; lo usa para validación de input en el borde y errores centralizados.

---

### Command

**Frecuencia:** ocasional

**Qué es**: encapsular una acción como un objeto con sus datos, para poder encolarla, deshacerla, registrarla o reintentarla.

**Cuándo sí**: undo/redo, colas de trabajo, jobs, macros, historial de acciones.

**Cuándo no**: si la acción solo se ejecuta al instante; una función alcanza (en lenguajes con closures, una función *es* un Command).

**Señal en el código**: funciones que reciben `action: string` más flags; un pedido de "poder deshacer".

```ts
interface Command { execute(): void; undo(): void }
const history: Command[] = [];
function run(cmd: Command) { cmd.execute(); history.push(cmd); }
```

**Cómo lo aplica la skill**: lo propone cuando el SPEC pide deshacer o trabajos diferidos; si no, usa funciones.

---

### Interpreter

**Frecuencia:** raro

**Qué es**: representar la gramática de un mini-lenguaje y evaluarla.

**Cuándo sí**: reglas configurables por el usuario (filtros de búsqueda, expresiones de reglas) cuando ya se sabe que hace falta un DSL.

**Cuándo no**: casi siempre. Para parsear algo real conviene una librería de parsing.

**Señal en el código**: strings de configuración con sintaxis propia que se parsean a mano con `split`.

```ts
type Expr =
  | { op: 'and' | 'or'; left: Expr; right: Expr }
  | { field: string; eq: string };
```

**Cómo lo aplica la skill**: no lo propone salvo que un requisito del SPEC pida reglas definidas por el usuario final.

---

### Iterator

**Frecuencia:** frecuente, pero **ya viene en el lenguaje**

**Qué es**: recorrer una colección sin exponer su estructura interna.

**Cuándo sí**: colecciones propias (un árbol, una API paginada, un stream).

**Cuándo no**: no implementarlo a mano. `for...of`, generadores y `yield` ya son el patrón.

**Señal en el código**: índices y punteros manuales para recorrer una estructura propia.

```ts
async function* pages(fetchPage: (n: number) => Promise<Item[]>) {
  for (let n = 1; ; n++) {
    const items = await fetchPage(n);
    if (items.length === 0) return;
    yield items;
  }
}
```

**Cómo lo aplica la skill**: usa el mecanismo nativo del lenguaje del stack (P3).

---

### Mediator

**Frecuencia:** ocasional

**Qué es**: un objeto central coordina la comunicación entre varios, en vez de que se conozcan entre sí.

**Cuándo sí**: componentes que se hablan todos con todos: un formulario con campos interdependientes, una sala de chat, un bus de comandos.

**Cuándo no**: con pocos participantes. Riesgo: el mediador se convierte en un God Object.

**Señal en el código**: N componentes con referencias cruzadas a los otros N−1.

```ts
class ChatRoom {
  private users: User[] = [];
  join(user: User) { this.users.push(user); }
  send(from: User, text: string) {
    this.users.filter(u => u !== from).forEach(u => u.receive(text));
  }
}
```

**Cómo lo aplica la skill**: no lo introduce; lo reconoce cuando los módulos del proyecto se llaman en malla.

---

### Memento

**Frecuencia:** raro

**Qué es**: guardar y restaurar el estado de un objeto sin romper su encapsulación.

**Cuándo sí**: undo, borradores, snapshots.

**Cuándo no**: si el estado es simple y basta copiarlo (`structuredClone`), o si ya hay un store con historial (time-travel de Redux).

**Señal en el código**: copias manuales del estado interno de un objeto "por si hay que volver atrás".

```ts
const snapshot = editor.save();
editor.type('texto');
editor.restore(snapshot);
```

**Cómo lo aplica la skill**: no lo propone; usa copia del estado o el historial del store.

---

### Observer

**Frecuencia:** frecuente

**Qué es**: los suscriptores reciben notificaciones de cambios sin acoplarse al emisor.

**Cuándo sí**: eventos, UI reactiva, integración entre módulos desacoplados. En frontend moderno ya viene con Redux, Zustand, Pinia o Signals.

**Cuándo no**: si el emisor necesita el resultado del receptor (usar una llamada directa). Cuidado con las cadenas de eventos que nadie puede seguir.

**Señal en el código**: un módulo que llama directamente a cinco otros solo para "avisar" que algo pasó.

```ts
bus.on('order.placed', sendConfirmationEmail);
bus.on('order.placed', reserveStock);
bus.emit('order.placed', order);
```

**Cómo lo aplica la skill**: es la base de la arquitectura orientada a eventos (ver `architecture-styles/event-driven.md`); en frontend usa el mecanismo del store elegido en P3.

---

### State

**Frecuencia:** frecuente

**Qué es**: el comportamiento de un objeto cambia según su estado, y cada estado (con sus transiciones válidas) se encapsula por separado.

**Cuándo sí**: máquinas de estado reales: pedido (pendiente → pagado → enviado → entregado), flujos de aprobación, estados de una conexión.

**Cuándo no**: dos estados con un booleano, o transiciones triviales.

**Señal en el código**: `switch (status)` repetido en muchos métodos; combinaciones de flags imposibles (`isPaid && isCancelled`).

```ts
type OrderState = 'pending' | 'paid' | 'shipped';
const transitions: Record<OrderState, OrderState[]> = {
  pending: ['paid'],
  paid: ['shipped'],
  shipped: [],
};
```

En TS/JS muchas veces alcanza una tabla de transiciones como esta, sin una clase por estado.

**Cómo lo aplica la skill**: si una entidad del dominio (P1.7) tiene un ciclo de vida con estados, modela las transiciones válidas de forma explícita.

---

### Strategy

**Frecuencia:** frecuente

**Qué es**: algoritmos intercambiables detrás de una misma interfaz.

**Cuándo sí**: varios algoritmos hacen lo mismo con implementación distinta (métodos de pago, sistemas de descuento, formatos de export). Es la forma habitual de cumplir Open/Closed (ver `solid.md`).

**Cuándo no**: con una sola variante. Y con funciones de primera clase basta pasar una función, sin clases.

**Señal en el código**: un `switch (type)` repetido en varios archivos.

```ts
type Discount = (total: number) => number;
const apply = (total: number, discount: Discount) => discount(total);

apply(100, t => t * 0.9); // 10% de descuento
```

**Cómo lo aplica la skill**: cuando varios algoritmos hacen lo mismo con implementación distinta, propone Strategy en vez de un `switch` que crece.

---

### Template Method

**Frecuencia:** ocasional

**Qué es**: una clase base define el esqueleto de un algoritmo y las subclases completan los pasos que varían.

**Cuándo sí**: el mismo flujo con pasos que cambian, y un framework que espera herencia (importadores CSV/JSON/XML: leer → validar → guardar).

**Cuándo no**: casi siempre se prefiere Strategy (composición sobre herencia, ver `general-principles.md`).

**Señal en el código**: subclases que copian el mismo esqueleto y cambian dos líneas.

```ts
abstract class Importer {
  run() { const rows = this.read(); this.validate(rows); this.save(rows); }
  protected abstract read(): Row[];
  protected validate(rows: Row[]) { /* común */ }
  protected abstract save(rows: Row[]): void;
}
```

**Cómo lo aplica la skill**: solo cuando el framework del stack lo impone; en el resto prefiere Strategy.

---

### Visitor

**Frecuencia:** raro

**Qué es**: agregar operaciones nuevas a una estructura de objetos sin modificar sus clases.

**Cuándo sí**: la estructura es estable (el AST de un compilador, un árbol de documento) y se suman operaciones seguido (exportar, validar, imprimir).

**Cuándo no**: si la estructura cambia seguido: cada clase nueva obliga a tocar todos los visitors. En TS, un `switch` sobre una unión discriminada da lo mismo con menos ceremonia.

**Señal en el código**: una cadena de `instanceof` para hacer operaciones distintas según el tipo.

```ts
type Shape = { kind: 'circle'; r: number } | { kind: 'rect'; w: number; h: number };
const area = (s: Shape) =>
  s.kind === 'circle' ? Math.PI * s.r ** 2 : s.w * s.h;
```

**Cómo lo aplica la skill**: usa uniones discriminadas o `match` del lenguaje; Visitor clásico casi nunca.
