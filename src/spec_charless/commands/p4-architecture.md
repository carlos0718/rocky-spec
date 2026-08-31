> Referencia de **charless-ia** — Paso P4 del flujo de creación: recomendación y decisión de arquitectura.

### P4 · Recomendar y decidir arquitectura

> Referencia de tipos y criterios de decisión: `.charless/reference/architectures.md`. Los árboles de carpetas están separados por categoría — `.charless/reference/architectures/codigo.md`, `creativo.md`, `hibrido.md`, `aprendizaje.md` — abrir solo el que corresponde al tipo de proyecto ya definido en P1.

Para **creativo** e **híbrido**, la estructura está predefinida en `.charless/reference/architectures/creativo.md` / `.charless/reference/architectures/hibrido.md` según corresponda. Mostrarla y confirmar directamente.

Para **código** (y la parte código de proyectos híbridos), ejecutar el flujo completo de recomendación:

#### Paso 1 — Evaluar el proyecto en 5 dimensiones

Basado en todo lo relevado hasta ahora (descripción de P1, análisis de dominio de P1.7, stack de P2-P3), puntuar en cada dimensión:

| Dimensión | Baja (1) | Media (2) | Alta (3) |
|---|---|---|---|
| **Complejidad de dominio** | 1-3 entidades simples, sin reglas | 4-8 entidades, algunas reglas | 9+ entidades, reglas complejas, estados |
| **Tamaño del equipo** | 1 persona | 2-3 personas | 4+ personas |
| **Horizonte de mantenimiento** | Semanas / prototipo | Meses | Años |
| **Escalabilidad** | Sin necesidad | Crecimiento moderado esperado | Alta carga, escala independiente |
| **Testabilidad requerida** | Tests básicos | TDD en partes críticas | TDD estricto, lógica aislada del framework |

> La fila de Escalabilidad se puntúa con el NFR ya definido en `SPEC.md` sección "Requisitos no funcionales" (P1.7) — si ahí quedó un objetivo concreto (no el default "sin proyección"), puntuar Alta directamente, no volver a preguntar.
>
> La fila de Testabilidad requerida se puntúa con la decisión de TDD ya tomada en P3: si el usuario eligió TDD → Alta directamente. Si no → puntuar según complejidad de dominio normal, sin asumir TDD.

**Score total (5–15):**
- 5–7 → arquitectura simple
- 8–11 → arquitectura mediana
- 12–15 → arquitectura compleja

#### Paso 2 — Recomendar arquitectura con explicación

Según el score y el tipo de proyecto, elegir de la lista completa en `.charless/reference/architectures.md` y mostrar la recomendación en este formato (el árbol de carpetas sale de `.charless/reference/architectures/codigo.md`):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Arquitectura recomendada: [NOMBRE]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Qué es?
[Explicación en 2-3 líneas, sin jerga. Como si le explicaras a alguien
que acaba de empezar a programar. Usar analogías si ayuda.]

¿Por qué para este proyecto?
→ [Razón 1 específica del análisis que hicimos]
→ [Razón 2 específica]
→ [Razón 3 si aplica]

¿Qué ventajas concretas te da?
✅ [Beneficio 1]
✅ [Beneficio 2]
✅ [Beneficio 3]

¿Qué sacrificás?
⚠️ [Trade-off 1 — ser honesto]
⚠️ [Trade-off 2 si aplica]

Estructura de carpetas resultante:
[árbol del proyecto según esta arquitectura]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Tono de la explicación según el perfil del usuario:**

- Si el perfil muestra poca experiencia o el usuario nunca mencionó estas arquitecturas → explicar desde cero con analogías simples. Ejemplo: *"Clean Architecture es como una empresa bien organizada: hay un CEO (el dominio) que toma decisiones de negocio, y hay empleados (la infraestructura) que ejecutan. El CEO no sabe cómo se usan las computadoras — eso es trabajo de los empleados. Así el dominio es independiente del framework."*

- Si el usuario ya mencionó términos técnicos o el perfil muestra experiencia → ser más conciso y técnico, ir directo a los trade-offs.

#### Paso 3 — Interacción y feedback

Después de mostrar la recomendación, ofrecer:

```
¿Qué hacés con esta propuesta?
> 1) La acepto — seguimos con esta estructura
  2) Quiero ver otra opción (decime cuál o qué cambiar)
  3) Tengo una pregunta sobre esta arquitectura
  4) Ya sé lo que quiero — la describo yo
```

**Si el usuario elige 2** → mostrarle las alternativas cercanas con sus trade-offs, y dejar que elija. No cambiar sin explicar por qué la alternativa podría ser mejor o peor para SU caso.

**Si el usuario elige 3** → responder la pregunta con ejemplos concretos del proyecto actual, no ejemplos genéricos.

**Si el usuario elige 4** → modo libre: el usuario describe la estructura, la skill la implementa sin opinar.

**Si el usuario elige 1** (acepta la recomendación) → guardar en `.skill-state.json`, para usar en P6 sección "Decisiones del setup" de `AGENTS.md`, una síntesis de 1-2 líneas de las razones ya mostradas en "¿Por qué para este proyecto?" del Paso 2 — no repetir la explicación completa, solo la conclusión. Este paso se salteaba antes (el razonamiento se mostraba en el chat y se perdía apenas terminaba la sesión) — ahora queda escrito.

**Si el usuario ya sabe de arquitecturas y da feedback** (ej: "prefiero Hexagonal porque vamos a tener múltiples adapters") → incorporar su razonamiento, confirmar que aplica, y documentar la decisión en el `AGENTS.md` del proyecto (sección "Decisiones del setup") con el razonamiento del usuario:
```
## Decisiones del setup
- Arquitectura: Hexagonal — elegida porque el proyecto necesita múltiples
  adapters de entrada (API REST + CLI + webhooks). El dominio define los
  ports y cada canal implementa su adapter.
```

#### Principios activos del perfil que influyen en la arquitectura

Leer `.charless/reference/coding-principles.md` + sección "Principios de código" de `profile.md`:

- **Repository activo + DB** → separar `domain/repositories/` (interfaces) de `infrastructure/persistence/` (implementaciones), aunque la arquitectura base sea feature-based.
- **SOLID activo + mediano+** → separar interfaces de implementaciones en general.
- **YAGNI activo + proyecto chico** → NO sobre-estructurar. Una landing no necesita `domain/` aunque Repository esté activo.
- **MVC/MVVM activo + framework que lo espera** (Rails, Django, NestJS, Angular) → respetar la convención nativa del framework.

Mencionar qué principios influyeron: *"Como tenés Repository y SOLID activos, separé `domain/` de `infrastructure/` aunque la arquitectura base sea feature-based."*

