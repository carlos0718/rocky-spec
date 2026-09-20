> Referencia de **rocky-spec** — ficha del estilo de arquitectura **Onion**. Mapa de todos los estilos y matriz de decisión en `.rocky-spec/reference/architectures.md`; abrir esta ficha solo cuando P4 (o Modo Adopción) ya apunta a este estilo.

# Onion Architecture

**Analogía**: una cebolla. Podés pelar las capas de afuera —cambiar la base de datos, el framework web, el proveedor de email— y el centro, las reglas del negocio, queda intacto.

## Qué es

Propuesta por Jeffrey Palermo (2008). El código se organiza en **anillos concéntricos con el modelo de dominio en el centro**, y la regla es una sola: **las dependencias apuntan siempre hacia adentro**. Un anillo conoce a los de adentro, nunca a los de afuera.

Los anillos típicos, de adentro hacia afuera:

1. **Domain Model** — entidades, value objects y sus reglas. No importa nada.
2. **Domain Services** — reglas que no caben en una sola entidad; también las **interfaces** de los repositorios, que el dominio define.
3. **Application Services** — los casos de uso: orquestan el dominio para cumplir una tarea. Definen las interfaces de lo que necesitan del exterior (enviar un mail, cobrar).
4. **Infraestructura, UI y tests** — el anillo externo: la base de datos, el framework web, los clientes HTTP. **Implementan** las interfaces definidas por los anillos internos.

La consecuencia importante: en una arquitectura en capas clásica el negocio depende de la base; acá **la base depende del negocio** (ver Dependency Inversion en `solid.md`).

## Diagrama

```
   ┌───────────────────────────────────────────┐
   │  Infraestructura / UI / Tests             │  ← Web, ORM, email, framework
   │  ┌─────────────────────────────────────┐  │
   │  │  Application Services (casos de uso)│  │
   │  │  ┌───────────────────────────────┐  │  │
   │  │  │  Domain Services              │  │  │
   │  │  │  ┌─────────────────────────┐  │  │  │
   │  │  │  │  Domain Model           │  │  │  │  ← el centro: no importa nada
   │  │  │  └─────────────────────────┘  │  │  │
   │  │  └───────────────────────────────┘  │  │
   │  └─────────────────────────────────────┘  │
   └───────────────────────────────────────────┘

   Dependencias:   afuera ──────►  adentro    (nunca al revés)
```

## Estructura de carpetas de ejemplo

```
src/
  Domain/                  ← el centro
    entities/              Order, Customer
    value-objects/         Money, Email
    services/              PricingService
    repositories/          OrderRepository (solo la interfaz)
  Application/             ← casos de uso
    use-cases/             PlaceOrder, CancelOrder
    ports/                 PaymentGateway, Mailer (interfaces)
    dto/
  Infrastructure/          ← implementa lo que definen los anillos internos
    persistence/           OrderRepositoryPg
    payments/              StripePaymentGateway
    email/                 SmtpMailer
  Web/                     ← controladores + composition root
```

Lo que se verifica: `Domain/` no importa nada de afuera de sí mismo; `Application/` solo importa de `Domain/`; `Infrastructure/` y `Web/` importan hacia adentro. El **composition root** (en `Web/` o `main`) es el único lugar que conoce todas las piezas y las cablea (ver Dependency Injection en `design-patterns.md`).

## Cuándo sí

- **Dominio con reglas ricas** y vida larga (años), donde el negocio es el activo.
- Necesidad de **testear el negocio sin base de datos ni HTTP**.
- La tecnología puede cambiar (otra base, otro framework, otro proveedor) sin reescribir las reglas.
- Equipos de 3+ personas que necesitan fronteras claras.
- Combina bien con **DDD**: los agregados y value objects viven en el Domain Model (de hecho es su hábitat natural).

## Cuándo no

- **CRUD sin reglas de negocio**: si casi todos los casos de uso son "guardar y listar", el ritual de capas cuesta más de lo que aporta.
- MVPs y prototipos (ver YAGNI en `general-principles.md`).
- Equipos que no la conocen y no tienen tiempo de aprenderla.
- Proyectos donde el dominio son cuatro tablas y dos validaciones.

## Señales de alarma

- **El dominio importa el ORM o el framework** (anotaciones del ORM en las entidades, `Request` en un caso de uso). A veces es un atajo consciente y aceptable, pero es acoplamiento: que sea una decisión, no un descuido.
- **Interface-itis**: una interfaz por cada clase, con una sola implementación y sin motivo de test.
- Cadenas de mapeos (DTO ↔ entidad ↔ modelo de la base) que no aportan nada porque los tres tienen la misma forma.
- Un Domain Service que se volvió cajón de sastre: toda la lógica cae ahí y las entidades quedan vacías (modelo anémico).
- Capas que se saltean: un controlador que llama directo al repositorio concreto.

## Qué ganás y qué sacrificás

| Ganás | Sacrificás |
|---|---|
| Reglas de negocio testeables en aislamiento y rápido | Más archivos e indirección para lo mismo |
| Cambiar detalles técnicos sin tocar el negocio | Curva de aprendizaje del equipo |
| Fronteras claras que evitan el acoplamiento gradual | Mapeos entre capas |
| Un lugar único para cada regla del dominio | Ceremonia excesiva si el dominio es simple |

## Onion, Clean y Hexagonal — la misma idea

Las tres aplican la **regla de dependencia** (todo apunta al dominio). Las diferencias son de énfasis:

| | Onion | Clean | Hexagonal |
|---|---|---|---|
| Autor | Palermo (2008) | Robert C. Martin (2012) | Cockburn (2005) |
| Metáfora | Capas concéntricas | Círculos concéntricos | Puertos y adaptadores |
| Énfasis | Los anillos internos del dominio | Entities / Use Cases / Interface Adapters / Frameworks | La *frontera* y su simetría entrada/salida |
| Prescribe capas internas | Sí | Sí | No |

En la práctica se combinan sin conflicto — ver `hexagonal.md`. Elegir una sobre otra importa menos que aplicar la regla de dependencia con disciplina.

## Cómo se combina con otros estilos

- **Dentro de un monolito modular**: cada módulo con su propio Onion es una combinación muy común (`monolith.md`).
- **Con event-driven**: los eventos de dominio nacen en el Domain Model y los handlers viven en Application (`event-driven.md`).
- **Con CQRS**: Application separa comandos (escriben) de consultas (leen), a veces con modelos de lectura distintos.
- **Migrando desde capas**: invertir primero la dependencia de datos (`layered.md`, sección "Cómo se combina").

## Cómo la usa la skill

- **P4**: aparece con score 12–15 (dominio alto, horizonte largo, testabilidad alta) junto a Clean y Hexagonal. Con Repository o SOLID activos y proyecto mediano+, P4 separa `domain/` de `infrastructure/` aunque la base sea feature-based.
- **Modo Adopción (MA-4)**: se reconoce por carpetas `Domain/`, `Application/`, `Infrastructure/`. Vale verificar que `Domain/` realmente no importe nada de afuera.
- **`PRACTICES.md`**: entran Repository, Dependency Injection y Adapter (`design-patterns.md`); la decisión y su porqué van a "Decisiones del setup" de `AGENTS.md`.
