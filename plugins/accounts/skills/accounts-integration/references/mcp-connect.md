# MCP Connect — login OAuth 2.1 para servidores MCP

Deja que Claude, ChatGPT, Claude Code y cualquier cliente MCP entren al servidor MCP de tu app con el login de tus propios usuarios. Accounts es el **servidor de autorización OAuth 2.1**; tú pones **tu página de login y aprobación** y tu servidor MCP valida las llaves con la llave pública de Accounts. No hay pantallas hospedadas.

Requiere que la instancia tenga `OAUTH_PUBLIC_URL` configurada; sin ella las rutas de esta sección no existen (404).

## Tres rutas distintas, tres contratos

| Prefijo | Quién llama | Auth | Formato |
|---------|-------------|------|---------|
| `{BASE_URL}/v1/mcp-resources`, `{BASE_URL}/v1/mcp/...` | Tu backend | `X-API-Key: sk_...` (secret) | Sobre de Accounts `{success, data, error}` |
| `{BASE_URL}/api/v1/me/mcp-connections` | Tu frontend | `X-API-Key: pk_...` + `Authorization: Bearer <access token>` | Sobre de Accounts |
| `{BASE_URL}/o/{app_id}/oauth/*`, `/o/{app_id}/userinfo`, `/.well-known/*` | El asistente (Claude, ChatGPT) | Ninguna (clientes públicos) | **OAuth puro**: form-urlencoded, JSON plano, `{"error": "...", "error_description": "..."}` |

**No llames tú a las rutas `/o/{app_id}/oauth/*`** desde tu integración: son para el asistente. Tu trabajo es registrar el recurso, poner dos valores en tu servidor MCP y construir la página de conexión.

## 1. Registrar tu servidor MCP (una vez)

```bash
curl -X POST "{BASE_URL}/v1/mcp-resources" \
  -H "X-API-Key: {secret_key}" -H "Content-Type: application/json" \
  -d '{
    "resource_url": "https://api.tuapp.com/mcp",
    "login_url": "https://app.tuapp.com/conectar",
    "scopes": [
      {"key": "plans:read",   "label": "Ver planes"},
      {"key": "dishes:write", "label": "Editar platillos", "is_write": true, "roles": ["kitchen"]}
    ]
  }'
```

Respuesta 201 `data`:

| Campo | Para qué |
|-------|----------|
| `id` | El recurso. |
| `issuer` | `{OAUTH_PUBLIC_URL}/o/{app_id}`. **Va a tu servidor MCP.** |
| `resource_url` | URL canónica (https, sin query, sin barra final). **Va a tu servidor MCP** y es lo que la persona pega en su asistente. |
| `protected_resource_metadata_url` | Dónde tu servidor debe publicar su documento RFC 9728. |
| `metadata_url`, `jwks_url` | Metadata RFC 8414 y llaves públicas del emisor. |
| `scopes[]` | `key`, `label`, `description`, `is_write`, `is_default`, `roles`. |
| `cimd_enabled`, `dcr_enabled` | Cómo se registran los asistentes (ambos `true` por defecto). |
| `allowed_redirect_domains` | Default `["claude.ai","chatgpt.com"]`; loopback siempre permitido. |
| `allowed_client_domains` | Vacío = cualquier ficha CIMD. |
| `access_ttl_seconds` | 300–86400, default 3600. |

Reglas de los scopes: `key` `^[a-z0-9][a-z0-9:._-]{0,63}$`, única; `label` obligatorio (≤ 80); `roles` deben existir en la app; `openid`, `email`, `profile` y `offline_access` están reservados. Sin `scopes` el recurso nace con `account:access` («Acceder a tu cuenta»). **Accounts no deduce scopes de la URL: los declaras tú.**

Otras rutas (todas con secret key): `GET /v1/mcp-resources`, `GET|PATCH|DELETE /v1/mcp-resources/{id}`, `PUT /v1/mcp-resources/{id}/scopes` (`{"scopes":[...]}` reemplaza la lista), `POST /v1/mcp-resources/{id}/verify` (sondea tu servidor y reporta `checks[]`), `POST|GET /v1/mcp-resources/{id}/clients` y `POST /v1/mcp-resources/{id}/clients/disable` (`{"client_id": "..."}`).

## 2. Configurar tu servidor MCP

Dos valores: `issuer` y `resource_url`. En Go usa el módulo `github.com/fundathyon/accounts/connect`:

```go
handler := connect.Protect(connect.Config{Issuer: issuer, Resource: resourceURL, ScopesSupported: []string{"plans:read", "dishes:write"}})(mux)
```

En otro lenguaje implementa el contrato: publicar `GET {origen}/.well-known/oauth-protected-resource{ruta}` con `{"resource", "authorization_servers": [issuer], "scopes_supported"}`; responder **401** con `WWW-Authenticate: Bearer resource_metadata="<esa URL>", scope="..."` a toda petición sin token válido; validar el JWT (RS256 vía `{issuer}/.well-known/jwks.json`, `typ at+jwt`, `iss` = issuer, `aud` = resource_url, `exp`); exigir el scope por herramienta con `403` + `WWW-Authenticate: Bearer error="insufficient_scope", scope="..."`. Nunca reenvíes ese token a otra API.

Comprueba con `POST /v1/mcp-resources/{id}/verify`.

## 3. Construir la página de conexión (`login_url`)

Accounts manda ahí al navegador con `?request={id}`. La solicitud vive 10 minutos.

1. Exige sesión en tu app (tu login de siempre).
2. Desde tu backend, lee la solicitud:

```bash
curl "{BASE_URL}/v1/mcp/authorization-requests/{request}" \
  -H "X-API-Key: {secret_key}" -H "X-User-Token: {access_token_de_la_persona}"
```

`data`: `status` (`pending|approved|denied|consumed|expired`), `client` (`client_id`, `kind`, `name`, `client_uri`, `logo_uri` solo si es del dominio del cliente), `redirect_host`, `scopes[]` (`key`, `label`, `description`, `is_write`, `roles`, y `allowed` si mandaste `X-User-Token`), `existing_connection` (`id`, `scope`, `granted_at`) si la persona ya tiene una conexión activa con ese cliente.

3. Muestra `client.name`, `redirect_host` y los scopes con `allowed: true`. Si `existing_connection.scope` ya cubre lo pedido puedes aprobar sin preguntar.
4. Aprueba o niega desde tu backend y manda el navegador a `redirect_to`:

```bash
curl -X POST "{BASE_URL}/v1/mcp/authorization-requests/{request}/approve" \
  -H "X-API-Key: {secret_key}" -H "Content-Type: application/json" \
  -d '{"user_token": "{access_token_de_la_persona}", "scope": "plans:read"}'
# → {"data": {"redirect_to": "https://claude.ai/api/mcp/auth_callback?code=...&state=...&iss=..."}}

curl -X POST "{BASE_URL}/v1/mcp/authorization-requests/{request}/deny" -H "X-API-Key: {secret_key}"
# → {"data": {"redirect_to": "...?error=access_denied&state=...&iss=..."}}
```

Solo se puede **quitar** scopes, nunca añadir; un scope con `roles` que el rol de la persona no cubre se rechaza aunque lo hayas mostrado.

## 4. Conexiones

```bash
# Backend (secret key): listar y revocar. Filtros: resource_id, user_id, email, client_id, status, page, size (≤100).
# Cada conexión trae la persona: user {id, email, name, is_test}.
curl "{BASE_URL}/v1/mcp/connections?status=active" -H "X-API-Key: {secret_key}"
curl "{BASE_URL}/v1/mcp/connections?email=ana@example.com" -H "X-API-Key: {secret_key}"
curl "{BASE_URL}/v1/mcp/connections/{id_o_sid}" -H "X-API-Key: {secret_key}"
# Conexiones activas por usuario (≤100 ids), para una columna en una tabla de usuarios
curl "{BASE_URL}/v1/mcp/connections/summary?user_ids={id1},{id2}" -H "X-API-Key: {secret_key}"
curl -X DELETE "{BASE_URL}/v1/mcp/connections/{id}" -H "X-API-Key: {secret_key}"

# Frontend (publishable key + access token): las de la propia persona
curl "{BASE_URL}/api/v1/me/mcp-connections" -H "X-API-Key: {publishable_key}" -H "Authorization: Bearer {access_token}"
curl -X DELETE "{BASE_URL}/api/v1/me/mcp-connections/{id}" -H "X-API-Key: {publishable_key}" -H "Authorization: Bearer {access_token}"
```

Cada conexión: `id`, `resource {id,name,resource_url}`, `client {client_id,kind,name}`, `user_id`, `session_id`, `scope[]`, `status`, `granted_at`, `last_used_at`, `revoked_at`, `revoked_reason` (`owner|user|client|code_replay|refresh_reuse|session_revoked`). Nunca tokens.

Revocar cierra la sesión: el siguiente refresh del asistente falla. El access token vigente muere solo al vencer (≤ `access_ttl_seconds`); para cortarlo antes, tu servidor MCP usa `POST {issuer}/oauth/introspect` con la secret key (`token=<jwt>` form-urlencoded → `{"active": true|false, ...}`).

## 5. Lo que ve el asistente (para entender los logs)

`POST resource_url` → 401 → lee el documento RFC 9728 → lee `{issuer}/.well-known/oauth-authorization-server` → se presenta con su ficha pública (CIMD, `client_id` = URL https) o se registra (`POST {issuer}/oauth/register`) → `GET {issuer}/oauth/authorize` → **tu página** → `POST {issuer}/oauth/token` (`authorization_code` + PKCE S256; luego `refresh_token`, que rota siempre) → `GET {issuer}/userinfo` si pidió `openid email`.

Access token de recurso: `iss` = issuer, `aud` = resource_url, claims `scope`, `client_id`, `sid`, `user_id`, `role`, `email`. **`/api/v1/validate-access` y `/api/v1/jwt/info` lo rechazan a propósito.**

## Webhooks

`accounts.mcp.resource.created|updated|deleted`, `accounts.mcp.client.registered`, `accounts.mcp.connection.granted`, `accounts.mcp.connection.revoked` (con `reason`), `accounts.mcp.authorization.denied`. Sin códigos ni tokens en el payload.

## Errores (scope)

| Scope | Significado |
|-------|-------------|
| `mcp_resources.invalid_resource_url` / `invalid_login_url` / `invalid_access_ttl` | 422, dato inválido |
| `mcp_resources.duplicate_resource_url` | 409, la app ya registró esa URL |
| `mcp_resources.invalid_scope_key` / `duplicate_scope_key` / `invalid_scope_label` / `unknown_role` | 422 |
| `mcp_resources.not_found` | 404, no existe o es de otra app |
| `mcp_resources.verify.blocked_destination` | 422, la URL resuelve a una dirección privada |
| `oauth_clients.not_found` / `invalid_redirect_uris` / `redirect_domain_not_allowed` | clientes pre-registrados |
| `mcp_authorization.not_found` / `expired` (410) | la solicitud |
| `mcp_authorization.approve.user_token_invalid` (401) / `scope_not_requested` (422) / `scope_not_allowed_for_user` (422) / `scope_required` (422) / `not_pending` (409) | aprobación |
| `mcp_authorization.deny.not_pending` (409) | negación repetida |
| `mcp_connections.not_found` / `mcp_connections.me.missing_token` / `me.invalid_token` / `mcp_connections.summary.too_many` | conexiones |
