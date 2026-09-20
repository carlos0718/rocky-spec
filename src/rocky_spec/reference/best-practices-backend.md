> Referencia de **rocky-spec** — buenas prácticas de backend, agnósticas de lenguaje y framework: capas, validación, errores, diseño de API, datos, configuración, trabajo asíncrono y testing. P5.9 las usa para derivar el `PRACTICES.md` de un proyecto con backend. No repite lo que ya cubren `security.md` (OWASP, auth, CORS, rate limiting), `observability.md` (logs, health checks, métricas) ni `coding-principles.md` (tamaño de archivo, code smells).

# Buenas prácticas — backend

Cada sección trae qué hacer, la **señal** de que algo anda mal y **cuándo no aplicarla**. El mecanismo concreto lo da el framework del stack (P3) — un middleware, un filtro, un decorador, un manejador de excepciones —; el criterio es el mismo. El tamaño del proyecto (P4) decide cuáles pesan: una API de tres endpoints no necesita una capa de casos de uso.

---

## 1 · Capas y límites

**Qué hacer**
- **El handler es fino.** El controlador o ruta recibe la request, llama a un servicio o caso de uso, y devuelve la respuesta. La lógica de negocio no vive ahí.
- La lógica de negocio **no conoce HTTP** ni el ORM: recibe y devuelve datos del dominio. Así se testea sin levantar un servidor ni una base.
- **DTO en el borde, entidad adentro.** No exponer directamente el modelo de la base como respuesta de la API: cualquier cambio de columna se convierte en un cambio de contrato, y se filtran campos que no debían salir (`passwordHash`).
- El acceso a datos va detrás de una abstracción (ver Repository en `design-patterns.md`) cuando hay lógica de negocio propia.

**Señal de que falla**: queries dentro del controlador; un servicio que importa `Request`/`Response`; la API devuelve el objeto del ORM tal cual.

**Cuándo NO**: en un CRUD de tres tablas sin reglas de negocio, un handler que llama al ORM directo es legítimo. Agregar capas ahí es sobreingeniería (ver `architecture-styles/layered.md` y `general-principles.md`).

## 2 · Validación en el borde

**Qué hacer**
- **Validar todo lo que entra** (body, query, params, headers) apenas llega, con un esquema declarativo (el del framework, o una librería de schemas), no con `if` desparramados por los handlers.
- Rechazar temprano con un error claro y el código HTTP correcto (`400`/`422`).
- Preferir **listas permitidas** (qué se acepta) a listas de bloqueo (qué se rechaza).
- Validar también **reglas de negocio** que dependen del estado (¿existe el usuario? ¿hay stock?) en la capa de negocio, no en el esquema.

**Señal de que falla**: la misma validación repetida en cinco handlers; un `TypeError` interno ante un campo faltante; el servidor acepta un campo inesperado y lo guarda.

## 3 · Manejo de errores

**Qué hacer**
- **Un solo manejador central** de errores (middleware, filtro o exception handler), no un `try/catch` en cada handler.
- Distinguir **errores de dominio** ("saldo insuficiente", "no encontrado": esperados, con su código HTTP) de **errores técnicos** (la DB se cayó: inesperados, `500`, se registran).
- **Formato de error consistente** en toda la API — por ejemplo Problem Details (RFC 9457): `type`, `title`, `status`, `detail`.
- Al cliente nunca le llega un stack trace ni un mensaje interno; a los logs sí (con el detalle completo).
- No tragar excepciones con un `catch` vacío.

**Señal de que falla**: respuestas de error con formas distintas según el endpoint; un `500` con el SQL en el mensaje; `except: pass`.

## 4 · Diseño de API

**Qué hacer**
- **Recursos y verbos HTTP** con su semántica: `GET` no modifica nada; `PUT` y `DELETE` son idempotentes; `POST` crea.
- **Idempotencia en las operaciones que cobran o crean algo** (pagos, pedidos): aceptar una `Idempotency-Key` para que un reintento del cliente no duplique el efecto.
- **Paginar** toda lista que pueda crecer. Cursor para datos que cambian seguido o son grandes; offset solo para listados chicos y estables.
- El **contrato** (OpenAPI o equivalente) es la fuente de verdad; idealmente se genera o se verifica contra el código, no se escribe aparte a mano.
- **No romper compatibilidad**: agregar campos es seguro; quitar o cambiar el significado de uno exige versionar.
- Códigos de estado correctos: `201` al crear, `204` sin cuerpo, `404` vs `403` con criterio, `409` ante conflicto.

**Señal de que falla**: un `GET` que borra; un listado que devuelve 50 000 filas; cada cliente rompe cuando se agrega un campo.

## 5 · Datos y persistencia

**Qué hacer**
- **Transacciones** para cualquier operación de varios pasos que tiene que ser todo o nada.
- **Migraciones versionadas** en el repo; nunca modificar el esquema a mano en producción.
- **Consultas parametrizadas** siempre; jamás concatenar input en un SQL (ver `security.md`).
- Vigilar el **N+1** (una query por cada fila de una lista) y crear **índices** para las consultas reales, no para las imaginadas.
- **Dinero como entero de centavos o decimal exacto**, nunca `float`. **Fechas en UTC**; convertir a la zona del usuario solo al mostrar.
- Decidir el borrado a propósito: *soft delete* cuando hay que auditar o restaurar, borrado real cuando hay un requisito de privacidad.

**Señal de que falla**: `0.1 + 0.2` en un total; queries que tardan más a medida que crece una tabla; columnas nuevas que existen en producción pero no en ningún archivo de migración.

## 6 · Configuración

**Qué hacer**
- La configuración viene del **entorno** (variables de entorno), distinta por ambiente, nunca hardcodeada. Los secrets no se commitean (ver `security.md`).
- **Fallar al arrancar** si falta una variable obligatoria, con un mensaje que diga cuál; no descubrirlo en la primera request.
- Un único módulo que lee y valida la configuración; el resto del código la recibe, no lee `process.env` por su cuenta.

**Señal de que falla**: un `undefined` en producción que solo aparece cuando se ejecuta cierto endpoint; una URL de la base en el código.

## 7 · Trabajo asíncrono y llamadas externas

**Qué hacer**
- **Timeout en toda llamada a un servicio externo.** Una llamada sin timeout puede colgar el proceso entero.
- Lo lento va **fuera del request**: enviar emails, generar reportes o procesar archivos se encola como un job y se responde rápido.
- **Reintentos con backoff exponencial y jitter**, y solo para operaciones idempotentes.
- Cuando una dependencia externa es inestable, sumar un **circuit breaker** para no arrastrar todo el sistema con ella.
- Un job puede ejecutarse dos veces: hacerlo **idempotente** (ver `architecture-styles/event-driven.md`).

**Señal de que falla**: un endpoint que tarda 30 segundos porque manda un mail dentro del request; un reintento automático que cobra dos veces.

**Cuándo NO**: sin infraestructura de colas y con un volumen chico, un envío directo con timeout es más simple y suficiente (KISS).

## 8 · Observabilidad y seguridad

No se duplica acá:
- **Logs estructurados (JSON)**, id de correlación por request, health checks, error tracking y métricas → `observability.md`.
- **Autenticación y autorización en cada endpoint** (denegar por defecto), autorización a nivel de recurso (que el usuario A no lea el pedido del usuario B), rate limiting y CORS explícito → `security.md`.

## 9 · Testing

**Qué hacer**
- **Unit tests del dominio** sin DB ni HTTP: es el beneficio directo de separar capas.
- **Tests de integración con una base real** (un contenedor efímero) para los repositorios y las queries; un mock de la base no prueba que el SQL funcione.
- **Tests de contrato o de API** sobre los endpoints críticos.
- No mockear lo que no es tuyo más de lo necesario: envolver la librería externa detrás de un adapter (ver `design-patterns/structural.md`) y mockear tu adapter.

**Cuándo NO**: en un prototipo descartable alcanza con probar a mano; la decisión de TDD del proyecto está en `AGENTS.md`.

---

## Herramientas típicas — insumo de `PRACTICES.md`

Se listan como **recomendación**; la skill no instala nada por su cuenta. La opción concreta depende del stack (P3).

| Objetivo | Qué buscar |
|---|---|
| Linter + formatter | El estándar del lenguaje (ESLint/Biome en JS/TS, ruff en Python, golangci-lint en Go) |
| Validación de input | Librería de schemas o el mecanismo del framework (Zod, Pydantic, validadores del framework) |
| Migraciones | La del ORM elegido (Prisma Migrate, Alembic, Flyway, migraciones de Django/Rails) |
| Contrato de API | OpenAPI generado o verificado contra el código |
| Tests | El runner del stack + un contenedor para la base en los tests de integración |
| Auditoría de dependencias | `npm audit`, `pip-audit`, `cargo audit` (ver `dependencies.md`) |

## Cómo lo aplica la skill

- **P4/P6**: usa las secciones 1 y 2 para decidir cuántas capas lleva el scaffolding según la escala del proyecto.
- **P5.9**: cruza este archivo con el stack (P3) y la arquitectura (P4) para derivar las prácticas y herramientas de `PRACTICES.md`. Una práctica solo entra si el SPEC del proyecto la justifica (ej. la idempotencia de la sección 4 solo si hay pagos o creación de recursos con reintentos).
