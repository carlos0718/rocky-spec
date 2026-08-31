# Estrategias de scan del background técnico

Este archivo lo usa `/charless-ia` en el **Paso 0** para construir o actualizar el `profile.md` del usuario.

La meta es popular el perfil sin pedir 20 preguntas al usuario. Se prefiere SIEMPRE el método más automático posible. Solo se pregunta cuando no hay más opción.

## Decisión inicial

Antes de scanear, preguntar al usuario en menú:

```
¿Dónde están tus proyectos? Elegí una opción:
  1) Estás corriendo Claude Code desde <cwd> — scaneá acá (o un nivel arriba)
  2) Mi workspace está en otra ruta (lo indico)
  3) No tengo proyectos locales, scaneá mi GitHub
  4) Ninguno de los anteriores, hagamos entrevista manual
```

Guardar la elección en `profile.md` bajo la sección **Configuración** para no volver a preguntar en futuras ejecuciones.

---

## Estrategia A — Scan local

Path a scanear: el indicado por el usuario en la opción 1 o 2.

### Qué buscar

Recorrer recursivamente con profundidad máxima 4 (para no explotar en `node_modules/`). Ignorar carpetas: `node_modules`, `.git`, `dist`, `build`, `.next`, `.venv`, `__pycache__`, `target`, `.cache`, `vendor`.

Detectar proyectos por la presencia de **archivos manifiesto**:

| Manifiesto | Tipo de proyecto | Qué extraer |
|---|---|---|
| `package.json` | Node / web | `name`, `dependencies`, `devDependencies`, `scripts` |
| `pyproject.toml` | Python | `[project] name`, `dependencies` |
| `requirements.txt` | Python (legacy) | lista de paquetes |
| `Cargo.toml` | Rust | `name`, `dependencies` |
| `go.mod` | Go | `module`, `require` |
| `pom.xml` | Java (Maven) | `artifactId`, `dependencies` |
| `build.gradle` | Java / Kotlin | `dependencies` |
| `Gemfile` | Ruby | `gem 'X'` líneas |
| `composer.json` | PHP | `require` |
| `*.csproj` | C# / .NET | `<PackageReference>` |
| `mix.exs` | Elixir | `deps` |
| `deno.json` / `bun.lockb` | Deno / Bun | confirmar runtime |

### Cómo extraer info útil

Por cada proyecto detectado, anotar:

- **Nombre** (del manifiesto o del nombre de carpeta).
- **Path absoluto**.
- **Lenguaje principal** (deducido del manifiesto).
- **Top 5 dependencias** más relevantes (filtrar las "infraestructura" como `@types/*`, `eslint`, `prettier`).
- **Último commit** (si hay `.git`): `git log -1 --format=%cd --date=short` en esa carpeta.
- **Tamaño aproximado** del proyecto (line count opcional).

### Heurísticas de stack

Después de scanear, agregar los proyectos encontrados al `profile.md` y deducir patrones:

- **Framework frontend dominante**: si `react`/`vue`/`svelte`/`@angular/core` aparecen en ≥3 proyectos → ese es el favorito.
- **Backend dominante**: `express`/`@nestjs/core`/`fastify`/`fastapi`/`django` → idem.
- **Estilos**: `tailwindcss`/`@mui/material`/`bootstrap`/`@chakra-ui/react` → idem.
- **Testing**: `vitest`/`jest`/`playwright`/`cypress` → idem.
- **Lenguaje default**: si ≥70% de los proyectos tienen `typescript` en devDeps → TS, sino JS.

Esos patrones poblan las secciones "Stacks dominantes" del perfil.

### Output esperado

Al final del scan, mostrar al usuario:

```
Encontré 12 proyectos en /home/charly/code/:
  • Frontend: React (8), Vue (2), Svelte (2)
  • Backend: Express (5), NestJS (3)
  • Estilos: Tailwind (9), MUI (2)
  • Testing: Vitest (6), Jest (2)
  • TypeScript: 10/12 proyectos
  
¿Confirmo estos hallazgos para tu profile.md? (S/n)
```

---

## Estrategia B — Cascada de GitHub

Cuando el usuario elige opción 3, ejecutar la cascada en silencio (sin molestar). Probar en orden, parar al primer método que funcione.

### Nivel 1 — MCP de GitHub en Claude Code

Verificar si la sesión actual de Claude tiene tools del plugin de GitHub disponibles. Típicamente nombradas:
- `mcp__plugin_engineering_github__*`
- o `mcp__github__*` según versión

Si están: usar esas tools directamente. Cobertura: repos públicos + privados, sin setup adicional para el usuario.

**Cómo usarlo en el flujo:**
1. Listar repos del usuario autenticado.
2. Para cada repo, leer `package.json` u otro manifiesto si existe.
3. Extraer lenguaje, tecnologías, descripción, fecha del último push.

### Nivel 2 — `gh` CLI

Detectar con: `gh --version` (silencioso). Si OK, verificar auth con: `gh auth status`.

Si autenticado, listar repos:

```bash
gh repo list --limit 100 --json name,description,languages,primaryLanguage,updatedAt,isPrivate
```

Para más detalle por repo (opcional, si el scan inicial vale la pena):

```bash
gh repo view <owner>/<repo> --json languages,topics,description,defaultBranchRef
```

Para leer `package.json` u otro manifiesto del repo sin clonarlo:

```bash
gh api repos/<owner>/<repo>/contents/package.json --jq '.content' | base64 -d
```

Cobertura: igual que el MCP (público + privado), pero requiere que el usuario instale `gh` una vez.

### Nivel 3 — API pública sin auth

Pedir al usuario: *"¿Cuál es tu username de GitHub?"*

Llamar a la API REST pública (sin token):

```
GET https://api.github.com/users/<username>/repos?per_page=100&sort=updated&type=owner
```

Cobertura: SOLO repos públicos. Rate limit: 60 calls/hora por IP. Suficiente para un scan inicial de hasta ~100 repos.

Para cada repo del listado, extraer: `name`, `description`, `language`, `topics`, `updated_at`, `stargazers_count`.

Si el usuario tiene muchos repos privados, este método los pierde y el perfil va a quedar incompleto. Avisar y ofrecer pasar a Nivel 2 o 4.

### Nivel 4 — Entrevista manual (siempre disponible)

Si todas las opciones de arriba fallan o el usuario las rechaza, hacer 8 preguntas guiadas:

1. ¿En qué lenguajes programás más? (multi-select: TS, JS, Python, Go, Rust, Java, C#, Ruby, PHP, otro)
2. ¿Cuál es tu framework frontend favorito? (React, Vue, Svelte, Angular, Astro, vanilla, ninguno)
3. ¿Y backend? (Express, NestJS, Fastify, Django, FastAPI, Spring, Rails, Laravel, ninguno)
4. ¿Qué estilos usás más seguido? (Tailwind, MUI, Bootstrap, Chakra, CSS puro, Sass, styled-components)
5. ¿Y testing? (Vitest, Jest, Playwright, Cypress, ninguno)
6. ¿Qué tipo de proyectos hacés más? (web app, API, mobile, scripts, videos/motion, otro)
7. ¿Tenés convenciones fuertes? (kebab-case vs camelCase, conventional commits, etc.)
8. ¿Algo más que querés que recuerde? (campo libre)

Las respuestas pueblan directamente las secciones del `profile.md`.

---

## Estrategia C — Modo creativo (no-code)

Si el usuario es perfil **creativo/motion/AI gen** (no programa), las opciones cambian:

- Scan local detecta carpetas con `*.aep`, `*.prproj`, `*.drp`, `*.blend`, `*.c4d`, `*.psd`, `*.afdesign` en lugar de manifiestos de código.
- Carpetas tipo `~/Movies`, `~/After Effects Projects`, `~/Documents/Editing` son candidatas comunes.
- GitHub no aplica (rara vez se versionan proyectos de motion).
- La entrevista manual reemplaza al scan: preguntas sobre AI image gen, AI video gen, editor, etc. (ver el `profile.md.template` sección "Stacks dominantes - Creativo").

---

## Notas para la implementación

- **Nunca correr el scan sin confirmación previa del usuario.** Pedirle el path explícitamente o usar el menú del Paso 0.
- **Mostrar siempre el resumen final** antes de escribir a `profile.md`. El usuario debe poder corregir.
- **Si la skill falla al detectar algo**, no asumir — preguntar.
- **El primer scan es la oportunidad de oro**: dejar al perfil bien poblado en ese momento ahorra preguntas en TODAS las futuras ejecuciones.
