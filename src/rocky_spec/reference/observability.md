# Observabilidad — referencia canónica

> Seguridad responde "¿alguien está atacando esto?". Observabilidad responde **"¿esto está funcionando bien ahora mismo, y si no, por qué?"**. Sin esto, la única forma de enterarse de que algo se rompió en producción es que un usuario se queje.

## Índice

- [Cómo se usa este archivo](#cómo-se-usa-este-archivo)
- [Los 3 pilares](#los-3-pilares-de-la-observabilidad)
- [Error tracking](#error-tracking)
- [Logging estructurado](#logging-estructurado)
- [Health check endpoint](#health-check-endpoint)
- [Uptime monitoring](#uptime-monitoring)
- [Métricas básicas](#métricas-básicas)
- [Nivel de exigencia según escala del proyecto](#nivel-de-exigencia-según-escala-del-proyecto)

## Cómo se usa este archivo

- **P5.7 (Observabilidad)**: detección automática + resumen de decisiones, genera `OBSERVABILITY.md` y el código base del health check endpoint.
- **P6 (Genera archivos base)**: escribe `OBSERVABILITY.md` desde `.rocky-spec/templates/OBSERVABILITY.md.template`.
- **Modo Adopción (MA-1.7)**: health-check de observabilidad sobre el proyecto existente (¿hay error tracking? ¿hay endpoint de health? ¿los logs son estructurados?).

## Los 3 pilares de la observabilidad

| Pilar | Responde | Herramienta típica |
|---|---|---|
| **Logs** | ¿Qué pasó, exactamente, en este request/proceso? | Logger estructurado (JSON) + agregador (o el log del propio hosting) |
| **Métricas** | ¿Cuántos requests, cuánto tardan, cuántos fallan, en el tiempo? | Dashboard de la plataforma, o APM si el proyecto lo justifica |
| **Trazas** | ¿Por dónde pasó este request específico, entre qué servicios, cuánto tardó cada paso? | Solo relevante con 2+ servicios (microservicios, colas) — un monolito no lo necesita |

La mayoría de los proyectos que arman esta skill son monolitos chicos/medianos — **logs + métricas cubren el 90% de los casos**. Trazas distribuidas solo entran en juego si la arquitectura elegida en P4 ya tiene múltiples servicios.

## Error tracking

Captura excepciones no manejadas en producción con contexto (stack trace, request que la disparó, usuario si aplica) — sin esto, un error solo se nota si alguien lo reporta.

| Herramienta | Cuándo | Notas |
|---|---|---|
| [Sentry](https://sentry.io) | Default recomendado | Tier gratuito generoso, SDKs para casi todos los stacks, setup en minutos |
| Bugsnag / Rollbar | Alternativas válidas | Si el equipo ya las usa en otro proyecto |
| Nada (solo logs) | Prototipo/demo | Ver "Nivel de exigencia" — no vale la pena para algo descartable |

**Setup mínimo** (Node/Express de ejemplo, el patrón es igual en cualquier stack):
```javascript
Sentry.init({ dsn: process.env.SENTRY_DSN, environment: process.env.NODE_ENV });
app.use(Sentry.Handlers.errorHandler()); // después de las rutas, antes de otros error handlers
```

**El DSN es un secret** (aunque Sentry lo trate como semi-público) — va en `.env`, nunca hardcodeado. Ver `.rocky-spec/reference/security.md`.

## Logging estructurado

Reemplaza `console.log("texto")` por logs en JSON con campos consistentes — permite filtrar y buscar en producción en vez de leer texto suelto.

| Stack | Librería recomendada |
|---|---|
| Node/TypeScript | `pino` (rápido, JSON nativo) o `winston` (más config, más adoptado) |
| Python | `structlog` o `loguru` |
| Go | `log/slog` (nativo desde Go 1.21) o `zerolog` |
| Rust | `tracing` + `tracing-subscriber` |

**Formato mínimo**: `{ level, timestamp, message, ...contexto }` — ej. `logger.info({ userId, orderId }, "order created")`, nunca `console.log("order created for " + userId)`.

**Niveles**: `debug` (detalle de desarrollo, no en prod) → `info` (eventos normales) → `warn` (algo raro pero no rompió nada) → `error` (algo falló).

**Qué nunca loguear** (ver `.rocky-spec/reference/security.md`): passwords, tokens completos, números de tarjeta, cualquier secret. Si hace falta debuggear su presencia, loguear `Boolean(value)`, no el valor.

**Dónde van los logs en producción**: por default, a `stdout`/`stderr` — la plataforma de deploy (Render, Railway, Fly.io, Vercel) los captura y los muestra en su dashboard sin configuración extra. Un agregador dedicado (Datadog Logs, Better Stack, Axiom) solo se justifica cuando el volumen o la necesidad de búsqueda avanzada lo amerita — no es un default, es una escalada.

## Health check endpoint

Un endpoint que responde "estoy vivo y mis dependencias funcionan" — lo usan la plataforma de deploy (para saber si reiniciar el proceso), el load balancer (para saber si mandarle tráfico), y cualquier uptime monitor externo.

```javascript
app.get('/health', async (req, res) => {
  const checks = { database: await checkDatabase(), server: true };
  const healthy = Object.values(checks).every(Boolean);
  res.status(healthy ? 200 : 503).json({ status: healthy ? 'ok' : 'degraded', checks });
});
```

**Liveness vs. readiness** (relevante solo si el proyecto usa Kubernetes o un orquestador similar — la mayoría de los proyectos de esta skill no lo necesitan):
- **Liveness** (`/health/live`): ¿el proceso sigue corriendo? Si falla, el orquestador reinicia el contenedor.
- **Readiness** (`/health/ready`): ¿puede recibir tráfico ahora? Si falla, se lo saca del load balancer sin reiniciarlo (ej. mientras conecta a la DB al arrancar).

Para el caso común (deploy en Render/Railway/Fly.io sin Kubernetes), un solo `/health` que chequea las dependencias críticas alcanza.

## Uptime monitoring

Alguien (o algo) externo al proyecto que pregunte "¿está vivo?" cada X minutos y avise si deja de responder — sin esto, un servidor caído solo se nota cuando un usuario se queja.

| Opción | Costo | Notas |
|---|---|---|
| [UptimeRobot](https://uptimerobot.com) | Gratis (50 monitores) | El default más simple — pega la URL del `/health`, listo |
| [Better Stack](https://betterstack.com) | Freemium | Más completo, incluye status page pública |
| Dashboard nativo de la plataforma | Gratis, incluido | Render/Railway/Fly.io ya muestran si el servicio está caído — no siempre alertan proactivamente, revisar cada caso |

## Métricas básicas

Requests por minuto, latencia (p50/p95/p99), tasa de error — permiten ver una tendencia (ej. "la latencia viene subiendo hace 3 días") antes de que se vuelva una caída total.

| Nivel | Opción |
|---|---|
| Default (la mayoría de los proyectos) | Dashboard nativo de la plataforma de deploy — ya viene incluido, sin nada que instalar |
| Intermedio | Middleware liviano que loguea duración por request (se puede armar con la misma librería de logging de arriba) |
| Avanzado (solo si el proyecto lo justifica) | APM dedicado — Datadog, New Relic, o Grafana + Prometheus si es self-hosted |

**Default de la skill**: dashboard nativo de la plataforma. Escalar a APM dedicado es una decisión posterior, no algo que se configure el día 1 de un proyecto chico.

## Nivel de exigencia según escala del proyecto

Mismo espíritu que `.rocky-spec/reference/security.md` y `.rocky-spec/reference/versioning.md`:

| Escala | Ejemplo | Nivel de exigencia |
|---|---|---|
| Prototipo / demo | MVP para mostrar, sin usuarios reales | Nada de esto — ni vale la pena el setup |
| Producto real, pocos usuarios | SaaS chico, primeros usuarios pagos | Error tracking (Sentry) + logging estructurado + `/health` + uptime monitor gratuito |
| Producto con SLA / crítico | Algo que si se cae, duele (pagos, salud, infra de terceros) | Todo lo anterior + métricas con alerting activo + considerar APM dedicado + trazas si hay múltiples servicios |
