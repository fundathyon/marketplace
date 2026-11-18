# Límites de seguridad por app (`security_limits`)

Community y Pro. Cada app ajusta sus límites contra fuerza bruta y los del segundo factor **dentro de rangos fijos**. Las variables de entorno de la instancia son el **default** de toda app que no fije el suyo. Una app **no puede apagar** un límite (ningún rango admite `0`); `AUTH_RATE_LIMIT_ENABLED=false` (operador) sigue apagando todo en la instancia.

## Endpoints (secret key)

| Método | Ruta | Cuerpo |
|--------|------|--------|
| GET | `{BASE_URL}/api/v1/app-behaviors/security-limits` | — |
| PUT | `{BASE_URL}/api/v1/app-behaviors/security-limits` | parcial (ver abajo) |

Header: `X-API-Key: <secret_key>`. **Nunca** desde el frontend.

## Cuerpo del PUT (parcial)

```json
{
  "rate_limit": {"ip_max": 60, "ip_window_sec": 60, "account_max": 10, "account_window_sec": 900},
  "lockout":    {"threshold": 10, "window_sec": 900, "durations_sec": [60, 300, 900], "reset_sec": 86400},
  "api_keys":   {"failure_max": 10, "failure_window_sec": 300},
  "mfa":        {"token_ttl_sec": 300, "max_attempts": 5, "failure_max": 10, "failure_window_sec": 900}
}
```

- Solo cambian los campos enviados.
- `null` en un campo → vuelve al default de la instancia.
- `{}` → no cambia nada.

## Respuesta (GET y PUT)

`data` trae `app_id`, las cuatro secciones con lo que la app fijó (**`null` = hereda**), `updated_at` (solo con fila), `effective` (lo que se aplica), `defaults` (los de la instancia) y `ranges` (`{"rate_limit.ip_max": {"min": 5, "max": 1000}, ...}`; `lockout.durations_sec` añade `min_items`/`max_items`).

## Rangos

| Campo | Env (default) | Rango |
|-------|---------------|-------|
| `rate_limit.ip_max` | `AUTH_RATE_LIMIT_IP_MAX` | 5–1000 |
| `rate_limit.ip_window_sec` | `AUTH_RATE_LIMIT_IP_WINDOW_SEC` | 10–3600 |
| `rate_limit.account_max` | `AUTH_RATE_LIMIT_ACCOUNT_MAX` | 3–100 |
| `rate_limit.account_window_sec` | `AUTH_RATE_LIMIT_ACCOUNT_WINDOW_SEC` | 60–86400 |
| `lockout.threshold` | `AUTH_LOCKOUT_THRESHOLD` | 3–100 |
| `lockout.window_sec` | `AUTH_LOCKOUT_WINDOW_SEC` | 60–86400 |
| `lockout.durations_sec` | `AUTH_LOCKOUT_DURATIONS_SEC` | 1 a 5 valores, cada uno 10–86400, no decrecientes |
| `lockout.reset_sec` | `AUTH_LOCKOUT_RESET_SEC` | 3600–604800 |
| `api_keys.failure_max` | `API_KEY_FAILURE_MAX` | 3–100 |
| `api_keys.failure_window_sec` | `API_KEY_FAILURE_WINDOW_SEC` | 60–3600 |
| `mfa.token_ttl_sec` | `MFA_TOKEN_TTL_SEC` | 60–900 |
| `mfa.max_attempts` | `MFA_MAX_ATTEMPTS` | 1–10 |
| `mfa.failure_max` | `MFA_FAILURE_MAX` | 3–50 |
| `mfa.failure_window_sec` | `MFA_FAILURE_WINDOW_SEC` | 60–86400 |

Si la env de la instancia cae fuera del rango, **ese valor es el default efectivo** (el operador manda); la app no puede fijar valores fuera de rango. Solo de la instancia (no por app): `AUTH_RATE_LIMIT_ENABLED`, `AUTH_RATE_LIMIT_STORE`, `API_KEY_ARGON2_*` y la guardia de webhooks.

## Errores

| Status | `error.scope` | `error.meta` |
|--------|---------------|--------------|
| 400 | `security_limits.out_of_range` | `{field, min, max}` (+ `index` en `durations_sec`) |
| 400 | `security_limits.invalid_field` | `{field}`: sección/campo desconocido, tipo equivocado, cuerpo no objeto |
| 400 | `security_limits.invalid_durations` | escalera vacía, >5 valores o que baja |
| 422 | `app_behaviors.create.use_security_limits_endpoint` / `app_behaviors.update.use_security_limits_endpoint` | rutas genéricas de behaviors |
| 500 | `app_behaviors.security_limits.read_error` / `save_error` | — |

## Notas

- El tope de secret keys inválidas por `key_id` es el de la **app dueña de la clave**; el contador por IP (antes de saber de quién es la clave) usa los defaults de la instancia.
- `mfa.token_ttl_sec` se ve en el `expires_in` del `mfa_token` del login.
- Caché por réplica de 30 s: el cambio aplica enseguida en la réplica que atendió el PUT y en menos de 30 s en las demás.
- Si el behavior no se puede leer, los límites siguen activos con los defaults de la instancia.
