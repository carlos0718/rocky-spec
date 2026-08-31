# Stacks creativos — tools por categoría

Este archivo lo usa `/charless-ia` cuando el tipo elegido en P1 es **creativo**. A diferencia del stack de código, acá no hay `npm install`: son herramientas externas que el usuario abre. La skill recomienda combinaciones, no las instala.

## Pipeline típico de un video ad de producto

```
AI image gen (hero shot, key visuals)
        ↓
AI video gen (img → video, transiciones)
        ↓
Editor (cortes, audio, color, exports)
```

## AI image generation

| Tool | Fortalezas | Notas |
|---|---|---|
| Midjourney | Estética cinematográfica, branding | Vía Discord o web; sin API pública oficial |
| Flux (Pro / Dev / Schnell) | Foto-realismo, tipografía decente | Open source (Dev/Schnell), local con ComfyUI |
| Krea | Real-time gen, Flux + tools | Buena UX para iteración |
| Ideogram | Tipografía dentro de imagen | Logos y posters |
| ChatGPT image (DALL-E / GPT-image) | Edición conversacional | Integración con ChatGPT |
| Leonardo | Modelos custom, control fino | Comunidad con presets |
| Recraft | Vectores, ilustración | Para UI y branding |

## AI video generation

| Tool | Modo | Notas |
|---|---|---|
| Runway Gen-4 | img→video, text→video | Estándar de la industria para spots |
| Kling | img→video | Calidad alta, control de movimiento |
| Hailuo / MiniMax | img→video | Buen movimiento facial y de cámara |
| Pika | img→video, lip sync | Iteración rápida |
| Luma Dream Machine | img→video | Cámaras dinámicas |
| Sora (OpenAI) | text→video | Disponibilidad limitada |
| Veo (Google) | text→video | Calidad alta, acceso via Vertex/Gemini |
| Higgsfield | img→video con cámara control | Movimientos de cámara específicos |

## Editores de video

| Categoría | Tools |
|---|---|
| Pro completo | DaVinci Resolve (free + Studio), Premiere Pro, Final Cut Pro |
| Ágil / social | CapCut (desktop y mobile), DaVinci Resolve, InShot |
| Open source | Kdenlive, OpenShot, Olive |

DaVinci Resolve es la recomendación default para alguien empezando porque la versión free es muy potente y el color es el mejor del mercado.

## Motion design / compositing

| Tool | Fortalezas |
|---|---|
| After Effects | Standard de motion design, plugins infinitos |
| Cavalry | Procedural motion, más rápido para gráficos generativos |
| Motion (Apple) | Para usuarios de FCP |
| Fusion (dentro de DaVinci) | Compositing node-based |
| Nuke | Compositing pro (cine), node-based |
| Lottie + LottieFiles | Export de AE a JSON para web/app |

## 3D / render

| Tool | Cuándo |
|---|---|
| Blender | Default open source, todo-en-uno (model + animate + render) |
| Cinema 4D | Motion design pro, integración con AE |
| Maya | Animación de personajes, pipeline cine |
| Houdini | VFX procedural, simulaciones |
| Spline | 3D web-first, no-code, exporta a React |
| Three.js (código) | Ver stacks-web-animation.md |

## Audio

| Tool | Cuándo |
|---|---|
| Audacity | Edición simple, free |
| Adobe Audition | Pro, limpieza, mastering |
| Logic Pro | Música y diseño sonoro |
| Ableton | Música electrónica, sound design |
| ElevenLabs | TTS y voice clone |
| Suno / Udio | AI music gen |

## Color / grading

| Tool | Notas |
|---|---|
| DaVinci Resolve | El mejor en la categoría, integrado al editor |
| Baselight | Cine pro |
| FilmConvert | Plugin con looks de película |
| LUTs custom | Para mantener consistencia de marca |

## Upscale / restore

| Tool | Cuándo |
|---|---|
| Topaz Video AI | Upscale de clips de baja resolución |
| Topaz Photo AI | Upscale de imágenes |
| Magnific | Upscale con detalle generativo |
| Krea Enhance | Upscale + restyle |

## Combos sugeridos por caso de uso

**Video ad de producto (estética DTC, vertical para social)**
- AI image: Midjourney o Flux para hero shot
- AI video: Runway Gen-4 o Kling para img→video
- Editor: CapCut o DaVinci Resolve
- Audio: música de Suno o licencia (Artlist / Epidemic), SFX de Splice

**Motion piece corto (10–15s) para branding**
- AI image: Midjourney o Flux para key visuals
- Motion: After Effects para layout y animación
- 3D si aplica: Blender o Cinema 4D
- Editor final: Premiere o DaVinci

**Social content batch (Reels semanal)**
- AI image: Krea para iteración rápida
- AI video: Pika o Kling
- Editor: CapCut (mobile o desktop)

**Producto con animación 3D web** → ver stacks-web-animation.md (esto es híbrido, no creativo puro).

## Libre / custom

Si el usuario usa una herramienta no listada, preguntar y agregarla a su `profile.md` para futuras ejecuciones.
