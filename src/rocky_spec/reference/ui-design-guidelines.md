# UI/UX Design Guidelines

Guía de referencia para P4.5 del flujo de `/rocky-spec`. Contiene estilos visuales, paletas por tipo de producto, pares tipográficos, y anti-patrones comunes. Basado en los principios de Apple HIG, Material Design 3, y patrones de productos reales.

---

## Estilos visuales disponibles

| Estilo               | Descripción breve                                          | Ideal para                            |
|----------------------|------------------------------------------------------------|---------------------------------------|
| **Minimal Clean**    | Blanco predominante, tipografía bold, espacio generoso     | SaaS, portfolios, blogs               |
| **Dark Tech**        | Dark mode, acentos neón/saturados, sensación de poder      | Dev tools, dashboards, startups tech  |
| **Glassmorphism**    | Fondos blur, layers translúcidas, profundidad visual       | Consumer apps, fintech, crypto        |
| **Warm Organic**     | Beige, terracota, verde sage, redondeado, cercano          | Wellness, food, lifestyle, ecommerce  |
| **Corporate Pro**    | Azul/gris, grid estricto, confiable, sin sorpresas         | B2B, legal, financiero, salud         |
| **Bold Brutalist**   | Colores llamativos, grids rotos, bordes visibles, raw      | Agencias creativas, portfolios, media |
| **Elegant Premium**  | Mucho whitespace, serif elegante, paleta contenida         | Lujo, moda, arquitectura, arte        |
| **Claymorphism**     | Sombras blandas, formas 3D suaves, colores pastel          | Apps mobile, kids, productos lúdicos  |
| **Neo-Brutalism**    | Bordes negros gruesos, fondos planos brillantes, sombras   | Startups disruptivas, fintechs        |
| **Neumorphism**      | Sombras internas/externas suaves, mismo color fondo/card   | Solo para elementos UI pequeños       |

---

## Paletas recomendadas por tipo de producto

### SaaS / Herramienta de productividad

**Tono minimal (recomendado):**
```
Primary:     #6366F1  (indigo-500)
Accent:      #10B981  (emerald-500)
Background:  #FFFFFF
Surface:     #F8FAFC  (slate-50)
Text:        #0F172A  (slate-900)
Text muted:  #64748B  (slate-500)
Border:      #E2E8F0  (slate-200)
```
Typography: Inter / DM Sans + body Inter

**Tono dark tech:**
```
Primary:     #818CF8  (indigo-400)
Accent:      #34D399  (emerald-400)
Background:  #0F0F0F
Surface:     #1A1A2E
Text:        #F1F5F9
Text muted:  #94A3B8
Border:      #1E293B
```
Typography: Space Grotesk + body Inter

---

### E-commerce / Tienda online

**Tono cálido (lifestyle/moda):**
```
Primary:     #C2855A  (terracota)
Accent:      #2D6A4F  (verde bosque)
Background:  #FDFAF6
Surface:     #F5EFE6
Text:        #1C1917  (stone-900)
Text muted:  #78716C  (stone-500)
Border:      #E7E5E4  (stone-200)
```
Typography: Playfair Display + body Lato

**Tono moderno/minimalista:**
```
Primary:     #000000
Accent:      #E11D48  (rose-600)
Background:  #FFFFFF
Surface:     #F9FAFB
Text:        #111827
Text muted:  #6B7280
Border:      #F3F4F6
```
Typography: Neue Haas Grotesk / Inter + body Inter

---

### Landing page / Marketing

**Tono startup vibrante:**
```
Primary:     #7C3AED  (violet-600)
Accent:      #F59E0B  (amber-500)
Background:  #FAFAFA
Surface:     #FFFFFF
Text:        #111827
Text muted:  #6B7280
Border:      #E5E7EB
```
Typography: Plus Jakarta Sans + body Inter

**Tono corporate confiable:**
```
Primary:     #1D4ED8  (blue-700)
Accent:      #0EA5E9  (sky-500)
Background:  #FFFFFF
Surface:     #F0F9FF
Text:        #0F172A
Text muted:  #475569
Border:      #CBD5E1
```
Typography: Lexend / Inter + body Inter

---

### Dashboard / Admin panel

```
Primary:     #2563EB  (blue-600)
Accent:      #10B981  (emerald-500)
Warning:     #F59E0B
Background:  #F1F5F9  (slate-100)
Surface:     #FFFFFF
Text:        #1E293B
Text muted:  #64748B
Border:      #E2E8F0
Sidebar bg:  #0F172A  (slate-900)
Sidebar text:#CBD5E1
```
Typography: Inter (toda la UI — sin serif en dashboards)

---

### Portfolio / Marca personal

**Tono creativo/bold:**
```
Primary:     #FF3B00  (naranja intenso)
Accent:      #0047AB  (azul cobalto)
Background:  #F5F5F0  (off-white cálido)
Surface:     #EBEBEB
Text:        #1A1A1A
Text muted:  #6E6E6E
Border:      #D4D4D4
```
Typography: DM Serif Display + body DM Sans

**Tono elegante/premium:**
```
Primary:     #1A1A1A
Accent:      #B8A06A  (dorado suave)
Background:  #FAFAF8
Surface:     #F0EFEB
Text:        #1A1A1A
Text muted:  #888888
Border:      #E0DED8
```
Typography: Cormorant Garamond + body Montserrat

---

## Pares tipográficos recomendados

| Heading              | Body            | Tono           | Google Fonts |
|----------------------|-----------------|----------------|--------------|
| Space Grotesk        | Inter           | Tech / moderno | ✅ ambas      |
| Plus Jakarta Sans    | Plus Jakarta Sans| SaaS vibrante  | ✅            |
| DM Serif Display     | DM Sans         | Elegante/editorial| ✅          |
| Playfair Display     | Lato            | Premium/fashion| ✅ ambas      |
| Sora                 | Sora            | Minimal limpio | ✅            |
| Cormorant Garamond   | Montserrat      | Lujo silencioso| ✅ ambas      |
| Fraunces             | Libre Franklin  | Orgánico/editorial| ✅         |
| Clash Display        | Inter           | Bold/startup   | Clash: CDN   |
| Cabinet Grotesk      | Satoshi         | Neo-modern     | CDN ambas    |

---

## Anti-patrones por tipo de producto

### Anti-patrones universales (nunca hacer)
- ❌ Íconos emoji como elementos de UI (🎨 🚀 ⚙️) — usar SVG: Lucide, Heroicons, Phosphor
- ❌ `box-shadow: 0 4px 20px rgba(0,0,0,0.5)` — sombra negra opaca, parece 2012
- ❌ Hero section con gradiente `#667eea → #764ba2` (el gradiente por defecto de IA)
- ❌ Grid de 3 features cards idénticas con ícono + título + 2 líneas de texto
- ❌ Sección "How it works" con pasos numerados en círculo
- ❌ Testimonials genéricos con avatar placeholder gris
- ❌ Footer con 4 columnas iguales siempre
- ❌ CTA button con gradiente horizontal (a menos que sea parte del design system)
- ❌ Animaciones de fade-in en scroll en absolutamente todos los elementos
- ❌ Texto blanco sobre imagen con un overlay oscuro semitransparente sin ajuste de contraste
- ❌ Más de 2 fuentes distintas en el mismo proyecto
- ❌ `font-size` menor a 16px para body text
- ❌ Mezclar border-radius distintos sin sistema (4px en un lado, 12px en otro, 50% en otro)

### Anti-patrones específicos por tipo

**SaaS:**
- ❌ Pricing section con 3 planes donde el del medio está "highlighted" con el mismo gradiente genérico
- ❌ Dashboard mockup con datos inventados que no tienen coherencia entre sí
- ❌ "Trusted by 10,000+ companies" sin logos reales

**E-commerce:**
- ❌ Product cards con sombra en hover que hace que "floten" dramáticamente
- ❌ Botón "Add to cart" con el mismo estilo que todos los demás botones
- ❌ Rating con estrellas SVG pero sin número de reviews

**Landing:**
- ❌ Video de fondo en autoplay con texto blanco encima (accesibilidad)
- ❌ Countdown timer falso para crear urgencia
- ❌ Social proof genérico: "⭐⭐⭐⭐⭐ Amazing product!" sin nombre ni empresa

**Dashboard:**
- ❌ Gráficos con colores aleatorios sin palette consistente
- ❌ Tablas con bordes en cada celda (prefer row dividers only)
- ❌ Sidebar con 15+ items al mismo nivel jerárquico

---

## Reglas de accesibilidad — mínimo indispensable

### Contraste
- Texto normal (< 18px): mínimo **4.5:1** contra el fondo
- Texto grande (≥ 18px bold o ≥ 24px regular): mínimo **3:1**
- Elementos UI (iconos, bordes de inputs): mínimo **3:1**
- Herramienta: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Pairs de contraste que NO cumplen WCAG AA
- ❌ Gris `#A0A0A0` sobre blanco → ratio 3.95:1 (falla texto normal)
- ❌ Amarillo `#FFD700` sobre blanco → ratio 1.07:1 (falla todo)
- ❌ Verde `#00CC00` sobre blanco → ratio 2.52:1 (falla texto normal)
- ✅ Slate-600 `#475569` sobre blanco → ratio 5.32:1 (pasa)
- ✅ Cualquier color sobre negro → verificar individualmente

### Touch targets
- Mínimo 44×44px para elementos clickeables/tapables
- Si el ícono es más chico, expandir el área de click con padding

### Otros mínimos
- `lang="es"` (o el idioma correcto) en el tag `<html>`
- Alt text en todas las imágenes que transmiten información
- `aria-label` en botones que solo tienen ícono
- Focus ring visible en todos los elementos interactivos
- No usar color como único indicador de estado (agregar ícono o texto)

---

## Espaciado — sistema base-8

```
4px  → micro (separación entre label e input)
8px  → pequeño (padding interno de badges, gap entre ícono y texto)
12px → compacto (padding de inputs, gap en listas densas)
16px → base (padding cards chicas, gap entre elementos)
24px → cómodo (padding cards normales, gap entre secciones internas)
32px → amplio (padding secciones, gap entre cards)
48px → sección (espacio entre bloques mayores)
64px → bloque (padding top/bottom de secciones en landing)
96px → hero (espacio en secciones hero, separación dramática)
128px → monumental (solo en layouts muy abiertos)
```

Regla: **todos los valores de margin/padding/gap deben ser múltiplos de 4**. Si algo "no cuadra" visualmente, revisar si hay valores que rompan el sistema.

---

## Border radius y elevación (sombras)

**Border radius** — elegir UNA escala y ser consistente en todo el proyecto (no mezclar 4px en un lado y 12px en otro sin sistema):

| Escala | Valores | Cuándo |
|---|---|---|
| Sharp (Brutalist, Dark Tech) | 0 · 2px · 4px | Estética angular, técnica |
| Standard (la mayoría de los estilos) | 4px · 8px · 12px · 16px | Default seguro para SaaS, dashboards, landings |
| Soft (Claymorphism, apps lúdicas) | 16px · 24px · 9999px (pill) | Cuando el tono es cálido/amigable |

**Sombras / elevación** — sistema de 3-4 niveles, sombras tenues con color (nunca negro opaco):

```
--shadow-sm:  0 1px 2px rgba(15, 23, 42, 0.06)                    /* inputs, botones */
--shadow-md:  0 4px 8px rgba(15, 23, 42, 0.08)                    /* cards en reposo */
--shadow-lg:  0 12px 24px rgba(15, 23, 42, 0.12)                  /* cards en hover, dropdowns */
--shadow-xl:  0 24px 48px rgba(15, 23, 42, 0.16)                  /* modales, popovers */
```

En Dark Tech/Glassmorphism, reemplazar el color de sombra por un tono oscuro saturado del acento (ej. `rgba(99, 102, 241, 0.15)`) en vez de negro puro — da sensación de "glow" en vez de "mancha".

## Breakpoints — sistema responsive

Estándar recomendado (mobile-first, coincide con Tailwind por default):

| Nombre | Ancho mínimo | Dispositivo típico |
|---|---|---|
| `sm` | 640px | Mobile grande / phablet |
| `md` | 768px | Tablet |
| `lg` | 1024px | Laptop |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Desktop grande |

Diseñar mobile-first: estilos base para mobile, `min-width` media queries para agrandar. Evitar diseñar desktop-first y "apretar" para mobile — casi siempre se nota.

## Iconografía

- **Librería recomendada por default**: Lucide (consistente, liviana, buena cobertura). Alternativas válidas: Heroicons (si el stack ya usa Tailwind UI), Phosphor (más variedad de pesos visuales).
- **Nunca emoji como ícono de UI** (🚀 ⚙️ 🎨) — no escalan, no se puede controlar el color/peso, y se ven distinto entre sistemas operativos.
- **Tamaño estándar**: 16px (inline con texto), 20px (default en botones/inputs), 24px (íconos standalone, nav).
- **Peso consistente**: elegir stroke-width (1.5 o 2) y mantenerlo en todo el proyecto — no mezclar íconos outline con filled sin criterio.

## Estados de componente

Todo componente interactivo (botón, input, card clickeable, link) necesita definir estos estados — no dejarlo librado al default del navegador/framework:

| Estado | Qué cambia | Ejemplo |
|---|---|---|
| **Default** | Estado de reposo | — |
| **Hover** | Señal de interactividad (desktop) | Oscurecer/aclarar 8-10%, o levantar sombra |
| **Focus** | Accesibilidad — navegación por teclado | Ring visible de 2px, color de acento, `outline-offset` |
| **Active** | Feedback al hacer click/tap | Oscurecer más que hover, o `scale(0.98)` |
| **Disabled** | No interactivo | Opacidad 40-50%, `cursor: not-allowed`, sin hover/focus |
| **Loading** | Acción en curso | Spinner o skeleton, deshabilitar re-click |
| **Error** | Validación fallida (inputs) | Borde rojo + mensaje, nunca solo el color (ver accesibilidad) |

## Motion — principios de animación

- **Timing**: 150-250ms para micro-interacciones (hover, focus, toggles), 300-500ms para transiciones de entrada/salida de elementos grandes (modales, drawers). Más de 500ms se siente lento para UI.
- **Easing**: `ease-out` para elementos que entran (empiezan rápido, terminan suave), `ease-in` para elementos que salen. Evitar `linear` salvo en loaders/progress bars.
- **Qué animar**: entradas de contenido (`whileInView` una sola vez, no en cada scroll), cambios de estado (hover/focus/active), transiciones de ruta. **Qué NO animar**: el elemento LCP de la página (bloquea el paint), texto largo completo (solo el contenedor), absolutamente todo al hacer scroll (fatiga visual).
- **Respeto a `prefers-reduced-motion`**: las animaciones no esenciales (decorativas) deben desactivarse o reducirse si el usuario tiene esta preferencia activada en su sistema.

---

## Cómo usar este archivo en P4.5

1. Identificar el tipo de producto del usuario
2. Identificar el tono deseado
3. Buscar la paleta correspondiente en este archivo
4. Si la combinación tipo+tono no está exactamente definida, interpolar: tomar la paleta del tipo más cercano y ajustar el tono
5. Seleccionar el par tipográfico que mejor encaje
6. Listar 3-5 anti-patrones específicos para ese producto
7. Completar `.rocky-spec/templates/MASTER.md.template` con los tokens de radios/sombras, breakpoints, iconografía, estados de componente y principios de motion de este archivo — son los mismos para todos los proyectos salvo que el tono elegido sugiera una variante (ver notas de Dark Tech/Glassmorphism en "Border radius y elevación")
7. Generar el design-system/MASTER.md con esos valores
