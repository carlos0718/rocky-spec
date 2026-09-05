> Referencia de **rocky-spec** — Modo Reanudación. Se carga cuando ya existe `.skill-state.json` (o `CLAUDE.md`/`TODO.md`/`SPEC.md`) en el proyecto y el usuario quiere continuar donde quedó.

## Reanudación

Antes de empezar P1, busca en el directorio actual un archivo `.skill-state.json`. Si existe, lee el último paso completado y pregunta:

> "Detecté un setup en curso de '<nombre>' que quedó en <paso>. ¿Continuamos desde ahí, o arrancamos de cero?"

Si el usuario continúa, salta directo al paso siguiente. Si arranca de cero, renombra el archivo viejo a `.skill-state.bak.json` y empieza P1.

Al final de cada paso completado, escribir/actualizar `.skill-state.json` con `{step, timestamp, decisions}`.

### Reanudación en modo desarrollo activo

Si la skill se invoca con frases de continuación ("qué sigue", "retomemos", "próxima tarea", etc.) y el proyecto ya está creado (existe `CLAUDE.md`, `TODO.md`, `SPEC.md`), ejecutar este flujo de verificación antes de arrancar:

1. **Leer `SPEC.md`** — ¿el alcance sigue igual o el usuario mencionó algo nuevo?
2. **Leer `TODO.md`** — ¿cuál es la próxima tarea sin hacer? ¿hay tareas pendientes de la sección actual?
3. **Si el usuario menciona una feature nueva o cambio de dominio** → aplicar el flujo Spec-Anchored (ver `AGENTS.md` del proyecto, sección "Agregar o modificar features") antes de escribir código. Además, el **Spec Drift Check** de `AGENTS.md` (Workflow de Git, paso 0) corre en cada commit durante esta sesión — no hace falta repetirlo acá al retomar, ya cubre los cambios que se hagan de ahora en más.
4. **Si el usuario dice algo tipo "el MVP está listo", "cerremos esta fase", "arranquemos la v2"** → aplicar el mecanismo de snapshot de `.rocky-spec/reference/methodologies.md` sección "Snapshots de fase — carpeta `specs/`": congelar el `SPEC.md` actual en `specs/<fase>/SPEC.md` antes de seguir editando el spec vivo para lo que sigue.
5. **Si es continuación normal** → retomar desde la próxima tarea del TODO, siguiendo el orden: Dominio/DB → API/Backend → Frontend/UI.

