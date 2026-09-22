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
    "secret": "whsec_..."
  }'
```

Accounts enviará POST a tu URL con payload del evento. Valida firma con el secret configurado.

---

## Eventos comunes

| Código | Cuándo |
|--------|--------|
| `accounts.user.signup` | Registro completado |
| `accounts.auth.login` | Login exitoso |
| `accounts.user.email_changed` | Email cambiado |

Lista completa: `GET /api/v1/webhooks/events`

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

Ver bodies exactos en [openapi.json](./openapi.json).
