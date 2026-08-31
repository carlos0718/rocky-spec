> Referencia de **charless-ia** — árboles de carpetas para proyectos **creativos** (video ad/motion, social content batch, branding visual). Ver `.charless/reference/architectures.md` para la tabla de decisión.

## CREATIVO

### Video ad / motion piece

Cuándo: cualquier producción de video con AI o motion design.

```
<project>/
├── 01-brief/
│   ├── BRIEF.md
│   └── client-.charless/reference/       ← assets que mandó el cliente
├── 02-.charless/reference/
│   ├── moodboard/               ← screenshots, key visuals
│   └── inspiration.md
├── 03-prompts/
│   └── prompts.md               ← plantilla por bloques (STYLE/BACKGROUND/FRAMING/OUTPUT)
├── 04-raw-frames/
│   ├── hero/                    ← outputs de AI image
│   ├── ingredients/
│   └── transitions/
├── 05-clips/
│   ├── runway/                  ← outputs de AI video por tool
│   ├── kling/
│   └── selects/                 ← los que pasaron el filtro
├── 06-edit/
│   ├── <project>.prproj         ← Premiere
│   ├── <project>.drp            ← DaVinci
│   └── <project>.aep            ← After Effects
├── 07-exports/
│   ├── 9x16/                    ← TikTok, Reels, Shorts
│   ├── 1x1/                     ← feed cuadrado
│   └── 16x9/                    ← YouTube, web
├── STORYBOARD.md
├── CONSTITUTION.md
├── AGENTS.md
├── CLAUDE.md
├── SECURITY.md
├── CHANGELOG.md
├── OBSERVABILITY.md
├── LICENSE
├── README.md
└── TODO.md
```

### Social content batch (semanal, recurrente)

Cuándo: producción seriada (un Reel por semana, threads, etc.).

```
<project>/
├── templates/
│   ├── BRIEF.template.md
│   └── prompts.template.md
├── episodes/
│   ├── 2026-W22-tema1/
│   │   ├── BRIEF.md
│   │   ├── prompts.md
│   │   ├── raw-frames/
│   │   ├── clips/
│   │   ├── edit/
│   │   └── exports/
│   └── 2026-W23-tema2/
├── shared-assets/
│   ├── logos/
│   ├── fonts/
│   └── music/
├── CONSTITUTION.md
├── AGENTS.md
├── CLAUDE.md
├── SECURITY.md
├── CHANGELOG.md
├── OBSERVABILITY.md
├── LICENSE
├── README.md
└── TODO.md
```

### Branding visual / key visuals

Cuándo: producción de assets estáticos sin video.

```
<project>/
├── brief/
├── .charless/reference/
├── prompts/
├── outputs/
│   ├── round-1/
│   ├── round-2/
│   └── final/
├── delivery/
│   ├── png/
│   ├── jpg/
│   └── tiff/
├── CONSTITUTION.md
├── AGENTS.md
├── CLAUDE.md
├── SECURITY.md
├── CHANGELOG.md
├── OBSERVABILITY.md
├── LICENSE
├── README.md
└── TODO.md
```

