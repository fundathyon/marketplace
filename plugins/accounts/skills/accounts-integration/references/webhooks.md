# Webhooks

Notificaciones HTTP desde Accounts hacia tu backend cuando ocurren eventos de dominio.

## Listar eventos disponibles (público)

```bash
curl "{BASE_URL}/api/v1/webhooks/events"
```

Respuesta ejemplo:

```json
{
  "success": true,
  "data": {
    "User": [
      { "code": "accounts.user.signup", "description": "New user signup" }
    ],
    "Auth": [
      { "code": "accounts.auth.login", "description": "Successful login" }
    ]
  }
}
```

---

## CRUD webhooks (secret key)

```bash
# Listar
curl "{BASE_URL}/api/v1/webhooks" \
  -H "X-API-Key: {secret_key}"

# Crear
curl -X POST "{BASE_URL}/api/v1/webhooks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "url": "https://tu-backend.com/webhooks/accounts",
    "events": ["accounts.user.signup", "accounts.auth.login"],
    "secret": "whsec_...",
    "retries": 3,
    "min_interval_ms": 2500,
    "backoff": "linear",
    "honor_retry_after": true
  }'

# Ajustar la entrega (PATCH parcial)
curl -X PATCH "{BASE_URL}/api/v1/webhooks/{id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"min_interval_ms": 2500, "backoff": "exponential"}'
```

Accounts enviará POST a tu URL con payload del evento y el secret en `X-Webhook-Secret`.

## Entrega en cola

Los envíos a un mismo webhook salen **uno tras otro y en orden** (no en paralelo), con la política del webhook:

| Campo | Default | Efecto |
|-------|---------|--------|
| `retries` | 3 | Reintentos tras el primer intento (0–10) |
| `min_interval_ms` | 0 | Espacio mínimo entre dos peticiones (0–60000) |
| `backoff` | `linear` | `linear` 1 s, 2 s, 3 s… · `exponential` 2 s, 4 s, 8 s… |
| `honor_retry_after` | `true` | Ante `429`/`503` con `Retry-After`, esperar eso antes del reintento y del siguiente envío (tope 10 min) |

Si tu receptor tiene rate limit (p. ej. 30/min), configura `min_interval_ms` (2500) y responde `429` con `Retry-After`. La cola vive en memoria: un reinicio pierde lo pendiente, así que tu receptor debe tolerar huecos y duplicados (entrega al menos una vez).

---

## Eventos comunes

| Código | Cuándo |
|--------|--------|
| `accounts.user.signup` | Registro completado |
| `accounts.auth.login` | Login exitoso |
| `accounts.user.email_changed` | Email cambiado |
| `accounts.user.deleted` | Usuario eliminado (solo si el webhook se suscribe; ninguno por default) |

Lista completa: `GET /api/v1/webhooks/events`

---

## Payload de `accounts.user.signup`

```json
{
  "type": "accounts.user.signup",
  "source": "tester",
  "app_id": "…",
  "data": {
    "user": {
      "id": "…",
      "name": "qa_1",
      "email": "qa_1@getfoundathyon.mock",
      "is_test": true,
      "expires_at": "2026-09-30T18:00:00Z"
    },
    "auth": { "id": "…", "method": "email", "is_verify": true, "source": "tester" },
    "roles": ["default"]
  }
}
```

- `data.user.is_test` y `data.user.expires_at` van **siempre** (`false` / `null` para una persona).
- `data.auth.source: "tester"` solo cuando el usuario nació por el módulo de testers; un lote de N dispara N eventos.
- Filtra por `is_test` para no contar testers como altas reales. Ver [testers.md](testers.md).

---

## Payload de `accounts.user.deleted`

```json
{
  "id": "…",
  "type": "accounts.user.deleted",
  "source": "accounts",
  "created_at": "2026-09-23T18:00:00Z",
  "app_id": "…",
  "data": {
    "user": { "id": "…", "email": "qa_7@getfoundathyon.mock", "name": "…", "is_test": true },
    "deleted_at": "2026-09-23T18:00:00Z",
    "initiated_by": "admin"
  }
}
```

- `initiated_by`: `admin` (secret key: `DELETE /users/{id}`, testers y sus trabajos), `user` (`DELETE /users/me`), `api` (otro origen).
- El usuario ya no existe al recibirlo: usa `data.user.id` para borrar lo tuyo; `email` es su primer correo (o el del login social).
- Autenticado con `X-Webhook-Secret`, igual que el alta.

---

## Integración típica

```
Cliente → Accounts (signup/signin)
Accounts → Event bus interno
Accounts → POST tu-webhook-url (async)
Tu backend → procesa evento (analytics, CRM, etc.)
```

Los webhooks **no reemplazan** el manejo de tokens en el cliente.

---

## Auth

| Endpoint | Auth |
|----------|------|
| `GET /webhooks/events` | Ninguna |
| `GET/POST/PATCH/DELETE /webhooks` | Secret key |

Ver bodies exactos en [openapi.json](../assets/openapi.json).
