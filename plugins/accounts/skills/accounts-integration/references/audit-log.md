# Audit log (Community y Pro)

Cada acción administrativa hecha con la **secret key** de la app (`X-API-Key: sk_…`) o con la **admin API key** (`X-Admin-API-Key`) queda como un evento de `fd_audit` (v0.1.0). Los logins de usuarios finales no van aquí: están en `/api/v1/login-events` (ver [login-security.md](login-security.md)).

## Leerlo

```bash
curl "{BASE_URL}/api/v1/audit-logs?action=accounts.user.&result=failure&limit=50" \
  -H "X-API-Key: sk_live_..."
```

| Query | |
| --- | --- |
| `action` | **Prefijo**: `accounts.user.` (todo lo de usuarios), `accounts.app_behavior.updated` |
| `actor_id` | `key_id` de una secret key (el segmento `<key_id>` de `sk_<env>_<key_id>_…`) o `admin_api_key` |
| `resource_type`, `resource_id` | `user`, `role`, `app_behavior` (id = código del behavior), `webhook`, `api_key`… |
| `result` | `success` \| `failure` |
| `from` (incl.), `to` (excl.) | RFC 3339 |
| `limit` | 1..200, default 50 |
| `cursor` | `next_cursor` de la página anterior |

Respuesta: `{ "success": true, "status_code": 200, "data": [Event], "next_cursor": "…" | null }`. `data` es `[]` si no hay eventos. Solo devuelve los eventos de la app de la secret key.

Errores: `400 audit.query.invalid_filter` (`error.meta.field`), `400 audit.query.invalid_cursor`, `404 audit.query.local_store_disabled` (`AUDIT_LOCAL_STORE=false`: el audit log está en core), `500 audit.query.failed`.

## El evento

```json
{
  "id": "UUID v7", "occurred_at": "RFC 3339 ms", "service": "accounts",
  "org_id": "", "project_id": "", "service_id": "",
  "actor": { "type": "api_key | operator", "id": "<key_id> | admin_api_key", "display": "<nombre de la key>" },
  "action": "accounts.<recurso>.<verbo>",
  "resource": { "type": "role", "id": "…", "display": "" },
  "result": "success | failure",
  "changes": { "before": {…}, "after": {…} } | null,
  "ip": "…", "user_agent": "…", "request_id": "…",
  "metadata": { "app_id": "…", "method": "PUT", "route": "/api/v1/…", "http_status": 200, "error_scope": "…", "via": "core" }
}
```

- `changes` trae **solo los campos que cambiaron** (alta: solo `after`; baja: solo `before`). Los secretos salen como `"[REDACTED]"` (contraseñas, `secret`, `client_secret`, `secret_hash`, tokens, cualquier `sk_live_…`, JWT o PEM). La contraseña de `set-password` y el refresh token de `revoke-refresh` nunca se copian.
- `result: failure` en cualquier 4xx/5xx de una ruta auditada, con `metadata.error_scope`. Una clave que no valida deja el intento con `metadata.authenticated: false` (sin `app_id`: no aparece en el listado de la app).
- `metadata.via: "core"`: lo hizo Foundathyon core con su clave dedicada (`Foundathyon core`) en nombre de alguien del admin.

## Acciones

`accounts.app.created/updated/deleted`, `accounts.api_key.created/updated/rotated/deactivated/deleted` (`updated` con `changes.before.scopes` / `changes.after.scopes` al cambiar scopes), `accounts.user.created/deleted/role_updated/password_set/email_verified/metadata_updated`, `accounts.role.*`, `accounts.policy.*`, `accounts.role_policy.created/deleted`, `accounts.app_behavior.updated` (todo `PUT /api/v1/app-behaviors/<code>`) y `.created`, `.verification_activated`, `.magic_link_activated`…, `accounts.email_access_settings.updated`, `accounts.email_access_entry.created/deleted`, `accounts.email_config.deleted`, `accounts.email_template.updated/deleted/tested`, `accounts.email_theme.activated`, `accounts.oauth_config.created/updated/deleted/disabled/legacy_redirects_applied`, `accounts.oauth_native_audience.created/deleted`, `accounts.webhook.created/updated/deleted/tested`, `accounts.session.revoked`, `accounts.tester.*`, `accounts.tester_batch.created/deleted`, `accounts.tester_job.created`, `accounts.tester_credential.viewed`, `accounts.pending_registration.created`, `accounts.user_metadata_policy.updated`, `accounts.mcp_*`, `accounts.system_env.viewed`, `accounts.system_email_template.viewed/previewed`.

No se auditan: `POST /api/v1/authorize`, los previews, `POST /api/v1/email-access/test`, las lecturas en general y los flujos de usuario final (publishable key).

## Configuración de la instancia

| Variable | Default | |
| --- | --- | --- |
| `AUDIT_SINK_URL` | vacío | URL base de core; vacía = no se manda a core (self-host) |
| `AUDIT_SINK_TOKEN` | vacío | Token de ingesta de `accounts` en core; obligatorio con `AUDIT_SINK_URL` |
| `AUDIT_LOCAL_STORE` | `true` | Guardar en la tabla `audit_events` (lo que sirve el endpoint) |
| `AUDIT_RETENTION_DAYS` | `365` | Días en `audit_events`; `0` = siempre |

Con core, los eventos van en lotes a `POST {AUDIT_SINK_URL}/api/v1/internal/audit-events` (`Authorization: Bearer <token>`, idempotente por `id`), sin bloquear la petición.
