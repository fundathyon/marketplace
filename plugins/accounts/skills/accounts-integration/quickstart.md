# Quickstart — Foundathon Accounts

Flujo mínimo para autenticar un usuario en **5 minutos**.

## Prerrequisitos

- API Accounts desplegada y accesible
- `{BASE_URL}` = host + `ROOT_PATH` (ej. `http://localhost:8000/accounts`)

## Paso 1 — Crear aplicación

Sin autenticación. Crea app, API keys, rol `default` y behavior email sin verificación.

```bash
curl -X POST "{BASE_URL}/v1/apps" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi App",
    "root_email": "admin@example.com"
  }'
```

**Respuesta 201** — guardar:

| Campo | Uso |
|-------|-----|
| `publishable_key` (`pk_live_...`) | Cliente: signup, signin, OAuth |
| `secret_key` (`sk_live_...`) | Servidor: admin, revoke, behaviors |
| `id` | ID de la app |

**Importante:** El `secret_key` solo se muestra **una vez**. Guárdalo en secrets del servidor.

## Paso 2 — Registrar usuario

Con behavior email simple (default), no hace falta activación por email.

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signup" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "usuario@example.com",
    "password": "SecurePass123!",
    "role": "default"
  }'
```

Campos:

| Campo | Requerido | Notas |
|-------|-----------|-------|
| `email` | Sí | Se normaliza según behavior |
| `password` | Sí | Debe cumplir password policy |
| `role` | Sí | Ej. `default` (creado al registrar app) |
| `user_name` | No | Opcional |
| `metadata` | No | Si metadata schema está activo |

## Paso 3 — Iniciar sesión

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "usuario@example.com",
    "password": "SecurePass123!"
  }'
```

**Respuesta 200:**

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  },
  "trace_id": "..."
}
```

Algunas respuestas usan `jwt` en lugar de `access_token` — son equivalentes.

## Paso 4 — Usar access token

```bash
curl -X GET "{BASE_URL}/api/v1/validate-access" \
  -H "Authorization: Bearer {access_token}"
```

## Paso 5 — Refrescar sesión

```bash
curl -X GET "{BASE_URL}/api/v1/refresh-jwt" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {refresh_token}"
```

## Resumen del flujo

1. `POST /v1/apps` → keys
2. `POST /api/v1/emails/signup` → usuario
3. `POST /api/v1/emails/signin` → tokens
4. `GET /api/v1/refresh-jwt` → renovar access

## Siguientes pasos

- Verificación email ON → [email-auth.md](./email-auth.md) + [behaviors.md](./behaviors.md)
- OAuth → [oauth.md](./oauth.md)
- Magic link → [magic-link.md](./magic-link.md)
- Errores → [error-scopes.md](./error-scopes.md)
