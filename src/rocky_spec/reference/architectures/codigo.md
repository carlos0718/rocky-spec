> Referencia de **rocky-spec** — árboles de carpetas para proyectos de **código** (Mini, Chico, Mediano, Grande, Libre). Ver `.rocky-spec/reference/architectures.md` para la tabla de decisión de qué tamaño elegir.

## CÓDIGO

### Mini — HTML/CSS/JS estático, landing, demo

Cuándo: 1 página, sin estado complejo, sin backend, sin build (o build mínimo).

```
<project>/
├── index.html
├── styles/
│   └── style.css
├── scripts/
│   └── main.js
├── assets/
│   ├── images/
│   └── fonts/
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

### Chico — SPA simple (1–2 features)

Cuándo: SPA con pocas pantallas, sin estado global pesado.

```
<project>/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── utils/
│   ├── styles/
│   └── main.tsx
├── public/
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

### Mediano — Feature-based (recomendado para casi todo)

Cuándo: varias features independientes, estado compartido, equipo chico.

```
<project>/
├── src/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api/
│   │   │   ├── types.ts
│   │   │   └── index.ts
│   │   └── dashboard/
│   │       └── ...
│   ├── shared/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── types/
│   ├── app/
│   │   ├── router.tsx
│   │   └── providers.tsx
│   └── main.tsx
├── public/
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

### Grande — Clean / Hexagonal

Cuándo: dominio complejo, multi-equipo, tests pesados, necesidad de aislar la lógica de negocio del framework. Por su tamaño, este es el caso típico donde el TODO se genera directamente en **modo orquestador** (ver `.rocky-spec/commands/p6-p7-files-todo.md`). El ejemplo de abajo muestra la organización **por capas** (útil si hay frontend/backend especializados); si el equipo es fullstack y prefiere avanzar por feature de punta a punta, esos mismos archivos se llamarían `todos/login.md`, `todos/checkout.md`, etc. en vez de `dominio-db.md`/`api-backend.md`/`frontend-ui.md` — mismo mecanismo, distinto criterio de agrupación.

```
<project>/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value-objects/
│   │   └── repositories/        ← interfaces
│   ├── application/
│   │   ├── use-cases/
│   │   ├── services/
│   │   └── ports/
│   ├── infrastructure/
│   │   ├── persistence/         ← implementaciones de repositories
│   │   ├── http/
│   │   ├── messaging/
│   │   └── external-services/
│   ├── presentation/
│   │   ├── components/          ← si hay UI
│   │   ├── controllers/         ← si es API
│   │   └── views/
│   └── main.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── todos/                       ← TODO.md como orquestador (proyecto grande)
│   ├── dominio-db.md
│   ├── api-backend.md
│   ├── frontend-ui.md
│   ├── infraestructura-deploy.md
│   ├── seguridad.md
│   └── observabilidad.md
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

### Libre

El usuario describe la estructura que quiere y la skill la crea. Sin opinión.

