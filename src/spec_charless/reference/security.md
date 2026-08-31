# Seguridad — referencia canónica

> Este archivo es la fuente de verdad para las prácticas de seguridad que la skill `charless-ia` aplica al generar y adoptar proyectos. Es a seguridad lo que `coding-principles.md` es a Clean Code y `ui-design-guidelines.md` es a diseño.

## Índice

- [Cómo se usa este archivo](#cómo-se-usa-este-archivo)
- [OWASP Top 10 adaptado](#owasp-top-10-adaptado) — qué es cada riesgo, cómo lo mitiga la skill
- [Reglas base — siempre activas](#reglas-base--siempre-activas)
- [Gestión de secrets y variables de entorno](#gestión-de-secrets-y-variables-de-entorno)
- [Auth — patrones según stack](#auth--patrones-según-stack)
- [CORS y security headers](#cors-y-security-headers)
- [Rate limiting](#rate-limiting)
- [Dependency scanning](#dependency-scanning)
- [Reglas por tipo de proyecto](#reglas-por-tipo-de-proyecto)
- [Nivel de exigencia según escala del proyecto](#nivel-de-exigencia-según-escala-del-proyecto)

## Cómo se usa este archivo

- **P5.6 (Seguridad)**: la skill hace las preguntas mínimas necesarias (tipo de proyecto, tiene auth, maneja datos de usuarios) y arma la sección de seguridad de `SECURITY.md` consultando este archivo.
- **P6 (Genera archivos base)**: rellena `SECURITY.md` desde `.charless/templates/SECURITY.md.template` con las decisiones tomadas en P5.6.
- **Modo Adopción (MA-1.6)**: corre un health-check de seguridad sobre el código existente (secrets hardcodeados, `.env` sin gitignorar, deps con vulnerabilidades conocidas) y lo reporta junto al health-check de code smells (MA-1.5).
- **`CONSTITUTION.md` del proyecto**: el Artículo 6 (Boundaries) ya incluye "no commitear secrets" como regla "Nunca" — `SECURITY.md` es donde vive el resto de las decisiones y el checklist completo.

## OWASP Top 10 adaptado

No todos los proyectos necesitan mitigar los 10 con el mismo rigor — un script interno no es un e-commerce. La tabla marca cuáles son **base** (siempre, para cualquier proyecto con backend) y cuáles son **si aplica** (según lo que el proyecto maneje).

| # | Riesgo | Qué es | Cómo lo mitiga la skill | ¿Cuándo aplica? |
|---|---|---|---|---|
| A01 | Broken Access Control | Un usuario accede a datos/acciones que no le corresponden (ej. `/api/users/123` sin verificar que el 123 sea el usuario logueado) | Middleware de autorización en cada endpoint que toque datos de usuario, no solo autenticación. Nunca confiar en IDs que vienen del cliente sin verificar ownership. | **Base** — cualquier proyecto con auth |
| A02 | Cryptographic Failures | Datos sensibles sin cifrar (passwords en texto plano, HTTP en vez de HTTPS, tokens débiles) | Passwords siempre hasheados (bcrypt/argon2, nunca MD5/SHA1 solos). HTTPS obligatorio en producción (lo fuerza la plataforma de deploy). | **Base** — cualquier proyecto con datos de usuario |
| A03 | Injection | SQL/NoSQL/command injection — inputs del usuario ejecutados como código | ORM/query builder con parámetros (nunca concatenar strings en queries). Validación de input en el borde (ver sección Auth/CORS). | **Base** — cualquier proyecto con DB o que ejecute comandos |
| A04 | Insecure Design | Falta de threat modeling — el problema de seguridad está en el diseño, no en un bug puntual | Se conversa en P5.6: ¿qué pasa si alguien intenta abusar de esta feature? (ej. rate limiting en signup para evitar spam de cuentas) | Si aplica — proyectos con lógica de negocio sensible (pagos, cuentas, límites de uso) |
| A05 | Security Misconfiguration | Headers de seguridad faltantes, CORS mal configurado, debug mode en producción, mensajes de error verbosos | Security headers por default (ver sección CORS/headers). `NODE_ENV=production` desactiva stack traces expuestos. | **Base** — cualquier proyecto con backend |
| A06 | Vulnerable and Outdated Components | Dependencias con CVEs conocidos sin parchear | Dependency scanning configurado en CI (ver sección Dependency scanning) | **Base** — cualquier proyecto de código |
| A07 | Identification and Authentication Failures | Passwords débiles permitidos, sin límite de intentos de login, sesiones que no expiran | Política mínima de password, rate limiting en `/login` y `/signup`, expiración de tokens/sesiones | **Base** — cualquier proyecto con auth |
| A08 | Software and Data Integrity Failures | CI/CD sin verificación de integridad, dependencias de fuentes no confiables | `package-lock.json`/`poetry.lock`/equivalente siempre commiteado (reproducibilidad), no instalar paquetes fuera de los registries oficiales | **Base** — cualquier proyecto de código |
| A09 | Security Logging and Monitoring Failures | No hay forma de detectar un ataque en curso o post-mortem | Logs estructurados (ya cubierto en `coding-principles.md`) + no loguear datos sensibles (passwords, tokens, tarjetas) en texto plano | **Base** — cualquier proyecto con backend |
| A10 | Server-Side Request Forgery (SSRF) | El backend hace requests a URLs controladas por el usuario sin validar destino | Si el proyecto acepta URLs de usuario (webhooks, importadores, proxies) → whitelist de dominios permitidos, nunca fetch directo a input crudo | Si aplica — solo proyectos que hacen requests salientes basados en input del usuario |

## Reglas base — siempre activas

Estas aplican a **cualquier proyecto con backend**, sin importar el perfil del usuario — igual que las reglas base de `coding-principles.md`:

- **Nunca secrets en el repo** — `.env` en `.gitignore` desde el primer commit, nunca API keys/tokens hardcodeados en el código.
- **Passwords siempre hasheados** — bcrypt (`bcryptjs`/`bcrypt`) o argon2, nunca en texto plano ni con hash reversible.
- **Validación de input en el borde** — middleware/decorador de validación (Zod, class-validator, Pydantic) antes de que el input llegue a la lógica de negocio.
- **HTTPS obligatorio en producción** — lo garantiza la plataforma de deploy (Render, Vercel, Fly.io, etc. lo hacen por default); verificar que no haya `http://` hardcodeado en configs.
- **Dependency scanning en CI** — ver sección dedicada abajo.
- **`.env.example` sin valores reales** — placeholders o valores dummy, nunca copiar-pegar el `.env` real con los `#` sacados.

Si el usuario pide explícitamente desactivar alguna para un proyecto puntual (ej. un prototipo interno de un día), confirmar antes:
> "Por default este proyecto va a tener [regla] activa (regla base de seguridad, no del perfil). ¿Querés que la desactive para este prototipo puntual?"

## Gestión de secrets y variables de entorno

- **Desarrollo local**: `.env` (gitignorado) + `.env.example` (commiteado, sin valores reales) — ya cubierto en P5.5.
- **CI**: secrets de GitHub Actions / GitLab CI (nunca hardcodeados en el YAML del workflow).
- **Producción**: el panel de secrets de la plataforma de deploy elegida (Render Environment Groups, Vercel Environment Variables, Fly.io secrets, AWS Secrets Manager / Parameter Store si es AWS).
- **Rotación**: si un secret se filtra accidentalmente (commit, log, error verboso), rotarlo inmediatamente — no alcanza con borrarlo del código, sigue válido hasta que se regenere del lado del proveedor.
- **Nunca loguear secrets** — ni completos ni parciales. Si hace falta debuggear, loguear solo si la variable existe (`Boolean(process.env.API_KEY)`), no su valor.

## Auth — patrones según stack

| Patrón | Cuándo | Notas |
|---|---|---|
| JWT stateless | APIs, SPAs, mobile | Expiración corta (15-60 min) + refresh token, o expiración media (7 días) sin refresh si el proyecto es simple. Firmar con `jose` o `jsonwebtoken`, nunca decodificar sin verificar la firma. |
| Sessions + cookie | Server-rendered (Rails, Django, Next.js con SSR) | Cookie `httpOnly`, `secure` (solo HTTPS), `sameSite: strict` o `lax`. |
| OAuth / social login | Cuando el usuario no quiere manejar passwords propios | Delegar a un provider (Auth0, Clerk, Supabase Auth, o el OAuth nativo de Google/GitHub) en vez de implementar el flow a mano, salvo que el proyecto lo pida explícitamente como aprendizaje. |
| API keys | Servicio-a-servicio, integraciones | Hashear igual que un password si se guardan en DB (nunca en texto plano), permitir revocación individual. |

**Regla transversal**: nunca implementar el hasheo de passwords o la verificación de JWT "a mano" (reinventar crypto) — usar las librerías estándar del ecosistema (`bcryptjs`, `jose`, `jsonwebtoken`, `passport`, `next-auth`, etc.).

## CORS y security headers

**CORS**: el origin permitido es **siempre explícito**, nunca `*` en producción si hay cookies o auth de por medio:

```
# Desarrollo
origin: 'http://localhost:5173'

# Producción — el dominio real del frontend, no un wildcard
origin: 'https://miapp.com'
```

**Security headers** (via `helmet` en Express/Fastify/NestJS, o headers nativos en Next.js/otros frameworks):

- `Content-Security-Policy` — al menos una política base, restrictiva por default
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (o `SAMEORIGIN` si el proyecto necesita ser embebido)
- `Strict-Transport-Security` — forzar HTTPS en el navegador

## Rate limiting

- **Base**: rate limiting en endpoints de auth (`/login`, `/signup`, `/forgot-password`) — previene brute-force y spam de cuentas. Librerías: `express-rate-limit`, `fastify-rate-limit`, o el rate limiting nativo de la plataforma (Cloudflare, Vercel Edge Config).
- **Si aplica**: rate limiting general en la API si es pública o tiene costos por request (ej. llamadas a APIs de terceros que cobran por uso).
- Límite sugerido de partida: 5-10 intentos de login por IP cada 15 minutos, ajustable según el caso.

## Dependency scanning

| Ecosistema | Herramienta | Cómo se integra |
|---|---|---|
| Node/npm | `npm audit` (nativo) | Correr en CI, fallar el build en vulnerabilidades `high`/`critical` |
| Python | `pip-audit` | `pip install pip-audit && pip-audit` |
| Rust | `cargo audit` | `cargo install cargo-audit && cargo audit` |
| Go | `govulncheck` | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| Cualquiera | Dependabot (GitHub nativo) | Archivo `.github/dependabot.yml` — actualiza deps automáticamente vía PR |
| Cualquiera | Renovate | Alternativa a Dependabot, más configurable, requiere GitHub App |

**Default de la skill**: generar `.github/dependabot.yml` en cualquier proyecto que use GitHub (ver P5.6), con chequeo semanal. Es la opción de menor fricción — no requiere cuenta ni configuración adicional del lado del usuario. La política de agrupamiento (patches auto-merge, majors sin agrupar) y el resto de la gestión de dependencias — pinning, auditoría de no-usadas, compliance de licencias — vive en `.charless/reference/dependencies.md`, no acá.

## Reglas por tipo de proyecto

- **API / Backend pura**: foco en A01, A03, A07, A10. CORS estricto, rate limiting en todos los endpoints públicos, no solo auth.
- **Frontend puro (SPA/landing sin backend propio)**: foco en no exponer API keys de servicios de terceros en el bundle del cliente (cualquier `VITE_*`/`NEXT_PUBLIC_*` es público, nunca poner ahí un secret real). Si consume una API de terceros que requiere secret, ese secret vive en un backend intermedio (BFF), no en el frontend.
- **Fullstack**: todo lo de API + frontend, más consistencia entre validaciones de ambos lados (mismo schema Zod compartido cuando sea posible).
- **Script / CLI**: foco en A06 (dependency scanning) y no loguear secrets si el script maneja credenciales (ej. un script de deploy con API keys).
- **Creativo**: no aplica salvo que el proyecto tenga alguna integración con API keys (ej. llamadas a un servicio de AI gen) — en ese caso, tratarlo como "script" para esa parte.

## Nivel de exigencia según escala del proyecto

Igual que con arquitectura (`architectures.md`) y tamaño de archivo (`coding-principles.md`), el nivel de seguridad debe **igualar** el tamaño y la sensibilidad del proyecto — no todo necesita threat modeling completo:

| Escala | Ejemplo | Nivel de exigencia |
|---|---|---|
| Prototipo / demo | MVP para mostrar a un inversor, sin datos reales | Solo reglas base (secrets, HTTPS, deps) |
| Producto real, pocos usuarios | SaaS chico, primeros usuarios pagos | Reglas base + auth hardening completo + rate limiting |
| Producto con datos sensibles | Fintech, salud, datos de menores | Todo lo anterior + threat modeling explícito (A04) + revisión de compliance (fuera del alcance de la skill — recomendar auditoría profesional) |

La skill nunca reemplaza una auditoría de seguridad profesional para proyectos que manejan datos sensibles o regulados — el objetivo de este módulo es que el proyecto arranque con buenas prácticas por default, no que certifique compliance.
