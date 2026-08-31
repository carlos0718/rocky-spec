# spec-charless

Toolkit multi-agente para **Spec-Driven Development**, nivel **Spec-Anchored** (el spec es un documento vivo, no una foto del día 1 — ver `src/spec_charless/reference/methodologies.md`).

Nacido como una skill de Claude, ahora es un framework agnóstico de agente: la misma base de conocimiento (`.charless/`) sirve para Claude Code, Cursor, y los agentes que se agreguen — sin duplicar contenido entre ellos.

## Instalación

```bash
pip install -e .
# o, cuando esté publicado:
# uv tool install spec-charless
```

## Uso

```bash
# Inicializar un proyecto con uno o más agentes
charless init mi-proyecto --agent claude
charless init mi-proyecto --agent claude --agent cursor

# Ver qué agentes soporta esta versión
charless list-integrations

# Health-checks deterministas (no dependen de que un LLM corra el comando bien)
charless check code .
charless check security .
charless check observability .
charless check qa .
```

## Cómo está armado

```
.charless/              ← se instala en el proyecto DESTINO, no acá
├── commands/            (los pasos del ciclo de vida — spec, arquitectura, seguridad...)
├── reference/           (principios, metodologías, arquitecturas, guías de diseño)
├── templates/           (SPEC.md, CONSTITUTION.md, AGENTS.md, SECURITY.md, etc.)
└── VERSION

src/spec_charless/
├── cli.py                    (comandos: init, check, list-integrations)
├── scaffold.py                (copia el conocimiento a .charless/ del proyecto destino)
├── integrations/
│   ├── base.py                (IntegrationBase — contrato que cumple cada agente)
│   ├── claude.py               (genera .claude/skills/charless-ia/SKILL.md)
│   └── cursor.py                (genera .cursor/commands/*.md + .cursor/rules/charless.mdc)
└── scripts/
    ├── render_template.py       (relleno determinista de {{PLACEHOLDER}})
    ├── health_check.py           (equivalente en código de MA-1.5/1.6/1.7)
    └── qa_review.py               (equivalente en código de P7.5 — trazabilidad RF→US→RNF→tarea)
```

**Principio de diseño**: el conocimiento (`commands/`, `reference/`, `templates/`) es uno solo y vive en `.charless/` dentro del repo del proyecto — versionado junto al código. Cada integración es un adaptador delgado que genera un puntero hacia ahí, en el formato que su agente espera. Agregar un agente nuevo (Windsurf, Copilot) es escribir una integración más, nunca reescribir el conocimiento.

## Agentes soportados

| Agente | Formato generado |
|---|---|
| Claude Code | `.claude/skills/charless-ia/SKILL.md` |
| Cursor | `.cursor/commands/charless-*.md` + `.cursor/rules/charless.mdc` |

## Licencia

MIT — ver [`LICENSE`](./LICENSE).
