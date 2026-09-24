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
| GET | `/v1/apps` | Admin | Listar apps |
| PATCH | `/v1/apps` | Secret | Actualizar app |

---

## API Keys

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/v1/api-keys/generate` | Secret | Generar par keys |
| GET | `/api/v1/api-keys` | Secret | Listar keys |
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
| GET | `/api/v1/jwt/info` | Bearer refresh | Info usuario |
| POST | `/api/v1/revoke-refresh` | Secret + Refresh | Revocar token |
| DELETE | `/api/v1/revoke-refresh/:id` | Secret | Revocar por ID |

---

## OAuth

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/oauths/link` | Public | URL autorización |
| GET | `/api/v1/oauth/:callback_key` | — | Callback proveedor |
| POST | `/api/v1/auth/social` | Public | Native SDK id_token |
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
| GET | `/api/v1/users` | Secret o Admin | Listar; `?is_test=true\|false` separa testers de personas |
| POST | `/api/v1/users` | Secret | Crear |
| DELETE | `/api/v1/users` | Public + Bearer | Eliminar (auth) — alias de /me |
| DELETE | `/api/v1/users/me` | Public + Bearer | Self-delete |
| DELETE | `/api/v1/users/:id` | Secret | Eliminar por ID |
| PATCH | `/api/v1/users/:id/role` | Secret | Cambiar rol (409 `testers.role_locked` en un tester) |
| POST | `/api/v1/users/:id/set-password` | Secret | Fijar contraseña (409 `testers.password_managed` en un tester) |
| POST | `/api/v1/users/exist` | Public | ¿Existe email? |
| PATCH | `/api/v1/users/me/metadata` | Bearer | Metadata propia |
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
| GET | `/api/v1/testers` | Secret | Listar (`status`, `n_from`, `n_to`, `q`, `page`, `size`) |
| GET | `/api/v1/testers/credentials` | Secret | Contraseñas de todos o de `ids=a,b` (`format=json\|csv`) |
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
| GET/POST | `/api/v1/policies` | Secret |
| POST | `/api/v1/role-policies` | Secret |
| GET | `/api/v1/role-policies/:role_id` | Secret |

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
| POST | `/api/v1/app-behaviors/email/metadata-schema/activate` | Secret |

---

## Webhooks

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/v1/webhooks/events` | — |
| GET/POST | `/api/v1/webhooks` | Secret (política de entrega: `retries`, `min_interval_ms`, `backoff`, `honor_retry_after`) |

---

## TOTP (2FA)

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/v1/totp/qr` | — |
| POST | `/api/v1/totp/setup` | Bearer |
| POST | `/api/v1/totp/verify` | Bearer |
| POST | `/api/v1/totp/disable` | Bearer |

---

## Pending registrations

| Método | Ruta | Auth |
|--------|------|------|
| POST | `/api/v1/pending-registrations` | — |

---

## Docs

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/docs/index.html` | Swagger UI |
