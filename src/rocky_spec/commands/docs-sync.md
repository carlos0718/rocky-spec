> Referencia de **rocky-spec** — paso `docs-sync`, servido por la skill separada `rocky-docs-sync` (no por el índice lineal de `rocky-spec`). Se carga al marcar el último checkbox de una sección de `TODO.md` (o de un archivo de `todos/`), al agregar un `RF-N`/`US-N`/`RNF-N` nuevo a `SPEC.md`, o al preguntar qué tareas implementan un requisito.

### docs-sync · Sincronización de documentación

## README sync — al completar una sección del TODO

**Regla:** cuando se marca el **último checkbox de una sección completa** del `TODO.md` (modo único) **o de un archivo de grupo completo** en `todos/` (modo orquestador, por capas o por features), actualizar la sección correspondiente del `README.md` antes del commit — así el README siempre refleja el estado real del proyecto.

| Sección de TODO.md / archivo de `todos/` | Qué actualizar en README.md                                                                   |
|--------------------------|-----------------------------------------------------------------------------------------------|
| **Setup**                | Verificar/completar scripts (`dev`, `build`, `test`, `lint`), pasos de instalación y variables de entorno |
| **Features iniciales** (modo único) / `todos/dominio-db.md`, `todos/api-backend.md`, `todos/frontend-ui.md` (modo orquestador) | Agregar o actualizar la sección "Features" con lo que realmente se construyó |
| **Calidad**              | Actualizar comando de lint/coverage, agregar badge si aplica                                  |
| **Infraestructura / Deploy** (modo único) / `todos/infraestructura-deploy.md` (modo orquestador) | Agregar URL de producción, hosting, y variables de entorno de prod si corresponde |
| **Seguridad** (modo único) / `todos/seguridad.md` (modo orquestador) | No suele necesitar sección propia en el README, salvo que el proyecto sea open source |
| **Documentación**        | Completar secciones vacías, agregar links a docs adicionales o diagramas generados            |

En modo orquestador, completar un archivo de grupo también actualiza la tabla "Estado por grupo" de `TODO.md` en el mismo commit (ver "Workflow de Git" de `AGENTS.md`, paso 1).

**Formato del commit cuando se hace README sync** (última tarea de la sección + README):
```
docs: update README — sección <nombre> completada (TODO: <última tarea>)
```

**Cuándo NO disparar el sync:**
- Si quedan `- [ ]` sin marcar en la sección — todavía no es el momento.
- Si la sección no tiene impacto visible en el README (ej. refactors internos) — se puede omitir.
- Si el usuario prefiere controlar el README manualmente — respetar, pero avisar al llegar al final de cada sección.

## Trazabilidad de requisitos

`SPEC.md` numera tres tipos de requisitos, cada uno con su prefijo: **`RF-N`** (Requisito Funcional — features), **`US-N`** (User Story — cómo se desglosa un RF desde la perspectiva del usuario), **`RNF-N`** (Requisito No Funcional — performance, escalabilidad, etc.). La cadena de trazabilidad completa:

```
RF-N (feature)  →  US-N (historia que la implementa)  →  tarea del TODO (US-N)
RNF-N (no funcional)  →  tarea del TODO (RNF-N), si el requisito tiene un objetivo concreto que exige trabajo puntual
```

Las tareas del TODO que implementan una historia terminan con su ID: `- [ ] Endpoint POST /login (US-1)`. Si además una tarea existe específicamente para cumplir un NFR (ej. agregar caché para cumplir un objetivo de performance), sumar también su ID: `- [ ] Agregar caché de Redis al endpoint de búsqueda (US-4, RNF-1)`. Tareas de infraestructura/setup/calidad genéricas no llevan ningún ID — no todo tiene que derivar de un requisito.

**Para responder "¿qué tareas implementan el RF-N / US-N / RNF-N?"**: `grep -rn "RF-N\|US-N\|RNF-N" SPEC.md TODO.md todos/ 2>/dev/null` — no hay una tabla de mapeo aparte que mantener sincronizada, el ID en cada línea es la fuente de verdad.

**Al agregar un requisito nuevo** (vía el flujo Spec-Anchored de `AGENTS.md`): asignarle el próximo ID disponible del tipo correspondiente en `SPEC.md`, y taguear las tareas nuevas del TODO con ese ID desde que se escriben — no como paso aparte al final.

> **Gestión de dependencias no vive acá a propósito.** A diferencia de lo de arriba (genérico, igual en cualquier proyecto), la política de pinning/cadencia/licencias se decide por proyecto durante el setup (P6/P7) y queda en la sección "Gestión de dependencias" de `AGENTS.md` con los valores reales elegidos — moverla a esta skill compartida le haría perder esa customización cada vez que se necesite, que es más seguido que "antes de un release grande".
