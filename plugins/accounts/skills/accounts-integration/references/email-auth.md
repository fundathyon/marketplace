# Email auth — endpoints completos

Todas las rutas requieren `X-API-Key: {publishable_key}` salvo indicación contraria.

Base: `{BASE_URL}/api/v1/emails`

---

## POST /login — login unificado

Un solo formulario: la API detecta signup vs signin.

```bash
curl -X POST "{BASE_URL}/api/v1/emails/login" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "role": "default"
  }'
```

`role` requerido si es signup nuevo.

---

## POST /signup — registro

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signup" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "role": "default",
    "user_name": "Nombre"
  }'
```

| verification OFF | verification ON |
|------------------|-----------------|
| Usuario activo de inmediato | Código enviado por email |
| Puede devolver tokens | Requiere `/activate` antes de signin |

`locale` (opcional, BCP 47: `"es"`, `"es-MX"`) elige el idioma del correo y
queda como idioma preferido del usuario; sin él cuenta `Accept-Language`. Lo
aceptan también `/signup/resend-code`, `/reset`, `/magic-link/request` y
`/email-code/request`. Ver [email-locale.md](email-locale.md).

---

## Intentos y reenvíos de los códigos

Los códigos de activación, reset, cambio de correo y registro delegado admiten
**5 intentos**, contando el correcto. Un código equivocado responde el error de
siempre con `error.meta.remaining_attempts`; el quinto lo bloquea con un scope
`…too_many_attempts` y desde ahí hay que pedir otro. Pedir un código nuevo
invalida los anteriores, y cada usuario puede pedir hasta **5 por tipo cada 15
minutos**: en reset y en el reenvío de activación, pasado ese tope no sale
ningún código pero la respuesta es la genérica de siempre (no dice si la cuenta
existe). El límite previo por cuenta (10 cada 15 minutos) y por IP responde
`429 auth.rate_limited`. Ver `error-scopes.md`.

---

## POST /signup/resend-code

Reenvía código de activación (verification ON). Invalida el anterior. Responde
siempre `201` con el mismo mensaje genérico, exista o no la cuenta, esté activa o
haya pedido ya 5 códigos en 15 minutos (entonces no sale ninguno): no sirve para
saber si un correo tiene cuenta. El límite por cuenta/IP responde
`429 auth.rate_limited` con `Retry-After`.

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signup/resend-code" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "email": "user@example.com" }'
```

---

## POST /signin — inicio de sesión

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Respuesta exitosa: `access_token`/`jwt`, `refresh_token`, opcional `expires_in`.

Errores: `401 emails.signin.invalid_credentials` tanto si el correo no tiene
cuenta como si la contraseña es mala (misma respuesta y mismo tiempo: mostrar
«email o contraseña incorrectos»). Tras 10 contraseñas fallidas en 15 minutos la
cuenta se bloquea 1, 5 y 15 minutos: `429 auth.rate_limited` con
`error.meta.retry_after_seconds` y `Retry-After`, también para correos sin
cuenta. Cada fallo sale como el webhook `accounts.auth.login_failed`
(`data.reason`: `bad_password`, `unknown_account`, `rate_limited`).

---

## POST /signin/resend-code

Usuario existe pero no verificó email — reenviar código desde pantalla de login.

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signin/resend-code" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "email": "user@example.com" }'
```

---

## POST /activate — activar cuenta

Tras signup con verification ON:

```bash
curl -X POST "{BASE_URL}/api/v1/emails/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "user@example.com",
    "code": "123456"
  }'
```

Devuelve tokens en éxito. Luego el usuario puede hacer signin si no vienen tokens.

---

## POST /activate/v2 (Pro)

Flujo de activación v2 — edición Pro. El registro lo crea antes el backend de
la app con `POST /api/v1/pending-registrations` y su **secret key** (`email`,
`user_name`, `role`); el rol se busca entre los roles de esa app. El usuario
recibe el código por correo y lo canjea aquí con la **publishable key** de la
misma app: un registro de otra app responde `404
emails.activate_v2.error_pending_registration_not_found`.

## POST /activate/v2/set-password (Pro)

Establecer contraseña post-activación v2 — requiere Bearer JWT.

---

## Reset de contraseña

### 1. Solicitar reset

```bash
curl -X POST "{BASE_URL}/api/v1/emails/reset" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "email": "user@example.com" }'
```

### 2. Validar código

```bash
curl -X POST "{BASE_URL}/api/v1/emails/reset/validate-code" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "email": "user@example.com", "code": "123456" }'
```

### 3. Establecer nueva contraseña

```bash
curl -X POST "{BASE_URL}/api/v1/emails/reset/set-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {temporary_jwt}" \
  -d '{ "password": "NewSecurePass123!" }'
```

Alternativa legacy: `POST /reset-confirm`

`validate-code` y `reset-confirm` comparten los 5 intentos del código, y en
`validate-code` cuenta también la validación correcta: basta con validar una
vez y guardar el `temporary_jwt`.

- Código y token de **un solo uso** (consumo atómico); el código vence a los
  minutos que dice el correo (10 por defecto).
- La contraseña pasa la política de `email_auth` (`422
  emails.validation.weak_password`) y, con `password.policy.check_breached`
  (true en apps nuevas, false en existentes), la comprobación de contraseñas
  filtradas (`400 password.breached`). Ninguno de los dos gasta el código.
- `set-password` devuelve `data.login`; si no puede abrir la sesión responde
  200 sin `data.login` (la contraseña ya cambió). `reset-confirm` nunca
  devuelve tokens.
- Al terminar: sesiones cerradas según el behavior, correo
  `password_changed_notice` y webhook `accounts.user.password_reset`.

---

## Flujo visual (verification ON)

```
signup → email con código → activate → signin → tokens
```

## Flujo visual (verification OFF)

```
signup → signin → tokens
```

Ver [behaviors.md](behaviors.md) y [auth-flows.md](auth-flows.md).
