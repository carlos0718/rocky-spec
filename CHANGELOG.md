# Changelog

Todos los cambios notables de `rocky-spec` (antes `spec-charless`) se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- **`rocky build` persiste los valores usados para renderizar cada archivo base en `.rocky-spec/values.json`** — mezclado con lo que ya hubiera, nunca lo pisa entero. Habilita regenerar un archivo puntual más adelante (ej. remediación de drift de contenido, RF-22) sin reconstruir a mano el JSON de placeholders. (US-26, RF-22)

## [0.19.1] - 2026-09-11

### Fixed
- **El gate de revalidación de drift en `mode-resume.md` (US-25) se podía saltear si `.skill-state.json` traía `step: "adoption_complete"`** — vivía como paso 0 de la sub-sección "Reanudación en modo desarrollo activo", condicionado a un trigger parecido al de la sección genérica de arriba (que lee `step` para detectar un setup interrumpido). Una sesión confundía ambos y pasaba directo al TODO sin correr `rocky check drift`, dejando archivos como `CONSTITUTION.md`/`SECURITY.md` sin generar. Se subió el gate al inicio de "## Reanudación", incondicional al valor de `step`. (US-25, RF-21)

## [0.19.0] - 2026-09-10

### Added
- **`rocky update`/`rocky check drift` terminan con un mensaje accionable de próximo paso cuando hay hallazgos de drift** — en vez de solo listarlos, indican qué escribirle al agente para resolverlos. (US-24, RF-21)
- **`mode-resume.md` revalida `.skill-state.json` contra `rocky check drift` al retomar sesión sobre un proyecto adoptado** — nuevo paso 0 del checklist de Reanudación, resuelve los hallazgos siguiendo la tabla P6 de `mode-adopt.md` antes de seguir con el TODO, en vez de depender de una auditoría manual. (US-25, RF-21)

## [0.18.1] - 2026-09-10

### Fixed
- **La recomendación de limpiar sesión (US-20) y el paso de borrar rama post-release disparaban en momentos distintos por una distinción sin motivo de fondo** — se unificaron en una sola pausa al cierre del flujo completo de integración (merge a `development`, version check, tag/release si corresponde, y merge a `master`/`main`), en vez de ofrecer la limpieza de sesión apenas se mergea a `development` con ese trabajo todavía pendiente. Portado también a `templates/AGENTS.md.template`.

## [0.18.0] - 2026-09-10

### Added
- **`rocky check drift` / integrado en `rocky update`** — detecta, para proyectos con `.skill-state.json` en `"mode": "adopted"`, qué archivos genera hoy Modo Adopción (MA-6: `CONSTITUTION.md`, `CHANGELOG.md`, `SECURITY.md`, `OBSERVABILITY.md`, `ACCESSIBILITY.md`/`design-system/MASTER.md` si el proyecto tiene UI, `LICENSE`) pero faltan porque la adopción corrió con una versión vieja de la skill. MA-6 ahora guarda `license_decision` en `.skill-state.json` para distinguir "el usuario ya eligió no tener LICENSE" de "nunca se le preguntó". (US-23)

## [0.17.3] - 2026-09-09

### Fixed
- **US-20 (limpieza de sesión) y el paso 6 de release (limpieza de ramas) tenían triggers parecidos y se confundieron en la práctica** — se ofreció borrar una rama `fix/*` apenas se mergeó a `development`, salteando el version check, el tag, el release y el merge a `master`. Agregada una aclaración cruzada explícita entre ambas reglas en `AGENTS.md`, y un nuevo chequeo general — "Trigger Ambiguity Check" — que corre al redactar cualquier regla nueva con disparador basado en eventos, para detectar solapamientos con reglas existentes antes de que causen el mismo tipo de confusión. Portado también a `templates/AGENTS.md.template` (junto con el Release Sync Check del release anterior), para que los proyectos generados por la skill no hereden la misma ambigüedad.

## [0.17.2] - 2026-09-09

### Fixed
- **`master` quedaba desincronizado incluso después de "arreglar" `pyproject.toml`** — el fix de `v0.17.1` (sincronizar `pyproject.toml`) se taggeó y liberó en `development`, pero el merge `development → master` de ese release nunca se volvió a correr, así que `uv tool install`/`upgrade` (que clona el HEAD de `master`, no el tag) siguió instalando `0.15.0` aunque el Release "Latest" en GitHub ya dijera `v0.17.1`. Agregado un paso explícito — "Release Sync Check" — al flujo de release en `AGENTS.md`: después de tagear, comparar `pyproject.toml` de `origin/master` contra la versión recién liberada y ofrecer el merge ahí mismo con `AskUserQuestion`, en vez de asumir que va a pasar después.

## [0.17.1] - 2026-09-09

### Fixed
- **`pyproject.toml` desincronizado del último release** — quedó en `0.15.0` mientras `CHANGELOG.md`/tags/Releases ya estaban en `0.17.0` (los releases `v0.16.0` y `v0.17.0` solo tocaron el CHANGELOG). Causaba que `uv tool upgrade rocky-spec` instalara un número de versión viejo. Corregido a `0.17.0`, y el paso de release en `AGENTS.md` ahora incluye explícitamente bumpear `pyproject.toml` junto con el CHANGELOG.

## [0.17.0] - 2026-09-09

### Added
- **CI del repo `rocky-spec`** (`.github/workflows/ci.yml`) — corre `pytest tests/ -v` automáticamente en cada push/PR a `development` y `master`, con matrix Python 3.9/3.12 (extremos del rango declarado en `pyproject.toml`). Sale de "Fuera del alcance (v1)" de `SPEC.md` al retomar la tarea pendiente de `TODO.md` (RF-19, US-22).
- **`rocky update [PATH] [--dry-run]`** — actualiza `commands/`, `reference/`, `templates/` y los archivos 100% del kit de cada integración ya instalada (`SKILL.md`, `.cursor/commands/rocky-*.md`) a la versión del paquete instalado, sin pisar ediciones manuales. Usa un hash-tracking nuevo (`shared-manifest.json`, escrito por `scaffold.ensure_shared_knowledge`) con el mismo criterio que ya usa `uninstall` para RF-4/US-6: archivo sin cambios desde el último install/update se refresca, archivo editado se preserva y se reporta, archivo nuevo del paquete se agrega, archivo que el paquete ya no incluye se reporta sin borrarse solo. `CLAUDE.md`/`rocky.mdc` no se tocan — ya vienen protegidos por su propia reparación de ancla. Pedido explícito del usuario: la única forma de actualizar el kit hasta ahora era `init --force`, que borra `commands/`/`reference/`/`templates/` completos sin distinguir archivos editados a mano (RF-18, US-21).

### Changed
- **Rama de integración renombrada `dev` → `development`** — mismo rol y reglas de GitFlow simplificado, solo cambia el nombre. Aplicado en la documentación de este repo (`AGENTS.md`, `CONSTITUTION.md`, `SPEC.md`, `TODO.md`), en los templates que la skill genera para proyectos nuevos (`templates/AGENTS.md.template`, `templates/TODO.md.template`, `templates/CONSTITUTION.md.template`, `commands/mode-adopt.md`), en `scripts/version_check.py` (antes asumía `dev` hardcodeado para el aviso de fixes acumulados) y su test, y en la rama real del repo. Pedido explícito del usuario.

## [0.16.0] - 2026-09-09

### Added
- **Recomendación post-merge de limpiar sesión** (`AGENTS.md`/template, sección "Branching") — justo después de confirmar un merge `feature/*`/`fix/*` → `dev`, el agente ofrece con `AskUserQuestion` limpiar la sesión (`/clear`), graduando el mensaje (🟢/🟡/🔴) según su visibilidad del consumo de contexto cuando el entorno se la da (en Claude Code, la señal de tokens restantes de los reminders del sistema); si no hay esa visibilidad, la pregunta se muestra igual, sin el dato. Pedido explícito del usuario para evitar arrastrar conversación de una feature ya integrada y gastar tokens sin beneficio (US-20).
- **Nuevo `TODO Drift Check`** (`AGENTS.md`/template, paso 0-quater del Workflow de Git) — hasta ahora nada detectaba una feature/fix que se resuelve sobre la marcha y nunca queda registrada en `TODO.md`; solo el Spec Drift Check (alcance de `SPEC.md`) y el flujo Plan→Confirmar (features anunciadas) cubrían casos parecidos. Encontrado auditando este mismo repo: 8 features reales (`RF-10` a `RF-16`, `US-12` a `US-19`) solo existían en `CHANGELOG.md`/`git log`, ninguna en `TODO.md` — backfill retroactivo aplicado.

### Fixed
- **El flujo de release nunca pedía publicar el Release en GitHub, solo el tag** — `git push origin vX.Y.Z` sube el tag pero no crea el objeto "Release" de GitHub, que es independiente. Consecuencia real: este repo tenía tags hasta `v0.15.0` pero la pestaña "Releases" mostraba `v0.10.0` como última versión — 6 releases (`v0.11.0` a `v0.15.0`, incluido `v0.14.1`) publicados retroactivamente con las notas de `CHANGELOG.md`. `AGENTS.md` y `templates/AGENTS.md.template` suman el paso `gh release create` a la sección "Versionado y releases", para que los proyectos generados con `rocky init` no repitan el gap.

## [0.15.0] - 2026-09-09

### Added
- **`CLAUDE.md` y `.cursor/rules/rocky.mdc` ahora se reparan solos si pierden el ancla al conocimiento compartido, sin pisar el resto del archivo** — hasta v0.14.1, el único remedio para un `CLAUDE.md` sin la línea `@AGENTS.md` (el caso real: pasó en la raíz de este mismo repo) era regenerarlo entero a mano o con `--force`, perdiendo cualquier nota o rol personalizado. `ensure_claude_md_anchor()` reinserta la línea si falta y no toca nada más; el equivalente para Cursor (`CursorIntegration._ensure_rule`) hace lo mismo con el puntero a `.rocky-spec/` en `rocky.mdc` — y de paso deja de pisarlo entero en cada `rocky init` como hacía antes, que era el problema inverso (Cursor sí sobreescribía sin avisar). Ambos casos se reportan en la salida de `init` (`🔧 ... se reinsertó` / `... se restauró`).
- **La nota que acompaña al ancla reparada es texto fijo, no prosa redactada al momento — en los dos agentes** — la primera reparación manual de este mismo `CLAUDE.md` (antes de que existiera `ensure_claude_md_anchor()`) llevó una nota explicativa distinta a la que terminó escribiendo el código. Ahora usa la constante `CLAUDE_MD_ANCHOR_NOTE`, más corta que la de `CLAUDE.md.template` a propósito (no promete la sección de roles de expertise, que la reparación no agrega). `rocky.mdc` tenía el mismo desbalance en el sentido inverso — la reparación pegaba el puntero con un comentario HTML de una línea, sin nada de la explicación que sí trae `RULE_TEMPLATE` en una instalación nueva — resuelto con `CURSOR_RULE_REPAIR_NOTE`, mismo criterio.
- **Nuevo `rocky check anchors [PATH]`** — health-check determinista que verifica que `CLAUDE.md` y `rocky.mdc` conserven su ancla, en cualquier proyecto, sin depender de correr `init`. Nace del mismo bug: nadie lo notó hasta que se abrió el explorador de archivos a mano; este check es la versión que no depende de que alguien se acuerde de mirar.

### Changed
- **`rocky init` ahora lista cada archivo que instala, no solo el nombre de la carpeta** — la salida decía "Conocimiento compartido instalado en .rocky-spec/ (commands, reference, templates)" sin detalle; probado en un proyecto real, eso llevó a no notar que se habían copiado los 57 archivos de `.rocky-spec/templates/`, `reference/` y `commands/` hasta abrir el explorador de archivos. `ensure_shared_knowledge` ahora devuelve `{carpeta: [archivos]}` en vez de solo los nombres de carpeta, y el CLI imprime cada uno agrupado por carpeta con su conteo.
- **`rocky init` termina con el siguiente paso explícito** — instalar los archivos no arranca ninguna conversación (`rocky init` es un proceso de terminal, no puede abrir un chat), pero nada se lo decía al usuario. El mensaje final ahora aclara que hay que abrir una sesión de Claude Code/Cursor en el proyecto y decir una frase gatillo ("quiero armar un proyecto nuevo", "continuemos", "tengo un proyecto ya avanzado") para que la skill lea `.rocky-spec/` y arranque el flujo P0 en adelante. El README suma la misma aclaración justo después del ejemplo de `rocky init` en la sección Uso, en vez de dejarla solo en la sección "Por qué en Claude Code no ejecutás nada y en Cursor sí", mucho más abajo.

## [0.14.1] - 2026-09-09

### Fixed
- **Faltaba `CLAUDE.md` en la raíz de este mismo repo** — `AGENTS.md` daba por hecho su existencia ("`CLAUDE.md` importa este archivo para Claude Code") pero nunca se había creado. Sin él, Claude Code no auto-cargaba `AGENTS.md`/`CONSTITUTION.md` al arrancar una sesión nueva (por ejemplo después de un `/clear`), y con eso se perdía la tabla acción → mecanismo del Artículo 7: las confirmaciones por `AskUserQuestion` antes de `git push`/`merge`/`tag`/borrar ramas dejaban de aplicarse hasta que algo forzaba releer esos archivos a mano. Se agrega el `CLAUDE.md` con el mismo patrón (`@AGENTS.md`) que `templates/CLAUDE.md.template` ya genera para los proyectos destino — la propia herramienta no se lo había aplicado a sí misma.

## [0.14.0] - 2026-09-07

### Added
- **`rocky init --agent claude` ahora instala también las reglas de confirmación del Artículo 7** en `permissions.ask` de `.claude/settings.json` (`git push`, `git merge`, `git tag`, `git branch -d/-D`). Hasta ahora la regla **escrita** viajaba en los templates pero el enforcement no existía: el proyecto generado heredaba la convención y nada que la hiciera cumplir. Van en `ask` y no en `deny` a propósito — `deny` impediría ejecutarlas incluso con autorización explícita del usuario, y son operaciones legítimas del día a día.
- **La fusión es no destructiva**: si `.claude/settings.json` ya existe se agregan solo las reglas que falten y se conserva todo lo demás (`model`, `env`, `hooks`, permisos propios); correr `init` dos veces no duplica nada; y si el archivo no es JSON válido no se toca y se avisa. El `settings.json` **no** entra en el manifiesto de instalación — `uninstall` borra los archivos trackeados cuyo hash no cambió, así que registrarlo permitiría borrarle al usuario su configuración entera al desinstalar.
- **Aviso de reglas anuladas por `allow`**: en Claude Code una regla de `permissions.allow` **gana** sobre la misma regla en `ask`, y la confirmación nunca aparece. `rocky init` detecta ese conflicto y lo reporta en la salida, sin sacar la regla del `allow` — eso es una decisión del usuario, no del instalador.

## [0.13.0] - 2026-09-07

### Added
- **Los servicios externos (email, pagos, storage, auth…) ahora se registran y se siguen** — antes no existía ningún lugar para ellos: si el usuario decía "los mails los mando con Resend", eso quedaba como una línea suelta en `Otros` del stack o solo en la conversación, y **no generaba ninguna tarea**. No es una feature del `SPEC.md` ni una capa del stack, así que se olvidaba hasta que alguien notaba que la app no manda emails. Tres piezas nuevas, encadenadas: (1) P3 pregunta explícitamente por servicios de terceros al confirmar el stack y captura nombre, para qué, variables y estado; (2) `AGENTS.md` gana una sección **Servicios externos** con esa tabla — separada de `Otros` a propósito, porque un servicio con cuenta y credenciales no es una herramienta de build; (3) `TODO.md` gana su propia sección con las tareas de seguimiento por servicio (crear cuenta → variables en `.env` → implementar → probar de punta a punta → credenciales en producción), incluidas las que el template no puede anticipar, como la verificación de dominio por DNS de un proveedor de email.
- **`rocky commands` ahora muestra los dos niveles de comandos** — la CLI (`rocky init`, `rocky check`…, se escriben en la terminal) y los del agente (`/rocky-*`, se escriben dentro de Claude Code o Cursor), con una columna "Para qué sirve" por comando y la explicación de cómo se dispara cada uno según el agente. Antes los `/rocky-*` no estaban documentados en ningún lado fuera del README, y los dos niveles se confundían entre sí.
- **README: sección "Por qué en Claude Code no ejecutás nada y en Cursor sí"** — en Claude Code la integración es una *skill* cuya `description` la auto-invoca (tipear `/rocky-spec` es opcional, para forzar un paso puntual); en Cursor los *commands* son Markdown sin frontmatter y solo se disparan al tipearlos, por eso se instalan 15 comandos en vez de un único punto de entrada, y la regla `alwaysApply` de `.cursor/rules/rocky.mdc` los *sugiere* sin ejecutarlos. Con la tabla de los 15 comandos y su propósito.

### Fixed
- **El conteo de comandos de Cursor estaba mal y ahora se deriva** — `INVOCATION_HINT` decía "14 comandos" cuando `rocky init --agent cursor` genera **15**; era un número escrito a mano, el mismo tipo de desfase que tenía el conteo de tests del `TODO.md`. Ahora sale de `len(COMMAND_CATALOG)`, así que se actualiza solo al sumar un paso. Nuevo `test_cursor_hint_matches_the_real_command_count`, que compara contra los archivos **realmente instalados** y no contra la constante de la que se deriva — verificado que falla si se reintroduce el "14". Más `test_every_command_has_a_purpose`, para que un paso nuevo sin descripción falle en vez de renderizar una celda vacía.

## [0.12.0] - 2026-09-06

### Changed
- **Las confirmaciones del humano pasan de prosa suelta a una tabla normativa acción → mecanismo** (`CONSTITUTION.md` Artículo 7, enmienda 1.5.0) — antes la obligación de usar `AskUserQuestion` regía **solo para `git push`**: `git merge` aceptaba texto libre ("mergeo", "dale", "sí"), y ni el borrado de ramas ni el tag fijaban mecanismo alguno. La tabla cierra el alcance (push, merge, tag, borrado de ramas, elección entre alternativas) y separa explícitamente las confirmaciones de los avisos que no piden decisión (Spec Drift, TODO Size), que siguen siendo texto y no bloquean.
- **Resuelta una contradicción interna de `AGENTS.md`** — el paso 4 del Workflow de Git decía "Hacer `git push` inmediatamente" mientras la sección Branching, 80 líneas después, exigía parar y esperar confirmación antes de pushear. Un agente que leyera el workflow en orden pusheaba sin preguntar **y cumplía la guía**; las enmiendas 1.3.0 y 1.4.0 habían agregado la pausa sin invalidar el paso que la contradecía. Ahora el paso 4 aclara que "inmediatamente" es sobre *cuándo se ofrece* el push, no sobre saltear la confirmación.
- **Los templates distribuidos heredan la regla** (`AGENTS.md.template`, `CONSTITUTION.md.template`) — no la tenían: `AskUserQuestion` aparecía **0 veces** en todo `templates/`, y sí viajaba el "git push inmediatamente" que la contradice. Los proyectos generados con `rocky init` no heredaban ninguna de las convenciones de confirmación del propio repo. Se suma también la preferencia por `git branch -d` sobre `-D` al limpiar ramas, para que la negativa de git actue como red de seguridad.

### Fixed
- **`CONSTITUTION.md` decía "subir `1.0.0`" en su regla de enmienda** — el placeholder `{{CONSTITUTION_VERSION}}` se renderizó con el valor inicial y quedó congelado ahí, así que la instrucción apuntaba a una versión fija en vez de a la vigente (ya en 1.5.0). Reemplazado por una referencia al campo, no a un número.

## [0.11.0] - 2026-09-06

### Fixed
- **Encontrada la causa real del banner descuadrado que se venía arrastrando desde v0.8.0** — no era el renderizado de la terminal del usuario (diagnóstico equivocado que motivó cinco cambios de fuente y dos de librería): **Rich descarta los espacios finales al medir cada línea de un `Text` con `justify="center"`**, así que el relleno de `ljust(BANNER_WIDTH)` se ignoraba y cada fila del arte ASCII terminaba centrada según su contenido visible — las filas que terminan antes (por la forma de las letras) quedaban corridas a la derecha la mitad de la diferencia. Reproducido determinísticamente capturando el render de `show_welcome()` (márgenes `21, 21, 23, 21, 21` en la versión con el bug). Arreglado centrando el bloque entero con `Align.center` en vez de justificar línea por línea. Nuevo test `test_banner_lines_are_vertically_aligned_when_rendered`, que verifica el **render completo** en vez del string — el test anterior (`test_banner_lines_all_have_the_same_width`) pasaba en verde con el bug presente, porque el string efectivamente tenía las líneas parejas; el problema aparecía recién al renderizar.

### Added
- **Protocolo anti-loop** (`AGENTS.md` y su template, sección "Cuando un arreglo no funciona dos veces seguidas") — qué hacer cuando se aplican fixes sucesivos sobre el mismo síntoma sin resolverlo: umbrales escalonados (🟡 a los 2 intentos, 🔴 a los 3+), prohibición de cerrar el diagnóstico en una causa externa que no se puede medir, verificar la capa correcta (salida real, no entrada), confirmar que un test de regresión falla con el bug antes de darlo por bueno, aislar variables de a una, y tratar la contra-hipótesis del usuario como dato. Incluye el caso de referencia real que lo motivó (el descuadre del banner, ver `Fixed` abajo). Pedido explícito del usuario tras esa sesión.

### Changed
- **Banner relleno: fuente `standard` → `ansi_shadow`, con la cara y la sombra en colores distintos** — `standard` dibuja solo el *contorno* de las letras (`_ | / \`), así que el color de marca pintaba el borde y el arte se veía hueco. `ansi_shadow` usa el glifo macizo `█` con sombra 3D de caracteres de caja, así que las letras quedan rellenas. Nuevo `_banner_text()`: colorea por tramos en vez de con un estilo único — la cara en `BRAND` (`#D97959`, bold) y la sombra en `BRAND_SHADOW` (`#8A4634`, el mismo matiz con la luminancia al ~0.63x), porque con un solo color la sombra se lee como parte del trazo y la profundidad se pierde. **`BANNER_WIDTH` pasa de 56 a 78**: el arte ahora pide una terminal de 84 columnas (78 + `OUTER_PANEL_OVERHEAD`) en vez de ~62; por debajo de eso sigue cayendo al `COMPACT_TITLE`, verificado a 84 (entra) y 83 (fallback). Elegido por el usuario entre tres opciones (fuente sólida, fondo de color, degradado).
  - **Ojo con esto**: `ansi_shadow` es la fuente que en v0.8.1 se reportó como "descuadrada" en Warp. Ese diagnóstico resultó equivocado — la causa real era el `justify="center"` de Rich, arreglado en esta misma versión — pero el riesgo de que los glifos de bloque Unicode se empalmen mal según la fuente del terminal es independiente y no se puede descartar desde acá. Confirmar en la terminal de uso real antes de publicar.
- **Banner cambiado de la librería `art`/`colossal` a `pyfiglet`/`standard`** — `art` y `pyfiglet` leen los mismos archivos de fuente FIGlet (`.flf`), así que para el mismo nombre de fuente generan contenido idéntico carácter por carácter; el cambio de librería no fue lo que resolvió el descuadre (ver `Fixed` arriba), es una elección estética confirmada por el usuario en su propia terminal. `art` se saca de las dependencias del paquete (`pyproject.toml`), `pyfiglet` entra en su lugar.

## [0.10.0] - 2026-09-04

### Changed
- **Fuente del banner cambiada de `chunky` a `colossal`** — pedido explícito del usuario tras confirmar que `chunky` ya se veía bien (v0.9.1), quería letras más altas y trazos más gruesos. Ajuste puramente estético, misma librería `art`, generado en runtime.

### Fixed
- **`BANNER` tenía líneas en blanco de más al final** (1 en `chunky`, 3 en `colossal`) — `text2art()` devuelve líneas con espacios (no vacías) en las filas de descendencia de la fuente, y `.rstrip("\n")` sobre el string completo no las eliminaba porque no terminaban en `\n` puro. Reemplazado por un loop que descarta líneas finales en blanco (`.strip()` vacío) después de `.splitlines()` — bug preexistente desde que se generaba en runtime (v0.9.0), no específico de `colossal`.
## [0.9.1] - 2026-09-04

### Fixed
- **El banner con fuente `epic` (v0.9.0) se veía "punteado"/distorsionado en Warp** — el problema no era Unicode vs ASCII (`epic` ya era ASCII plano), era el grosor/densidad de los trazos: paréntesis y guiones bajos apilados en trazos finos se distorsionan en algunos terminales a tamaño de fuente chico, el mismo tipo de artefacto de renderizado que el bug de `ansi_shadow` en v0.8.0/v0.8.1, con otra causa concreta. Reemplazado por `chunky` (misma librería `art`), con formas más sólidas y menos diagonales/trazos finos.

## [0.9.0] - 2026-09-04

### Changed
- **Fuente del banner cambiada de `pyfiglet`/`standard` (hardcodeado) a `art`/`epic` generado en runtime** — puramente estético en el resultado (sigue siendo ASCII plano, sin caracteres de dibujo de cajas Unicode, así que no reintroduce el bug de descuadre de v0.8.0 en Warp/Windows Terminal), pero cambia el mecanismo: `art` pasa a ser dependencia real del paquete (`pyproject.toml`) y `welcome.py` llama a `art.text2art()` cada vez que muestra el banner, en vez de tener el texto fijo en el código. Decisión explícita del usuario, con el trade-off (una dependencia más a instalar) discutido antes de aplicarlo.

## [0.8.1] - 2026-09-04

### Fixed
- **El banner seguía descuadrado en Warp/Windows Terminal después del fix de v0.8.0** — ese fix corrigió el padding del string, pero el problema real era otro: la fuente `ansi_shadow` de `pyfiglet` arma las letras con caracteres Unicode de dibujo de cajas (`█ ═ ║ ╗ ╔`) que necesitan que el terminal empalme los glifos sin espacio extra entre líneas para verse limpios — varios terminales modernos agregan suficiente espaciado/anti-aliasing como para romper ese empalme, sin importar que el texto esté perfectamente alineado en columnas (verificado con `rich.cells.cell_len`, igual en las 6 líneas). Reemplazado por la fuente `standard` de `pyfiglet` (ASCII plano: `/ \ | _`, sin ambigüedad de renderizado en ningún terminal/fuente). Elegida por el usuario entre 3 alternativas.

## [0.8.0] - 2026-09-04

### Changed
- **Color de marca del CLI**: reemplazado `cyan` por `#D97959` (terracota/salmón, `hsla(15, 63%, 60%, 1)`, elegido por el usuario) en el banner, bordes de paneles y acentos de tablas/hints de `welcome.py`. Los colores con significado semántico (`green` = agente activo, `dim` = secundario) quedan sin cambios.

### Fixed
- **El banner "ROCKY SPEC" del welcome se veía descuadrado/"derretido" en Warp y en la terminal nativa de Windows** — dos de las seis líneas del arte ASCII perdieron el padding con espacios al final (probablemente un editor recortó espacios en blanco al guardar durante el rename manual del banner), quedando 5 caracteres más cortas que el resto. Como `Text(BANNER, justify="center")` centra cada línea por separado, esa diferencia de ancho desalineaba las filas entre sí. `BANNER` ahora se rellena con `ljust(BANNER_WIDTH)` calculado en código en vez de depender de que el string hardcodeado nunca pierda espacios — no vuelve a pasar aunque un editor recorte trailing whitespace de nuevo. Test de regresión: todas las líneas de `BANNER` deben medir lo mismo.

## [0.7.0] - 2026-09-04

### Changed
- **Rename completo: `spec-charless`/`charless` → `rocky-spec`/`rocky`** — pedido explícito del usuario. Toca prácticamente todo el repo:
  - Paquete pip: `spec-charless` → `rocky-spec`. Módulo Python: `src/spec_charless/` → `src/rocky_spec/` (`git mv`, historial de archivos preservado).
  - Comando de terminal: `charless` → `rocky` (sin alias de compatibilidad — corte limpio, decisión explícita dado que el proyecto está en `0.x.y` sin usuarios externos conocidos).
  - Carpeta compartida en cada proyecto destino: `.charless/` → `.rocky-spec/`.
  - Skill de Claude Code generada: `.claude/skills/spec-charless/` → `.claude/skills/rocky-spec/` (`/rocky-spec`). Comandos de Cursor: `.cursor/commands/charless-*.md` → `.cursor/commands/rocky-*.md`, `.cursor/rules/charless.mdc` → `.cursor/rules/rocky.mdc`.
  - Repo de GitHub: `carlos0718/spec-charless` → `carlos0718/rocky-spec` (GitHub redirige la URL vieja).
  - Banner de bienvenida regenerado con `pyfiglet` (fuente `ansi_shadow`): "ROCKY" + "SPEC" en vez de "SPEC" + "CHARLESS". Título compacto (terminales angostas) → "ROCKY SPEC".
  - Las 68 referencias en `commands/*.md`/`reference/*.md`/`templates/*.template` (incluida la skill fuente, ya renombrada externamente de `charless-ia` a `rocky-spec`) actualizadas para que el paquete generado quede en sync con la skill que lo produce.
  - `SPEC.md`/`SECURITY.md`/`OBSERVABILITY.md` de este mismo repo: contenido vivo actualizado; la sección "Historial de cambios" de `SPEC.md` **no se reescribió** — sigue describiendo los nombres reales que existían en cada momento pasado, con sus hashes de commit sin tocar.
  - De paso, dos gaps reales encontrados haciendo el audit de consistencia (no relacionados al rename en sí, pero corregidos de una): `rocky check accessibility` y el modo single-file de `rocky build` (`--template`/`--output`) nunca se habían agregado a la tabla de comandos del README ni a `welcome.py`.
  - Sin alias `charless` de compatibilidad — quien ya lo tenía instalado necesita reinstalar (`uv tool uninstall spec-charless && uv tool install git+https://github.com/carlos0718/rocky-spec.git`).

### Fixed
- **Hashes de commit rotos en el "Historial de cambios" de `SPEC.md`/`SECURITY.md`/`OBSERVABILITY.md`** — la reescritura de identidad de git (`git-filter-repo`, ver `v0.3.1`) cambió el SHA de todos los commits del repo; las referencias sueltas en prosa que se habían escrito antes de esa reescritura (`b90cf74`, `0b8c761`, `HEAD` literal, `(pendiente del primer commit)`) quedaron apuntando a revisiones inexistentes o ambiguas. Reemplazadas por los hashes reales actuales (`a855f64`, `88db0fa`, `8da96ec`, `c045465`, `c47b505`), verificados uno por uno contra `git log`. Encontrado por el usuario al revisar `SECURITY.md`.
## [0.6.1] - 2026-09-01

### Added
- **`MA-1.8` en `mode-adopt.md`** — wiring de `charless check accessibility` en Modo Adopción, simétrico a `MA-1.5`/`MA-1.6`/`MA-1.7`: si el proyecto detectado tiene interfaz visual, corre el chequeo determinista (o un heurístico manual reducido de fallback, con nota explícita de que 3 de los 5 heurísticos no tienen aproximación confiable en bash). Nueva fila `ACCESSIBILITY.md` en la tabla `MA-6`, condicional como `design-system/MASTER.md`. Cierra la pieza de "testear código ya escrito" que faltaba — `P5.8` (creación) genera el documento de decisiones, `MA-1.8` (adopción) audita código real, misma distinción que ya existe entre `P5.6`/`P5.7` y `MA-1.6`/`MA-1.7`. El resto del wiring diferido (`TODO.md.template`, `p7.5-qa-review.md`, `p8-p8.5-validation-systemprompt.md`) sigue pendiente.
- **`reference/flow-diagram.md`** — 4 diagramas Mermaid (router de detección de modo, Modo Creación P0→P8.5, Modo Adopción MA-1→MA-8, Modo Reanudación) con los condicionales reales de cada paso (`**Saltear si:**` de cada `commands/*.md`), para entender de un vistazo cómo itera la skill sin leer los 14 archivos de comandos. Enlazado desde `README.md`.

### Changed
- **Limpieza de ramas después de cada release** (`AGENTS.md` sección "Versionado y releases", y su template): tras mergear a la rama principal, el flujo ahora incluye listar las ramas ya mergeadas y preguntarle al usuario cuáles borrar (local + remoto) — nunca automático, nunca ofrecer una rama que no esté 100% mergeada.

## [0.6.0] - 2026-08-31

### Added
- **`charless check accessibility`** (RF-9/US-11) — health-check determinista de accesibilidad web, primera pieza de tres para cerrar el gap encontrado en conversación (no existía ningún chequeo automático, solo prosa en `ui-design-guidelines.md`/`coding-principles.md`). Corre sobre `.html`/`.jsx`/`.tsx` (y `.css` para contraste): `<img>` sin `alt`, `<html>` sin `lang`, `<div onClick>` sin `role`/`tabIndex`, `<button>` solo-ícono sin `aria-label`, y contraste WCAG AA básico (4.5:1) sobre pares `color`/`background` hardcodeados. Puramente diagnóstico, como el resto de los `check` — nunca edita código. Cada heurístico documenta explícitamente sus límites conocidos (spread props, `var(--x)`, Tailwind, texto oculto con `display:none`) en vez de esconderlos.
- **`charless build --template/--output`** — segunda pieza: modo de un solo archivo, para templates condicionales que no aplican a todo proyecto. Cierra un gap real encontrado al diseñar `ACCESSIBILITY.md.template`: `MASTER.md.template` (design system, P4.5) se generaba a mano por el LLM, fuera del mecanismo determinista de `build()` — mismo problema no-determinista que `build()` ya había resuelto para los otros 9 archivos, sin conectar. `p4.5-design-system.md` ahora prefiere `charless build . --template MASTER.md.template --output design-system/MASTER.md` en vez de reescribir el archivo a mano.
- **`ACCESSIBILITY.md.template` + nuevo paso `P5.8 · Accesibilidad`** — tercera y última pieza: documento vivo por proyecto, mismo patrón que `SECURITY.md`/`OBSERVABILITY.md` (nivel de exigencia, decisiones, checklist `- [ ]` que arranca sin marcar), condicional a que el proyecto tenga interfaz visual — se genera igual que `design-system/MASTER.md`, vía el nuevo modo single-file de `charless build`. `p5.8-accessibility.md` documenta el paso completo (detección automática, confirmación, generación). Wireado en `scaffold.py` (`COMMAND_CATALOG`), `qa_review.py` (entra al chequeo de placeholders sin resolver) y `AGENTS.md.template` (línea "Generado por"). El wiring en Modo Adopción (`MA-1.8`, `TODO.md.template`) queda diferido para una iteración posterior — documentado explícitamente, no perdido.

## [0.5.1] - 2026-08-31

### Fixed
- **El diseño del welcome se rompía al angostar la terminal** — `Text(BANNER, ...)` no tenía `no_wrap`/`overflow` seteados en el `console.print()` real, así que Rich repartía cada línea del ASCII art a la mitad e intercalaba los pedazos con la línea siguiente. Ahora usa `no_wrap=True, overflow="crop"` (crop limpio, sin corrupción), y por debajo de `BANNER_WIDTH` (~103 cols) muestra un título compacto ("SPEC CHARLESS") en vez de un banner recortado a la mitad.

### Changed
- **El merge nunca es automático** (`AGENTS.md` sección "Branching", `CONSTITUTION.md` Artículo 7, y sus templates): después de commitear y pushear una rama `feature/*`/`fix/*` (o de dejar `dev` lista para un release), el flujo ahora exige parar y mostrar un resumen del cambio antes de ejecutar `git merge`, esperando confirmación explícita — nunca encadenar commit → push → merge sin que el usuario vea qué se integra a `dev`/`master`. Pedido explícito del usuario tras notar que los merges se venían haciendo en cadena sin pausa.
- **Los recuadros "Glosario" y "Agentes soportados"/"Este proyecto ya usa spec-charless" ahora se arman en dos columnas lado a lado cuando el ancho de la terminal alcanza para los dos** (`rich.columns.Columns`, centrado como grupo) — si no entran, se apilan uno debajo del otro, cada uno igual centrado (antes quedaban pegados a la izquierda). El layout se recalcula contra `console.width` en cada corrida, no queda fijo.

## [0.5.0] - 2026-08-31

### Fixed
- **`charless check qa` no detectaba placeholders con sintaxis `{{NOMBRE, default: valor}}`** que sobrevivían sin rellenar en el archivo final — `qa_review.py` tenía su propio regex, separado y más simple que el de `render_template.py`, que solo reconocía `{{NOMBRE}}`. Unificado: ahora reusa `render_template.find_unresolved()`, la misma fuente de verdad para "qué es un placeholder sin resolver" en todo el proyecto.

### Changed
- **`mode-adopt.md` (MA-1.5/1.6/1.7) y `p7.5-qa-review.md` (Pasos 1 y 4) ahora prefieren los `charless check *` deterministas** en vez de duplicar la misma lógica en heurísticos de `find`/`grep`/`wc -l` como único camino — el heurístico en prosa queda como fallback explícito para cuando `charless` no está instalado. `health_check.py` ya se declaraba a sí mismo "equivalente determinista" de estos pasos en sus propios docstrings; faltaba conectarlo. Segundo paso de tres para cerrar la brecha entre los checks en código y las instrucciones que sigue el LLM.

### Added
- **`charless build`** (RF-8/US-10) — conecta `render_template.py` (existía, con tests propios, pero nada lo llamaba) al flujo real de P6/P7. Toma un JSON plano de valores y renderiza `CONSTITUTION.md`, `SPEC.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `OBSERVABILITY.md`, `CHANGELOG.md`, `README.md`, `TODO.md` y `LICENSE` (si se pasa `LICENSE_CHOICE`) desde `.charless/templates/*.template` en una sola pasada — no pisa un archivo que ya exista salvo `--force`, y reporta placeholders sin resolver por archivo (mismo `find_unresolved()` que ya usa `check qa`). `p6-p7-files-todo.md` documenta correrlo en vez de que el LLM copie cada template y reemplace los marcadores a mano. Tercer y último paso del plan para cerrar la brecha entre los checks deterministas y las instrucciones en prosa del flujo P0-P8.5.

## [0.4.0] - 2026-08-31

### Added
- **Rediseño de la pantalla de bienvenida** (`welcome.py`): todo el contenido queda envuelto en un borde único, título/autoría/tagline centrados, y la versión instalada visible junto al autor (`by Carlos Jesus · v0.4.0`).
- **`charless commands`** — comando nuevo que imprime la tabla completa de comandos con su descripción (espejo de la tabla del README), para no tener que ir a buscarla fuera de la terminal.
- La tabla de "Agentes soportados" del welcome ahora incluye una columna "Se invoca con", aclarando que `/spec-charless` (Claude Code) y `/charless-*` (Cursor) son comandos del **agente**, distintos de `charless` (la CLI).
- README: nueva sección "Tres nombres parecidos, tres cosas distintas" — desambigua `charless` (comando), `spec-charless` (paquete pip + skill generada en el proyecto destino) y `charless-ia` (la skill original con la que se construye este framework).

## [0.3.1] - 2026-08-31

### Fixed
- **README — instalación con `uv`/`pipx` daba error en la práctica**, por dos motivos que faltaba documentar: (1) el README asumía que `uv`/`pipx` ya estaban instalados, sin explicar cómo instalarlos; (2) después de `uv tool install`/`pipx install`, el ejecutable queda en una carpeta que no está en el PATH de la sesión actual hasta correr `uv tool update-shell`/`pipx ensurepath` y reabrir la terminal — el instalador no lo hace solo. Reproducido y verificado contra `v0.3.0` real antes de escribir la corrección.

## [0.3.0] - 2026-08-31

### Fixed
- **La versión estaba hardcodeada en tres lugares** (`pyproject.toml`, `scaffold.CHARLESS_VERSION`, `__init__.__version__` — este último ni se usaba en ningún lado) — ahora `__init__.py` la lee de los metadatos del paquete instalado, una sola fuente de verdad. Bug real encontrado al usar la skill en un IDE separado y notar que la versión no había cambiado tras un fix.

### Added
- Tests de regresión para la fuente única de verdad de la versión (`test_versioning.py`).
- **Branching GitFlow simplificado**, portado desde la skill original (`~/.claude/skills/charless-ia`) a los templates de este paquete: nueva sección "Branching" en `AGENTS.md.template` (`main`/`dev`/`feature/*`/`fix/*`, con el recordatorio de bump de versión al mergear a `dev`/`main`), un **Branch Discipline Check** como paso 0-ter del Workflow de Git, dos artículos nuevos en `CONSTITUTION.md.template` (Boundaries y Versionado), una fila de detección de estado de branching en el scan de `mode-adopt.md` (MA-1), y la tarea "Crear rama `dev` desde `main`" en `TODO.md.template`.
- **Flujo de iteración Plan → Confirmar → Implementar**, también portado desde la skill original: reemplaza el flujo "Agregar o modificar features (Spec-Anchored)" de `AGENTS.md.template`, que solo cubría cambios de alcance. Ahora cualquier pedido de cambio (feature o corrección) pasa primero por un plan breve y espera confirmación explícita antes de tocar código — Paso 1 decide si afecta `SPEC.md` (Paso 2a) o no (Paso 2b), y el Paso 3 implementa recién con el ok del usuario.
- **`charless check version`** (RF-7/US-9) — calcula el bump de SemVer exacto a partir de los commits reales desde el último tag (Conventional Commits, regla "el más alto gana": MAJOR > MINOR > PATCH, sin apilar bumps), reemplazando el recordatorio en prosa de `AGENTS.md`. Maneja el caso pre-1.0 (breaking change sugiere MINOR, no salto automático a `1.0.0`) y avisa con umbrales escalonados (🟡 3-5, 🔴 6+) si una rama `feature/*` acumuló demasiados `fix` comparado contra `dev`. El cálculo se dispara al mergear `feature/*`/`fix/*` → `dev` (o `fix/*` → `master` en un hotfix) — nunca al mergear `dev` → `master`, donde la versión se hereda tal cual. El footer `BREAKING CHANGE:` se detecta anclado a inicio de línea, no en cualquier parte del body — una mención suelta dentro de una viñeta (ej. un commit que *describe* la feature) no cuenta como footer real.

### Docs
- `references/versioning.md` (skill y framework): dos lecciones nuevas encontradas en producción — (1) la versión debe leerse de una única fuente en runtime, nunca hardcodeada en más de un lugar; (2) distribución vía `git+https://...` antes de publicar en un registry hace que cada push sea una publicación de hecho, exige taguear con más disciplina en esa etapa. Ambas ahora también en `CONSTITUTION.md.template` Artículo 7, para que todo proyecto nuevo las tenga desde el arranque.

## [0.2.0] - 2026-08-31

### Added
- Interfaz de bienvenida (`welcome.py`, con `rich`) — banner al correr `charless` sin argumentos, con estado del proyecto (agentes activos) si ya tiene `.charless/`, o la lista de agentes disponibles si es la primera vez. Banner corto antes de `init`.
- Banner ampliado: "CHARLESS" ahora tiene el mismo arte ASCII (fuente `ansi_shadow`) que "SPEC", con "by Carlos Jesus" como autoría. Sumada una reseña de features del kit y un glosario de siglas propias (RF, US, RNF, MA, P) antes de la tabla de integraciones.

### Changed
- Instalación: el README documenta `uv tool install` / `pipx install` / `pip install` desde el repo (`git+https://...`) para Windows, Linux y macOS, con verificación, actualización y desinstalación. PyPI deja de ser requisito de uso y pasa a mejora opcional (RF-6/US-8).

### Fixed
- El wheel no se podía construir: `tool.hatch.build.targets.wheel.force-include` volvía a agregar `commands/`, `reference/` y `templates/`, que `packages` ya incluye por vivir dentro de `src/spec_charless/`, y hatchling abortaba con "A second file is being added to the wheel archive at the same path". Esto rompía `pip install git+...` y cualquier build para PyPI; `pip install -e .` no lo exponía porque el modo editable no construye el wheel.
- URLs del proyecto en `pyproject.toml` — apuntaban a `github.com/charly` (usuario inexistente) y a la rama `main`; el repo publicado es `carlos0718/spec-charless` en `master`.
- `qa_review.check_traceability`: una mención suelta de un `RNF-N` fuera de su fila de definición (ej. en el Historial de cambios) generaba un falso positivo de "sin plan de trabajo", ignorando el marcador de default de la fila real. Mismo fix propagado a `.charless/commands/p7.5-qa-review.md` y a la skill original `charless-ia`.
- Agregado el marcador `"no aplica"` a los reconocidos como default en NFRs — antes solo se reconocían las frases exactas del template.
- **`v0.1.0` nunca había sido tagueado** — la sección del CHANGELOG existía pero el release nunca se completó (le faltaba el paso de `git tag`). Tagueado retroactivamente sobre el commit que corresponde a ese contenido.

## [0.1.0] - 2026-08-31

### Added
- Arquitectura de integraciones (`IntegrationBase`, `INTEGRATION_REGISTRY`) — plugin pattern inspirado en GitHub Spec Kit.
- Integración de Claude Code (`.claude/skills/spec-charless/SKILL.md`).
- Integración de Cursor (`.cursor/commands/*.md` + `.cursor/rules/charless.mdc`).
- Conocimiento compartido migrado desde la skill original: `commands/` (14 pasos del ciclo de vida), `reference/` (17 documentos de principios/metodologías/arquitecturas), `templates/` (18 plantillas de archivos generados).
- Scripts deterministas: `render_template` (relleno de placeholders), `health_check` (code smells/seguridad/observabilidad), `qa_review` (trazabilidad RF→US→RNF→tarea).
- CLI: `charless init`, `charless check {code,security,observability,qa}`, `charless list-integrations`.
- `SPEC.md`, `CONSTITUTION.md`, `AGENTS.md`, `SECURITY.md`, `OBSERVABILITY.md`, `TODO.md` generados vía Modo Adopción — el framework aplicado sobre sí mismo.

### Changed
- Rename del paquete: `charless-cli` → `spec-charless` (el comando sigue siendo `charless`, corto para tipear).
