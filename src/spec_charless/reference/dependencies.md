# Gestión de dependencias — referencia canónica

> El **escaneo de vulnerabilidades** (`npm audit`, Dependabot, etc.) ya vive en `.charless/reference/security.md` — es la mitad de seguridad de este tema. Este archivo cubre la otra mitad: mantener las dependencias sanas en el tiempo (no desactualizadas, no infladas, no con licencias incompatibles) — es mantenimiento, no seguridad.

## Índice

- [Cómo se usa este archivo](#cómo-se-usa-este-archivo)
- [Pinning de versiones](#pinning-de-versiones)
- [Cadencia de actualización](#cadencia-de-actualización)
- [Dependencias sin usar](#dependencias-sin-usar)
- [Compliance de licencias de terceros](#compliance-de-licencias-de-terceros)
- [Nivel de exigencia según escala del proyecto](#nivel-de-exigencia-según-escala-del-proyecto)

## Cómo se usa este archivo

- **P6 (Genera archivos base)**: rellena la sección "Gestión de dependencias" de `AGENTS.md` y la configuración de Dependabot/Renovate (extiende la de `.charless/reference/security.md`, no la duplica) con la cadencia y política elegidas.
- **Modo Adopción (MA-1.6, extendido)**: el health-check de seguridad ya corre `npm audit` — acá se suma, en el mismo paso, un chequeo de dependencias no usadas y de licencias incompatibles.

## Pinning de versiones

| Tipo de dependencia | Estrategia | Por qué |
|---|---|---|
| Librerías de aplicación (`dependencies`) | Rango caret (`^1.2.3`) | Recibe patches y minors automáticamente — la mayoría son seguros por SemVer (ver `.charless/reference/versioning.md`) |
| Herramientas de build/CI (`devDependencies` críticas: bundler, test runner) | Versión exacta (`1.2.3`, sin `^`/`~`) | Reproducibilidad — no querés que el build cambie de comportamiento sin que nadie lo pida explícitamente |
| El lockfile (`package-lock.json`, `poetry.lock`, `Cargo.lock`) | **Siempre commiteado**, nunca en `.gitignore` | Es lo que realmente fija qué versión exacta se instaló — sin esto, el rango caret no garantiza nada reproducible entre máquinas (ver `CONSTITUTION.md` Artículo 8) |

## Cadencia de actualización

No todas las actualizaciones pesan lo mismo — la política por default agrupa por riesgo, no trata todo igual:

| Tipo de update | Política default | Revisión |
|---|---|---|
| Patch (`1.2.3` → `1.2.4`) | Auto-merge si CI pasa | Ninguna — el riesgo de un patch es bajo y el costo de revisar cada uno no vale la pena |
| Minor (`1.2.x` → `1.3.0`) | PR agrupado semanal | Revisión rápida del changelog de la dependencia antes de mergear |
| Major (`1.x.x` → `2.0.0`) | PR individual, nunca agrupado | Revisión completa — leer el changelog de breaking changes, correr los tests, probar manualmente si toca algo crítico |

**Configuración de Dependabot** (extiende la de `.charless/reference/security.md`, no la reemplaza):

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      minor-and-patch:
        update-types: ["minor", "patch"]
    # Los majors NO se agrupan — Dependabot los abre como PR individual por default
```

**Renovate** (alternativa más configurable) permite además auto-merge real de patches vía `automerge: true` en su config — Dependabot solo abre el PR, no lo mergea solo. Si el proyecto quiere auto-merge de verdad, Renovate es la opción, no Dependabot.

## Dependencias sin usar

Con el tiempo, un proyecto acumula dependencias que ya no se importan en ningún lado — pesan en el bundle, en el tiempo de instalación, y en la superficie de ataque (más código de terceros = más riesgo, ver `.charless/reference/security.md`).

| Ecosistema | Herramienta |
|---|---|
| Node/npm | `npx depcheck` |
| Python | `pip install pip-check` o `deptry` |
| Rust | `cargo install cargo-udeps && cargo +nightly udeps` |

No es algo para correr en cada commit — alcanza con revisarlo antes de un release grande, o cuando `node_modules`/tiempo de instalación empiezan a notarse pesados.

## Compliance de licencias de terceros

Cada dependencia trae su propia licencia, y no todas son compatibles entre sí. El caso que más importa: una dependencia con licencia **copyleft fuerte** (GPL, AGPL) puede obligar a que el proyecto completo se distribuya bajo esa misma licencia si se usa de cierta forma — esto choca directo con la licencia que el proyecto eligió en `LICENSE` (ver más abajo).

| Ecosistema | Herramienta |
|---|---|
| Node/npm | `npx license-checker --summary` |
| Python | `pip install pip-licenses && pip-licenses` |

**Regla práctica**: si el proyecto es MIT/Apache-2.0 (permisivas) y aparece una dependencia GPL/AGPL en el resultado, no es necesariamente un problema — depende de cómo se use (link dinámico vs. estático, si se distribuye el binario) — pero es una señal para revisar, no para ignorar. Si el proyecto es privado/propietario (no se distribuye a terceros), esto generalmente no aplica — el riesgo de licencias copyleft es sobre todo para software que se redistribuye.

## Nivel de exigencia según escala del proyecto

Mismo espíritu que `.charless/reference/security.md` y `.charless/reference/versioning.md`:

| Escala | Nivel de exigencia |
|---|---|
| Prototipo / demo | Nada de esto — ni vale la pena el setup |
| Producto real | Dependabot semanal + revisión de majors + auditoría de no-usadas antes de releases grandes |
| Producto que se redistribuye o es open source | Todo lo anterior + compliance de licencias obligatorio (un solo GPL colado puede obligar a relicenciar todo el proyecto) |
