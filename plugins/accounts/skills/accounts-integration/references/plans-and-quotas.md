# Planes y cuotas por organización

Opcional: solo con `ENTITLEMENTS_URL` configurada y en apps que el **operador** asoció a un tenant de facturación (`tenant_ref`). Sin eso, nada cambia.

## Para una app integradora

- Toda alta de usuario final (signup con o sin verificación, OAuth web y nativo de un usuario nuevo, `POST /api/v1/users`, `POST /api/v1/pending-registrations`) puede responder:
  - `403 quota.users_exceeded`: la organización llegó al techo de usuarios de su plan (suma de todas sus apps; los testers no cuentan). `error.meta.limit` / `error.meta.current` solo vienen con secret key; las rutas de publishable key y públicas no los llevan.
  - `403 quota.tenant_read_only` con `error.meta.status`: el plan está impagado (gracia vencida), suspendido o cancelado.
- Con el plan en solo lectura, las mutaciones con **secret key** (configuración, behaviors, usuarios, roles, policies, webhooks, API keys, OAuth, plantillas…) también responden `403 quota.tenant_read_only`. Los `GET` siguen.
- **Nunca se bloquean**: signin, refresh, logout, MFA, reset de contraseña, perfil y sesiones del usuario, aprobar una conexión MCP (es un login), y lo que quita acceso con secret key (revocar sesiones, rotar/desactivar/borrar una API key, borrar un usuario, testers, un webhook, un proveedor OAuth o un recurso MCP, denegar/revocar una conexión MCP).
- Generar una API key en solo lectura solo se permite si la app ya no tiene ninguna key activa con `"*"`.
- Magic link y código por correo con `auto_signup` **no** dan 403: mantienen su 200 genérico (anti-enumeración) y no crean al usuario ni mandan correo.
- Techos duros por tenant (suman todas sus apps; solo cierran altas nuevas, nunca borran lo existente), con secret key y `error.meta` `{limit_key, limit, used, current}`:
  - `403 quota.api_keys_exceeded` en `POST /api/v1/api-keys/generate` (`max_api_keys`; rotar no cuenta; no cuentan la key inicial de cada app ni la dedicada de core, marcadas con `system_kind`; el nombre no exime). La marca `"system_kind":"core"` solo vale con `X-Admin-API-Key` (si no, `403 api_keys.system_kind.forbidden`).
  - `403 quota.roles_exceeded` en `POST /api/v1/roles` (`max_roles`; el rol `default` de cada app no cuenta).
  - `403 quota.webhooks_exceeded` en `POST /api/v1/webhooks` (`max_webhooks`).
  - `403 quota.oauth_providers_exceeded` en `POST /api/v1/oauth-configs` habilitado o `PATCH …/{id}` que vuelve a habilitar (`max_oauth_providers`).
- `403 quota.feature_not_in_plan` (`meta.feature`: `geo_access`, `embedded_auth`, `email_branding`) si el plan tiene `accounts_pro_features: 0`: habilitar geo (`mode` ≠ `off`), `PUT …/embedded-auth`, branding no vacío en `PUT /api/v1/email-templates/themes/active` o `email_branding` en magic-link/email-code activate. Solo cuenta si el cambio deja algo distinto de lo guardado: volver a guardar lo mismo, apagar o limpiar siempre pasa; lo ya configurado sigue funcionando.
- Planes de pago con `overage.max_accounts_users.allowed: true`: `quota.users_exceeded` no sale nunca; el exceso se cuenta.
- `max_mau` es blando: nunca bloquea. Logins y refresh anotan el MAU en segundo plano.
- Webhook `accounts.entitlement.limited` (una vez por mes y umbral, a cada app del tenant) al 80 % y 100 % de `max_accounts_users` o `max_mau`: `data` `{limit_key, threshold, limit, current, period, plan, overage_allowed, blocking}`. También queda en el audit log.
- Mapear por `error.scope`; no reintentar.

## Para el operador (admin API key)

| Ruta | Qué hace |
|------|----------|
| `POST /v1/apps` con `"tenant_ref"` | Crea la app asociada (sin admin key el campo se ignora). La respuesta trae `tenant_ref` (o `null`). |
| `PUT /v1/apps/{id}/tenant` `{"tenant_ref":"org_…"}` | `200 {"data":{"app_id","tenant_ref","changed"}}`; idempotente (`changed:false`). `404 apps.not_found`, `400 apps.tenant_ref.invalid`. |
| `GET /api/v1/system/entitlements/{tenant_ref}` | Plan guardado, `mode` (`normal`/`past_due`/`read_only`), `limits`, `usage`, `stale`, `last_error`. |
| `POST /api/v1/system/entitlements/{tenant_ref}/refresh` | Pide el plan al proveedor ya (`409 entitlements.disabled`, `502 entitlements.provider_unavailable`). |
| `GET /api/v1/system/usage/{tenant_ref}` | `{tenant_ref, period, accounts_users, mau, accounts_users_over, api_keys, roles, webhooks, oauth_providers}` de todas las apps del tenant; `?period=YYYY-MM` opcional (`400 entitlements.period.invalid`). |

`tenant_ref`: 1–64 caracteres `[A-Za-z0-9._:-]`. La secret/publishable key de la app nunca lo ve ni lo cambia.

## Proveedor

`GET {ENTITLEMENTS_URL}/{tenant_ref}` con `X-API-Key: ENTITLEMENTS_API_KEY` → `{version:1, tenant_ref, plan{slug,name}, status, grace_until, limits{}, overage{}, checked_at}` (`overage` opcional: por límite `{allowed, unit_price_usd, unit}`; un límite sin entrada no admite pasarse). Tras un cambio de plan, `POST /api/v1/system/entitlements/{tenant_ref}/refresh` lo aplica ya y vacía la caché de esa réplica. `limits` `-1` o ausente = sin techo. Cacheado en `tenant_entitlements` + 60 s por réplica; refresco en segundo plano cada `ENTITLEMENTS_REFRESH_SEC` (300). Un 503 conserva lo último bueno. Sin ninguna fila y con el proveedor caído, las altas pasan (fail-open).

Retención por plan: las purgas de `login_events` y `audit_events` usan `login_events_retention_days` / `audit_retention_days` del tenant (`-1` = siempre) y, sin plan, `LOGIN_EVENTS_RETENTION_DAYS` / `AUDIT_RETENTION_DAYS`.

Variables: `ENTITLEMENTS_URL`, `ENTITLEMENTS_API_KEY`, `ENTITLEMENTS_REFRESH_SEC` (300), `ENTITLEMENTS_TIMEOUT_MS` (2000), `ENTITLEMENTS_STALE_ALERT_HOURS` (24).
