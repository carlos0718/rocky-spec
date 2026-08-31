# Diccionario de keywords de activación — /charless-ia

Este archivo documenta todas las frases y palabras clave que deben activar la skill `/charless-ia`, organizadas por modo y por idioma. Sirve como referencia para ajustar el frontmatter `description` sin superar el límite de 1024 caracteres.

---

## Modo 1 — Proyecto nuevo (desde cero)

El usuario quiere arrancar un proyecto que no existe todavía.

### Español
- nuevo proyecto
- armar proyecto
- iniciar proyecto
- crear proyecto
- empezar proyecto
- arrancar proyecto
- hacer un proyecto
- scaffold
- boilerplate
- setup inicial
- quiero empezar algo desde cero
- quiero construir una app
- quiero hacer una web
- quiero hacer una API
- quiero hacer un script
- hagamos una app
- hacer una landing
- quiero desarrollar
- proyecto de cero
- fresh start

### Inglés
- new project
- start a project
- create a project
- build a project
- scaffold a project
- set up a project
- project setup
- start from scratch
- let's build
- I want to make an app
- I want to make a website
- I want to build an API
- initialize project
- init project
- project boilerplate
- kick off a project
- fresh project

---

## Modo 2 — Reanudación (proyecto creado con esta skill)

El usuario ya tiene un proyecto iniciado con `/charless-ia` y quiere continuar desde donde quedó. La skill busca `.skill-state.json` para saber en qué punto retomar.

### Español
- continuemos
- continuamos
- seguimos
- retomemos el proyecto
- retomemos
- sigamos con el proyecto
- qué sigue
- qué me falta hacer
- qué me falta
- qué falta
- próxima tarea
- próximo paso
- siguiente paso
- en qué estaba
- en qué estábamos
- dónde quedamos
- seguir trabajando
- seguir con el TODO
- sigamos con el TODO
- qué hay pendiente
- qué queda por hacer
- continuemos el proyecto
- retomar

### Inglés
- let's continue
- continue the project
- resume the project
- where did we leave off
- what's next
- next step
- next task
- what's left to do
- what's pending
- keep going
- continue where we left off
- pick up where we left off
- what do I still need to do
- resume
- continue working

---

## Modo 3 — Adopción (proyecto existente sin la skill)

El usuario tiene un proyecto ya avanzado que NO fue creado con esta skill, pero quiere aplicar las convenciones: SPEC.md, AGENTS.md, CLAUDE.md, TODO.md, design system, arquitectura documentada.

### Español
- tengo un proyecto ya avanzado
- tengo un proyecto ya iniciado
- el proyecto ya tiene código
- el proyecto ya estaba iniciado
- el proyecto ya existe
- ya tengo el proyecto armado
- adoptar proyecto
- adoptar este proyecto
- aplicar la skill a este proyecto
- integrar a proyecto existente
- quiero organizar mi proyecto
- quiero documentar mi proyecto
- quiero aplicar las convenciones al proyecto
- quiero agregar CLAUDE.md a mi proyecto
- quiero agregar AGENTS.md a mi proyecto
- quiero agregar SPEC.md a mi proyecto
- quiero armar el TODO de mi proyecto
- mi proyecto no tiene SPEC.md
- mi proyecto no tiene CLAUDE.md
- mi proyecto no tiene AGENTS.md
- quiero aplicar SDD a mi proyecto
- quiero aplicar DDD a mi proyecto
- quiero agregar arquitectura al proyecto
- quiero estructurar mejor el proyecto
- quiero orden en mi proyecto
- el proyecto ya corría cuando empecé a usar la skill

### Inglés
- I already have a project
- the project already exists
- adopt this project
- adopt existing project
- apply the skill to an existing project
- I want to organize my project
- I want to document my project
- add CLAUDE.md to my project
- add AGENTS.md to my project
- add SPEC.md to my project
- set up TODO for my project
- my project is already started
- my project already has code
- apply conventions to existing project
- retrofit the skill to my project
- I have an existing codebase
- onboard existing project
- the project was already running

---

## Señales de detección automática (sin frase explícita)

Cuando el usuario invoca la skill sin frase clara, la skill detecta el modo por el estado del directorio:

| Señal en el cwd | Modo inferido |
|---|---|
| No hay `.git`, no hay `package.json` | Proyecto nuevo |
| Hay `.skill-state.json` con `"step"` | Reanudación |
| Hay `.git` o `package.json` pero no `.skill-state.json` | Adopción |
| Hay `.skill-state.json` con `"mode": "adopted"` | Reanudación (post-adopción) |

---

## Sinónimos y variaciones ortográficas a tener en cuenta

| Canónico | Variantes |
|---|---|
| retomemos | retomar, reanudar, volvamos |
| qué sigue | qué viene, qué hacemos ahora, cuál es el próximo paso |
| adoptar proyecto | onboarding proyecto, integrar skill, aplicar skill |
| nuevo proyecto | fresh project, proyecto desde cero, empezar de cero |
| scaffold | boilerplate, template inicial, estructura base |
