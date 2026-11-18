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
- **Formato:** `sk_<env>_<key_id>_<aleatorio>`. Desde 0.14.0 la publishable del mismo par lleva **otro** id (`pk_<env>_<publishable_key_id>_…`): no derives el `key_id` de la secret a partir de la publishable. Las claves anteriores conservan el id compartido y siguen valiendo
- **Scopes (revisión 21):** cada secret key lleva scopes. La key inicial de la app y todas las que existían tienen `"*"` (poder total). Una key nueva puede limitarse (`"scopes": ["users:read"]`); sin el scope de la ruta → `403 api_keys.scope_denied` con `error.meta.required_scope`. Ver [Scopes de secret keys](#scopes-de-secret-keys)
- **Límites:** 10 secret keys inválidas cada 5 min por IP o por `key_id` → `429 api_keys.rate_limited` (`Retry-After`). Una clave anterior a 0.14.0 puede responder una vez `503 api_keys.verifier_busy` (`Retry-After: 1`) mientras se reescribe: reintentar

### 3. Admin API Key

- **Header:** `X-Admin-API-Key: ...`
- **Para:** operaciones de sistema (`GET /v1/apps` listar todas las apps)

### 4. Access Token (JWT)

- **Header:** `Authorization: Bearer eyJ...`
- **Para:** endpoints de usuario autenticado (delete me, change email, mis sesiones, etc.)

### 5. Refresh Token (JWT)

- **Header:** `Authorization: Bearer eyJ...` (el refresh, no el access)
- **Para:** `GET /api/v1/refresh-jwt`, validate-refresh, `POST /api/v1/logout`
- **Además:** public key en refresh-jwt; logout no lleva API key

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
| `POST /api/v1/logout` | — | — | — | — | ✅ |
| `POST /api/v1/revoke-refresh` | — | ✅ | — | — | ✅ |
| `GET /api/v1/users/me/sessions` | ✅ | — | — | ✅ | — |
| `DELETE /api/v1/users/me/sessions/:id` | ✅ | — | — | ✅ | — |
| `GET /api/v1/users/:id/sessions` | — | ✅ | — | — | — |
| `POST /api/v1/roles` | — | ✅ | — | — | — |
| `POST /api/v1/app-behaviors` | — | ✅ | — | — | — |
| `DELETE /api/v1/users/me` | ✅ | — | — | ✅ | — |
| `DELETE /api/v1/users` | ✅ | — | — | ✅ | — |
| `GET /api/v1/webhooks` | — | ✅ | — | — | — |
| `GET`/`PUT /api/v1/app-behaviors/embedded-auth` (Pro) | — | ✅ | — | — | — |
| `GET /api/v1/embedded-auth/config` (Pro) | ✅ | — | — | — | — |

### Componente embebido (Pro)

Las peticiones de los componentes de [Embedded Auth](embedded-auth.md) no usan `X-API-Key` ni `Authorization`: mandan `X-Accounts-Client: embedded/1`, la publishable key en `X-Accounts-Publishable-Key` y los tokens en `X-Accounts-Authorization: Bearer …`. Un gate valida la key y el `Origin` contra `allowed_origins` y las traduce a `X-API-Key` / `Authorization`, así que la matriz de arriba aplica igual. Sin esas cabeceras nada cambia.

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

## Listar keys y claves expuestas

```bash
curl "{BASE_URL}/api/v1/api-keys?page=0&size=10" \
  -H "X-API-Key: sk_live_..."
```

Cada item (nunca trae `secret_key` ni `secret_hash`) lleva **`"exposed": bool`** y **`"exposed_at": "<RFC 3339>" | null`** (nunca se omite). La revisión 17 marcó como expuestas todas las secret keys que existían (core podía mostrarlas antes de core v1.16.0). Una key expuesta **sigue funcionando**: hay que rotarla.

```bash
# Rotar: mismo id, nombre y descripción; par nuevo; el anterior deja de servir ya
curl -X POST "{BASE_URL}/api/v1/api-keys/{id}/rotate" \
  -H "X-API-Key: sk_live_..."
```

La respuesta de `rotate`, la de `generate` y la de `POST /v1/apps` (key inicial) traen `"exposed": false, "exposed_at": null`. La `secret_key` nueva solo se devuelve en esa respuesta.

## Scopes de secret keys

`GET /api/v1/api-keys/scopes` devuelve el catálogo `{"data":[{"id","group","description"}]}` (incluye `"*"`). Cada key de la lista, del detalle (`GET /api/v1/api-keys/{id}`), de `generate` y de `rotate` trae `"scopes": ["*"]` o su lista; `validate-secret` devuelve los de la key que llama.

```bash
# Key acotada: solo lee usuarios
curl -X POST "{BASE_URL}/api/v1/api-keys/generate" \
  -H "X-API-Key: sk_live_..." -H "Content-Type: application/json" \
  -d '{"name":"Backend lectura","scopes":["users:read"]}'

# Cambiar scopes (y/o name, description)
curl -X PATCH "{BASE_URL}/api/v1/api-keys/{id}" \
  -H "X-API-Key: sk_live_..." -H "Content-Type: application/json" \
  -d '{"scopes":["users:read","users:write"]}'
```

Reglas:

- Sin `scopes` (o con `[]`), `generate` crea la key con `"*"` (como antes). Un scope desconocido, o `[]` en `PATCH` → `400 api_keys.invalid_scopes`
- Solo `"*"` o `api_keys:write` gestionan keys (`api_keys:read` para leerlas y para `validate-secret`)
- Sin escalada: una key no crea, rota, edita, desactiva ni borra otra con scopes que ella no tiene → `403 api_keys.scope_escalation` (`error.meta.missing_scopes`)
- La última key activa con `"*"` de la app no puede perderlo → `409 api_keys.last_full_access_key`
- Los scopes son independientes (`users:write` no incluye `users:read`); `"*"` alcanza para todo
- La publishable key no cambia

| Scope | Rutas (secret key) |
|-------|--------------------|
| `api_keys:read` / `api_keys:write` | `/api/v1/api-keys/*` (leer · generar, editar, rotar, desactivar, borrar) |
| `apps:write` | `PATCH /api/v1/apps` |
| `audit:read` | `GET /api/v1/audit-logs` |
| `authorize` | `POST /api/v1/authorize` |
| `behaviors:read` / `behaviors:write` | `/api/v1/app-behaviors/*`, `/api/v1/user-metadata-policy` |
| `dashboard:read` | `GET /api/v1/dashboard-stats` |
| `email:read` / `email:write` | `/api/v1/email-config`, `/api/v1/email-templates/*`, `/api/v1/email-access/*` |
| `jwt:read` | `GET /api/v1/system/public-key-jwt` (Pro) |
| `login_events:read` | `GET /api/v1/login-events`, `/summary` |
| `mcp:read` / `mcp:write` | `/v1/mcp-resources/*`, `/v1/mcp/authorization-requests/*`, `/v1/mcp/connections/*` |
| `mcp:introspect` | `POST /o/{app_id}/oauth/introspect` |
| `oauth:read` / `oauth:write` | `/api/v1/oauth-configs/*` (configs, redirects, audiencias nativas) |
| `roles:read` / `roles:write` | `/api/v1/roles`, `/api/v1/policies`, `/api/v1/role-policies` (y `role_policies`) |
| `sessions:read` / `sessions:write` | `GET /api/v1/users/{id}/sessions` · `/api/v1/revoke-refresh` |
| `testers:read` / `testers:write` | `/api/v1/testers/*` (ver credenciales y emitir tokens es `testers:write`) |
| `users:read` / `users:write` | `/api/v1/users` (listar, buscar y `GET /users/{id}` · crear, borrar, rol, contraseña, verificación, metadata), `POST /api/v1/pending-registrations` |
| `webhooks:read` / `webhooks:write` | `/api/v1/webhooks/*` |

Lectura (`GET`, previews y tests que no guardan) va con `:read`; lo que cambia algo, con `:write`. Tabla exacta ruta por ruta: `docs/api-docs/tokens-and-security/api-key-scopes.mdx`.

## Seguridad

- Dale a cada backend una key con solo los scopes que usa; deja `"*"` para la administración
- Rotar secret keys si se exponen o si `exposed: true` (la rotación también las pasa al formato nuevo: HMAC e ids separados)
- Public key puede estar en el cliente
- Access token: memoria o storage seguro; evitar logs
- Refresh token: preferir HttpOnly cookie o secure storage en móvil
