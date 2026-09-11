> Referencia de **rocky-spec** — Modo Reanudación. Se carga cuando ya existe `.skill-state.json` (o `CLAUDE.md`/`TODO.md`/`SPEC.md`) en el proyecto y el usuario quiere continuar donde quedó.

## Reanudación

Antes de empezar P1 — o cualquier otra cosa — busca en el directorio actual un archivo `.skill-state.json`.

**Gate obligatorio, corre primero, antes de leer `step` o decidir nada más:** si `.skill-state.json` existe y `"mode"` es `"adopted"`, correr `rocky check drift .` siempre. El valor de `step` **no exime este chequeo bajo ninguna condición** — en particular, `step: "adoption_complete"` (el único valor que usa este modo, ver `mode-adopt.md`) significa "la adopción terminó en su momento", **no** "ya se revalidó drift en esta sesión". Confundir esos dos significados es el bug conocido de este archivo — ver nota abajo. Si `rocky check drift .` devuelve hallazgos, resolverlos siguiendo la tabla de remediación P6 de `mode-adopt.md` (generar los archivos faltantes con detección real del proyecto — stack, arquitectura, hallazgos de seguridad/observabilidad/accesibilidad; para `LICENSE`, preguntar explícitamente si no hay `license_decision` registrada) antes de seguir con cualquier otro paso, incluido el resto de esta sección.

> **Por qué este gate es imperativo y no una mención en prosa más abajo:** hasta v0.19.0, este chequeo vivía como paso 0 de la sub-sección "Reanudación en modo desarrollo activo" (más abajo), condicionado a "si la skill se invoca con frases de continuación...". En la práctica, una sesión veía `step: "adoption_complete"` en `.skill-state.json`, razonaba (con la lógica del párrafo siguiente, que es sobre *setups interrumpidos*) "la adopción ya está completa, no hay nada que reanudar" y pasaba directo al TODO sin ejecutar el paso 0 — nunca llegaba a correr `rocky check drift`. Subir el gate acá, antes de cualquier lectura de `step`, elimina la ambigüedad estructuralmente en vez de depender de que el agente no cruce el razonamiento de una sección con el trigger de la otra.

Recién después de este gate — o si `.skill-state.json` no existe, o `"mode"` no es `"adopted"` — seguir con la lógica de `step`: leer el último paso completado y preguntar:

> "Detecté un setup en curso de '<nombre>' que quedó en <paso>. ¿Continuamos desde ahí, o arrancamos de cero?"

Si el usuario continúa, salta directo al paso siguiente. Si arranca de cero, renombra el archivo viejo a `.skill-state.bak.json` y empieza P1.

Al final de cada paso completado, escribir/actualizar `.skill-state.json` con `{step, timestamp, decisions}`.

### Reanudación en modo desarrollo activo

Si la skill se invoca con frases de continuación ("qué sigue", "retomemos", "próxima tarea", etc.) y el proyecto ya está creado (existe `CLAUDE.md`, `TODO.md`, `SPEC.md`), el gate de Modo Adopción ya corrió como parte de "## Reanudación" de arriba — no se repite acá. Ejecutar este flujo de verificación antes de arrancar:

1. **Leer `SPEC.md`** — ¿el alcance sigue igual o el usuario mencionó algo nuevo?
2. **Leer `TODO.md`** — ¿cuál es la próxima tarea sin hacer? ¿hay tareas pendientes de la sección actual?
3. **Si el usuario menciona una feature nueva o cambio de dominio** → aplicar el flujo Spec-Anchored (ver `AGENTS.md` del proyecto, sección "Agregar o modificar features") antes de escribir código. Además, el **Spec Drift Check** de `AGENTS.md` (Workflow de Git, paso 0) corre en cada commit durante esta sesión — no hace falta repetirlo acá al retomar, ya cubre los cambios que se hagan de ahora en más. No confundir con el gate de Modo Adopción de arriba: ese es sobre `.skill-state.json` vs. MA-6 (corre una sola vez, al arrancar la sesión), este es sobre SPEC.md vs. código nuevo (corre en cada commit).
4. **Si el usuario dice algo tipo "el MVP está listo", "cerremos esta fase", "arranquemos la v2"** → aplicar el mecanismo de snapshot de `.rocky-spec/reference/methodologies.md` sección "Snapshots de fase — carpeta `specs/`": congelar el `SPEC.md` actual en `specs/<fase>/SPEC.md` antes de seguir editando el spec vivo para lo que sigue.
5. **Si es continuación normal** → retomar desde la próxima tarea del TODO, siguiendo el orden: Dominio/DB → API/Backend → Frontend/UI.

