# Versionado y Changelog — referencia canónica

> Esta es la extensión natural del Workflow de Git que ya existe en `AGENTS.md.template` — no introduce un flujo nuevo, formaliza y completa el que ya está: el `<tipo>` de cada commit deja de ser una convención suelta y pasa a ser **Conventional Commits** de verdad, con su mapeo directo a **Semantic Versioning** y a las entradas de `CHANGELOG.md`.

## Índice

- [Cómo se usa este archivo](#cómo-se-usa-este-archivo)
- [Conventional Commits](#conventional-commits)
- [Semantic Versioning (SemVer)](#semantic-versioning-semver)
- [Keep a Changelog](#keep-a-changelog)
- [Cuándo actualizar el changelog vs. cuándo no](#cuándo-actualizar-el-changelog-vs-cuándo-no)
- [Tags y releases](#tags-y-releases)
- [Automatización opcional](#automatización-opcional)
- [Nivel de exigencia según escala del proyecto](#nivel-de-exigencia-según-escala-del-proyecto)

## Cómo se usa este archivo

- **P6 (Genera archivos base)**: genera `CHANGELOG.md` desde `.charless/templates/CHANGELOG.md.template`.
- **`AGENTS.md` del proyecto**: la sección "Workflow de Git" ya formaliza Conventional Commits y agrega el paso de actualizar `CHANGELOG.md` por tarea, más una sección nueva "Versionado y releases" con el criterio de cuándo taguear.
- **Modo Adopción (MA-6)**: si el proyecto ya tiene un `CHANGELOG.md`, se mergea (se respeta el historial ya escrito) en vez de reemplazarlo.

## Conventional Commits

El `<tipo>` del mensaje de commit no es libre — sigue [Conventional Commits](https://www.conventionalcommits.org/), porque de ahí sale automáticamente qué tan grande es el cambio (para SemVer) y si merece una línea en el changelog:

| Tipo | Qué es | ¿Bump de versión? | ¿Entra al changelog? |
|---|---|---|---|
| `feat` | Feature nueva | MINOR | Sí — `Added` |
| `fix` | Corrección de bug | PATCH | Sí — `Fixed` |
| `docs` | Solo documentación | — | No (salvo que sea documentación pública relevante) |
| `style` | Formato, espacios, sin cambio de lógica | — | No |
| `refactor` | Reestructurar código sin cambiar comportamiento | — | No (salvo que sea un refactor grande que valga mencionar) |
| `perf` | Mejora de performance | PATCH | Sí — `Changed` |
| `test` | Agregar o corregir tests | — | No |
| `build` | Cambios en build system o dependencias | — | No (salvo actualización de dependencia relevante para el usuario) |
| `ci` | Cambios en CI/CD | — | No |
| `chore` | Tareas de mantenimiento sin impacto en código de producción | — | No |
| `revert` | Revertir un commit anterior | Depende del commit revertido | Sí, si el original estaba en el changelog |

**Breaking changes**: se marcan con `!` después del tipo (`feat!: cambiar formato de respuesta de /api/users`) o con un footer `BREAKING CHANGE: <descripción>` en el cuerpo del commit. Siempre → MAJOR, siempre entra al changelog bajo `Changed` con una nota explícita de breaking change.

**Formato completo** (ya lo trae `AGENTS.md`, esto es la referencia formal):
```
<tipo>[!][(scope opcional)]: <descripción corta> (TODO: <texto de la tarea>)

[cuerpo opcional]

[BREAKING CHANGE: descripción, si aplica]
```

## Semantic Versioning (SemVer)

Formato `MAJOR.MINOR.PATCH` (ej. `1.4.2`):

- **MAJOR** (`1.x.x` → `2.0.0`): rompe compatibilidad con versiones anteriores. Cualquier `feat!`/`fix!`/`BREAKING CHANGE`.
- **MINOR** (`1.4.x` → `1.5.0`): agrega funcionalidad sin romper nada existente. Cualquier `feat`.
- **PATCH** (`1.4.2` → `1.4.3`): corrige bugs sin agregar funcionalidad ni romper nada. Cualquier `fix`.

**Antes de la primera versión estable**: `0.x.y` es válido y esperable mientras el proyecto está en desarrollo activo sin garantías de estabilidad — durante esta etapa, incluso un `feat!` puede bumpear MINOR en vez de saltar a `1.0.0` directamente (la spec de SemVer lo permite explícitamente). Pasar a `1.0.0` es una decisión del usuario, no automática — típicamente al llegar al primer release público real o al primer cliente/usuario que dependa de la API.

**Regla de oro**: la versión de un paquete/API describe **el contrato con quien lo consume**, no el esfuerzo que costó — un cambio interno enorme que no afecta la interfaz pública puede ser un PATCH; un cambio de una línea que rompe un endpoint es MAJOR.

## Keep a Changelog

`CHANGELOG.md` sigue el formato de [Keep a Changelog](https://keepachangelog.com/): orden cronológico inverso (lo último arriba), y cada versión agrupa sus cambios en categorías fijas:

- **Added** — funcionalidad nueva
- **Changed** — cambios en funcionalidad existente
- **Deprecated** — funcionalidad que va a eliminarse en el futuro
- **Removed** — funcionalidad eliminada
- **Fixed** — corrección de bugs
- **Security** — corrección de vulnerabilidades (ver `.charless/reference/security.md`)

Siempre hay una sección `[Unreleased]` arriba de todo, que acumula los cambios que todavía no se taguearon como versión — es donde va cada entrada nueva, commit a commit, hasta que se decide hacer un release.

## Cuándo actualizar el changelog vs. cuándo no

**Sí actualiza** (agregar línea a `[Unreleased]`, categoría correspondiente, en el mismo commit que el código — mismo principio de sincronía que el resto del Workflow de Git):
- `feat` → `Added`
- `fix` → `Fixed`
- `feat!`/`fix!`/`BREAKING CHANGE` → `Changed` (con nota explícita de breaking change)
- Fix de seguridad → `Security`

**No actualiza** (el commit se hace normal, sin tocar `CHANGELOG.md`):
- `docs`, `style`, `refactor` (menor), `test`, `build`, `ci`, `chore`

**Criterio simple si hay duda**: ¿alguien que use este proyecto (no quien lo programa) notaría o le importaría este cambio? Si sí, va al changelog. Si es puramente interno, no.

## Tags y releases

El versionado no se hace en cada commit — se hace en momentos puntuales, llamados **release**:

```bash
# 1. Mover [Unreleased] a una versión con fecha en CHANGELOG.md
## [Unreleased]

## [0.2.0] - 2026-08-29
### Added
- ...

# 2. Commitear el cambio de changelog
git commit -m "chore(release): v0.2.0"

# 3. Taguear
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# 4. (opcional, si el repo está en GitHub) crear el Release con las notas del changelog
gh release create v0.2.0 --notes-file <(sed -n '/## \[0.2.0\]/,/## \[/p' CHANGELOG.md | head -n -1)
```

**Cuándo taguear**: no en cada commit ni en cada `feat`/`fix` — en hitos reales: primer deploy a producción, antes de un cambio grande, o cuando el usuario lo pide explícitamente. Para proyectos que son librerías/paquetes publicados (npm, PyPI), taguear en cada publish es la norma.

**Relación con los snapshots de `specs/`**: cerrar una fase de producto (ver `.charless/reference/methodologies.md` sección "Snapshots de fase") y hacer un release de código son decisiones parecidas pero independientes — pueden coincidir (cerrar el MVP y taguear `v1.0.0` el mismo día) o no.

## Automatización opcional

| Herramienta | Qué hace | Cuándo conviene |
|---|---|---|
| Manual (default de la skill) | Seguir los pasos de arriba a mano | La mayoría de los proyectos — mínima fricción, sin configuración |
| [semantic-release](https://semantic-release.gitbook.io/) | Analiza los commits (Conventional Commits) y bumpea versión + genera changelog + tag + publish automáticamente en CI | Librerías/paquetes con publish frecuente, equipos que ya confían 100% en Conventional Commits |
| [Changesets](https://github.com/changesets/changesets) | Similar, pero pensado para monorepos con múltiples paquetes versionados independientemente | Monorepos (ej. frontend + shared packages en el mismo repo) |

**Default de la skill**: manual. Ofrecer automatización solo si el usuario lo pide explícitamente o el proyecto es una librería que se publica seguido — automatizar versionado desde el día 1 de un proyecto chico es más fricción que la que ahorra.

## Nivel de exigencia según escala del proyecto

Mismo espíritu que `.charless/reference/security.md` — no todo proyecto necesita el mismo rigor:

| Escala | Ejemplo | Nivel de exigencia |
|---|---|---|
| Prototipo / script descartable | Demo de un día, script de un solo uso | Sin CHANGELOG ni tags — no hay a quién comunicarle una versión |
| Producto real | SaaS, app con usuarios | CHANGELOG.md + SemVer + tag en cada deploy a producción |
| Librería / paquete publicado | Paquete de npm/PyPI, SDK interno compartido | Todo lo anterior + SemVer estricto (romper compatibilidad es SIEMPRE MAJOR) + considerar automatización, porque hay consumidores externos que fijan versiones exactas en sus propios `package.json`/`requirements.txt` |
