---
name: accounts-integration
description: >-
  Integra Foundathyon Accounts (autenticación y cuentas de usuario) con las
  rutas, headers y formato de respuesta reales. Usar para signup, signin,
  refresh token y logout, OAuth (Google, Apple, Microsoft, GitHub) con canje
  del code en POST /api/v1/oauth/exchange, magic link, código por correo
  (email OTP), segundo factor (MFA TOTP, mfa_required), usuarios de prueba
  (testers), webhooks, roles y RBAC (claim role, /authorize), behaviors,
  componentes web embebidos (Embedded Auth), MCP Connect (OAuth 2.1 para
  servidores MCP), historial de logins y bloqueo por país (geo_access),
  enlace de identidades, límites de seguridad, seguridad de sesiones,
  idioma de los correos, planes y cuotas (403 quota.*) y manejo de errores
  por error.scope. Skill portable: no requiere el repo de accounts.
metadata:
  version: "0.33.0"
---

# Foundathyon Accounts API — skill completo de integración

**Skill autocontenido y portable.** Copia la carpeta entera a otros proyectos (Cursor o Claude Code). Toda la documentación está en **`references/`** y el contrato en `assets/` — no depende del repo de accounts.

## Cómo usar este skill (agentes)

Antes de generar código de integración, **lee los archivos de `references/` según el flujo**. No inventes rutas ni headers: usa solo lo documentado aquí.

| Archivo | Cuándo leerlo |
|---------|---------------|
| [quickstart.md](references/quickstart.md) | Primer contacto, flujo mínimo app → signup → signin |
| [setup.md](references/setup.md) | Docker, variables de entorno, `{BASE_URL}` |
| [api-keys-and-auth.md](references/api-keys-and-auth.md) | Tipos de auth, matriz por endpoint, scopes de las secret keys (catálogo, `403 api_keys.scope_denied`, sin escalada) |
| [response-format.md](references/response-format.md) | Formato JSON success/error; qué errores llegan con message genérico (5xx, seguridad) y por qué hay que guardar el `trace_id` |
| [auth-flows.md](references/auth-flows.md) | Árbol de decisión de flujos |
| [email-auth.md](references/email-auth.md) | Signup, signin, activate, reset, login unificado |
| [tokens.md](references/tokens.md) | Refresh (y rotación), logout desde el cliente, sesiones activas, validate, revoke, jwt/info |
| [oauth.md](references/oauth.md) | OAuth web redirect y native SDK |
| [magic-link.md](references/magic-link.md) | Autenticación passwordless por enlace |
| [email-code.md](references/email-code.md) | Autenticación passwordless por código (email OTP): entrar y crear cuenta con un código |
| [embedded-auth.md](references/embedded-auth.md) | Componentes web (Pro): `<script>` + `<accounts-sign-in>`…, `Accounts.getToken()`, behavior `embedded_auth` (`allowed_origins`), cabeceras `X-Accounts-*`, verificar el JWT en el backend |
| [behaviors.md](references/behaviors.md) | Config por app que cambia los flujos |
| [users.md](references/users.md) | CRUD usuario, búsqueda (Criteria: `q`, filtros, `sort`), `GET /users/{id}`, metadata, change-email |
| [testers.md](references/testers.md) | Usuarios de prueba: crear en lote, credenciales, vigencia, token directo, borrado |
| [roles-policies.md](references/roles-policies.md) | RBAC: roles, policies (alta, edición, borrado), asignación a roles, claim `role`, `POST /api/v1/authorize`, JWKS y verificador Go (`authz`) |
| [mfa.md](references/mfa.md) | Segundo factor: behavior `mfa`, respuesta `mfa_required` / `mfa_enrollment_required` en los logins, `/api/v1/mfa/*`, TOTP del usuario y códigos de respaldo |
| [security-limits.md](references/security-limits.md) | Límites de seguridad por app (`security_limits`, Community y Pro): rate limit por IP y cuenta, bloqueo progresivo, secret keys inválidas y MFA dentro de rangos fijos sobre los defaults de la instancia; `PUT` parcial, `null` = default |
| [session-security.md](references/session-security.md) | Seguridad de sesiones (`session_security`, Community y Pro): entrega de tokens del login OAuth web por `code` (`POST /api/v1/oauth/exchange`) o por query, rotación del refresh, revocación al cambiar la contraseña, denylist de access tokens; apps existentes sin cambios, apps nuevas en modo seguro |
| [mcp-connect.md](references/mcp-connect.md) | Login OAuth 2.1 para servidores MCP: registrar el recurso, configurar el servidor MCP, construir la página de conexión, conexiones |
| [email-locale.md](references/email-locale.md) | Idioma de los correos transaccionales (`email_locale`, Community y Pro): campo `locale` del body, `Accept-Language`, idioma guardado del usuario, `default_locale` de la app y `en`; reintentos sin correos duplicados |
| [identity-linking.md](references/identity-linking.md) | Enlace de identidades por correo (`identity_linking`, Community y Pro): regla de correo verificado (Microsoft `xms_edov`, GitHub primario verificado), modos `link_with_proof`/`separate`, signup sin tokens hasta el código |
| [login-security.md](references/login-security.md) | Historial de logins (`/api/v1/login-events`, resumen por país, `ip_changed`) y bloqueo regional por país (Pro, `geo_access`): config, 403 `geo_access.*`, webhook `accounts.auth.login_failed`, `TRUSTED_PROXIES` |
| [plans-and-quotas.md](references/plans-and-quotas.md) | Planes y cuotas por organización (`tenant_ref`, operador): techo `max_accounts_users` en toda alta (overage en planes de pago), techos de API keys/roles/webhooks/OAuth (`403 quota.*_exceeded`), funciones Pro (`403 quota.feature_not_in_plan`), MAU, `accounts.entitlement.limited`, uso por tenant, retención por plan, modo de solo lectura (`403 quota.tenant_read_only`); los logins nunca se bloquean; `ENTITLEMENTS_*` |
| [metrics.md](references/metrics.md) | Métricas del dashboard con secret key: `GET /api/v1/metrics/{overview,users,logins,webhooks,usage}`, `from`/`to`/`interval`/`tz`, activos nuevos/reactivados/retenidos, fallos por motivo, top IPs, entregas de webhooks y uso del plan; campos null o vacíos no viajan; `metrics.query.*` |
| [audit-log.md](references/audit-log.md) | Audit log de las acciones administrativas (secret key / admin key): `GET /api/v1/audit-logs` con filtros de core y cursor, forma del evento `fd_audit`, `changes` redactado, `via=core`, `AUDIT_*` |
| [webhooks.md](references/webhooks.md) | Eventos HTTP hacia tu backend: verificar la firma, los 43 eventos que se emiten (usuarios, sesiones, identidades, roles, API keys, MFA, testers…), garantías del outbox, registro de entregas |
| [endpoints-reference.md](references/endpoints-reference.md) | Tabla completa de endpoints |
| [error-scopes.md](references/error-scopes.md) | Errores por `scope` con la acción sugerida, por flujo |
| [error-catalog.md](references/error-catalog.md) | Catálogo completo de `error.scope`, generado desde el código: status y si el message es descriptivo o genérico |
| [sdk-patterns.md](references/sdk-patterns.md) | Patrones frontend/backend |
| [openapi.json](assets/openapi.json) | Contrato HTTP machine-readable (Swagger 2.0) |

---

## Qué es Accounts

API REST **self-hosted** de autenticación multi-tenant:

- Email/contraseña, magic link, código de acceso por correo, OAuth (Google, Apple, Microsoft, GitHub)
- Componentes web de login embebidos (Pro): un `<script>` servido por la instancia y `<accounts-sign-in>` en cualquier página
- JWT (RSA) + refresh tokens
- API keys por app (publishable + secret)
- Roles, políticas RBAC (claim `role` y `POST /api/v1/authorize`), webhooks
- Segundo factor TOTP con códigos de respaldo (behavior `mfa`: `off` / `optional` / `required`)
- Límites contra fuerza bruta ajustables por app dentro de rangos fijos (behavior `security_limits`)
- Behaviors configurables por app (verificación email, password policy, etc.)
- Usuarios de prueba (testers) en el dominio reservado `@getfoundathyon.mock`, con vigencia y credenciales descargables
- MCP Connect: servidor de autorización OAuth 2.1 para que Claude, ChatGPT y otros clientes MCP entren al servidor MCP de tu app con tu login
- Historial de logins con la ubicación aproximada de cada IP (Community y Pro) y bloqueo regional por país (Pro)

---

## Reglas que nunca debes violar

| Regla | Detalle |
|-------|---------|
| `{BASE_URL}` | `https://host` + `ROOT_PATH` → ej. `http://localhost:8000/accounts` |
| Rutas de apps | `POST {BASE_URL}/v1/apps` — **sin** `/api` |
| Rutas de auth | `{BASE_URL}/api/v1/...` — **con** `/api` |
| Cliente | `X-API-Key: pk_live_...` (publishable_key) |
| Servidor admin | `X-API-Key: sk_live_...` (secret_key) — **nunca en frontend**. Lleva scopes (`"*"` = todo; sin el scope → `403 api_keys.scope_denied` con `error.meta.required_scope`) |
| Access token | `Authorization: Bearer <access_token>` |
| Refresh | `GET /api/v1/refresh-jwt` + Bearer refresh + public key; **guarda el `refresh_token` de cada respuesta** (con la rotación activa, el anterior ya no sirve) |
| Logout | `POST /api/v1/logout` + Bearer refresh — sin API key; el cliente cierra su propia sesión |
| Respuesta | `{ success, status_code, data?, error?: { code, message, scope, meta? }, trace_id? }` |
| Errores | Mapea por `error.scope` (estable), nunca por `message`. Un 5xx o un error de seguridad trae un `message` genérico (`Internal server error`…): muestra tu propio texto y guarda el `trace_id` para soporte — ver [response-format.md](references/response-format.md) |
| Token fields | `access_token`, `jwt` → equivalentes; siempre guardar `refresh_token` |
| Behaviors | Signup/signin cambian si `verification.enabled` — ver [behaviors.md](references/behaviors.md) |
| Testers | `@getfoundathyon.mock` es reservado: no lo uses en signup; los testers se crean con secret key — ver [testers.md](references/testers.md) |
| Bloqueo regional (Pro) | Un login puede responder `403 geo_access.country_not_allowed` / `geo_access.unknown_country` con el país en `error.meta.country_code`: muéstralo, no reintentes — ver [login-security.md](references/login-security.md) |
| Segundo factor | Cualquier login puede responder `{mfa_required \| mfa_enrollment_required, mfa_token}` **sin tokens** (default `optional`: usuarios con TOTP activo). Mira esos campos antes de leer `access_token` y completa con `/api/v1/mfa/*` — ver [mfa.md](references/mfa.md) |
| OAuth web | La redirección final trae `access_token`/`refresh_token` (modo `query`, apps existentes) **o** `code` (modo `code`, apps nuevas): canjéalo una vez y en < 60 s con `POST /api/v1/oauth/exchange` + publishable key — ver [session-security.md](references/session-security.md) |
| Revocación | Un access token de una sesión cerrada falla en `/validate-access` (`refresh_tokens.validate.revoked`); la verificación local con JWKS no lo ve hasta su `exp` |
| Embedded Auth (Pro) | El componente manda `X-Accounts-Client` + `X-Accounts-Publishable-Key` (nunca `X-API-Key`/`Authorization`); el origen de la página debe estar en `allowed_origins`. Sin `X-Accounts-*` nada cambia — ver [embedded-auth.md](references/embedded-auth.md) |

---

## Happy path (copiar tal cual)

```bash
# 1. Crear app
curl -X POST "{BASE_URL}/v1/apps" \
  -H "Content-Type: application/json" \
  -d '{"name":"Mi App","root_email":"admin@example.com"}'

# 2. Signup (public key)
curl -X POST "{BASE_URL}/api/v1/emails/signup" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{"email":"user@example.com","password":"SecurePass123!","role":"default"}'

# 3. Signin
curl -X POST "{BASE_URL}/api/v1/emails/signin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'

# 4. Refresh
curl -X GET "{BASE_URL}/api/v1/refresh-jwt" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {refresh_token}"
```

---

## Anti-patrones

- Hardcodear URL sin `ROOT_PATH`
- `secret_key` en frontend o en repos públicos
- Asumir tokens en signup con verification ON
- Asumir tokens en signin/OAuth/magic link sin mirar `mfa_required` / `mfa_enrollment_required`
- Poner `mfa_token` o el secreto TOTP en una URL o en logs
- Confundir `/v1/apps` con `/api/v1/emails/...`
- Omitir `role` en signup
- Usar refresh token donde se espera access token
- Parsear `error.message` o mostrar al usuario el de un 5xx esperando detalle: es genérico a propósito
- Descartar el `refresh_token` que devuelve `refresh-jwt`: con la rotación activa, reutilizar el anterior revoca la sesión
- Ignorar `error.scope` y manejar solo HTTP status

---

## Compartir entre proyectos

Copia **toda la carpeta** del skill a:

```text
# Global (todos tus proyectos)
~/.agents/skills/accounts-integration/   # Cursor, Codex y Copilot
~/.cursor/skills/accounts-integration/
~/.claude/skills/accounts-integration/

# Por proyecto
tu-proyecto/.agents/skills/accounts-integration/
tu-proyecto/.cursor/skills/accounts-integration/
tu-proyecto/.claude/skills/accounts-integration/
```

Variables de entorno en tu app consumidora:

```env
ACCOUNTS_BASE_URL=https://api.tudominio.com/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...
ACCOUNTS_SECRET_KEY=sk_live_...   # solo backend
```

---

## Checklist de entrega

- [ ] `{BASE_URL}` correcto con `ROOT_PATH`
- [ ] Public key en cliente; secret key solo servidor
- [ ] Refresh automático (401 → refresh-jwt → retry o re-login), guardando el `refresh_token` de cada respuesta
- [ ] Logout con `POST /api/v1/logout` (y borrar los tokens aunque responda 401)
- [ ] Manejo de `error.scope`
- [ ] Flujo activate si verification ON
- [ ] Paso de segundo factor (`mfa_required` → `/mfa/verify`; `mfa_enrollment_required` → `/mfa/enroll/*`)
- [ ] OpenAPI consultado para campos exactos del body
