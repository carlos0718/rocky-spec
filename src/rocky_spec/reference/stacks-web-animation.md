# Stacks de animación web — Three.js, R3F, GSAP y compañía

Este archivo lo usa `/rocky-spec` para proyectos **híbridos** (web + motion/3D avanzado) o cuando un proyecto de código necesita animaciones más serias que Framer Motion.

## 3D web

| Stack | Comando | Cuándo |
|---|---|---|
| Three.js (vanilla) | `npm i three @types/three` | Control total, sin React |
| React Three Fiber (R3F) | `npm i three @react-three/fiber` | Three.js dentro de React |
| drei (helpers para R3F) | `npm i @react-three/drei` | OrbitControls, environment, gltf loader, etc. |
| R3F postprocessing | `npm i @react-three/postprocessing` | Bloom, DOF, glitch effects |
| R3F XR (VR/AR) | `npm i @react-three/xr` | WebXR |
| Theatre.js | `npm i @theatre/core @theatre/studio` | Animaciones keyframed visuales para R3F |
| Spline (React) | `npm i @splinetool/react-spline @splinetool/runtime` | 3D no-code, exportado de Spline app |
| Babylon.js | `npm i @babylonjs/core` | Alternativa a Three.js, más game-engine |
| PlayCanvas | usar via web editor | 3D con editor visual |

## Combo recomendado por nivel

**Principiante en 3D web** → Spline + React. Modelás visualmente en Spline app y lo embebés.

**Intermedio** → R3F + drei. La curva es razonable y la documentación es buena.

**Avanzado** → Three.js puro o R3F + shaders custom (GLSL).

## Animación 2D / motion en web

| Stack | Comando | Cuándo |
|---|---|---|
| GSAP | `npm i gsap` | Timeline-based, el más maduro del mercado |
| GSAP ScrollTrigger | viene con GSAP | Animaciones disparadas por scroll |
| GSAP MorphSVG / DrawSVG | viene con GSAP (Club plugins) | Animar paths SVG |
| Framer Motion | `npm i framer-motion` | Animaciones declarativas en React |
| Anime.js | `npm i animejs` | Liviano, alternativa a GSAP |
| Motion One | `npm i motion` | API moderna basada en Web Animations API |
| Auto-Animate | `npm i @formkit/auto-animate` | Animaciones automáticas de entrada/salida |

## Lottie y vector

| Stack | Comando | Cuándo |
|---|---|---|
| Lottie (React) | `npm i lottie-react` | Animaciones exportadas de After Effects |
| Lottie web (vanilla) | `npm i lottie-web` | Sin React |
| dotLottie | `npm i @lottiefiles/dotlottie-react` | Formato comprimido nuevo |

## Interactivo / state machines

| Stack | Comando | Cuándo |
|---|---|---|
| Rive | `npm i @rive-app/react-canvas` | Animaciones interactivas con state machines (alternativa moderna a Lottie) |

## 2D acelerado por GPU

| Stack | Comando | Cuándo |
|---|---|---|
| PIXI.js | `npm i pixi.js` | 2D con WebGL, juegos y visuals |
| p5.js | `npm i p5` | Creative coding, generativo, prototipado rápido |
| Konva | `npm i konva react-konva` | Canvas 2D declarativo |
| Two.js | `npm i two.js` | SVG/Canvas 2D simple |

## Shaders y bajo nivel

| Stack | Comando | Cuándo |
|---|---|---|
| GLSL (escribir shaders) | sin install, archivos `.glsl` o strings inline | Custom effects, post-processing |
| react-three-shader-material | `npm i three-custom-shader-material` | Helpers para shaders en R3F |
| TSL (Three.js Shading Language) | viene con three | Shaders en JS, compila a WGSL/GLSL |
| Lygia (shader library) | importar from CDN | Funciones GLSL reutilizables |

## Audio reactivo / visualización

| Stack | Comando | Cuándo |
|---|---|---|
| Tone.js | `npm i tone` | Audio en navegador, sintetizado |
| Web Audio API | nativo | Análisis de frecuencias para visualizers |
| Meyda | `npm i meyda` | Feature extraction (BPM, MFCC, etc.) |

## Físicas

| Stack | Comando | Cuándo |
|---|---|---|
| Rapier (R3F) | `npm i @react-three/rapier` | Físicas rápidas en 3D |
| Cannon.js (R3F) | `npm i @react-three/cannon` | Alternativa más madura |
| Matter.js | `npm i matter-js` | 2D físicas (no 3D) |

## Asset pipeline típico (3D web)

```
Blender / Cinema 4D / Spline
        ↓ (export)
GLTF / GLB (3D models, optimizado para web)
        ↓
public/models/<name>.glb
        ↓
useGLTF de drei lo carga en R3F
```

Para texturas: exportar a `.hdr` (environment), `.ktx2` (comprimida) o `.webp`.

Tools para optimizar GLB: `gltfpack`, `gltf-transform`, gltf-pipeline.

## Combo sugerido por tipo de proyecto híbrido

**Landing con un objeto 3D rotando + scroll**
- Vite + React + R3F + drei + GSAP ScrollTrigger

**Portfolio inmersivo con varias escenas**
- Next.js + R3F + drei + GSAP + Theatre.js (para coreografía)

**Visualización audio-reactiva**
- Vite + R3F + drei + Tone.js + custom shaders

**Web inmersiva con interactivos no-code**
- Next.js + Spline (no-code 3D) + Framer Motion

**Producto con vista 3D interactiva** (e-commerce)
- Vite + R3F + drei + postprocessing (bloom para hero shot)

## Libre / custom

Si el usuario quiere una librería no listada, pedir el comando y agregar al setup.
