# Referencia completa de endpoints

`{BASE_URL}` = host + ROOT_PATH. Auth: ver [api-keys-and-auth.md](api-keys-and-auth.md).

Contrato detallado (schemas, params): [openapi.json](../assets/openapi.json)

---

## Health

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |

---

## Apps

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/v1/apps` | — | Crear app + keys |
| GET | `/v1/apps` | Admin | Listar apps (con `tenant_ref`) |
| PUT | `/v1/apps/{id}/tenant` | Admin | Fijar el tenant de facturación (`{"tenant_ref"}` → `{app_id, tenant_ref, changed}`) |
| GET | `/api/v1/system/entitlements/{tenant_ref}` | Admin | Plan guardado del tenant, modo y uso |
| POST | `/api/v1/system/entitlements/{tenant_ref}/refresh` | Admin | Refrescar el plan desde el proveedor |
| PATCH | `/v1/apps` | Secret | Actualizar app |

---

## API Keys

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/v1/api-keys/generate` | Secret (`api_keys:write`) | Generar par keys (`scopes` opcional; sin él, `["*"]`) |
| GET | `/api/v1/api-keys` | Secret (`api_keys:read`) | Listar keys (con `scopes`, `exposed` / `exposed_at`) |
| GET | `/api/v1/api-keys/scopes` | Secret (`api_keys:read`) | Catálogo de scopes |
| GET | `/api/v1/api-keys/:id` | Secret (`api_keys:read`) | Ver una key (con `scopes`) |
| PATCH | `/api/v1/api-keys/:id` | Secret (`api_keys:write`) | Editar `name`, `description`, `scopes` |
| POST | `/api/v1/api-keys/:id/rotate` | Secret | Rotar el par (queda `exposed: false`) |
| PATCH | `/api/v1/api-keys/:id/deactivate` | Secret | Desactivar |
| DELETE | `/api/v1/api-keys/:id` | Secret | Eliminar |
| GET | `/api/v1/api-keys/validate-public` | Public | Validar pk |
| GET | `/api/v1/api-keys/validate-secret` | Secret | Validar sk |

---

## Email auth

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/v1/emails/login` | Public | Login unificado |
| POST | `/api/v1/emails/signup` | Public | Registro |
| POST | `/api/v1/emails/signup/resend-code` | Public | Reenviar código signup |
| POST | `/api/v1/emails/signin` | Public | Login |
| POST | `/api/v1/emails/signin/resend-code` | Public | Reenviar código signin |
| POST | `/api/v1/emails/activate` | Public | Activar cuenta |
| POST | `/api/v1/emails/activate/v2` | Public | Activar v2 (Pro) |
| POST | `/api/v1/emails/activate/v2/set-password` | Bearer | Password post-activate |
| POST | `/api/v1/emails/reset` | Public | Solicitar reset |
| POST | `/api/v1/emails/reset-confirm` | Public | Confirmar reset (legacy) |
| POST | `/api/v1/emails/reset/validate-code` | Public | Validar código reset |
| POST | `/api/v1/emails/reset/set-password` | Bearer | Nueva password |
| POST | `/api/v1/emails/magic-link/request` | Public | Solicitar magic link |
| POST | `/api/v1/emails/magic-link/claim` | Public | Canjear magic link |
| POST | `/api/v1/emails/email-code/request` | Public | Solicitar código de acceso por correo |
| POST | `/api/v1/emails/email-code/claim` | Public | Canjear código de acceso (challenge_id + code) |

---

## Tokens / JWT

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/refresh-jwt` | Public + Refresh | Renovar access |
| GET | `/api/v1/validate-access` | Bearer access | Validar access |
| GET | `/api/v1/validate-refresh` | Bearer refresh | Validar refresh |
| GET | `/api/v1/jwt/info` | Bearer access | Info usuario |
| POST | `/api/v1/logout` | Bearer refresh | Cerrar la sesión desde el cliente (sin API key) |
| POST | `/api/v1/revoke-refresh` | Secret + Refresh | Revocar token |
| DELETE | `/api/v1/revoke-refresh/:id` | Secret | Revocar por ID de sesión |

---

## OAuth

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/oauths/link` | Public | URL de inicio del flujo |
| GET | `/api/v1/oauth/:callback_key/start` | — | Inicio del flujo (navegación): state + cookie + PKCE → 302 al proveedor |
| GET | `/api/v1/oauth/:callback_key` | — | Callback proveedor (necesita la cookie del inicio): 302 con tokens (modo `query`) o `code` (modo `code`) |
| POST | `/api/v1/oauth/exchange` | Public | `{code, redirect_uri?}` → `{access_token, refresh_token, provider}`; code de un solo uso, 60 s, ver [session-security.md](session-security.md) |
| GET | `/api/v1/oauth/:callback_key/embedded-start` | — | (Pro) Inicio del popup de los componentes embebidos (`?origin=&nonce=`), ver [embedded-auth.md](embedded-auth.md) |
| POST | `/api/v1/auth/social` | Public | Native SDK id_token |
| POST | `/api/v1/auth/social/nonce` | Public | Nonce de un solo uso para el login nativo |
| GET | `/api/v1/oauth-configs` | Secret | Listar configs |
| POST | `/api/v1/oauth-configs` | Secret | Crear config |
| PATCH | `/api/v1/oauth-configs/:id` | Secret | Actualizar |
| DELETE | `/api/v1/oauth-configs/:id` | Secret | Eliminar |
| GET | `/api/v1/oauth-configs/link` | Secret | Link admin |
| POST | `/api/v1/oauth-configs/:id/audiences` | Secret | Native audiences |

---

## Usuarios

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/users` | Secret o Admin | Listar y buscar (Criteria: `q`, `email`, `role`, `verified`, `mfa_enabled`, `provider`, `created_from/to`, `last_login_from/to`, `is_test`, `sort`); 422 con `error.meta.field` |
| GET | `/api/v1/users/:id` | Secret o Admin | Un usuario (forma de un elemento del listado); 404 `users.get.not_found` |
| POST | `/api/v1/users` | Secret | Crear |
| DELETE | `/api/v1/users` | Public + Bearer | Eliminar (auth) — alias de /me |
| DELETE | `/api/v1/users/me` | Public + Bearer | Self-delete |
| DELETE | `/api/v1/users/:id` | Secret | Eliminar por ID |
| PATCH | `/api/v1/users/:id/role` | Secret | Cambiar rol (409 `testers.role_locked` en un tester) |
| POST | `/api/v1/users/:id/set-password` | Secret | Fijar contraseña (409 `testers.password_managed` en un tester) |
| POST | `/api/v1/users/exist` | Public | ¿Existe email? |
| PATCH | `/api/v1/users/me/metadata` | Bearer | Metadata propia |
| GET | `/api/v1/users/me/sessions` | Public + Bearer | Mis sesiones activas (`current` marca la de este token) |
| DELETE | `/api/v1/users/me/sessions/:id` | Public + Bearer | Cerrar una de mis sesiones |
| POST | `/api/v1/users/me/password` | Public + Bearer | Cambiar mi contraseña (actual + nueva) |
| GET | `/api/v1/users/:id/sessions` | Secret | Sesiones activas de un usuario |
| PATCH | `/api/v1/users/:id/metadata` | Secret | Metadata admin |
| POST | `/api/v1/users/change-email/request` | Public + Bearer | Solicitar cambio |
| POST | `/api/v1/users/change-email/confirm` | Public + Bearer | Confirmar cambio |

---

## Testers (usuarios de prueba)

Todos con **secret key**; requieren `email_auth.testers` activo. Ver [testers.md](testers.md).

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/v1/testers` | Secret | Crear uno (`ttl` obligatorio) |
| POST | `/api/v1/testers/bulk` | Secret | Crear 1–200 (`realistic` o `pattern`) |
| GET | `/api/v1/testers` | Secret | Listar (`status`, `n_from`, `n_to`, `q`, `batch`, `order_by`, `order`, `page`, `size`, `offset`) |
| GET | `/api/v1/testers/batches` | Secret | Tandas con testers vivos (`batch`, `created_at`, `count`, `active`, `expired`) y `unbatched` |
| GET | `/api/v1/testers/credentials` | Secret | Contraseñas de todos, de `ids=a,b` o de una tanda `batch=<tanda>` (`format=json\|csv`) |
| GET | `/api/v1/testers/:id/credentials` | Secret | Contraseña de uno |
| POST | `/api/v1/testers/regenerate` | Secret | Re-hashear tras rotar `SECRET_PASSWORD` |
| PATCH | `/api/v1/testers/:id/expiry` | Secret | Alargar o revivir (`ttl`) |
| POST | `/api/v1/testers/:id/token` | Secret | Par de tokens sin contraseña |
| DELETE | `/api/v1/testers/:id` | Secret | Borrar uno |
| DELETE | `/api/v1/testers` | Secret | Borrar en lote (`status`, `confirm=true`) |
| POST | `/api/v1/testers/jobs` | Secret | Trabajo en segundo plano (`create` hasta 1000, `delete` con `confirm`, `set_expiry`) → 202 `{job_id, status}` |
| GET | `/api/v1/testers/jobs` | Secret | Listar trabajos, recientes primero (`page`, `size`) |
| GET | `/api/v1/testers/jobs/:id` | Secret | Progreso: `status`, `total`, `done`, `params`, `failed_item`, `result` |
| POST | `/api/v1/testers/preview` | Secret | Primeros 5 de un `create` + `seed` |
| GET | `/api/v1/testers/mock-kinds` | Secret | `kind` de mock por campo con su `label` |

---

## Roles, policies, role-policies

| Método | Ruta | Auth |
|--------|------|------|
| GET/POST | `/api/v1/roles` | Secret |
| PATCH/DELETE | `/api/v1/roles/:id` | Secret |
| GET/POST | `/api/v1/policies` | Secret | (`size` hasta 100) |
| PATCH | `/api/v1/policies/:id` | Secret | mismos campos que el POST, parcial |
| DELETE | `/api/v1/policies/:id` | Secret | la borra y la quita de todos los roles |
| POST | `/api/v1/role-policies` | Secret | `{role_id, policy_id}` |
| GET | `/api/v1/role-policies/:role_id` | Secret | `{role, policies: [policy completa…]}` |
| DELETE | `/api/v1/role-policies/:role_id/:policy_id` | Secret | quita la asignación |
| POST | `/api/v1/authorize` | Secret | `{user_id \| access_token, action, resource}` → `{allowed, role, matched_policy_id, effect}` |
| GET | `/api/v1/jwks/:app_id` | — | llaves públicas de los access tokens de la app |

`/api/v1/role_policies/...` (guion bajo) es un alias con los mismos handlers; usa `/api/v1/role-policies`.

---

## App behaviors

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/v1/app-behaviors` | Secret |
| GET | `/api/v1/app-behaviors/:id` | Secret |
| POST | `/api/v1/app-behaviors` | Secret |
| PUT | `/api/v1/app-behaviors/:id` | Secret |
| POST | `/api/v1/app-behaviors/email/verification/activate` | Secret |
| POST | `/api/v1/app-behaviors/email/verification/deactivate` | Secret |
| POST | `/api/v1/app-behaviors/email/magic-link/activate` | Secret |
| POST | `/api/v1/app-behaviors/email/email-code/activate` | Secret |
| POST | `/api/v1/app-behaviors/email/testers/activate` | Secret |
| POST | `/api/v1/app-behaviors/email/sessions/activate` | Secret | (deprecado: usa `PUT /tokens`) |
| GET | `/api/v1/app-behaviors/tokens` | Secret | (Pro) behavior tokens: config guardada y efectiva |
| PUT | `/api/v1/app-behaviors/tokens` | Secret | (Pro) vidas, sesiones, límite de sesiones, revocación |
| GET | `/api/v1/app-behaviors/embedded-auth` | Secret | (Pro) behavior embedded_auth: config, efectiva y disponible; no crea la fila |
| PUT | `/api/v1/app-behaviors/embedded-auth` | Secret | (Pro) orígenes, redirects del magic link, estrategias y marca de los componentes |
| GET | `/api/v1/app-behaviors/geo-access` | Secret | (Pro) bloqueo regional: `{mode, countries, unknown_country}`; sin fila, defaults y no crea nada |
| PUT | `/api/v1/app-behaviors/geo-access` | Secret | (Pro) reemplaza la config del bloqueo regional (`off`/`allowlist`/`blocklist`) |
| POST | `/api/v1/app-behaviors/email/metadata-schema/activate` | Secret |
| GET | `/api/v1/app-behaviors/email-locale` | Secret | idioma por defecto de los correos: `{default_locale?, effective_default_locale, updated_at?}`; sin fila `en` y no crea nada |
| PUT | `/api/v1/app-behaviors/email-locale` | Secret | `{default_locale: "es" \| ""}`; `400 email_locale.invalid_locale` |
| GET | `/api/v1/app-behaviors/mfa` | Secret | segundo factor: `{mode, flows, app_id, updated_at?}`; sin fila `optional` con los 5 flujos |
| PUT | `/api/v1/app-behaviors/mfa` | Secret | `{mode: off\|optional\|required, flows}` |
| GET | `/api/v1/app-behaviors/security-limits` | Secret | límites por app: secciones con `null` = hereda, `effective`, `defaults`, `ranges`, `updated_at?` |
| PUT | `/api/v1/app-behaviors/security-limits` | Secret | parcial `{rate_limit?, lockout?, api_keys?, mfa?}`; `null` = default de la instancia |
| GET | `/api/v1/app-behaviors/session-security` | Secret | `{oauth_token_delivery, refresh_rotation, revoke_sessions_on_password_change, updated_at?, defaults_for_new_apps}` |
| PUT | `/api/v1/app-behaviors/session-security` | Secret | parcial; `400 session_security.invalid_field` / `invalid_value` |

---

## Embedded Auth (Pro)

Ver [embedded-auth.md](embedded-auth.md). En Community estas rutas responden 404.

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/embedded-auth/config` | Public (el componente la pide con `X-Accounts-Client` + `X-Accounts-Publishable-Key`) | Estrategias efectivas, `start_url` de OAuth, signup y branding |
| GET | `/ui/v1/:file` | — | `accounts.js`, `oauth-callback.html`, `oauth-callback.js`, `manifest.json` |

---

## Historial de logins

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/login-events` | Secret | Historial paginado (`page`, `size`, `user_id`, `country`, `type`, `method`, `from`, `to`) |
| GET | `/api/v1/login-events/summary` | Secret | Resumen por país (`from`, `to`; default últimos 30 días) |

## Audit log

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/audit-logs` | Secret | Acciones administrativas de la app, recientes primero (`action` prefijo, `actor_id`, `resource_type`, `resource_id`, `result`, `from`, `to`, `limit` ≤ 200, `cursor`); `{data, next_cursor}` |

## Webhooks

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/v1/webhooks/events` | — (cada evento con `emitted`) |
| GET/POST | `/api/v1/webhooks` | Secret (política de entrega: `retries`, `min_interval_ms`, `backoff`, `honor_retry_after`; `send_secret_header`) |
| PATCH/DELETE | `/api/v1/webhooks/{id}` | Secret |
| POST | `/api/v1/webhooks/{id}/test` | Secret (entrega de prueba firmada) |
| GET | `/api/v1/webhooks/{id}/deliveries` | Secret (registro de entregas: `status`, `event_type`, `page`, `size`) |
| GET | `/api/v1/webhooks/deliveries` | Secret (registro de toda la app: `webhook_id`, `status`, `event_type`, `page`, `size`) |

---

## MCP Connect (login OAuth 2.1 para servidores MCP)

Solo con `OAUTH_PUBLIC_URL` configurada. Ver [mcp-connect.md](mcp-connect.md).

| Método | Ruta | Auth |
|--------|------|------|
| GET/POST | `/v1/mcp-resources` | Secret (sin `/api`) |
| GET/PATCH/DELETE | `/v1/mcp-resources/{id}` | Secret |
| PUT | `/v1/mcp-resources/{id}/scopes` | Secret (reemplaza la lista) |
| POST | `/v1/mcp-resources/{id}/verify` | Secret (sondea el servidor MCP) |
| GET/POST | `/v1/mcp-resources/{id}/clients` | Secret (clientes pre-registrados) |
| POST | `/v1/mcp-resources/{id}/clients/disable` | Secret |
| GET | `/v1/mcp/authorization-requests/{id}` | Secret (+ `X-User-Token` opcional) |
| POST | `/v1/mcp/authorization-requests/{id}/approve` | Secret (`user_token`, `scope`) |
| POST | `/v1/mcp/authorization-requests/{id}/deny` | Secret |
| GET | `/v1/mcp/connections` | Secret (`resource_id`, `user_id`, `email`, `client_id`, `status`, `page`, `size`); cada conexión trae `user` {id, email, name, is_test} |
| GET | `/v1/mcp/connections/summary` | Secret (`user_ids` separados por coma, ≤ 100) → `{user_id: conexiones activas}` |
| GET/DELETE | `/v1/mcp/connections/{id}` | Secret (también por `sid`) |
| GET | `/api/v1/me/mcp-connections` | Publishable + Bearer |
| DELETE | `/api/v1/me/mcp-connections/{id}` | Publishable + Bearer |
| GET | `/.well-known/oauth-authorization-server{ROOT_PATH}/o/{app_id}`, `/o/{app_id}/.well-known/oauth-authorization-server` (y `openid-configuration`) | — (metadata RFC 8414, la lee el asistente) |
| GET | `/o/{app_id}/.well-known/jwks.json` | — |
| GET | `/o/{app_id}/oauth/authorize` | — (OAuth; redirige a `login_url`) |
| POST | `/o/{app_id}/oauth/token` | — (OAuth, form-urlencoded) |
| POST | `/o/{app_id}/oauth/register` | — (DCR, RFC 7591) |
| POST | `/o/{app_id}/oauth/introspect` | Secret en `X-API-Key` (RFC 7662) |
| POST | `/o/{app_id}/oauth/revoke` | — (RFC 7009) |
| GET | `/o/{app_id}/userinfo` | Bearer (access token de recurso) |

---

## Segundo factor (MFA)

| Método | Ruta | Auth |
|--------|------|------|
| POST | `/api/v1/mfa/verify` | Public | `{mfa_token, method, code}` → tokens |
| POST | `/api/v1/mfa/enroll/start` | Public | `{mfa_token}` → `secret`, `url`, `qr_image` |
| POST | `/api/v1/mfa/enroll/confirm` | Public | `{mfa_token, code}` → tokens + `backup_codes` |

Ver [mfa.md](mfa.md).

---

## TOTP (2FA)

Todas: publishable key + Bearer access token (el usuario de la sesión).

| Método | Ruta | Auth |
|--------|------|------|
| POST | `/api/v1/totp/setup` | Public + Bearer | `secret`, `url`, `qr_image` (data URI) |
| GET | `/api/v1/totp/qr` | Public + Bearer | PNG del secreto pendiente |
| POST | `/api/v1/totp/verify` | Public + Bearer | `{code}`; la 1.ª vez activa y devuelve `backup_codes` |
| POST | `/api/v1/totp/disable` | Public + Bearer | `{code}` obligatorio |
| GET | `/api/v1/totp/backup-codes` | Public + Bearer | `{remaining}` |
| POST | `/api/v1/totp/backup-codes/regenerate` | Public + Bearer | `{code}` → 10 códigos nuevos |

---

## Pending registrations

| Método | Ruta | Auth |
|--------|------|------|
| POST | `/api/v1/pending-registrations` | Secret |

---

## Docs

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/docs/index.html` | Swagger UI |
