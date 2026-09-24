---
name: accounts-integration
description: >-
  Documentación completa y autocontenida de Foundathyon Accounts API. Usar para
  integrar signup, signin, refresh token, OAuth, magic link, código de acceso
  por correo (email OTP), usuarios de prueba (testers), webhooks, roles y
  behaviors. Skill portable — no requiere el repo de accounts.
metadata:
  version: "0.6.0"
---

# Foundathyon Accounts API — skill completo de integración

**Skill autocontenido y portable.** Copia la carpeta entera a otros proyectos (Cursor o Claude Code). Toda la documentación está en **`references/`** y el contrato en `assets/` — no depende del repo de accounts.

## Cómo usar este skill (agentes)

Antes de generar código de integración, **lee los archivos de `references/` según el flujo**. No inventes rutas ni headers: usa solo lo documentado aquí.

| Archivo | Cuándo leerlo |
|---------|---------------|
| [quickstart.md](references/quickstart.md) | Primer contacto, flujo mínimo app → signup → signin |
| [setup.md](references/setup.md) | Docker, variables de entorno, `{BASE_URL}` |
| [api-keys-and-auth.md](references/api-keys-and-auth.md) | Tipos de auth, matriz por endpoint |
| [response-format.md](references/response-format.md) | Formato JSON success/error |
| [auth-flows.md](references/auth-flows.md) | Árbol de decisión de flujos |
| [email-auth.md](references/email-auth.md) | Signup, signin, activate, reset, login unificado |
| [tokens.md](references/tokens.md) | Refresh, validate, revoke, jwt/info |
| [oauth.md](references/oauth.md) | OAuth web redirect y native SDK |
| [magic-link.md](references/magic-link.md) | Autenticación passwordless por enlace |
| [email-code.md](references/email-code.md) | Autenticación passwordless por código (email OTP): entrar y crear cuenta con un código |
| [behaviors.md](references/behaviors.md) | Config por app que cambia los flujos |
| [users.md](references/users.md) | CRUD usuario, metadata, change-email, filtro `is_test` |
| [testers.md](references/testers.md) | Usuarios de prueba: crear en lote, credenciales, vigencia, token directo, borrado |
| [roles-policies.md](references/roles-policies.md) | RBAC admin |
| [webhooks.md](references/webhooks.md) | Eventos HTTP hacia tu backend |
| [endpoints-reference.md](references/endpoints-reference.md) | Tabla completa de endpoints |
| [error-scopes.md](references/error-scopes.md) | Errores por `scope` |
| [sdk-patterns.md](references/sdk-patterns.md) | Patrones frontend/backend |
| [openapi.json](assets/openapi.json) | Contrato HTTP machine-readable (Swagger 2.0) |

---

## Qué es Accounts

API REST **self-hosted** de autenticación multi-tenant:

- Email/contraseña, magic link, código de acceso por correo, OAuth (Google, Apple, Microsoft, GitHub)
- JWT (RSA) + refresh tokens
- API keys por app (publishable + secret)
- Roles, políticas RBAC, webhooks
- Behaviors configurables por app (verificación email, password policy, etc.)
- Usuarios de prueba (testers) en el dominio reservado `@getfoundathyon.mock`, con vigencia y credenciales descargables

---

## Reglas que nunca debes violar

| Regla | Detalle |
|-------|---------|
| `{BASE_URL}` | `https://host` + `ROOT_PATH` → ej. `http://localhost:8000/accounts` |
| Rutas de apps | `POST {BASE_URL}/v1/apps` — **sin** `/api` |
| Rutas de auth | `{BASE_URL}/api/v1/...` — **con** `/api` |
| Cliente | `X-API-Key: pk_live_...` (publishable_key) |
| Servidor admin | `X-API-Key: sk_live_...` (secret_key) — **nunca en frontend** |
| Access token | `Authorization: Bearer <access_token>` |
| Refresh | `GET /api/v1/refresh-jwt` + Bearer refresh + public key |
| Respuesta | `{ success, status_code, data?, error?: { message, scope }, trace_id? }` |
| Token fields | `access_token`, `jwt` → equivalentes; siempre guardar `refresh_token` |
| Behaviors | Signup/signin cambian si `verification.enabled` — ver [behaviors.md](references/behaviors.md) |
| Testers | `@getfoundathyon.mock` es reservado: no lo uses en signup; los testers se crean con secret key — ver [testers.md](references/testers.md) |

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
- Confundir `/v1/apps` con `/api/v1/emails/...`
- Omitir `role` en signup
- Usar refresh token donde se espera access token
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
- [ ] Refresh automático (401 → refresh-jwt → retry o re-login)
- [ ] Manejo de `error.scope`
- [ ] Flujo activate si verification ON
- [ ] OpenAPI consultado para campos exactos del body
