# Seguridad de sesiones (`session_security`)

Behavior por app (Community y Pro). Secret key.

| Método | Ruta | Body |
|--------|------|------|
| GET | `{BASE_URL}/api/v1/app-behaviors/session-security` | — |
| PUT | `{BASE_URL}/api/v1/app-behaviors/session-security` | parcial: `{oauth_token_delivery?, refresh_rotation?, revoke_sessions_on_password_change?}` |

```json
{
  "app_id": "…",
  "oauth_token_delivery": "query",
  "refresh_rotation": false,
  "revoke_sessions_on_password_change": false,
  "updated_at": "2026-10-23T18:02:11Z",
  "defaults_for_new_apps": {"oauth_token_delivery": "code", "refresh_rotation": true, "revoke_sessions_on_password_change": true},
  "query_delivery": {"in_use": true, "last_used_at": "2026-10-28T17:42:10Z", "uses_last_30d": 412, "window_days": 30},
  "migration_guide_url": "https://docs.foundathyon.com/accounts/oauth-code-delivery"
}
```

- **Apps que existían** antes de la revisión 18: tienen la fila con su comportamiento de antes (`query`, su rotación y su revocación efectivas). Nada cambia para ellas.
- **Apps nuevas** (sin fila, sin `updated_at`): `defaults_for_new_apps` → entrega por **code**, rotación encendida, revocación al cambiar la contraseña.
- `PUT` parcial; `{}` no cambia nada. Errores `400 session_security.invalid_field` (campo desconocido, cuerpo no objeto) y `400 session_security.invalid_value` (tipo, `null`, modo distinto de `query`/`code`), con `error.meta.field`. Las rutas genéricas lo rechazan (`422 app_behaviors.*.use_session_security_endpoint`).
- `query_delivery` (revisión 24) es el **uso real** del modo `query`: `in_use` es `true` solo si la app está en `query` **y** algún login OAuth web (o el popup embebido) le entregó los tokens en la URL en los últimos `window_days` (30) días. Es la señal para pedir la migración a `code`; con `false` no hay que avisar. `uses_last_30d` y `last_used_at` (`null` sin registro, hasta 90 días atrás) cuentan desde la revisión 24 y pueden ir hasta un minuto atrasados. Si el uso no se pudo leer, `query_delivery` no sale: trátalo como "sin aviso". `migration_guide_url` es la guía de docs.foundathyon.com para migrar.
- `refresh_rotation` y `revoke_sessions_on_password_change` son un **mínimo**: el nodo `sessions` (email_auth / tokens) y `revocation` del behavior `tokens` (Pro) pueden endurecerlo, no relajarlo.

## Entrega de tokens del login OAuth web

| Modo | Redirección final (`redirect_url`) |
|------|------------------------------------|
| `query` | `?access_token=…&refresh_token=…&provider=…` |
| `code` | `?code=…&provider=…` — **nunca tokens** |

En modo `code`, canjea **una vez** y en **< 60 s**:

```bash
curl -X POST "{BASE_URL}/api/v1/oauth/exchange" \
  -H "X-API-Key: {publishable_key}" -H "Content-Type: application/json" \
  -d '{"code": "{code}", "redirect_uri": "https://tuapp.com/auth/callback"}'
# 200 {"data": {"access_token": "…", "refresh_token": "…", "provider": "google"}}
```

| Scope | HTTP | Acción |
|-------|------|--------|
| `oauth.exchange.validation` | 400 | Falta `code` |
| `oauth.exchange.invalid_code` | 400 | Code desconocido o de otra app → re-login |
| `oauth.exchange.code_used` | 400 | Ya canjeado: la sesión que abrió se revocó → re-login |
| `oauth.exchange.code_expired` | 400 | Pasaron 60 s → re-login |
| `oauth.exchange.redirect_mismatch` | 400 | `redirect_uri` (opcional) no coincide |
| `session_security.lookup_error` | 503 | (callback) Reintenta el login |

- Segundo factor: la redirección sigue llevando `mfa_token` (sin code ni tokens) en los dos modos.
- Componentes embebidos: soportan los dos modos solos (el popup trae `code` y el componente lo canjea).
- Tu página de callback debe aceptar **los dos** formatos (`code` o `access_token`) y limpiar la URL con `history.replaceState`.

## Revocación propagada (todas las apps)

Cerrar una sesión (logout, `revoke-refresh`, `DELETE /users/me/sessions/{id}`, reuso de refresh o de code, inactividad, cambio/reset de contraseña con revocación, borrar el usuario) invalida sus **access tokens** antes del `exp` en Accounts: `GET /api/v1/validate-access` → `401 refresh_tokens.validate.revoked` (`503 refresh_tokens.validate.lookup_error` si no pudo consultar), y las rutas de Accounts con access token → 401. Denylist por sesión (claim `sid`).

**La verificación solo local con el JWKS no ve revocaciones**: un token vale hasta su `exp`. Usa `/validate-access` o `authz.Config{RevocationCheck: true}` (Go) cuando importe.
