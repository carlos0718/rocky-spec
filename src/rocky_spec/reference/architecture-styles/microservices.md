> Referencia de **rocky-spec** — ficha del estilo de arquitectura de **microservicios**. Mapa de todos los estilos y matriz de decisión en `.rocky-spec/reference/architectures.md`; abrir esta ficha solo cuando P4 (o Modo Adopción) ya apunta a este estilo.

# Microservicios

**Analogía**: en vez de una empresa con un único departamento que lo hace todo, muchas empresas chicas y especializadas que se contratan entre sí por contrato (una API). Cada una decide cómo trabajar y puede crecer o fallar por su cuenta; a cambio, ahora hay que coordinar llamados, plazos y facturas entre todas.

## Qué es

La aplicación es un conjunto de **servicios pequeños y autónomos**, desplegables por separado, organizados alrededor de **capacidades de negocio** (pedidos, pagos, catálogo), no de capas técnicas. Lo que los define:

- **Cada servicio es dueño de sus datos.** Tiene su propia base (o su propio esquema aislado) y **nadie más la lee**: el resto accede solo por su API o por sus eventos.
- **Se despliegan de forma independiente**, con su propio pipeline.
- **Se comunican por red**: de forma síncrona (REST, gRPC) cuando hace falta la respuesta ya, o asíncrona (mensajes y eventos, ver `event-driven.md`) para desacoplarse.
- Los límites entre servicios se trazan siguiendo los **Bounded Contexts** de DDD.

## Diagrama

```
                    [ Cliente ]
                         │
                  ┌──────▼──────┐
                  │ API Gateway │
                  └──┬───┬───┬──┘
        ┌────────────┘   │   └────────────┐
        ▼                ▼                ▼
  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  users   │     │  orders  │     │ payments │
  └────┬─────┘     └────┬─────┘     └────┬─────┘
       ▼                ▼                ▼
   [ DB users ]    [ DB orders ]    [ DB payments ]

        orders ──── evento OrderPlaced ────► broker ────► payments, email
```

## Estructura de carpetas de ejemplo

Monorepo (un repositorio, varios servicios):

```
services/
  users/
    src/  Dockerfile  migrations/  openapi.yaml
  orders/
    src/  Dockerfile  migrations/  openapi.yaml
  payments/
    src/  Dockerfile  migrations/  openapi.yaml
libs/
  contracts/          esquemas de eventos y clientes generados (versionados)
gateway/              enrutamiento, autenticación, rate limit
infra/                docker-compose, manifiestos de despliegue, CI
```

Cada servicio, por dentro, se organiza con su propio estilo (lo habitual es Hexagonal u Onion; ver `hexagonal.md`).

## Prerrequisitos — sin esto, no

Microservicios cambian complejidad de código por **complejidad operativa**. Antes de elegirlos tiene que existir:

- **CI/CD por servicio**: cada uno se construye, prueba y despliega solo.
- **Observabilidad madura**: logs con id de correlación, trazas distribuidas, métricas y alertas (ver `observability.md`). Sin eso, cuando algo falla no se sabe en qué servicio.
- **Contenedores y algún orquestador**, o una plataforma gestionada que lo resuelva.
- **Equipos que puedan ser dueños de un servicio de punta a punta** (la estructura del sistema termina reflejando la de la organización).
- **Un dominio bien entendido**, para trazar fronteras que no haya que mover después: mover una frontera entre servicios es carísimo.

## Cuándo sí

- **Varios equipos** que necesitan desplegar de forma independiente sin coordinarse.
- Partes con **necesidades de escala o de tecnología muy distintas** (el módulo de pagos necesita más recursos que el de perfil; un componente de ML en otro lenguaje).
- Un dominio grande, estable y bien entendido, con contextos claros.
- Se requiere **aislamiento de fallos**: que la caída de una parte no derribe el resto.

## Cuándo no

- **Equipos pequeños**: la complejidad operativa es enorme para el beneficio.
- **MVPs o dominios inciertos**: vas a trazar mal las fronteras.
- Sin observabilidad ni CI/CD maduros.
- Cuando "queremos escalar" pero no hay una parte concreta con ese problema.

> **Regla de oro**: "Monolito primero. Microservicios cuando duele." — Martin Fowler. Ver `monolith.md` (modular) y su camino de evolución.

## Señales de alarma

- **Monolito distribuido**: para cambiar algo hay que desplegar cuatro servicios a la vez. Tenés todos los costos de los microservicios y ningún beneficio.
- **Servicios que comparten la misma base de datos**: es acoplamiento por el dato, invisible en el código.
- **Llamadas síncronas en cadena** (A → B → C → D): la latencia se suma y la disponibilidad se multiplica; si uno cae, caen todos.
- **Nanoservicios**: servicios de un solo endpoint que solo agregan red a algo que era una función.
- Un cambio de contrato rompe a todos los clientes: no hay versionado ni compatibilidad hacia atrás.
- Nadie sabe qué servicio es dueño de qué dato.
- Transacciones distribuidas de dos fases (2PC) atravesando servicios.

## Conceptos que hay que resolver

- **Datos propios y consistencia eventual**: ya no hay una transacción ACID que abarque todo. Un flujo que cruza servicios (crear pedido → cobrar → reservar stock) se resuelve con una **Saga**: una secuencia de pasos locales donde, si uno falla, se ejecutan **acciones compensatorias** (reembolsar) en lugar de un rollback. Puede ser por coreografía (cada servicio reacciona a eventos) o por orquestación (un coordinador dirige los pasos).
- **Comunicación**: síncrona solo cuando se necesita la respuesta; con timeouts, reintentos con backoff y circuit breaker (`best-practices-backend.md`, sección 7). Asíncrona para lo demás.
- **Contratos versionados y compatibles hacia atrás**, con contract tests: agregar campos es seguro; quitar o cambiar el significado exige una versión nueva.
- **API Gateway** (un punto de entrada, autenticación y rate limit) y, si hay varios tipos de cliente, un BFF por cliente.
- **Idempotencia** en todo lo que pueda recibirse dos veces (ver `event-driven.md`).

## Qué ganás y qué sacrificás

| Ganás | Sacrificás |
|---|---|
| Despliegue y escala independientes por servicio | Complejidad operativa y de red (latencia, fallos parciales) |
| Equipos autónomos que no se bloquean entre sí | Consistencia eventual y sagas en vez de transacciones simples |
| Aislamiento de fallos | Debugging y testing distribuidos, mucho más difíciles |
| Libertad de tecnología por servicio | Duplicación de datos, costo de infraestructura, gobernanza de contratos |

## Cómo se combina con otros estilos

- **Cada servicio, por dentro, Hexagonal u Onion**: es la combinación más frecuente (`hexagonal.md`, `onion.md`).
- **Con event-driven**: casi inevitable para desacoplar servicios sin cadenas síncronas (`event-driven.md`).
- **Desde un monolito modular — Strangler Fig**: no se reescribe todo. Se extrae **un** módulo por vez, empezando por el de fronteras y datos más claros; el monolito sigue funcionando mientras tanto. Un híbrido de "monolito más unos pocos servicios" es una arquitectura legítima, no una etapa de transición vergonzosa (`monolith.md`).

## Cómo la usa la skill

- **P4**: por defecto **no lo recomienda**; propone un monolito modular y deja los servicios como evolución. Solo lo sugiere si el score de escalabilidad es alto **y** el equipo es de 4+ personas **y** hay infraestructura y observabilidad disponibles. Siempre con la advertencia de "Monolito primero" en la sección "¿Qué sacrificás?".
- **Modo Adopción (MA-4)**: se reconoce por varios `Dockerfile` o `package.json` bajo `services/` y un `docker-compose` con varios servicios. Chequeo clave: **¿comparten la base de datos?** Si sí, es un monolito distribuido y hay que decirlo.
- **Documentación**: el proyecto necesita la observabilidad completa de P5.7, no la versión mínima; se recomienda dejarlo escrito en `OBSERVABILITY.md`. Un broker gestionado (SQS, un servicio de mensajería) se registra como servicio externo en P3.
