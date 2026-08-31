> Referencia de **charless-ia** — Paso P0 del flujo de creación: detección de workspace y populado del perfil (solo primera ejecución).

### P0 · Detectar workspace y popular perfil (primera ejecución)

**Cuándo ejecutar este paso:** solo si `profile.md` no tiene la sección **Configuración** completa (ni `workspace_root` ni `github_username`). Si ya están, saltar directo a P1.

El objetivo es popular el perfil del usuario sin pedirle 20 preguntas. Se prefiere SIEMPRE el método más automático posible.

**Diálogo del Paso 0:**

```
Antes de arrancar, necesito conocer tu background técnico.
Estás corriendo Claude Code desde: <cwd>

¿Cómo prefieres que arme tu perfil?
  1) Scaneá <cwd> (asumo que esta es tu carpeta de proyectos)
  2) Scaneá otra carpeta (la indico)
  3) Scaneá mi GitHub (sin proyectos locales)
  4) Hagamos entrevista manual (no scanear nada)
```

**Según la elección, ejecutar:**

- **Opción 1 / 2** → ver `.charless/reference/scan-strategies.md` sección "Estrategia A — Scan local".
  - Si la opción 1 detecta un proyecto único (cwd con `package.json`/`.git`), preguntar: *"Detecté que estás dentro de un proyecto. ¿Querés que suba un nivel y scanee `<parent>`?"*
- **Opción 3** → cascada de GitHub: `.charless/reference/scan-strategies.md` sección "Estrategia B — Cascada de GitHub".
  - Probar en orden: MCP de GitHub en sesión → `gh` CLI → API pública (sin auth) → entrevista manual.
- **Opción 4** → entrevista manual: 8 preguntas guiadas (ver `scan-strategies.md` sección "Nivel 4").

**Después del scan, guardar en `profile.md` la sección Configuración:**

```markdown
## Configuración

- **workspace_root**: /home/charly/code/
- **github_username**: charly18
- **scan_method**: local | github-mcp | gh-cli | github-api | manual
- **last_scan_date**: 2026-05-30
```

Y popular las secciones "Stacks dominantes" con lo encontrado.

**Mostrar el resumen antes de escribir el archivo** y pedir confirmación al usuario. El usuario debe poder corregir cualquier inferencia equivocada antes de que se persista.

**Tip importante para el usuario en la opción 1:** si el cwd parece ser el home (`~/`) o una carpeta genérica, sugerir paths comunes (`~/Documents/projects/`, `~/dev/`, `~/code/`, `D:\dev\`) en vez de scanear el home entero (que sería lento y ruidoso).

