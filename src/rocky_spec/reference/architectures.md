# Arquitecturas — referencia completa para `/rocky-spec`

Este archivo tiene dos partes:
1. **Tipos de arquitectura** — qué son, cuándo usarlas, cuándo no, y la matriz de decisión que usa P4.
2. **Árboles de carpetas** — la estructura concreta que la skill crea en P5.

---

## PARTE 1 — Tipos de arquitectura y cuándo elegir cada uno

> **Regla del mentor:** el tamaño de la arquitectura debe **igualar** el tamaño del problema. Una landing no necesita Clean Architecture. Una plataforma multi-equipo no sobrevive en una carpeta `components/` plana.

### Dimensiones para elegir arquitectura

P4 evalúa el proyecto en 5 dimensiones para hacer la recomendación:

| Dimensión | Señales que la suben |
|---|---|
| **Complejidad de dominio** | Muchas entidades, reglas de negocio complejas, estados, flujos ramificados |
| **Tamaño del equipo** | Más de 2 personas trabajando en simultáneo |
| **Horizonte de mantenimiento** | El proyecto va a durar años, no meses |
| **Escalabilidad requerida** | Miles de usuarios, carga variable, necesidad de escalar partes independientemente |
| **Necesidad de testabilidad** | TDD estricto, lógica de negocio que hay que testear aislada del framework |

---

### Los 10 tipos de arquitectura

#### 1. Monolítica simple
**Una sola aplicación, todo junto.**

La arquitectura más simple posible. Todo el código vive en un mismo proceso: interfaz, lógica de negocio y acceso a datos en el mismo proyecto. No hay separación formal de capas.

✅ **Cuándo usarla:**
- MVPs y prototipos donde la velocidad importa más que la estructura
- Proyectos de 1 persona con horizonte corto
- Herramientas internas pequeñas
- Primeras versiones de un producto antes de saber si va a crecer

❌ **Cuándo NO:**
- Cuando más de 2 personas van a tocar el mismo código
- Cuando la lógica de negocio es compleja y necesita testearse aislada
- Cuando se anticipa crecimiento fuerte en 6+ meses

**Señal de alarma:** "todo está en el mismo archivo" o "no hay separación entre lo que muestra la pantalla y lo que calcula el servidor".

---

#### 2. MVC (Model-View-Controller)
**El clásico: datos, pantalla, y el coordinador en el medio.**

Divide la app en tres responsabilidades claras:
- **Model** = los datos y las reglas de negocio
- **View** = lo que ve el usuario
- **Controller** = recibe las acciones del usuario y coordina Model y View

✅ **Cuándo usarla:**
- Apps web tradicionales con formularios, páginas y CRUD (Rails, Django, Laravel style)
- Cuando el equipo ya conoce el patrón
- Backend APIs con poca lógica de negocio

❌ **Cuándo NO:**
- Cuando la lógica de negocio es muy compleja (el Model se vuelve un "fat model")
- Cuando necesitás testear lógica sin tocar la DB o el HTTP

---

#### 3. Arquitectura en Capas / N-tier
**Cada capa solo habla con la de abajo.**

Organiza el código en capas verticales: Presentación → Lógica de negocio → Acceso a datos → Base de datos. Cada capa solo puede llamar a la inmediatamente inferior.

```
┌─────────────────────────┐
│   Presentación (UI/API) │
├─────────────────────────┤
│   Lógica de negocio     │
├─────────────────────────┤
│   Acceso a datos (DAL)  │
├─────────────────────────┤
│   Base de datos         │
└─────────────────────────┘
```

✅ **Cuándo usarla:**
- Apps enterprise con equipos separados por capa
- CRUD pesado con poca lógica de negocio compleja
- Cuando el equipo viene de arquitecturas enterprise clásicas

❌ **Cuándo NO:**
- Cuando la lógica de negocio está tan ligada a la DB que el "acceso a datos" termina teniendo reglas de negocio (el problema del anemic domain model)

---

#### 4. Feature-based (Vertical Slices)
**Cada feature es un módulo independiente.**

En vez de organizar por tipo de archivo (todos los componentes juntos, todos los servicios juntos), organiza por feature: cada carpeta contiene todo lo que necesita esa feature (componentes, hooks, servicios, tipos, tests).

```
features/
  auth/         ← todo lo de autenticación
  checkout/     ← todo lo de compra
  dashboard/    ← todo lo de dashboard
```

✅ **Cuándo usarla:**
- SPAs con múltiples features independientes
- Apps de productividad, dashboards, SaaS frontends
- Equipos medianos donde cada persona/squad trabaja en su feature

❌ **Cuándo NO:**
- Cuando las features están muy acopladas entre sí (todo toca todo)
- Proyectos muy chicos donde separar por feature es over-engineering

---

#### 5. Clean Architecture
**El dominio al centro, el framework afuera.**

Creada por Robert C. Martin (Uncle Bob). El código se organiza en capas concéntricas donde las dependencias siempre apuntan hacia adentro: el dominio (lógica de negocio pura) no sabe nada del framework, de la DB, ni de HTTP.

```
         ┌─────────────────────────────┐
         │   Frameworks & Drivers      │  ← Express, React, Prisma
         │  ┌─────────────────────┐    │
         │  │   Interface Adapters│    │  ← Controllers, Presenters
         │  │  ┌─────────────┐   │    │
         │  │  │ Use Cases   │   │    │  ← Lógica de aplicación
         │  │  │ ┌─────────┐ │   │    │
         │  │  │ │Entities │ │   │    │  ← Dominio puro (reglas de negocio)
         │  │  │ └─────────┘ │   │    │
         │  │  └─────────────┘   │    │
         │  └─────────────────────┘   │
         └─────────────────────────────┘
```

✅ **Cuándo usarla:**
- Dominio complejo con muchas reglas de negocio
- Necesidad de testear lógica de negocio sin DB ni HTTP
- Equipo de 3+ personas, proyecto de largo plazo
- Cuando la tecnología (framework, DB) puede cambiar en el futuro

❌ **Cuándo NO:**
- Proyectos chicos o MVPs (es sobre-engineering)
- Cuando el equipo no conoce el patrón y no hay tiempo de aprenderlo

---

#### 6. Arquitectura Hexagonal (Ports & Adapters)
**El dominio habla con el mundo a través de "enchufes".**

Similar a Clean Architecture pero con una metáfora diferente. El dominio es el hexágono central. Todo lo externo (DB, HTTP, cola de mensajes, email) se conecta a través de "ports" (interfaces definidas por el dominio) y "adapters" (implementaciones concretas de esas interfaces).

```
      [Test] [API] [CLI]          ← Driving adapters (entrada)
           │   │   │
      ┌────┴───┴───┴────┐
      │                  │
      │    DOMINIO       │
      │                  │
      └────┬───┬───┬────┘
           │   │   │
      [DB] [Email] [Queue]        ← Driven adapters (salida)
```

La diferencia clave con Clean: Hexagonal es más explícita sobre los "ports" (interfaces) que el dominio define para comunicarse con el exterior.

✅ **Cuándo usarla:**
- Mismo caso que Clean Architecture
- Cuando hay múltiples "adaptadores" posibles para la misma "port" (ej: la misma lógica de negocio puede exponerse por API REST, CLI o cola de mensajes)
- TDD estricto con mocks de adapters

❌ **Cuándo NO:**
- Proyectos simples (overkill)

---

#### 7. Onion Architecture
**Las capas protegen al dominio como una cebolla.**

Variante de Clean/Hexagonal. Las capas van desde el dominio central hasta la infraestructura exterior, y las dependencias siempre apuntan hacia adentro (hacia el dominio). La diferencia con N-tier: en Onion la DB depende del dominio, no al revés.

✅ **Cuándo usarla:**
- Dominio complejo, larga vida útil del proyecto
- Similar a Clean y Hexagonal — los tres son variantes del mismo principio

---

#### 8. MVVM (Model-View-ViewModel)
**El ViewModel como intermediario reactivo.**

Variante de MVC pensada para interfaces reactivas. El ViewModel expone estado observable que la View consume directamente, sin que el Controller tenga que coordinar. La View se "enlaza" al ViewModel y se actualiza sola cuando cambia el estado.

✅ **Cuándo usarla:**
- Apps mobile (SwiftUI, Jetpack Compose, Flutter)
- Frontends con estado complejo y reactividad (Angular, WPF)
- Cuando el estado de la UI es complicado de manejar con MVC clásico

En React/Vue moderno, los stores (Zustand, Pinia) + componentes funcionan como MVVM aunque no se llamen así.

❌ **Cuándo NO:**
- Backend APIs (no tiene sentido sin UI)

---

#### 9. Microservicios
**Cada dominio es un servicio independiente.**

La aplicación se divide en múltiples servicios pequeños, cada uno con su propia DB, su propio deployment y su propio equipo. Se comunican por HTTP (REST/gRPC) o colas de mensajes.

✅ **Cuándo usarla:**
- Equipos grandes donde distintos squads trabajan en dominios separados
- Necesidad de escalar partes independientemente (el módulo de pagos necesita más recursos que el de perfil)
- Distintas partes del sistema tienen requirements técnicos muy diferentes

❌ **Cuándo NO:**
- Equipos pequeños (la complejidad operacional es enorme)
- MVPs (siempre empezar monolítico, partir después si hace falta)
- Sin infraestructura de observabilidad (logs, trazas, alertas) madura

**Regla de oro:** "Monolito primero. Microservicios cuando duele." — Martin Fowler

---

#### 10. Arquitectura Orientada a Eventos (Event-Driven)
**Las partes del sistema se comunican publicando y suscribiéndose a eventos.**

En vez de que el servicio A llame directamente al servicio B, A publica un evento ("OrderPlaced") y cualquier servicio interesado lo consume (servicio de email, de inventario, de analytics). El productor no sabe nada del consumidor.

✅ **Cuándo usarla:**
- Flujos asíncronos donde no necesitás respuesta inmediata (notificaciones, generación de reportes)
- Alta carga con picos de tráfico (la cola actúa como buffer)
- Sistemas distribuidos donde querés desacoplar productores de consumidores

❌ **Cuándo NO:**
- Cuando necesitás respuesta inmediata (checkout → confirmación)
- Proyectos simples donde una llamada directa es suficiente
- Sin infraestructura de mensajería (Kafka, RabbitMQ, SQS) disponible

---

### Matriz de decisión rápida

| Si el proyecto es... | Arquitectura recomendada |
|---|---|
| Landing / demo / script simple | Monolítica plana |
| SPA con pocas features, 1 persona | Feature-based chica |
| App web CRUD con backend simple | MVC o N-tier |
| SPA mediana / SaaS frontend con múltiples features | Feature-based mediana |
| App mobile o frontend muy reactivo | MVVM |
| Fullstack con dominio moderado, equipo chico | Clean Architecture simplificada (sin over-engineering) |
| Fullstack con dominio complejo, largo plazo, 3+ personas | Clean / Hexagonal / Onion |
| Sistema con múltiples canales de entrada (API + CLI + cron) | Hexagonal (Ports & Adapters) |
| Plataforma grande, múltiples equipos, escala independiente | Microservicios (con precaución) |
| Flujos asíncronos, notificaciones, alta carga | Event-Driven (complementa otra arquitectura) |

---

## PARTE 2 — Árboles de carpetas por tipo y tamaño

> Lo que la skill crea físicamente en P5 según la arquitectura elegida en P4.

## Cómo elegir (regla del mentor)

> El tamaño de la arquitectura debe **igualar** el tamaño del proyecto. Una landing con HTML+CSS+JS no necesita Clean Architecture. Una app empresarial multi-equipo no se sostiene en una carpeta `components/` plana.

Si el usuario duda, recomendá con justificación corta basada en el alcance que describió en P1.


Cada categoría tiene su propio archivo con los árboles de carpetas completos — abrir solo el que corresponde al tipo de proyecto ya definido en P1, no los cuatro:

- `.rocky-spec/reference/architectures/codigo.md` — Mini, Chico, Mediano, Grande, Libre
- `.rocky-spec/reference/architectures/creativo.md` — Video ad/motion, Social content batch, Branding visual
- `.rocky-spec/reference/architectures/hibrido.md` — Landing con animación 3D, Web inmersiva multi-escena
- `.rocky-spec/reference/architectures/aprendizaje.md` — `/learning-roadmap`
