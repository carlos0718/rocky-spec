# Observability — spec-charless

> Generado por skill `charless-ia` · Ver `.charless/reference/observability.md` de la skill para el detalle completo de cada decisión. Documento vivo — se actualiza cada vez que cambia una decisión de observabilidad, con su línea en "Historial de cambios".
>
> Seguridad (`SECURITY.md`) responde "¿alguien está atacando esto?". Este archivo responde **"¿esto está funcionando bien ahora mismo, y si no, por qué?"**.

## Nivel de exigencia de este proyecto

- **Escala**: Prototipo/demo — es un CLI de uso local, no un servicio en producción; error tracking/uptime no aplican en el sentido tradicional <!-- Prototipo/demo | Producto real, pocos usuarios | Producto con SLA/crítico -->

## Decisiones de este proyecto

| Área | Decisión |
|---|---|
| **Error tracking** | Sentry |
| **Logging** | print()/click.echo() por ahora — sin logging estructurado, no lo justifica el tamaño del proyecto todavía — formato JSON, niveles debug/info/warn/error |
| **Dónde van los logs** | stdout, capturado por la plataforma de deploy |
| **Health check** | `no aplica — no es un servidor` — chequea: no aplica <!-- ej. conexión a DB --> |
| **Uptime monitoring** | no configurado |
| **Métricas** | dashboard nativo de la plataforma |

## Setup

- [ ] Variable de entorno `SENTRY_DSN` configurada en `.env` y en la plataforma de deploy (ver `SECURITY.md` gestión de secrets)
- [ ] Logger estructurado inicializado (`print()/click.echo() por ahora — sin logging estructurado, no lo justifica el tamaño del proyecto todavía`)
- [ ] Endpoint `no aplica — no es un servidor` respondiendo antes del primer deploy
- [ ] Uptime monitor apuntando a `no aplica — no es un servidor` en producción (si aplica según nivel de exigencia)

## Qué nunca loguear

Passwords, tokens completos, números de tarjeta, cualquier secret — ver `.charless/reference/security.md` de la skill. Si hace falta debuggear la presencia de un valor sensible, loguear `Boolean(valor)`, nunca el valor.

---

## Historial de cambios

| Fecha | Cambio | Commit |
|-------|--------|--------|
| 2026-08-31 | Observability inicial (P5.7) | `a855f64` |
