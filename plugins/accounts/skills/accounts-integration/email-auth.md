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

---

## POST /signup/resend-code

Reenvía código de activación (verification ON).

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

Flujo de activación v2 — edición Pro.

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

---

## Flujo visual (verification ON)

```
signup → email con código → activate → signin → tokens
```

## Flujo visual (verification OFF)

```
signup → signin → tokens
```

Ver [behaviors.md](./behaviors.md) y [auth-flows.md](./auth-flows.md).
