> Referencia de **rocky-spec** — árboles de carpetas para proyectos **híbridos** (landing con animación 3D, web inmersiva multi-escena). Ver `.rocky-spec/reference/architectures.md` para la tabla de decisión.

## HÍBRIDO

### Landing con animación 3D

Cuándo: web con un objeto 3D, animación scroll-driven, o efectos avanzados.

```
<project>/
├── src/
│   ├── components/
│   ├── scenes/                  ← componentes R3F
│   ├── shaders/                 ← .glsl o strings GLSL
│   ├── hooks/
│   ├── styles/
│   └── main.tsx
├── public/
│   ├── models/                  ← .glb, .gltf
│   ├── textures/                ← .hdr, .ktx2, .webp
│   └── lottie/                  ← .json de Lottie
├── assets-raw/                  ← .blend, .c4d, archivos fuente
├── .rocky-spec/reference/                  ← inspiración visual
├── tests/
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

### Web inmersiva (multi-escena)

Cuándo: portfolio inmersivo, sitio con varias escenas 3D coreografiadas.

```
<project>/
├── src/
│   ├── scenes/
│   │   ├── intro/
│   │   ├── about/
│   │   └── work/
│   ├── components/
│   ├── shaders/
│   ├── hooks/
│   ├── choreography/            ← Theatre.js timelines
│   └── main.tsx
├── public/
│   ├── models/
│   ├── textures/
│   └── audio/
├── assets-raw/
├── .rocky-spec/reference/
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

