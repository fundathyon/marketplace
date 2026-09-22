# API Keys y autenticación

## Tipos de credenciales

### 1. Publishable Key (`pk_live_...`)

- **Header:** `X-API-Key: pk_live_...`
- **Dónde:** Frontend, móvil, SPA
- **Para:** signup, signin, activate, OAuth link, magic link, refresh-jwt

### 2. Secret Key (`sk_live_...`)

- **Header:** `X-API-Key: sk_live_...`
- **Dónde:** Solo backend / CI / admin
- **Para:** roles, policies, behaviors, oauth-configs, revoke-refresh, webhooks
- **Nunca** en frontend ni repos públicos

### 3. Admin API Key

- **Header:** `X-Admin-API-Key: ...`
- **Para:** operaciones de sistema (`GET /v1/apps` listar todas las apps)

### 4. Access Token (JWT)

- **Header:** `Authorization: Bearer eyJ...`
- **Para:** endpoints de usuario autenticado (delete me, change email, etc.)

### 5. Refresh Token (JWT)

- **Header:** `Authorization: Bearer eyJ...` (el refresh, no el access)
- **Para:** `GET /api/v1/refresh-jwt`, `GET /api/v1/jwt/info`, validate-refresh
- **Además:** public key en refresh-jwt

## Nota sobre headers

El header aceptado es `X-API-Key` (también tolerado como `X-API-KEY` en algunos entornos). Usar siempre:

```http
X-API-Key: pk_live_...
Content-Type: application/json
```

## Matriz de autenticación

| Endpoint | Public | Secret | Admin | Bearer JWT | Bearer Refresh |
|----------|--------|--------|-------|------------|----------------|
| `POST /v1/apps` | — | — | — | — | — |
| `GET /v1/apps` | — | — | ✅ | — | — |
| `POST /api/v1/emails/signup` | ✅ | — | — | — | — |
| `POST /api/v1/emails/signin` | ✅ | — | — | — | — |
| `POST /api/v1/emails/activate` | ✅ | — | — | — | — |
| `GET /api/v1/oauths/link` | ✅ | — | — | — | — |
| `POST /api/v1/auth/social` | ✅ | — | — | — | — |
| `GET /api/v1/refresh-jwt` | ✅ | — | — | — | ✅ |
| `GET /api/v1/validate-access` | — | — | — | ✅ | — |
| `POST /api/v1/revoke-refresh` | — | ✅ | — | — | ✅ |
| `POST /api/v1/roles` | — | ✅ | — | — | — |
| `POST /api/v1/app-behaviors` | — | ✅ | — | — | — |
| `DELETE /api/v1/users/me` | ✅ | — | — | ✅ | — |
| `GET /api/v1/webhooks` | — | ✅ | — | — | — |

## Validar keys

```bash
# Public key
curl "{BASE_URL}/api/v1/api-keys/validate-public" \
  -H "X-API-Key: pk_live_..."

# Secret key
curl "{BASE_URL}/api/v1/api-keys/validate-secret" \
  -H "X-API-Key: sk_live_..."
```

## Generar nuevo par de keys (secret)

```bash
curl -X POST "{BASE_URL}/api/v1/api-keys/generate" \
  -H "X-API-Key: sk_live_..."
```

## Seguridad

- Rotar secret keys si se exponen
- Public key puede estar en el cliente
- Access token: memoria o storage seguro; evitar logs
- Refresh token: preferir HttpOnly cookie o secure storage en móvil
