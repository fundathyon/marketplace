# Segundo factor (MFA) y códigos de respaldo

Community y Pro. El behavior `mfa` de cada app decide cuándo un login necesita un código TOTP (app autenticadora) además del primer factor. Cuando lo necesita, **el login no emite tokens**: devuelve un paso (`mfa_token`) que se completa en `/api/v1/mfa/*`.

> **Cambio que rompe:** el modo por defecto es `optional` en los cinco flujos. Un usuario que ya tenía TOTP activo recibe ahora `mfa_required` (sin `access_token` ni `refresh_token`) en signin, OAuth, nativo, magic link y código por correo. Si tu cliente asumía tokens en esas respuestas, maneja el paso o pon la app en `mode: "off"`.

---

## Behavior `mfa`

```bash
curl "{BASE_URL}/api/v1/app-behaviors/mfa" -H "X-API-Key: {secret_key}"

curl -X PUT "{BASE_URL}/api/v1/app-behaviors/mfa" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"mode": "required", "flows": ["password", "oauth", "native", "magic_link", "email_code"]}'
```

| Campo | Valores |
|-------|---------|
| `mode` | `off` (nunca, aunque el usuario tenga TOTP) · `optional` (default: solo a quien tiene TOTP activo) · `required` (todos; quien no tiene TOTP se enrola durante el login) |
| `flows` | `password` (signin, signup sin verificación, activación, registro delegado) · `oauth` (callback web y popup embebido) · `native` (`POST /api/v1/auth/social`) · `magic_link` · `email_code`. Ausente = los cinco; `[]` = ninguno |

Respuesta: `{app_id, mode, flows, updated_at}` (`updated_at` solo si existe la fila). Sin fila, `GET` devuelve `optional` con los cinco flujos y no crea nada. Errores: `400 mfa.invalid_mode`, `400 mfa.invalid_flow`. Las rutas genéricas de behaviors lo rechazan (`422 app_behaviors.create.use_mfa_endpoint` / `app_behaviors.update.use_mfa_endpoint`).

**Testers exentos:** las cuentas de prueba (`@getfoundathyon.mock`) nunca piden segundo factor.

Si Accounts no puede leer el behavior o el usuario, el login falla cerrado: `503 mfa.lookup_error`.

---

## Respuesta de un login con segundo factor pendiente

Mismo sobre y status que el login (p. ej. `200` en signin, `201` en signup), sin tokens:

```json
{ "success": true, "status_code": 200,
  "data": { "mfa_required": true, "mfa_token": "mfa_…", "methods": ["totp", "backup_code"], "expires_in": 300 } }
```

```json
{ "success": true, "status_code": 200,
  "data": { "mfa_enrollment_required": true, "mfa_token": "mfa_…", "methods": ["totp"], "expires_in": 300 } }
```

- `methods` incluye `backup_code` solo si al usuario le quedan códigos de respaldo.
- El `mfa_token` es de **un solo uso**, vence en `MFA_TOKEN_TTL_SEC` (300 s), está ligado a la app y al usuario y admite `MFA_MAX_ATTEMPTS` (5) códigos.
- Rutas que pueden devolverlo: `/emails/signin`, `/emails/signup` (sin verificación), `/emails/activate`, `/emails/activate/v2/set-password` (registro delegado, Pro), `/emails/magic-link/claim`, `/emails/email-code/claim`, `/auth/social` (nativo), callback OAuth web y popup embebido.

Regla para clientes: **antes de leer `access_token`, mira `mfa_required` / `mfa_enrollment_required`**.

---

## Completar el paso (publishable key)

```bash
# Verificar (TOTP por defecto, o method: backup_code)
curl -X POST "{BASE_URL}/api/v1/mfa/verify" \
  -H "Content-Type: application/json" -H "X-API-Key: {publishable_key}" \
  -d '{"mfa_token": "mfa_…", "method": "totp", "code": "123456"}'
# 200 → {access_token, refresh_token, mfa: "totp"|"backup_code", backup_codes_remaining?}

# Enrolamiento (mfa_enrollment_required)
curl -X POST "{BASE_URL}/api/v1/mfa/enroll/start" \
  -H "Content-Type: application/json" -H "X-API-Key: {publishable_key}" \
  -d '{"mfa_token": "mfa_…"}'
# 200 → {secret, url (otpauth://), qr_image (data:image/png;base64,…), expires_in}

curl -X POST "{BASE_URL}/api/v1/mfa/enroll/confirm" \
  -H "Content-Type: application/json" -H "X-API-Key: {publishable_key}" \
  -d '{"mfa_token": "mfa_…", "code": "123456"}'
# 200 → {access_token, refresh_token, mfa: "totp", backup_codes: [10 códigos]}
```

`enroll/start` se puede repetir (cada llamada reemplaza el secreto pendiente) y no emite tokens. `backup_codes` se muestran **solo** en `enroll/confirm`: pide al usuario que los guarde.

| Error | Status | Qué hacer |
|-------|--------|-----------|
| `mfa.invalid_code` | 401 | Código equivocado; `error.meta.attempts_remaining` |
| `mfa.invalid_token` | 401 | Token desconocido, vencido, usado o de otra app → volver a iniciar sesión |
| `mfa.too_many_attempts` | 429 | El token agotó sus intentos → volver a iniciar sesión |
| `auth.rate_limited` | 429 | `MFA_FAILURE_MAX` (10) fallos del usuario en `MFA_FAILURE_WINDOW_SEC` (900 s), o límite por IP; respeta `Retry-After` |
| `mfa.invalid_method` | 400 | `method` distinto de `totp` / `backup_code` |
| `mfa.enrollment_required` | 409 | Llamaste `verify` con un token de enrolamiento |
| `mfa.already_enrolled` | 409 | Llamaste `enroll/*` con un token de verificación o el usuario ya tiene TOTP |
| `mfa.enrollment_not_started` | 409 | `enroll/confirm` antes de `enroll/start` |
| `sessions.limit_reached` | 409 | Límite de sesiones (behavior `tokens`, Pro) |
| `mfa.lookup_error` | 503 | Reintentar |

Un código TOTP ya aceptado no se acepta otra vez (401).

---

## OAuth

- **Web (redirect):** el callback redirige al `redirect_uri` de la app con `?mfa_required=true&mfa_methods=totp,backup_code&mfa_token=…&provider=…` (o `?mfa_enrollment_required=true&mfa_token=…&provider=…`). **Nunca hay tokens en la URL antes del segundo factor**: tu página llama `/api/v1/mfa/verify` y recibe los tokens en el cuerpo.
- **Popup embebido (Pro):** el fragmento de `oauth-callback.html` lleva `status=mfa_required` (o `mfa_enrollment_required`), `mfa_token` y `mfa_methods`; el componente completa el paso (ver [embedded-auth.md](embedded-auth.md)).
- **Nativo (`POST /api/v1/auth/social`):** `200` con `{mfa_required | mfa_enrollment_required, mfa_token, methods, expires_in}` y sin `user` ni tokens.

---

## Webhooks e historial

- Cada código rechazado (o token agotado) deja una fila `login_failed` (`block_reason: "mfa_failed"`) y el webhook `accounts.auth.login_failed` con `data.reason: "mfa_failed"`; los bloqueos por `MFA_FAILURE_MAX` salen con `reason: "rate_limited"`.
- `accounts.auth.login` sale **después** del segundo factor, con el `method` del login original.
- `login_events` registra el segundo factor en `mfa` (`totp`, `backup_code` o vacío si no se pidió).

---

## Gestión del TOTP del usuario (sesión)

Todas con `X-API-Key: {publishable_key}` + `Authorization: Bearer {access_token}`; el usuario siempre es el de la sesión.

| Método | Ruta | Detalle |
|--------|------|---------|
| POST | `/api/v1/totp/setup` | `{secret, url, qr_image (data URI PNG), totp_enabled: false}`; `409` si ya está activo. El secreto **nunca** viaja en una URL (ya no existe `qr_page_url` ni la página `?key=`) |
| GET | `/api/v1/totp/qr` | PNG del QR del secreto pendiente; `404 totp.qr.not_configured`, `409 totp.qr.already_enabled` |
| POST | `/api/v1/totp/verify` | `{code}`. La primera vez activa TOTP y devuelve `backup_codes` (10) y `just_verified: true`; después solo valida |
| POST | `/api/v1/totp/disable` | `{code}` **obligatorio** (`401 totp.disable.invalid_code`) |
| GET | `/api/v1/totp/backup-codes` | `{remaining}` (nunca los códigos) |
| POST | `/api/v1/totp/backup-codes/regenerate` | `{code}` TOTP actual → 10 códigos nuevos (los anteriores dejan de servir); `409 totp.backup_codes.totp_not_enabled`, `401 totp.backup_codes.invalid_code` |

`verify`, `disable` y `regenerate` cuentan para `MFA_FAILURE_MAX` y tienen límite por IP (`429 auth.rate_limited` con `Retry-After`).

**Códigos de respaldo:** 10 por usuario, formato `xxxxx-xxxxx`, guardados con HMAC, de un solo uso. Se gastan con `POST /api/v1/mfa/verify` y `method: "backup_code"`; la respuesta trae `backup_codes_remaining`.

---

## Variables de entorno

| Variable | Default | Uso |
|----------|---------|-----|
| `MFA_TOKEN_TTL_SEC` | `300` | Vida del `mfa_token` |
| `MFA_MAX_ATTEMPTS` | `5` | Códigos por `mfa_token` |
| `MFA_FAILURE_MAX` | `10` | Fallos por usuario en la ventana que bloquean su segundo factor |
| `MFA_FAILURE_WINDOW_SEC` | `900` | Ventana de `MFA_FAILURE_MAX` |
