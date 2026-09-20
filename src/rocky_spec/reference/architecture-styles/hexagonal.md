> Referencia de **rocky-spec** — ficha del estilo de arquitectura **Hexagonal** (Ports & Adapters). Mapa de todos los estilos y matriz de decisión en `.rocky-spec/reference/architectures.md`; abrir esta ficha solo cuando P4 (o Modo Adopción) ya apunta a este estilo.

# Arquitectura Hexagonal (Ports & Adapters)

**Analogía**: los enchufes. La lógica es un electrodoméstico que define qué clase de enchufe necesita; cualquier adaptador que encaje lo alimenta —la pared de tu país, la de otro, un generador—. El aparato no cambia; cambia el adaptador.

## Qué es

Propuesta por Alistair Cockburn (2005). La aplicación —dominio y casos de uso— ocupa el centro, y **se comunica con el exterior solo a través de puertos y adaptadores**:

- **Puerto** (*port*): una interfaz que **la aplicación define**, expresada en el lenguaje del negocio (`PaymentGateway.charge`, no `Stripe.createPaymentIntent`).
- **Adaptador** (*adapter*): la implementación que traduce entre el mundo externo y el puerto. Es el patrón Adapter de GoF (`design-patterns/structural.md`) puesto al servicio de la arquitectura.

Hay dos lados, y conviene no confundirlos:

- **Lado que maneja la aplicación** (*driving* o primario): quién le dice a la app qué hacer — una API REST, un CLI, una cola de mensajes, un cron, **un test**. Sus puertos son los *casos de uso* (puertos de entrada).
- **Lado manejado por la aplicación** (*driven* o secundario): a quién le pide cosas la app — la base de datos, el email, la pasarela de pago. Sus puertos son interfaces que la app define y la infraestructura implementa (puertos de salida).

El hexágono es solo una metáfora para dibujar varios lados; **no significa seis** de nada.

## Diagrama

```
   Adaptadores de ENTRADA (manejan a la app)
   [ REST ]   [ CLI ]   [ Cola ]   [ Test ]
       │         │         │          │
       ▼         ▼         ▼          ▼
   ┌─────────────────────────────────────────┐
   │        Puertos de entrada               │
   │        (casos de uso)                   │
   │                                         │
   │         DOMINIO + APLICACIÓN            │
   │                                         │
   │        Puertos de salida                │
   │        (interfaces que la app define)   │
   └─────────────────────────────────────────┘
       │         │         │          │
       ▼         ▼         ▼          ▼
   [ Postgres ] [ Stripe ] [ SMTP ] [ Broker ]
   Adaptadores de SALIDA (manejados por la app)
```

## Estructura de carpetas de ejemplo

```
src/
  domain/                    entidades y reglas
  application/
    ports/
      in/                    PlaceOrder            (caso de uso, lo que la app ofrece)
      out/                   OrderRepository,      (lo que la app necesita)
                             PaymentGateway
    services/                implementan los puertos de entrada
  adapters/
    in/
      http/                  controladores REST
      cli/                   comandos
      queue/                 consumidor de mensajes
    out/
      postgres/              OrderRepositoryPg
      stripe/                StripePaymentGateway
      smtp/                  SmtpMailer
  main.ts                    composition root: elige y cablea los adaptadores
```

Lo que se verifica: `domain/` y `application/` no importan nada de `adapters/`. Los adaptadores importan los puertos, nunca al revés. El **composition root** es el único lugar que decide qué adaptador va con qué puerto (ver Dependency Injection en `design-patterns.md`).

## Cuándo sí

- **Varios canales de entrada** para la misma lógica: API REST + CLI + cron + webhooks, sin duplicar el negocio.
- **Proveedores intercambiables** detrás de un puerto (pagos, storage, email), o dependencias externas inestables que pueden cambiar.
- **TDD estricto**: se prueba el caso de uso con adaptadores falsos en memoria, sin levantar nada.
- Dominio complejo y de larga vida, igual que Onion y Clean.

## Cuándo no

- Apps simples con un solo canal de entrada y un solo proveedor sin previsión de cambio.
- Prototipos y MVPs.
- Si todos los puertos serían un reenvío uno a uno del ORM o del SDK del proveedor: no hay nada que aislar y solo agregás pegamento.

## Señales de alarma

- **Lógica de negocio dentro de un adaptador**: el controlador calcula descuentos, o el adaptador de Postgres decide reglas.
- **El dominio importa tipos de un adaptador** (`Request`, una entidad del ORM, un tipo del SDK del proveedor).
- **Puertos que copian la API del proveedor** (`StripePort.createPaymentIntent`) en vez de expresar la necesidad del negocio (`PaymentGateway.charge`): el proveedor se filtra al dominio a través de la interfaz, y cambiarlo sigue doliendo.
- **Explosión de puertos** (uno por método) o un puerto God con veinte operaciones (ver Interface Segregation en `solid.md`).
- Adaptadores sin tests de contrato: nadie verifica que realmente cumplan lo que el puerto promete.

## Qué ganás y qué sacrificás

| Ganás | Sacrificás |
|---|---|
| Probar la lógica sin infraestructura, con adaptadores en memoria | Más código "de pegamento" y mapeos |
| Cambiar tecnología o proveedor sin tocar el negocio | Indirección: seguir una llamada cuesta más pasos |
| Sumar un canal de entrada nuevo sin duplicar la lógica | Disciplina para que las fronteras no se filtren |
| Fronteras explícitas y nombradas | Sobreingeniería si el problema es simple |

## Hexagonal frente a Onion y Clean

Las tres aplican la misma **regla de dependencia**: todo apunta al dominio. Hexagonal pone el foco en la **frontera** —qué puertos hay y cómo se enchufan los adaptadores, con simetría entre entrada y salida— y **no prescribe capas internas**; Onion y Clean sí (ver la tabla comparativa en `onion.md`). Por eso se combinan bien: "hexagonal por fuera, Onion por dentro". Un puerto de entrada equivale a un caso de uso de la capa Application.

## Cómo se combina con otros estilos

- **Con event-driven**: el consumidor del broker es un adaptador de entrada y quien publica eventos es un adaptador de salida. La aplicación no sabe si detrás hay Kafka, RabbitMQ o SQS (`event-driven.md`).
- **Dentro de un monolito modular**: cada módulo puede tener sus propios puertos y adaptadores (`monolith.md`).
- **Con microservicios**: la forma más habitual de organizar por dentro **cada servicio** (`microservices.md`).
- **Con Repository y Dependency Injection**: son las piezas con las que se implementan los puertos de salida (`design-patterns.md`).

## Cómo la usa la skill

- **P4**: la matriz de decisión lo recomienda para "sistema con múltiples canales de entrada (API + CLI + cron)" y para dominio complejo con 3+ personas. Si el usuario ya lo pide ("prefiero Hexagonal porque vamos a tener múltiples adapters"), se documenta su razonamiento en "Decisiones del setup" de `AGENTS.md`.
- **Modo Adopción (MA-4)**: se reconoce por carpetas `ports/` y `adapters/`. Vale verificar que los puertos hablen el lenguaje del negocio y que no haya lógica en los adaptadores.
- **`PRACTICES.md`**: Adapter, Dependency Injection y Repository entran como patrones activos (`design-patterns.md`).
