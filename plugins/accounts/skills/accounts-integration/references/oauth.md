# OAuth — web redirect y native SDK

## Modos soportados

| Modo | Cuándo | Endpoints |
|------|--------|-----------|
| **Web redirect** | SPA, web clásica | `GET /oauths/link` → `/oauth/{callback_key}/start` → proveedor → callback |
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

### 1. Obtener el enlace (cliente)

```bash
curl -G "{BASE_URL}/api/v1/oauths/link" \
  -H "X-API-Key: {publishable_key}" \
  --data-urlencode "provider=google" \
  --data-urlencode "platform=web" \
  --data-urlencode "redirect_url=https://tuapp.com/auth/callback"
```

Respuesta (`data`): la URL de inicio del flujo en Accounts, en el host del
callback: `…/api/v1/oauth/{callback_key}/start?platform=web&rt=…`. **Navega a
ella** (`window.location`, Custom Tabs, `ASWebAuthenticationSession`): no la
llames por XHR ni armes la URL del proveedor a mano.

### 2. Inicio del flujo

`GET /api/v1/oauth/{callback_key}/start` (sin API key) emite un `state`
aleatorio de un solo uso (15 minutos), deja una cookie `HttpOnly` y
`SameSite=Lax` que ata el login a ese navegador y responde `302` al proveedor
con el `state` y el `code_challenge` de PKCE (S256; Apple no documenta PKCE).

### 3. Callback

El proveedor redirige a Accounts:

```
GET {BASE_URL}/api/v1/oauth/{callback_key}?code=...&state=...
```

**Sin API key** — es redirect del proveedor OAuth. El callback solo sigue con
un `state` que emitió el inicio, sin usar, vigente y con la cookie del mismo
navegador; canjea el código con el `code_verifier` y redirige a tu app con
`access_token`, `refresh_token` y `provider` en la query (modo `query`, apps
existentes) o con `code` y `provider` (modo `code`, apps nuevas: canjea el code
con `POST /api/v1/oauth/exchange` + publishable key, una vez y en < 60 s). Lo
decide el behavior `session_security` — ver [session-security.md](session-security.md).

**Segundo factor pendiente** (behavior `mfa`): en vez de tokens, la query lleva
`mfa_required=true&mfa_methods=totp,backup_code&mfa_token=…&provider=…` (o
`mfa_enrollment_required=true&mfa_token=…&provider=…`). Tu página completa con
`POST /api/v1/mfa/verify` (o `/mfa/enroll/*`) y recibe los tokens en el cuerpo.
Ver [mfa.md](mfa.md).

| Scope | HTTP | Qué pasó |
|-------|------|----------|
| `oauths.callback.invalid_state` | 400 | `state` desconocido, vencido o ya usado: empezar el login otra vez |
| `oauths.callback.state_mismatch` | 403 | El login se empezó en otro navegador (o se perdió la cookie) |
| `oauths.start.rt_not_found` | 400 | El `rt` no es un destino de esa configuración y plataforma |

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

### Nonce (recomendado)

Ata cada `id_token` a un intento de login: un token robado o repetido no abre otra sesión.

1. `POST {BASE_URL}/api/v1/auth/social/nonce` con la publishable key → `201 {nonce, expires_in: 600}`.
2. Pasar al SDK el **SHA-256 en hex** del nonce (Sign in with Apple: `request.nonce`) o el valor tal cual (Google Sign-In). Accounts acepta las dos formas.
3. Mandar el nonce **en claro** en el campo `nonce` de `POST /api/v1/auth/social`.

Cada nonce sirve una sola vez y vence en 10 minutos. Sin `nonce` en la petición el login sigue funcionando, salvo que la config del proveedor tenga `require_nonce: true` (`PATCH /api/v1/oauth-configs/{id}`, default `false`). Errores: `auth.social.nonce_required`, `auth.social.nonce_mismatch`, `auth.social.nonce_invalid` ([error-scopes.md](error-scopes.md)).

Con segundo factor pendiente responde `200` con `{mfa_required | mfa_enrollment_required, mfa_token, methods, expires_in}` y sin `user` ni tokens → `/api/v1/mfa/*` ([mfa.md](mfa.md)).

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
