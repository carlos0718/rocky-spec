# Pattern · `cinematic-product-landing`

> Single-page parallax cinematográfica para marca de producto físico (bebida, snack, perfume, sneaker, gadget). Hero con WebP image sequence mapeado al scroll, variantes navegables, dark mode por default.

## Match criteria

Se ofrece este patrón si la descripción del usuario en P1 contiene **2 o más** de las siguientes señales:

| Categoría | Señales detectables |
|---|---|
| Tipo de página | "single-page", "landing", "one-pager", "página de producto", "sitio de marca" |
| Producto físico | "bebida", "lata", "botella", "snack", "perfume", "gadget", "sneaker", "auriculares", "electrónica", "cerveza", "consumo", "packaging", "DTC", o nombre concreto de marca de producto |
| Aesthetic / animación | "parallax", "scroll-driven", "cinematográfica", "cinematic", "inmersiva", "immersive", "WebP sequence", "scroll animation", "video-like", "premium", "hero animado" |
| Variantes | "varios sabores", "variantes", "flavors", "colores", "modelos", "navegación de productos", "PREV/NEXT" |

## Stack recomendado (opinado, no negociable salvo que el usuario insista)

| Capa | Elección | Por qué |
|---|---|---|
| Framework | Next.js 15 (App Router) | SEO + image optimization + Server Components para SSG del hero |
| Lenguaje | TypeScript | El patrón es premium, conviene tipado |
| Estilos | Tailwind CSS (dark mode = class strategy) | Velocidad + el patrón pide dark por default |
| Animación scroll | GSAP + ScrollTrigger | Mapping preciso de scroll position a frame index |
| Smooth scroll | Lenis | Inercia cinematográfica sin jank en trackpad/scroll wheel |
| Sequence player | Custom hook con `<canvas>` o `<img>` swap | Carga progresiva, sin libs externas |
| Image processing | sharp (build-time) | Convertir frames raw (PNG/JPG de Runway o After Effects) a WebP optimizado |
| Iconos | lucide-react | Sociales en footer, navegación |
| Fonts | next/font (Inter o similar bold para hero) | Sin layout shift |
| Deploy | Vercel | Cero-config + Image CDN |

**Si el usuario es principiante en algo de esto**, ofrecer alternativa más amigable:
- En vez de GSAP custom: `motion` (Framer Motion) con `useScroll`/`useTransform`.
- En vez de Lenis: scroll nativo (perdés algo de smoothness, ganás simplicidad).

## Arquitectura de carpetas

```
<project>/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx              ← single page con el hero
│   │   └── globals.css
│   ├── components/
│   │   ├── Hero.tsx              ← contiene SequenceCanvas + overlays
│   │   ├── SequenceCanvas.tsx    ← el WebP player tied to scroll
│   │   ├── VariantNav.tsx        ← PREV / NEXT lateral derecho
│   │   ├── ThemeToggle.tsx       ← dark / light
│   │   ├── CTAButtons.tsx
│   │   └── Footer.tsx
│   ├── hooks/
│   │   ├── useScrollFrame.ts     ← mapea scrollY a índice de frame
│   │   └── useLenis.ts
│   ├── lib/
│   │   ├── variants.ts           ← config de cada flavor (nombre, color, ruta de sequence)
│   │   └── theme.ts
│   └── styles/
├── public/
│   └── sequences/
│       ├── cherry/
│       │   ├── frame-0001.webp
│       │   ├── frame-0002.webp
│       │   └── ... (60-120 frames típicamente)
│       ├── grape/
│       └── lemon/
├── public/
│   └── cta-images/
│       ├── cherry-can.webp
│       ├── grape-can.webp
│       └── lemon-can.webp
├── scripts/
│   └── optimize-frames.mjs       ← sharp: PNG/JPG → WebP optimizado
├── assets-raw/                   ← frames originales antes de optimizar (gitignored)
├── BRIEF.md                      ← brief del producto/marca
├── prompts.md                    ← prompts para WebP sequences + CTA images
├── STORYBOARD.md                 ← scene-by-scene del hero
├── CLAUDE.md
├── README.md
└── TODO.md
```

## Comandos de setup (para P5)

```bash
# 1. Scaffold Next.js
npx create-next-app@latest <project-name> --typescript --tailwind --app --no-src-dir

# Ajustar a estructura con src/
# (Next pregunta interactivo, pero si querés src/ explicit:)
# npx create-next-app@latest <project-name> --typescript --tailwind --app --src-dir --use-npm

cd <project-name>

# 2. Animación + smooth scroll
npm i gsap @studio-freight/lenis

# 3. Imágenes / iconos
npm i lucide-react

# 4. Image processing (dev only)
npm i -D sharp

# 5. Configurar Tailwind para dark mode = class
#    Editar tailwind.config.ts: darkMode: 'class'
#    (la skill lo hace automáticamente en P6)

# 6. Crear estructura de carpetas
mkdir -p src/components src/hooks src/lib src/styles
mkdir -p public/sequences public/cta-images
mkdir -p scripts assets-raw
```

## Templates derivados

### BRIEF.md (custom para este patrón)

```markdown
# Brief — {{PROJECT_NAME}}

## Marca / producto
- **Marca**:
- **Producto**: (ej. soda artesanal, perfume, sneakers premium)
- **Descripción en 1-2 frases**:
- **CTA principal**: (ej. "Agregar al carrito", "Pre-order", "Suscribirme")

## Identidad visual
- **Modo default**: dark (recomendado por el patrón)
- **Theme color** (acento de la marca): #________
- **Paleta complementaria**:
- **Tipografía hero**: (bold, uppercase — sugerencia: Inter Black, Space Grotesk Bold)
- **Tipografía body**:

## Variantes a mostrar
| # | Nombre | Color de tema | Frames de sequence | Notas |
|---|---|---|---|---|
| 01 | Cherry | #B91C1C | 90 | |
| 02 | Grape | #6D28D9 | 90 | |
| 03 | Lemon | #CA8A04 | 90 | |

## Sequences (WebP)
- **Resolución**: 1920x1080 (desktop) + variante mobile 1080x1920
- **Frame rate equivalente**: 30fps si se quiere percepción de video
- **Cantidad de frames por variante**: 60-120 (más = más smooth, más peso)
- **Origen**: Runway Gen-4 / Kling / After Effects render — ver `prompts.md`
- **Optimizado a**: WebP quality 75, target <50KB/frame
```

### prompts.md (custom — combina sequences + CTAs)

```markdown
# Prompts — {{PROJECT_NAME}}

## Parte 1 · WebP sequence del hero (img→video, después extraer frames)

**Tool sugerido**: Runway Gen-4 (img-to-video) + ffmpeg para extracción.

### Variante 01 — {{FLAVOR_1}}

**Prompt para el frame inicial (img gen):**
```
Premium {{PRODUCT_TYPE}} of {{BRAND}} {{FLAVOR_1}} floating in the center of the frame on pure {{BG_COLOR}} background. Cinematic studio lighting, soft highlights on the metallic rim, slight forward tilt for a hero-shot angle. Sharp label details, no motion blur, full vertical frame.

STYLE: cinematic commercial, premium DTC aesthetic
BACKGROUND: {{BG_COLOR}}, no gradients
FRAMING: full vertical (9:16) for mobile, 16:9 for desktop
OUTPUT: high-resolution still, optimized for masking
```

**Prompt para el video (img→video):**
```
Animate the product with a slow rotation revealing all sides while {{INGREDIENT}} elements gradually burst around it. The motion progresses linearly with no easing. End frame: product centered with full ingredient burst. Pure {{BG_COLOR}} background, no additional effects.

Duration: 3 seconds (90 frames at 30fps)
Camera: locked, no movement
```

**Después extraer frames con ffmpeg:**
```bash
ffmpeg -i variant-01.mp4 -vf "scale=1920:1080" public/sequences/{{FLAVOR_1}}/frame-%04d.png
node scripts/optimize-frames.mjs public/sequences/{{FLAVOR_1}}
```

(Repetir para cada variante)

## Parte 2 · CTA product images (imagen fija para botones / detalle)

**Tool sugerido**: Midjourney v6+ o Flux.

**Prompt:**
```
Create a square CTA product image of {{BRAND}} {{FLAVOR}} in pop-art commercial style.

BACKGROUND: bold monochrome {{THEME_COLOR}}, smooth studio gradient, clean and minimal
PRODUCT POSITION: centered upright, crisp studio lighting, soft shadow underneath
SURROUNDING ELEMENTS: realistic glossy {{INGREDIENT}} piled across the width
AESTHETIC: vibrant pop-art, bright colors, high contrast, slightly reflective surface, clean edges
STYLE: simple, bold, color-blocked (no Memphis patterns, no decorative overlays)
MOOD: playful, modern, vibrant, clean

OUTPUT: 1:1 square, high resolution, transparent or {{THEME_COLOR}} background
```

## Glosario de variables

- `{{BRAND}}`: marca (Olipop, Liquid Death, etc.)
- `{{PRODUCT_TYPE}}`: "beverage can", "perfume bottle", "sneaker", "headphones"
- `{{FLAVOR_X}}`: nombre de la variante (Cherry, Grape, Lemon, etc.)
- `{{INGREDIENT}}`: ingrediente o elemento visual asociado (cherries, grapes, mint leaves, ice cubes)
- `{{BG_COLOR}}`: color del background del frame ("pure solid black #000000", "off-white #F5F5F0")
- `{{THEME_COLOR}}`: acento de la marca para esa variante
```

### TODO.md base (semilla para P7)

```markdown
# TODO — {{PROJECT_NAME}}

## Setup técnico
- [ ] Verificar que Next dev server arranca
- [ ] Configurar Tailwind dark mode = class
- [ ] Configurar Lenis en root layout
- [ ] Variables de tema (theme color por variante) en lib/variants.ts

## Brief y diseño
- [ ] Completar BRIEF.md
- [ ] Definir paleta y tipografía
- [ ] Storyboard de 3-5 frames clave por variante

## Assets — sequences
- [ ] Generar hero shot inicial con AI image gen (por variante)
- [ ] Generar img→video con Runway/Kling (por variante, 3s c/u)
- [ ] Extraer frames con ffmpeg
- [ ] Optimizar a WebP con scripts/optimize-frames.mjs (target <50KB/frame)
- [ ] Validar peso total <5MB por variante (para Vercel)

## Assets — CTA images
- [ ] Generar CTA square por variante con Midjourney/Flux
- [ ] Optimizar a WebP

## Componentes
- [ ] SequenceCanvas con scroll-to-frame mapping
- [ ] VariantNav (PREV / NEXT)
- [ ] ThemeToggle (dark / light)
- [ ] CTAButtons con estados hover
- [ ] Footer con sociales y links legales

## Performance
- [ ] Lighthouse > 90 en mobile
- [ ] Pre-cargar frames de la variante visible
- [ ] Lazy-load de variantes no activas

## Deploy
- [ ] Deploy a Vercel
- [ ] Custom domain
- [ ] OG image para link previews
```

### CLAUDE.md (extras a agregar sobre el base)

```markdown
## Patrón usado
Este proyecto se generó con el patrón `cinematic-product-landing`.
Ver `.charless/reference/project-patterns/cinematic-product-landing.md` en la skill para entender decisiones.

## Decisiones clave del patrón
- Next.js App Router (no Pages) para SSG del hero y SEO
- WebP sequences en `public/sequences/<flavor>/` — NO en src/ (deben ser servidas estáticas)
- Tailwind dark mode = class (no media), para que el toggle del usuario gane
- GSAP ScrollTrigger en lugar de IntersectionObserver puro (más control sobre frame mapping)
- Frames pre-renderizados — NO hacer render en runtime de la animación
```

## Notas para Claude al cargar este patrón

- **No preguntes el stack en P2/P3** — está fijado arriba. Solo confirmá: *"Voy con Next + Tailwind + GSAP + Lenis según el patrón. ¿OK o cambiamos algo?"*
- **No preguntes la arquitectura en P4** — está fijada arriba.
- **P5 sí preguntá el modo (Auto/Step/Manual)** y corré los comandos del patrón.
- **P6 usá los templates de este archivo**, no los genéricos.
- **P7 mostrá el TODO base de este archivo como semilla del modo C (Auto)**.
- Si el usuario quiere ALGO específico distinto al patrón (ej. usar Astro en vez de Next), respetá su elección y avisá: *"Salimos del patrón, vuelvo a P2 normal."*.

## Prompt original (referencia inmutable)

Este patrón se derivó del siguiente prompt aportado por el usuario en mayo 2026. Se preserva textual para futura consulta:

```
Website Prompt
Design a premium, single-page parallax website for a canned differents branda.

User Customization
Drink name (e.g. "Coca Cola")
Drink description (1–3 sentences)
Theme color (brand accent)
Dark or light mode
Multiple WebP background parallax image sequences (one sequence per drink variant)

Hero Layout & Visual Style
Create a full-screen hero section with this layout:

Background
The entire hero background is a WebP image sequence that fills the screen.
As the user scrolls down, the sequence plays forward; scrolling up reverses it.
This animation should feel cinematic and smooth.

Overlay Text Block (Left Side)
Below the logo: Large, bold, uppercase drink name (e.g. "CHERRY").
Under the name: smaller subtitle line, light font weight (e.g. "COLA").
Under the subtitle: a short descriptive paragraph.
Below the paragraph: two full rounded CTA buttons side by side (e.g. "ADD TO" and "CART").
Left button: transparent background, white text color.
Right button: solid background, black text.
All text overlays directly on top of the moving background.

Center Area
Keep the center visually clean and mostly empty of additional UI, so the animated background remains visible.

Right Side Variant Navigation
Vertically centered number representing current flavor index (01, 02, 03…).
Slim vertical navigation strip with:
- "PREV" label and arrow for previous flavor.
- Vertical divider line.
- "NEXT" label and arrow for next flavor.
Clicking PREV/NEXT switches drink variant (text, theme color, and WebP sequence).

Bottom Center
Small row of social icons (Twitter/X, Instagram, Facebook, etc.), minimal and monochrome.

Theme & Mode
Default: dark, cinematic look (near-black background, bright text).
Toggle for dark/light mode.
Dark: black/charcoal background, white/gray text.
Light: off-white background, dark text.
Apply theme color to CTAs, accents, active indicators, and subtle highlights.

Parallax Scroll Behavior
Map scroll position to frame index of WebP sequence.
Scrolling down advances frames.
Scrolling up reverses frames.
Animation tied to page scroll, not time-based autoplay.
Keep performance smooth and responsive.

Footer
Brand logo or name, Links (About, Contact, Privacy Policy, Terms), Social icons, Copyright text.
Consistent visual theme. Black background.

CTA Images (separate prompt for AI image gen):
Create a square CTA product image in the same style as the reference:
- Background: Bold monochrome color, smooth studio gradient, clean and minimal.
- Can Position: Centered and upright, crisp studio lighting, soft shadow.
- Surrounding Elements: Realistic, glossy ingredient piled across the width.
- Aesthetic: Vibrant pop-art — bright colors, high contrast, slightly reflective surface, clean edges.
- Style: Simple, bold, color-blocked (no Memphis patterns).
- Mood: Playful, modern, vibrant, clean.
```
