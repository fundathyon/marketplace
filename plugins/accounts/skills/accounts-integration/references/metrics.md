# Métricas del dashboard

Endpoints de lectura con la **secret key** (solo backend). Cada número es de la app de la key. Community y Pro.

| Endpoint | Responde | Rango máximo |
| --- | --- | --- |
| `GET /api/v1/metrics/overview` | KPIs `{value, previous}` del rango y del anterior de la misma duración: `users_total`, `signups`, `active_users`, `sign_ins`, `failed_sign_ins`, `blocked_sign_ins`, `failure_rate`, `mfa_users_pct` (sin `previous`) | `LOGIN_EVENTS_RETENTION_DAYS` (90) |
| `GET /api/v1/metrics/users` | `series[]`: `start`, `signups`, `active` = `new` + `reactivated` + `retained`, `sign_ins`, `users_total` (acumulado); `activity_since` | `ACTIVITY_RETENTION_DAYS` (400) |
| `GET /api/v1/metrics/logins` | `methods`, `failures` (`method`, `reason`, `count`, `rate`), `series` (`succeeded`, `failed`, `blocked`), `top_ips` (20), `countries`, `platforms`, `browsers` | 90 |
| `GET /api/v1/metrics/webhooks` | `totals` (`delivered`, `retried`, `failed`, `blocked`, `pending`, `success_rate`, `avg_attempts`), `series`, `status_codes` (`2xx`…`none`), `events`, `endpoints`; `?webhook_id=` filtra | 30 |
| `GET /api/v1/metrics/usage` | `plan` (`slug`, `name`, `status`, `period`, `resets_at`), `limits`, `usage` del tenant en el mes UTC; sin plan solo `usage.accounts_users` | — |

Métricas por sección (`GET /api/v1/metrics/<métrica>`, mismos parámetros; "foto" ignora el rango):

| Métrica | Trae | Rango máximo |
| --- | --- | --- |
| `summary` | `health`, `activation` de las altas, `recent_changes` (10 del audit log) | 90 |
| `accounts` | foto: `states`, `inactivity`, `linked_methods`; `cohorts` semanales del rango | 400 |
| `access` | `hours` 7×24 (0 = lunes, en `tz`), `ip_changes`, `cities` | 90 |
| `rbac` | foto: `roles`, `matrix`, `policies`, `unassigned_policies` | — |
| `api_keys` | foto: `totals`, `keys` con `status` | — |
| `oauth` | `series` por proveedor, `providers`, `platforms` | 90 |
| `mcp` | `totals`, `series` (`granted`, `revoked`), `clients`, `revoke_reasons` | 400 |
| `email_access` | `magic_link`, `email_code`, `time_to_use` | 400 |
| `user_metadata` | foto: `keys`, `token_keys` | — |
| `embedded` | sign-ins por canal `embedded`/`api`, `since` | 90 |
| `geo_access` | bloqueos por cubeta y país, `affected_users` | 90 |
| `identity_linking` | foto: `methods_per_account` | — |
| `mfa` | `adoption`, `challenges`, `backup_codes` | 90 |
| `security_limits` | logins limitados: `series`, `total`, `top_ips` | 90 |
| `sessions` | foto: `totals`, `durations`, `generations`; `endings` del rango | 400 |
| `behaviors` | foto: `behaviors` | — |
| `emails` | `totals`, `series` por plantilla, `templates`, `top_errors`, `locales` (sin `from`: 7 días) | 7 |
| `tokens` | refresh por día, `total`, `since` | 400 |

`/webhooks` suma `queue`, `latency` (p50/p95) y `top_errors`.

Parámetros (los cuatro primeros): `from`, `to` (RFC 3339 o `YYYY-MM-DD` en `tz`; `to` con fecha sola es inclusivo; por defecto los últimos 30 días), `interval` (`day` \| `week` desde lunes \| `month`), `tz` (IANA, `UTC`). Una cubeta por intervalo, con ceros; máximo 400.

Reglas:
- Testers y usuarios borrados no cuentan en usuarios, signups ni activos.
- La sesión que abre un signup con contraseña no es un sign-in.
- Activos = sesión abierta o refrescada ese día (UTC). No hay activos antes de `activity_since`.
- **Los campos `null` o vacíos no viajan** (convención de la API): trata un campo ausente como vacío.

Errores: `400 metrics.query.invalid` \| `metrics.query.invalid_tz` \| `metrics.query.range_too_large`, `404 metrics.webhook_not_found`, `500 metrics.query.failed`.

Motivos de fallo (`failures[].reason` y webhook `accounts.auth.login_failed`): `bad_password`, `unknown_account`, `account_not_verified`, `rate_limited`, `mfa_failed`, `oauth_failed`, `link_invalid`, `code_invalid`.

Docs: `docs/api-docs/integration/dashboard-metrics.mdx`.
