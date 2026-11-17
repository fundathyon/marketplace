# Historial de logins y bloqueo regional

Dos piezas que comparten la ubicación de la IP del cliente (base DB-IP Lite City; **IP Geolocation by [DB-IP](https://db-ip.com)**, CC BY 4.0):

| Pieza | Edición | Endpoints |
|-------|---------|-----------|
| Historial de logins | Community y Pro | `GET /api/v1/login-events`, `GET /api/v1/login-events/summary` |
| Bloqueo regional (`geo_access`) | **Solo Pro** | `GET`/`PUT /api/v1/app-behaviors/geo-access` |

Todo con `X-API-Key: <secret_key>` — **nunca desde un frontend**.

Cada ubicación sale, en este orden, de: la base DB-IP cargada en Postgres (`geo_source: "database"`), los headers de ubicación de Cloudflare de un proxy de confianza (`CF-IPCountry`, `cf-region`, `cf-ipcity` → `"headers"`), o nada (`country_code: "XX"`, `"none"`). `country_code` y `geo_source` nunca son `""`. El sobre de respuesta omite los strings vacíos: trata un campo ausente como vacío.

---

## Historial (`login_events`)

| `type` | Cuándo |
|--------|--------|
| `login_succeeded` | Un login abrió sesión (todos los `method` de `accounts.auth.login`) |
| `login_blocked` | El bloqueo regional lo rechazó; `user_id`/`session_id` pueden faltar; `block_reason` = `country_not_allowed` \| `unknown_country` |
| `ip_changed` | Un refresh llegó desde otra IP que la última de la sesión (sin `method`) |
| `login_failed` | Signin con contraseña rechazado; `block_reason` = `bad_password` \| `unknown_account` (sin `user_id`) \| `rate_limited` (cuenta bloqueada por intentos). También el segundo factor rechazado: `block_reason` = `mfa_failed` (o `rate_limited` con `MFA_FAILURE_MAX`) con el `method` del login; `account_not_verified` (correo sin verificar), `oauth_failed` (OAuth web, embebido o nativo, con `provider`), `link_invalid` (magic link) y `code_invalid` (código por correo; sin intentos, `rate_limited`) |

Testers (token directo) y MCP Connect no dejan filas. Retención: `LOGIN_EVENTS_RETENTION_DAYS` (90 por default; `0` = siempre).

### Listado

```bash
curl "{BASE_URL}/api/v1/login-events?page=0&size=20&country=MX&type=login_succeeded&method=password&geo_source=database&user_id=...&from=2026-10-01T00:00:00Z&to=2026-10-31T23:59:59Z" \
  -H "X-API-Key: sk_live_..."
```

- `page` desde 0; `size` 20 por default, máximo 100.
- `country` ISO alpha-2 o `XX`; `type`, `method` y `geo_source` (`database` \| `headers` \| `none`) validados; `from`/`to` RFC 3339 inclusivos.
- Recientes primero. `data` siempre es una lista (`[]` si no hay nada) y `meta.pagination` trae `page`, `size`, `total`, `totalPages`.
- Error de parámetros: `422 dto.validate.ListLoginEventsQuery`.

Evento:

```json
{
  "id": "…", "app_id": "…", "user_id": "…", "session_id": "…",
  "type": "login_succeeded", "method": "oauth", "provider": "google",
  "ip": "201.141.10.20", "country_code": "MX", "country_name": "Mexico",
  "region": "Jalisco", "city": "Guadalajara", "geo_source": "database",
  "user_agent": "Mozilla/5.0 …", "device_name": "iPhone de Ana",
  "block_reason": "country_not_allowed",
  "created_at": "2026-10-21T15:04:05Z"
}
```

(`block_reason` solo en `login_blocked` y `login_failed`; `provider` solo en OAuth; `mfa` = `totp` \| `backup_code` cuando el login pasó por el segundo factor, omitido si no.)

### Resumen

`GET /api/v1/login-events/summary?from=&to=` (default: últimos 30 días):

```json
{
  "from": "…", "to": "…",
  "logins": 120, "blocked": 7, "unique_ips": 64, "unique_users": 41,
  "countries": [
    { "country_code": "MX", "country_name": "Mexico", "logins": 98, "blocked": 0, "unique_ips": 50 }
  ],
  "sources": { "database": 118, "headers": 7, "none": 2 }
}
```

`countries` de más logins a menos; `sources` cuenta los mismos intentos por `geo_source`; `ip_changed` y `login_failed` no cuentan. `from > to` → `422 dto.validate.LoginEventsSummaryQuery`.

### Otros lugares con la ubicación

- Sesiones (`GET /api/v1/users/me/sessions`, `GET /api/v1/users/{id}/sessions`): `country_code`, `region`, `city`, `geo_source` y `last_country_code` (si `last_ip` cambió).
- Webhooks `accounts.auth.login` y `accounts.auth.login_failed`: `data.geo: {country_code, country_name, region, city, source}`.

---

## Bloqueo regional (`geo_access`, Pro)

```bash
curl -X PUT "{BASE_URL}/api/v1/app-behaviors/geo-access" \
  -H "X-API-Key: sk_live_..." -H "Content-Type: application/json" \
  -d '{"mode":"allowlist","countries":["MX","US"],"unknown_country":"allow"}'
```

| Campo | Valores |
|-------|---------|
| `mode` | `off` \| `allowlist` \| `blocklist` |
| `countries` | ISO 3166-1 alpha-2 (más `XK`), mayúsculas, únicos, ≤ 250; ≥ 1 con `allowlist` |
| `unknown_country` | `allow` (default) \| `deny` |

Respuesta (`GET` y `PUT`): `{ id?, app_id, config: {mode, countries, unknown_country}, created_at?, updated_at? }`. Sin fila: defaults `{mode: "off", countries: [], unknown_country: "allow"}` y no se escribe nada.

- Config inválida: `422 app_behaviors.geo_access.invalid_config` (`message` "campo: error; …" y `error.meta.errors[]`).
- Rutas genéricas con `geo_access`: `422 app_behaviors.create.use_geo_access_endpoint` / `422 app_behaviors.update.use_geo_access_endpoint`.
- En Community las rutas no existen y no se bloquea nada.

### Qué pasa en el login

Solo el **login** (nunca el refresh): contraseña, signup, activación, reset/set-password, magic link (pedir y canjear), código por correo (pedir y canjear), OAuth web, popup embebido y SDK nativo. Se comprueba **antes de cualquier efecto** (no se crea usuario, no sale correo, no se gasta el código).

```json
{
  "success": false, "status_code": 403,
  "error": {
    "code": 403,
    "message": "Sign-in is not allowed from your country (US).",
    "scope": "geo_access.country_not_allowed",
    "meta": { "country_code": "US", "country_name": "United States" }
  }
}
```

| Scope | HTTP | Qué hacer |
|-------|------|-----------|
| `geo_access.country_not_allowed` | 403 | Mostrar "no disponible en tu país" con `error.meta.country_code` |
| `geo_access.unknown_country` | 403 | No se pudo ubicar la IP y la app pide `deny` (`country_code: "XX"`) |
| `geo_access.lookup_error` | 503 | Reintentar: no se pudo leer la política (falla cerrado) |

En el popup OAuth embebido el error llega a la página del popup (`status=error`, `error=geo_access.country_not_allowed`).

Cada rechazo deja un `login_blocked` y sale el webhook `accounts.auth.login_failed` (`data.reason: "geo_blocked"`, ver [webhooks.md](webhooks.md)).

Exentos: testers (token directo y cuentas `@getfoundathyon.mock`), MCP Connect, refresh.

### IP del cliente (operador)

- `TRUSTED_PROXIES` (CIDRs/IPs): solo se aceptan `X-Forwarded-For`/`X-Real-IP` de esos proxies. **Vacía = se confía en cualquiera** (un cliente elige su país); con el bloqueo activo sale el WARN `geo_access.trusted_proxies.missing`.
- `CLIENT_IP_HEADER`: p. ej. `CF-Connecting-IP` detrás de Cloudflare. Con `TRUSTED_PROXIES` configurada también habilita los headers de ubicación de Cloudflare como respaldo de la base; sin `TRUSTED_PROXIES` nunca se aceptan.
- `GEOIP_SYNC=true`: la API carga la base DB-IP Lite City en Postgres en segundo plano y revisa cada día si hay edición nueva (una réplica a la vez, cambio atómico; ~690 MB por base). `GEOIP_SYNC_BASE_URL` = origen de las ediciones. En Lambda se ignora: programa `cmd/queue/geoip_sync`. Mientras la base no está, se usan los headers o `XX`.
