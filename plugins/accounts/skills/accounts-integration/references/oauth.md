# OAuth — web redirect y native SDK

## Modos soportados

| Modo | Cuándo | Endpoints |
|------|--------|-----------|
| **Web redirect** | SPA, web clásica | `GET /oauths/link` → callback |
| **Native SDK** | iOS, Android | `POST /auth/social` |

Proveedores: Google, Apple, Microsoft, GitHub (según config).

---

## Configuración admin (secret key)

Antes de OAuth en cliente, configurar proveedor:

```bash
curl -X POST "{BASE_URL}/api/v1/oauth-configs" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "provider": "google",
    "client_id": "...",
    "client_secret": "...",
    "redirect_urls": ["https://tuapp.com/auth/callback"]
  }'
```

Gestión completa en `/api/v1/oauth-configs` (CRUD, disable, redirects, audiences).

Activar behavior OAuth en app si aplica vía `/api/v1/app-behaviors`.

---

## OAuth web — flujo redirect

### 1. Obtener URL de autorización (cliente)

```bash
curl -G "{BASE_URL}/api/v1/oauths/link" \
  -H "X-API-Key: {publishable_key}" \
  --data-urlencode "provider=google" \
  --data-urlencode "redirect_uri=https://tuapp.com/auth/callback"
```

Respuesta: URL del proveedor → redirigir al usuario.

### 2. Callback

El proveedor redirige a Accounts:

```
GET {BASE_URL}/api/v1/oauth/{callback_key}?code=...&state=...
```

**Sin API key** — es redirect del proveedor OAuth.

Accounts procesa el código y devuelve tokens o redirige a tu app con tokens en query/fragment según config.

### 3. Link admin alternativo

Con secret key para obtener link desde backend admin:

```
GET {BASE_URL}/api/v1/oauth-configs/link
Header: X-API-Key: sk_...
```

---

## OAuth native SDK

Frontend obtiene `id_token` del SDK nativo (Sign in with Apple, Google Sign-In, etc.):

```bash
curl -X POST "{BASE_URL}/api/v1/auth/social" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "provider": "google",
    "id_token": "eyJ..."
  }'
```

### Audiences nativas (admin)

Whitelist de `aud` del id_token por plataforma:

```bash
curl -X POST "{BASE_URL}/api/v1/oauth-configs/{config_id}/audiences" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "audience": "com.tuapp.clientid", "platform": "ios" }'
```

---

## Respuesta típica (tokens)

Igual que signin email:

```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

---

## Errores OAuth comunes

| Scope / situación | Acción |
|-------------------|--------|
| Provider no configurado | Configurar oauth-configs |
| Redirect URI mismatch | Añadir URL en oauth-configs redirects |
| id_token aud inválido | Configurar native audiences |
| Cuenta existente | Link identity o signin email |

---

## Diagrama web

```
Tu app → GET /oauths/link → redirect proveedor
       → usuario autoriza
       → GET /oauth/{callback_key}
       → tokens → tu app autenticada
```

Ver también [auth-flows.md](auth-flows.md).
