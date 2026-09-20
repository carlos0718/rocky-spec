> Referencia de **rocky-spec** — patrones **creacionales** de GoF (5): cómo se crean los objetos. Índice y criterios generales en `.rocky-spec/reference/design-patterns.md`.

# Patrones creacionales

Resuelven *quién* crea un objeto y *cómo*, para que el resto del código no dependa de las clases concretas ni de los detalles de construcción.

---

### Factory Method

**Frecuencia:** frecuente

**Qué es**: una función o método que decide qué objeto concreto crear, para que quien lo usa no conozca las clases concretas ni el `if`/`switch` que elige.

**Cuándo sí**: hay 3+ tipos de un mismo objeto que se crean con lógica distinta (notificaciones por email, SMS o push).

**Cuándo no**: con uno o dos tipos y creación trivial alcanza un `new` directo.

**Señal en el código**: un `if`/`switch` largo para instanciar objetos, repetido en varios lugares.

```ts
function createNotifier(channel: 'email' | 'sms' | 'push'): Notifier {
  switch (channel) {
    case 'email': return new EmailNotifier();
    case 'sms': return new SmsNotifier();
    case 'push': return new PushNotifier();
  }
}
```

**Cómo lo aplica la skill**: si el código generado tiene un `switch` largo para crear objetos, lo refactoriza a una factory.

---

### Abstract Factory

**Frecuencia:** raro

**Qué es**: una interfaz para crear **familias** de objetos relacionados que tienen que usarse juntos, sin nombrar sus clases concretas.

**Cuándo sí**: hay varias familias intercambiables y mezclar piezas de familias distintas sería un bug (un kit de UI claro/oscuro con `Button` + `Input`; un proveedor cloud A o B con su storage + cola).

**Cuándo no**: una sola familia, o piezas sueltas que no se combinan. Es el patrón más sobreaplicado de la lista.

**Señal en el código**: varias factories que siempre cambian a la vez, elegidas por el mismo flag.

```ts
interface UiKit { button(): Button; input(): Input }
const kit: UiKit = darkMode ? new DarkKit() : new LightKit();
```

**Cómo lo aplica la skill**: no lo propone salvo que un requisito del SPEC pida varias familias intercambiables.

---

### Builder

**Frecuencia:** frecuente

**Qué es**: construir un objeto complejo paso a paso, con muchos parámetros opcionales, y validarlo recién al terminar.

**Cuándo sí**: un constructor con 5+ parámetros, varios opcionales (el smell *Long Parameter List*); objetos con pasos (requests HTTP, queries, configuraciones).

**Cuándo no**: 3 parámetros o menos. En lenguajes con objetos de opciones o argumentos con nombre (TS, Python), un objeto de opciones suele bastar sin el patrón.

**Señal en el código**: llamadas como `new Request(url, null, null, true, undefined, 3)` donde nadie recuerda qué es cada argumento.

```ts
const request = new RequestBuilder('/users')
  .method('POST')
  .header('X-Trace-Id', traceId)
  .body(payload)
  .build(); // valida acá
```

**Cómo lo aplica la skill**: ante un *Long Parameter List* propone primero un objeto de opciones; Builder solo si además hay pasos o validación al construir.

---

### Prototype

**Frecuencia:** raro

**Qué es**: crear un objeto nuevo copiando uno existente, en vez de construirlo desde cero.

**Cuándo sí**: la creación es cara y las variantes difieren poco de un modelo (plantillas de documento, estado inicial de un juego).

**Cuándo no**: casi siempre. `structuredClone`, el spread o `copy.deepcopy` ya lo resuelven sin el patrón.

**Señal en el código**: clonado manual campo por campo de un objeto grande.

```ts
const draft = structuredClone(template);
draft.title = 'Nuevo informe';
```

**Cómo lo aplica la skill**: no lo propone; usa la copia nativa del lenguaje cuando hace falta.

---

### Singleton

**Frecuencia:** ocasional — **usar con cuidado**

**Qué es**: una única instancia de algo, con acceso global.

**Cuándo sí**: recursos que de verdad son únicos: un pool de conexiones, un logger, la configuración cargada una vez.

**Cuándo no**: casi siempre. Es estado global con otro nombre: oculta dependencias y no se puede reemplazar en un test. La alternativa es crear la instancia **una vez** en el punto de entrada e inyectarla (ver Dependency Injection en `design-patterns.md`).

**Señal en el código**: `Foo.getInstance()` en medio de la lógica de negocio.

```ts
// Anti-patrón: dependencia oculta
const db = Database.getInstance();

// Correcto: se crea una vez y se inyecta
const db = new Database(config);
const users = new UserService(db);
```

**Cómo lo aplica la skill**: si está activo, advierte cuando se usa "por costumbre" y la instancia podría inyectarse.
