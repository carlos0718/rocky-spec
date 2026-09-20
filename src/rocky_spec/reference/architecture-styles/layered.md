> Referencia de **rocky-spec** — ficha del estilo de arquitectura **en capas** (layered / N-tier). Mapa de todos los estilos y matriz de decisión en `.rocky-spec/reference/architectures.md`; abrir esta ficha solo cuando P4 (o Modo Adopción) ya apunta a este estilo.

# Arquitectura en capas

**Analogía**: un edificio de oficinas. La recepción atiende al público, los gerentes deciden, el archivo guarda los papeles. La recepción no entra al archivo por su cuenta: le pide al gerente, y el gerente le pide al archivo.

## Qué es

El código se organiza en **capas horizontales**, cada una con una responsabilidad distinta, y **cada capa depende solo de la inferior**:

1. **Presentación** — recibe la request y devuelve la respuesta (controladores, rutas, vistas).
2. **Negocio** — las reglas y los casos de uso (servicios, lógica de dominio).
3. **Acceso a datos** — habla con la base (repositorios, DAOs, ORM).
4. **Base de datos**.

Dos matices que suelen confundirse:

- **Capas (layers)** son una organización *lógica* del código, normalmente dentro de un mismo proceso. **Tiers** son una separación *física* (cliente, servidor y base en máquinas distintas). "N-tier" mezcla ambos; acá se habla de capas lógicas.
- En la versión **estricta**, una capa solo llama a la inmediatamente inferior; en la **relajada**, puede llamar a cualquiera de las de abajo.

## Diagrama

```
┌───────────────────────────┐
│  Presentación (UI / API)  │
├─────────────┬─────────────┤
│             ▼             │   la flecha de dependencia
│  Negocio (servicios)      │   va siempre hacia ABAJO
├─────────────┬─────────────┤
│             ▼             │
│  Acceso a datos           │
├─────────────┬─────────────┤
│             ▼             │
│  Base de datos            │
└───────────────────────────┘
```

## Estructura de carpetas de ejemplo

Por capa técnica (la convención de Spring, Rails o Laravel):

```
src/
  presentation/     controllers, routes, DTOs de request/response
  business/         services, reglas de negocio
  data/             repositories, modelos del ORM, migraciones
  shared/           config, logger, errores comunes
```

Layered **por feature** (recomendado al crecer): las capas se repiten dentro de cada feature, así un cambio no cruza todo el proyecto:

```
src/features/orders/
  orders.controller.ts     ← presentación
  orders.service.ts        ← negocio
  orders.repository.ts     ← datos
```

## Cuándo sí

- CRUD con poca lógica de negocio: la mayoría de los casos de uso son "guardar, listar, editar".
- Equipos que vienen de arquitecturas empresariales clásicas, o donde el framework ya impone esta forma (Spring MVC, Rails, Laravel, Django).
- Dominio simple a mediano, sin reglas ricas ni necesidad de aislar el negocio de la base.
- Se quiere una estructura que cualquiera entienda sin explicación.

## Cuándo no

- **Dominio con reglas complejas**: como el negocio depende de la capa de datos, termina atado a la forma de la base. Es el origen del *anemic domain model*.
- Se necesita **testear el negocio sin base de datos**: la capa de negocio importa la de datos, así que hay que mockearla.
- Múltiples canales de entrada o proveedores intercambiables (ver `hexagonal.md`).
- Proyectos donde un cambio de negocio típico cruza las cuatro capas y las cuatro carpetas.

## Señales de alarma

- **Capas de adorno**: servicios que son un pasamanos de una línea (`return repo.findAll()`).
- **Anemic domain model**: entidades con solo getters/setters y servicios que concentran toda la lógica.
- La lógica de negocio se filtra a los controladores o a stored procedures.
- El modelo del ORM se usa en todas las capas, incluida la respuesta de la API (sin DTO).
- El "salto de capas" (controlador → repositorio directo) se vuelve la norma.
- Una capa `common`/`utils` gigante de la que todo depende.

## Qué ganás y qué sacrificás

| Ganás | Sacrificás |
|---|---|
| Simplicidad y familiaridad: casi todos la conocen | Un cambio de negocio suele tocar todas las capas |
| Fácil repartir trabajo por capa | Negocio acoplado a la persistencia |
| Poca ceremonia, arranque rápido | Testear el negocio arrastra a la capa de datos |
| Los frameworks clásicos la traen resuelta | Tendencia al modelo anémico y a las capas vacías |

## Cómo se combina con otros estilos

- **Con MVC**: la capa de presentación de una app web clásica *es* MVC (ver `architectures.md`); MVC organiza la interfaz, layered organiza todo el backend.
- **Dentro de un monolito**: es la organización interna más común de un monolito (ver `monolith.md`).
- **Evolución barata a Onion/Hexagonal**: el paso incremental es **invertir la dependencia** entre negocio y datos — definir la interfaz del repositorio en la capa de negocio y que la capa de datos la implemente. Sin mover ninguna carpeta ya se obtiene el beneficio principal (`onion.md`, `hexagonal.md`; principio D de `solid.md`).
- **Layered por feature + capas adentro**: combina la organización vertical (`architectures.md`, feature-based) con la horizontal.

## Cómo la usa la skill

- **P4**: aparece para dominio bajo o medio (matriz: "App web CRUD con backend simple → MVC o N-tier"), típicamente con score 5–11. Si Repository o SOLID están activos y el proyecto es mediano o más, P4 propone invertir la dependencia de datos aunque la base sea en capas.
- **Modo Adopción (MA-4)**: se reconoce por carpetas `controllers/`, `services/`, `repositories/`, `models/` (o `presentation/`, `business/`, `data/`) en la raíz de `src/`. Vale alertar si hay señales de modelo anémico.
- **`PRACTICES.md`**: Repository y DTO en el borde son las prácticas que casi siempre entran para este estilo (`best-practices-backend.md`, secciones 1 y 5).
