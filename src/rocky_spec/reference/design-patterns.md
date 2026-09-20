> Referencia de **rocky-spec** — patrones de diseño: los 23 de GoF más tres frecuentes que no son GoF (Repository, Dependency Injection, Registry/Plugin). Este archivo es el **índice y los criterios**; el detalle de cada patrón GoF vive en `design-patterns/` — abrir solo el archivo del tipo que hace falta.

# Patrones de diseño

Un patrón es una solución con nombre a un problema que se repite. Sirve para que el equipo (y el agente) se entienda en una palabra — no para decorar el código.

## Criterios — cuándo usar un patrón

1. **Primero el problema, después el patrón.** Si no hay una señal concreta en el código (un `switch` que crece, un constructor de 7 parámetros), no hay motivo para introducirlo.
2. **Un patrón solo entra al `PRACTICES.md` del proyecto si un requisito del SPEC lo pide.** Que exista en este catálogo no lo hace aplicable (evita sobreaplicar).
3. **Con funciones de primera clase, muchos desaparecen.** Strategy es pasar una función, Command es un closure, Iterator es un generador, Observer es un emisor de eventos. Antes de crear una clase, mirar si el lenguaje ya lo resuelve.
4. **La complejidad se paga siempre; el beneficio, solo si el problema aparece.** Ante la duda, la versión sin patrón (KISS/YAGNI, ver `general-principles.md`).
5. **Los patrones frecuentes son pocos.** Con seis o siete (Factory Method, Builder, Adapter, Decorator, Facade, Observer, Strategy) se cubre casi todo lo que aparece en proyectos reales.

Cada patrón usa la misma plantilla: **qué es, cuándo sí, cuándo no, señal en el código, ejemplo mínimo, cómo lo aplica la skill**, y una marca de frecuencia (*frecuente*, *ocasional*, *raro*).

## Los 23 de GoF

| Patrón | Frecuencia | Problema que resuelve | Detalle |
|---|---|---|---|
| Factory Method | frecuente | Crear el objeto correcto sin `switch` repartidos | `design-patterns/creational.md` |
| Abstract Factory | raro | Crear familias de objetos que van juntas | `design-patterns/creational.md` |
| Builder | frecuente | Construir objetos con muchos parámetros opcionales | `design-patterns/creational.md` |
| Prototype | raro | Crear copiando un modelo | `design-patterns/creational.md` |
| Singleton | ocasional, con cuidado | Una sola instancia global (casi siempre mejor inyectar) | `design-patterns/creational.md` |
| Adapter | frecuente | Aislar una API o librería externa | `design-patterns/structural.md` |
| Bridge | raro | Dos dimensiones que varían por separado | `design-patterns/structural.md` |
| Composite | ocasional | Tratar igual hoja y rama de un árbol | `design-patterns/structural.md` |
| Decorator | frecuente | Sumar comportamiento envolviendo, sin subclases | `design-patterns/structural.md` |
| Facade | frecuente | Una entrada simple a un subsistema complejo | `design-patterns/structural.md` |
| Flyweight | raro | Compartir estado para ahorrar memoria | `design-patterns/structural.md` |
| Proxy | ocasional | Controlar el acceso a un objeto | `design-patterns/structural.md` |
| Chain of Responsibility | frecuente | Pipeline de handlers (middlewares) | `design-patterns/behavioral.md` |
| Command | ocasional | Acciones como objetos: deshacer, encolar | `design-patterns/behavioral.md` |
| Interpreter | raro | Evaluar un mini-lenguaje | `design-patterns/behavioral.md` |
| Iterator | frecuente (ya viene en el lenguaje) | Recorrer sin exponer la estructura | `design-patterns/behavioral.md` |
| Mediator | ocasional | Coordinar objetos que se hablan todos con todos | `design-patterns/behavioral.md` |
| Memento | raro | Guardar y restaurar estado | `design-patterns/behavioral.md` |
| Observer | frecuente | Avisar cambios sin acoplar emisor y receptor | `design-patterns/behavioral.md` |
| State | frecuente | Comportamiento según el estado (máquina de estados) | `design-patterns/behavioral.md` |
| Strategy | frecuente | Algoritmos intercambiables | `design-patterns/behavioral.md` |
| Template Method | ocasional | Esqueleto fijo con pasos variables | `design-patterns/behavioral.md` |
| Visitor | raro | Operaciones nuevas sobre una estructura estable | `design-patterns/behavioral.md` |

## Guía inversa — tengo este problema

| Si veo… | Considerar |
|---|---|
| `switch (type)` repetido en varios archivos | Strategy o Factory Method |
| Un constructor con 5+ parámetros, varios opcionales | Objeto de opciones; Builder si hay pasos |
| Tipos o errores de un proveedor en la lógica de negocio | Adapter |
| La misma cadena de 4–5 llamadas en varios controladores | Facade (un servicio o caso de uso) |
| Cache, logs o reintentos mezclados con la lógica | Decorator |
| Un `switch (status)` en muchos métodos | State (tabla de transiciones) |
| Un módulo que llama a otros solo para "avisar" | Observer |
| Validaciones o pasos en secuencia con `if` anidados | Chain of Responsibility |
| Queries a la DB dentro de la lógica de negocio | Repository |
| `new` de servicios con efectos dentro de la lógica | Dependency Injection |

## Patrones frecuentes que no son GoF

### Repository

**Frecuencia:** frecuente

**Qué es**: separa el acceso a datos (DB, API, archivos) de la lógica de negocio. El negocio habla con una abstracción tipo "colección de entidades", no con la base.

**Cuándo sí**: cualquier proyecto con persistencia y lógica de negocio propia. Casi siempre vale la pena.

**Cuándo no**: scripts y CRUD trivial donde el repositorio sería un reenvío uno a uno de cada llamada al ORM sin lógica que aislar.

**Señal en el código**: queries SQL o del ORM dentro de controladores o servicios de negocio; tests que necesitan una DB real para probar una regla.

```ts
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}
```

**Cómo lo aplica la skill**: crea `domain/repositories/<Entity>Repository.ts` (interface) y `infrastructure/persistence/<Entity>RepositoryImpl.ts` (implementación concreta). Los servicios reciben la interface, no la implementación.

### Dependency Injection

**Frecuencia:** frecuente

**Qué es**: las dependencias de un objeto se le pasan desde afuera (constructor o parámetros) en vez de que las cree o las busque él. Es el *mecanismo* de Dependency Inversion (ver `solid.md`).

**Cuándo sí**: siempre que un objeto use algo con efectos (DB, red, reloj, email). Permite reemplazarlo por un fake en un test.

**Cuándo no**: no hace falta un contenedor ni un framework para inyectar. Pasar las dependencias a mano desde el punto de entrada (el *composition root*) alcanza en proyectos chicos; un contenedor se justifica cuando el grafo es grande (NestJS, Spring y .NET ya traen uno).

**Señal en el código**: `new` de servicios con efectos dentro de la lógica de negocio; `Singleton.getInstance()` por todos lados.

```ts
// composition root, en el punto de entrada
const repo = new UserRepositoryPg(db);
const users = new UserService(repo);
```

**Cómo lo aplica la skill**: arma el composition root en el punto de entrada del proyecto y usa el contenedor del framework solo si el stack (P3) ya lo trae.

### Registry / Plugin

**Frecuencia:** ocasional

**Qué es**: un registro central donde los módulos se anotan por nombre o clave, y el núcleo los resuelve sin conocerlos de antemano. Agregar un caso nuevo es registrar una pieza, sin tocar el núcleo (Open/Closed).

**Cuándo sí**: sistemas extensibles con variantes que crecen (integraciones, exportadores, comandos). Es la arquitectura de este mismo kit: `INTEGRATION_REGISTRY` deja sumar un agente escribiendo solo una clase.

**Cuándo no**: si las variantes son pocas y fijas; un `switch` chico es más legible. Cuidado con el registro global mutable: es un Singleton disfrazado. Construirlo y pasarlo explícitamente.

**Señal en el código**: un `if (name === 'x') … else if (name === 'y')` que crece con cada extensión.

```ts
const registry = new Map<string, Integration>();
registry.set('claude', new ClaudeIntegration());
registry.set('cursor', new CursorIntegration());
const integration = registry.get(agentName);
```

**Cómo lo aplica la skill**: lo propone en P4 cuando el SPEC pide "agregar X sin tocar el núcleo".

## MVC y MVVM

No son patrones de diseño de clases sino **arquitecturas de UI**: están en `.rocky-spec/reference/architectures.md` (MVC y MVVM) junto con los demás estilos.
