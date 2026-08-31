> Referencia de **charless-ia** — Comportamiento transversal de menús (texto vs interactivo). Consultar cada vez que se presenta un menú al usuario, en cualquier paso del flujo P0–P8 o de los modos Adopción/Reanudación.

## Modo de menús — texto vs interactivo

Esta skill presenta menús al usuario en muchos pasos (tipo de proyecto, stack, modo de install, etc.).

**Modo texto (default)**: el menú se renderiza como texto markdown numerado en el chat. El usuario responde tipeando número o nombre.

**Modo interactivo (opt-in)**: si `~/.claude/profile.md` tiene `prefer_interactive_menus: true`, en vez de renderizar el menú en chat, **invocar bash** con el helper `choose.js`:

```bash
node ~/.claude/skills/_helpers/choose.js "<pregunta>" "<opcion 1>" "<opcion 2>" "<opcion 3>"
```

El helper:
- Renderiza un menú con flechas ↑/↓ en el terminal del usuario (raw mode TTY).
- Devuelve la opción elegida **tal cual** (texto) a stdout.
- Sale con código 0 si eligió, 1 si canceló (Ctrl+C), 2 si no es TTY.

**Cómo leer la respuesta**: tomar la última línea de stdout del bash. Esa es la opción que el usuario eligió. Mapear de vuelta al valor interno que necesites.

**Fallback automático**: si bash falla, sale con código 2 (no-TTY), o el usuario rechaza el permiso → caer **automáticamente al modo texto** sin pedir nada. No molestar al usuario si el helper no anda.

**Cuándo usar cada uno**:
- Modo texto: menús cortos (≤3 opciones), respuesta de texto libre, default seguro.
- Modo interactivo: menús largos (4+ opciones), donde elegir con flechas es más cómodo que tipear un número.

Ejemplo de invocación para P5 (modo de install):

```bash
node ~/.claude/skills/_helpers/choose.js \
  "¿Cómo querés que ejecutemos los comandos?" \
  "Auto — los ejecuto todos, te aviso si algo falla" \
  "Paso a paso — confirmás con Enter antes de cada comando" \
  "Manual — los pegás vos en tu terminal"
```

Claude lee el stdout y mapea: si la respuesta empieza con "Auto" → modo A, "Paso" → modo B, "Manual" → modo C.

