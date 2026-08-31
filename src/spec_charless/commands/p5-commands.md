> Referencia de **charless-ia** — Paso P5 del flujo de creación: ejecución de comandos (modos Auto / Paso a paso / Manual).

### P5 · Comandos a ejecutar (interactivo, paso a paso)

El objetivo de este paso es **evitar que el usuario tipee los comandos a mano** (riesgo de typos) y darle control granular sobre qué se ejecuta.

#### Vista previa primero

Antes de ejecutar nada, mostrar la lista completa para que el usuario vea el alcance:

```
Para armar tu proyecto necesito correr 6 comandos:

  [1] cd /home/charly/code
  [2] npm create vite@latest mi-proyecto -- --template react-ts
  [3] cd mi-proyecto
  [4] npm install
  [5] npm i -D tailwindcss postcss autoprefixer
  [6] npx tailwindcss init -p

¿Cómo querés que avancemos?
> 1) Auto       — los ejecuto todos, te aviso si algo falla
  2) Paso a paso — te muestro cada comando y confirmás con Enter antes de ejecutar
  3) Manual     — los pegás vos en tu terminal, yo solo confirmo al final
```

**Default sugerido**: si el `profile.md` tiene `default_install_mode` seteado, usar eso sin preguntar y avisarle al usuario *"Voy en modo <X> según tu perfil. Si querés cambiar, decime."*.

Si el usuario elige un modo distinto al default, ofrecer al final: *"¿Querés que lo grabe en tu perfil como tu modo default? (s/n)"*.

#### Modo A — Auto

Ejecutar todos los comandos en orden vía bash, reportando cada uno:

```
[1/6] cd /home/charly/code
      OK

[2/6] npm create vite@latest mi-proyecto -- --template react-ts
      corriendo...
      OK (proyecto creado en 12s)

[3/6] cd mi-proyecto
      OK

[4/6] npm install
      corriendo... (esto puede tardar 30-60s)
      OK (245 paquetes instalados)
```

**Si algún comando falla**, pausar y preguntar:

```
[5/6] npm i -D tailwindcss postcss autoprefixer
      ERROR: npm ERR! code ERESOLVE
      <stderr completo>

¿Cómo seguimos?
> 1) Reintentar el mismo comando
  2) Modificar el comando y reintentar (lo edito junto con vos)
  3) Saltarlo y seguir con el próximo
  4) Abortar el setup (deja el proyecto a medias)
```

#### Modo B — Paso a paso

Para cada comando, mostrar y esperar confirmación explícita:

```
[2/6] Próximo comando:

      npm create vite@latest mi-proyecto -- --template react-ts

¿Qué hacés?
> 1) [Enter] / "s" / "ok"   — lo ejecuto yo
  2) "no" / "skip"            — saltarlo
  3) "yo"                     — lo corrés vos, yo espero tu "listo"
  4) <pegar comando custom>   — uso el que pegues en vez del sugerido
```

Después de ejecutar (o de que el usuario confirme su ejecución manual), seguir con el próximo. Si falla, mismo menú de error que en Modo A.

**Atajo útil**: si el usuario tipea "todo" en cualquier paso, switchear a Modo A para los restantes.

#### Modo C — Manual

Mostrar toda la lista en un bloque copiable de una vez:

````
```bash
cd /home/charly/code
npm create vite@latest mi-proyecto -- --template react-ts
cd mi-proyecto
npm install
npm i -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Copialos y corrélos en tu terminal. Cuando termines, decime "listo" o pegá lo que haya fallado.
````

Esperar el "listo" antes de seguir.

#### Excepción: acciones seguras siempre las hace la skill

Las siguientes acciones **NO** son parte de P5 y la skill las ejecuta sin preguntar:

- Crear carpetas según la arquitectura de P4 (`mkdir -p src/features/auth/components`, etc.).
- Escribir archivos de configuración generados (`tailwind.config.js`, `vitest.config.ts`, `.eslintrc`).
- Escribir los archivos base de P6 (`SPEC.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `TODO.md`).

Estas son operaciones de filesystem deterministas y no destructivas, sin riesgo de typo.

#### Si la skill no tiene permisos de Bash en la sesión

Si Claude no puede ejecutar bash en la sesión actual (modo restringido), avisar al usuario y **caer automáticamente a Modo C** sin preguntar. Mostrar:

```
No tengo permisos para ejecutar comandos en esta sesión.
Te voy a mostrar todo para que lo corras vos. Decime "listo" cuando termines.
```

#### Reporte intermedio al final de P5

Antes de pasar a P6, mostrar resumen:

```
=== Resumen de P5 ===
Modo elegido:   Paso a paso
Ejecutados:     5 / 6
Saltados:       1 (npm i -D vitest — usuario eligió omitir)
Fallidos:       0
Tiempo total:   2 min 14 s
```

Si hubo saltos o fallos, ofrecer revisar el TODO.md para registrarlos como pendientes (en P7).

