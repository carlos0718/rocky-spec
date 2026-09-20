> Referencia de **rocky-spec** — ficha del estilo de arquitectura **orientada a eventos** (event-driven). Mapa de todos los estilos y matriz de decisión en `.rocky-spec/reference/architectures.md`; abrir esta ficha solo cuando P4 (o Modo Adopción) ya apunta a este estilo.

# Arquitectura orientada a eventos

**Analogía**: el pregonero de un pueblo. Anuncia "llegó el barco" en la plaza, y quien esté interesado reacciona —el panadero prepara harina, la aduana manda un inspector—. El pregonero no sabe quién escucha ni cuántos son; y si mañana se suma un vecino nuevo, no hace falta avisarle al pregonero.

## Qué es

Los componentes se comunican **publicando y reaccionando a eventos** en vez de llamarse directamente. Un **evento** es un hecho que **ya ocurrió**, nombrado en pasado (`OrderPlaced`, `PaymentFailed`). El productor lo publica y no sabe quién lo consume; los consumidores no saben quién lo produjo. Un **broker** (Kafka, RabbitMQ, SQS/SNS, NATS, Redis Streams) los transporta.

La distinción que más se confunde:

| | Evento | Comando / mensaje dirigido |
|---|---|---|
| Qué dice | "Ocurrió X" | "Hacé X" |
| Destinatario | Ninguno en particular; quien quiera | Uno concreto |
| Nombre | Pasado: `OrderPlaced` | Imperativo: `SendEmail` |
| Acoplamiento | El productor no depende de nadie | El emisor depende del receptor |

Si un "evento" en realidad ordena algo a alguien concreto, es un comando con otro nombre y el acoplamiento está oculto.

Variantes, de menor a mayor costo:

- **Notificación de evento**: evento liviano ("cambió el pedido 42"); el consumidor consulta el detalle.
- **Event-carried state transfer**: el evento trae los datos que el consumidor necesita, así no vuelve a preguntar.
- **Event Sourcing**: el estado no se guarda como una fila, sino como la **secuencia de eventos** que lo produjeron, y se reconstruye reproduciéndolos. Y **CQRS**: separar el modelo de escritura del de lectura. Son potentes y caros; **no son lo mismo que event-driven a secas** y casi nunca hacen falta.

## Diagrama

```
┌─────────────┐                  ┌────────────┐          ┌─────────────┐
│    orders   │ ───────────────► │   BROKER   │ ───────► │    email    │
│ (productor) │   OrderPlaced    │   topic:   │ ───────► │  inventory  │
└─────────────┘                  │   orders   │ ───────► │  analytics  │
                                 └────────────┘          └─────────────┘
                                                         (consumidores)

El productor no conoce a los consumidores. Sumar uno nuevo no lo toca.
```

## Estructura de carpetas de ejemplo

```
src/
  domain/
    events/                OrderPlaced.ts       ← contrato del evento (versionado)
  modules/
    orders/
      publishers/          publica OrderPlaced tras guardar el pedido
    inventory/
      handlers/            reserva stock cuando llega OrderPlaced
    notifications/
      handlers/            manda el mail cuando llega OrderPlaced
  infrastructure/
    messaging/             adaptador del broker + outbox + reintentos + DLQ
```

El broker vive detrás de un adaptador (ver `hexagonal.md`): el módulo de negocio publica en una interfaz, no en el SDK de Kafka.

## Cuándo sí

- **Flujos asíncronos donde no hace falta respuesta inmediata**: notificaciones, generación de reportes, integraciones, analytics.
- **Picos de carga**: la cola actúa de buffer y los consumidores procesan a su ritmo.
- **Desacoplar** módulos o servicios, o cuando **varios consumidores** reaccionan al mismo hecho.
- Se necesita un **registro de auditoría** de todo lo que pasó.
- Se quiere **extensibilidad**: sumar un consumidor nuevo sin tocar al productor (Open/Closed, ver `solid.md`).

## Cuándo no

- Cuando necesitás **respuesta inmediata y consistente**: checkout → confirmación de pago. Ahí una llamada directa es lo correcto.
- Flujos simples donde una llamada a función o a un servicio alcanza (KISS).
- Sin infraestructura de mensajería, o sin nadie que pueda operarla.
- Cuando nadie va a poder seguir el flujo de punta a punta y responder "¿quién reacciona a este evento?".

## Señales de alarma

- **Espagueti de eventos**: eventos que disparan eventos que disparan eventos, y nadie entiende el flujo completo.
- **Comandos disfrazados de eventos** (`SendEmailNow`): acoplamiento oculto.
- Consumidores que **asumen un orden** que el broker no garantiza.
- Un evento gigante que expone el modelo interno del productor: cualquier cambio interno rompe a los consumidores.
- **Sin idempotencia**: un mensaje duplicado cobra dos veces.
- **Sin dead-letter queue**: un mensaje que siempre falla bloquea la cola o se pierde en silencio.
- Eventos sin versionado de esquema.

## Conceptos que hay que resolver

- **Entrega al menos una vez** → los consumidores deben ser **idempotentes**: procesar el mismo evento dos veces produce el mismo resultado (deduplicar por el id del evento). Asumir que los duplicados ocurren.
- **Orden**: los brokers lo garantizan solo **dentro de una partición o clave**, no globalmente. No diseñar como si hubiera orden global.
- **Consistencia eventual**: el efecto de un evento no es instantáneo. La UI y la API tienen que tolerar que el resultado tarde en aparecer.
- **Outbox pattern**: guardar el evento en la **misma transacción** que el cambio de datos y publicarlo después desde esa tabla. Evita el clásico "guardé el pedido pero se cayó antes de publicar" (*dual write*).
- **Reintentos con backoff** y **dead-letter queue** para lo que sigue fallando.
- **Versionado de esquemas** compatibles hacia atrás.
- **Observabilidad**: un **id de correlación** que viaja dentro del evento y aparece en los logs de cada consumidor (ver `observability.md`).

## Qué ganás y qué sacrificás

| Ganás | Sacrificás |
|---|---|
| Desacople: productor y consumidores no se conocen | El flujo queda implícito y es difícil de seguir y depurar |
| Consumidores que escalan por separado | Consistencia eventual en vez de inmediata |
| Resiliencia: si un consumidor cae, los mensajes esperan | Más infraestructura para operar |
| Extensibilidad: un consumidor nuevo no toca al productor | Duplicados y desorden que hay que manejar |

## Cómo se combina con otros estilos

Es un **complemento**, no un estilo base: casi siempre se suma a otro.

- **Dentro de un monolito modular**: un bus de eventos en memoria desacopla los módulos sin sumar infraestructura; más tarde puede pasar a un broker real (`monolith.md`).
- **Entre microservicios**: su medio natural para comunicarse sin cadenas síncronas (`microservices.md`).
- **Con Hexagonal**: el consumidor del broker es un adaptador de entrada; quien publica eventos es un adaptador de salida (`hexagonal.md`).
- **Con Onion o Clean**: los eventos de dominio nacen en el Domain Model y los handlers viven en Application (`onion.md`).
- **Observer** (`design-patterns/behavioral.md`) es la misma idea dentro de un solo proceso; event-driven la lleva a través de la red.

## Cómo la usa la skill

- **P4**: lo trata como **complemento** de la arquitectura elegida. Se suma cuando el SPEC tiene flujos asíncronos, notificaciones o picos de carga, no como estilo base (matriz: "complementa otra arquitectura").
- **Modo Adopción (MA-4)**: se reconoce por dependencias de mensajería (`kafkajs`, `amqplib`, `@aws-sdk/client-sqs`, `celery`, `pika`) y carpetas `events/`, `handlers/`, `consumers/`. Vale preguntar si los consumidores son idempotentes y si hay DLQ.
- **`PRACTICES.md`**: Observer, Outbox e idempotencia entran como prácticas activas. Si el broker es un servicio gestionado, se registra como servicio externo en P3.
