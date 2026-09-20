> Referencia de **rocky-spec** — ficha del estilo de arquitectura **monolítica** (simple y modular). Mapa de todos los estilos y matriz de decisión en `.rocky-spec/reference/architectures.md`; abrir esta ficha solo cuando P4 (o Modo Adopción) ya apunta a este estilo.

# Arquitectura monolítica

**Analogía**: una casa de una planta. Una puerta, una cocina, todo a mano: para una persona o una pareja es perfecta. Cuando viven veinte, hay que ordenar en habitaciones (monolito modular) mucho antes de pensar en mudarse a un edificio de departamentos (microservicios).

## Qué es

Una **única unidad de despliegue**: todo el código se construye, se ejecuta y se despliega junto, en un solo proceso. No significa "código desordenado": un monolito puede estar muy bien organizado. Hay dos variantes que conviene distinguir:

- **Monolito plano**: sin fronteras internas — la interfaz, la lógica y el acceso a datos conviven sin separación formal. Correcto para prototipos, MVPs y herramientas chicas.
- **Monolito modular**: un solo despliegue, pero dividido en **módulos con fronteras explícitas**. Cada módulo expone una API interna (un `index` público) y esconde sus datos y detalles; los demás módulos no llegan a sus tablas ni a sus archivos internos. Es el punto medio recomendado cuando el proyecto crece.

## Diagrama

```
Monolito plano                  Monolito modular

┌──────────────────────┐        ┌────────────────────────────────────┐
│  UI + lógica + datos │        │ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  (todo mezclado)     │        │ │  users  │ │ orders  │ │ billing ││
└──────────┬───────────┘        │ └─────────┘ └─────────┘ └─────────┘│
           │                    │  se hablan solo por su API pública │
        [ DB ]                  └─────────────────┬──────────────────┘
                                               [ DB ]
                                 (cada módulo es dueño de sus tablas)
```

## Estructura de carpetas de ejemplo

**Plano** (Mini/Chico — ver `architectures/codigo.md`):

```
src/
  index.ts
  routes.ts
  db.ts
  utils.ts
```

**Modular** (cada módulo es una mini-aplicación):

```
src/
  modules/
    users/
      index.ts          ← única puerta de entrada del módulo
      users.service.ts
      users.repository.ts
      users.types.ts
    orders/
      index.ts
      ...
    billing/
      index.ts
      ...
  shared/               ← solo lo verdaderamente transversal (config, logger)
  main.ts               ← arranca y cablea los módulos
```

La regla del monolito modular: **un módulo solo importa de otro a través de su `index`**, nunca de sus archivos internos, y nunca lee las tablas del otro.

## Cuándo sí

- MVPs y prototipos donde la velocidad importa más que la estructura.
- Equipos chicos (una a cinco personas) trabajando sobre el mismo producto.
- Dominio todavía incierto: no sabés dónde van a estar los límites reales, y equivocarse de frontera en un monolito se corrige con un refactor, no con una migración de infraestructura.
- Baja o moderada carga, o una carga que se escala bien escalando el proceso entero.
- Se quiere un solo pipeline de deploy, un solo lugar donde mirar logs, transacciones ACID simples y debugging local.

## Cuándo no (o cuándo evolucionarlo)

- Varios equipos se pisan en el mismo código y un deploy de uno bloquea a los otros.
- Una parte concreta necesita **escalar o desplegarse de forma independiente** (un procesamiento pesado que no debería competir con la API).
- Una parte necesita una tecnología distinta (un componente de ML en Python dentro de un backend en otro lenguaje).
- El build y los tests tardan tanto que frenan el trabajo.

Ojo: en estos casos el primer paso casi siempre es **modularizar**, no partir en servicios (ver "Cómo se combina").

## Señales de alarma

- **Big ball of mud**: imports circulares entre "módulos"; cualquier cambio rompe algo lejano.
- Un módulo lee directamente las tablas de otro.
- Nadie sabe dónde poner el código nuevo, así que va a `utils` o a `shared`.
- La carpeta `shared/` o `common/` crece más rápido que los módulos.
- El tiempo de build y de tests crece sin parar.

## Qué ganás y qué sacrificás

| Ganás | Sacrificás |
|---|---|
| Simplicidad operativa: un deploy, un proceso, un lugar para los logs | Se escala todo junto, aunque solo una parte lo necesite |
| Transacciones ACID sin coordinar servicios | Sin disciplina, el acoplamiento crece hasta el barro |
| Refactors seguros con el IDE, debugging local | Un bug grave puede tirar todo el sistema |
| Cero latencia de red entre partes | Un solo stack tecnológico para todo |

## Cómo se combina con otros estilos

- **Con Clean/Onion/Hexagonal por dentro**: un monolito hexagonal (o cada módulo con su propio núcleo) es una combinación muy habitual y sana. El estilo de organización interna y el de despliegue son decisiones independientes.
- **Con event-driven dentro del proceso**: un bus de eventos en memoria desacopla los módulos sin sumar infraestructura; si más adelante un módulo sale a un servicio, el evento pasa a un broker real.
- **Camino a microservicios — Strangler Fig**: modularizar primero; extraer **un** módulo a la vez, empezando por el de fronteras y datos más claros; el monolito sigue funcionando mientras tanto. Mucho equipo pasa de "monolito plano" a "microservicios" saltando la etapa modular y termina con un monolito distribuido (ver `microservices.md`).

> **Regla de oro**: "Monolito primero. Microservicios cuando duele." — Martin Fowler.

## Cómo la usa la skill

- **P4**: score 5–7 → monolito plano (Mini/Chico). Score 8–11 → monolito modular, que en la práctica es el tamaño Mediano feature-based (`architectures/codigo.md`). Score 12–15 sin necesidad real de escala o despliegue independiente → monolito modular con Clean/Hexagonal por dentro, no microservicios.
- **Modo Adopción (MA-4)**: se reconoce por un único artefacto desplegable (un solo `package.json`/`pyproject.toml`/`Dockerfile`) y sin carpeta `services/`. Si hay fronteras entre carpetas, decir que es modular; si no, plano.
- **Documentación**: la decisión y el porqué van a "Decisiones del setup" de `AGENTS.md`.
