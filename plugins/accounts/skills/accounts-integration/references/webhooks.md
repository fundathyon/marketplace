# Webhooks

Notificaciones HTTP desde Accounts hacia tu backend cuando ocurren eventos de dominio.

## Listar eventos disponibles (público)

```bash
curl "{BASE_URL}/api/v1/webhooks/events"
```

Respuesta ejemplo:

```json
{
  "success": true,
  "data": {
    "User": [
      { "code": "accounts.user.signup", "description": "Triggered when a new user signs up", "category": "User", "emitted": true }
    ],
    "Auth": [
      { "code": "accounts.auth.login", "description": "Triggered when a user successfully logs in and a new session is opened", "category": "Auth", "emitted": true }
    ]
  }
}
```

`emitted: true` = Accounts lo envía hoy: **43 de los 74 códigos** (ver la tabla de abajo). El resto está reservado: se acepta al suscribirse, pero nunca llega. No construyas lógica que espere un evento con `emitted: false`.

---

## CRUD webhooks (secret key)

```bash
# Listar
curl "{BASE_URL}/api/v1/webhooks" \
  -H "X-API-Key: {secret_key}"

# Crear
curl -X POST "{BASE_URL}/api/v1/webhooks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "name": "Mi backend",
    "url": "https://tu-backend.com/webhooks/accounts",
    "events": ["accounts.user.signup", "accounts.user.deleted"],
    "secret": "whsec_...",
    "retries": 3,
    "min_interval_ms": 2500,
    "backoff": "linear",
    "honor_retry_after": true,
    "send_secret_header": false
  }'

# Ajustar la entrega (PATCH parcial)
curl -X PATCH "{BASE_URL}/api/v1/webhooks/{id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"min_interval_ms": 2500, "backoff": "exponential"}'
```

**Destino (desde 0.15.0):** la `url` tiene que ser `https` y su host tiene que resolver **solo** a IPs públicas. Si no, el alta y el `PATCH` con `url` responden `422`: `webhooks.url.insecure_scheme` (no es https), `webhooks.url.blocked_destination` (loopback, red privada, link-local —incluida la metadata `169.254.169.254`—, CGNAT, ULA, multicast, IPv4 mapeada en IPv6, o nombres como `localhost`, `*.internal`, `*.local`, sin punto), `webhooks.url.unresolvable_host` o `webhooks.url.invalid_url`. Cada entrega revisa la IP al conectar (DNS rebinding), sin proxy del entorno y **sin seguir redirecciones**: un `3xx` es una entrega `failed`; configura la URL final. Un webhook antiguo con `http` o destino interno no se borra: sus entregas quedan `status: "blocked"` con `blocked_reason` (`insecure_scheme` | `blocked_destination`) y el listado de webhooks lo marca con `blocked_reason`. En desarrollo local, `WEBHOOK_ALLOW_INSECURE_TARGETS=true` en el servidor de Accounts admite `http://localhost` (se ignora en producción).

Accounts envía un POST a tu URL con el evento en el cuerpo, **firmado** con el `secret` del webhook. `send_secret_header` decide si además viaja el secret en claro en `X-Webhook-Secret`: default `false` en un webhook nuevo (solo firma); los webhooks creados antes conservan `true`. Sale en las respuestas de crear, listar y actualizar. Verifica siempre la firma.

## Verificar la firma (obligatorio en el receptor)

| Cabecera | Valor |
|----------|-------|
| `X-Webhook-Id` | `id` del evento; se repite en los reintentos y es el mismo para todos los webhooks del evento |
| `X-Webhook-Delivery-Id` | id de esta entrega (webhook + evento, = `id` del registro de entregas); el mismo en todos los reintentos y tras un reinicio → **clave de idempotencia** |
| `Idempotency-Key` | mismo valor que `X-Webhook-Delivery-Id` |
| `X-Webhook-Timestamp` | Segundos Unix del intento (cambia en cada reintento) |
| `X-Webhook-Signature` | `v1=<hex>`: HMAC-SHA256(`secret`, `<id>.<timestamp>.<cuerpo crudo>`). Lista separada por comas: acepta si alguna coincide |
| `X-Webhook-Secret` | Secret en claro. **Obsoleta**, solo con `send_secret_header: true`. No la uses en código nuevo |
| `X-Webhook-Test` | `true` solo en `POST /webhooks/{id}/test` |

Reglas:

1. Firma sobre el **cuerpo crudo** (bytes recibidos), nunca sobre el JSON re-serializado.
2. Comparación en **tiempo constante**. Sin coincidencia → `401`.
3. Tolerancia de **5 minutos** en `X-Webhook-Timestamp`, hacia atrás y hacia adelante.
4. **Idempotencia** por `X-Webhook-Delivery-Id` (o `Idempotency-Key`): si ya lo procesaste, responde `2xx` sin repetir el trabajo (la entrega es al menos una vez; con varias réplicas de Accounts cada entrega la envía una sola réplica, pero un fallo de red se reintenta).

```js
// Node.js + Express
import crypto from "node:crypto";
import express from "express";

const SECRET = process.env.ACCOUNTS_WEBHOOK_SECRET;

function verify(headers, rawBody) {
  const id = headers["x-webhook-id"];
  const timestamp = headers["x-webhook-timestamp"];
  const signatures = headers["x-webhook-signature"];
  if (!id || !timestamp || !signatures) return false;
  const age = Math.abs(Date.now() / 1000 - Number(timestamp));
  if (!Number.isFinite(age) || age > 300) return false;
  const expected = Buffer.from(
    "v1=" + crypto.createHmac("sha256", SECRET).update(`${id}.${timestamp}.`).update(rawBody).digest("hex"),
  );
  return signatures.split(",").some((candidate) => {
    const got = Buffer.from(candidate.trim());
    return got.length === expected.length && crypto.timingSafeEqual(got, expected);
  });
}

const app = express();
app.post("/webhooks/accounts", express.raw({ type: "application/json" }), (req, res) => {
  if (!verify(req.headers, req.body)) return res.sendStatus(401);
  const event = JSON.parse(req.body.toString("utf8"));
  // if (alreadyProcessed(event.id)) return res.sendStatus(204);
  res.sendStatus(204);
});
```

```python
# Python (FastAPI: raw_body = await request.body(); Flask: request.get_data())
import hashlib, hmac, time

def verify(secret: str, headers, raw_body: bytes) -> bool:
    webhook_id = headers.get("X-Webhook-Id")
    timestamp = headers.get("X-Webhook-Timestamp")
    signatures = headers.get("X-Webhook-Signature")
    if not (webhook_id and timestamp and signatures):
        return False
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False
    signed = f"{webhook_id}.{timestamp}.".encode() + raw_body
    expected = "v1=" + hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(c.strip(), expected) for c in signatures.split(","))
```

Vector de prueba: secret `whsec_5f4dcc3b5aa765d61d8327deb882cf99`, id `73bf90db-0c17-4f63-908c-7cf8f1e8f347`, timestamp `1727270400`, cuerpo `{"type":"accounts.user.signup"}` → `v1=97996e9346dff32fba74ac6144fb7b351baa9b5722673cddec48e9c22925fb01`.

**Migrar un receptor que lee `X-Webhook-Secret`:** 1) verifica la firma aceptando aún el secret como respaldo; 2) prueba con `POST /api/v1/webhooks/{id}/test` (va firmada); 3) `PATCH /api/v1/webhooks/{id}` con `{"send_secret_header": false}`; 4) quita el respaldo. Si el receptor usa `X-Webhook-Secret` como su API key, no apagues la cabecera antes del paso 1.

**Rotar el secret:** `PATCH` con `secret` nuevo; lo que ya estaba en cola sale con el anterior, así que acepta ambos unos minutos.

## Entrega en cola

Los envíos a un mismo webhook salen **uno tras otro y en orden** (no en paralelo), con la política del webhook:

| Campo | Default | Efecto |
|-------|---------|--------|
| `retries` | 3 | Reintentos tras el primer intento (0–10) |
| `min_interval_ms` | 0 | Espacio mínimo entre dos peticiones (0–60000) |
| `backoff` | `linear` | `linear` 1 s, 2 s, 3 s… · `exponential` 2 s, 4 s, 8 s… |
| `honor_retry_after` | `true` | Ante `429`/`503` con `Retry-After`, esperar eso antes del reintento y del siguiente envío (tope 10 min) |

**Outbox transaccional:** cada evento se escribe en la misma transacción que el cambio que lo produce y sale tras el commit. Un cambio que se deshace (un signup que falla a mitad) no avisa nada; un evento confirmado sale aunque Accounts se caiga justo después (lo entrega el relay al arrancar). El `id` del sobre y `X-Webhook-Id` son los mismos en cada reintento, réplica o reinicio.

Si tu receptor tiene rate limit (p. ej. 30/min), configura `min_interval_ms` (2500) y responde `429` con `Retry-After`. Cada envío queda en el registro de entregas y un reinicio de Accounts retoma lo pendiente al arrancar, así que no se pierde; la entrega es **al menos una vez**: descarta duplicados por `X-Webhook-Delivery-Id`. Con varias réplicas, cada entrega pendiente tiene un lease (`FOR UPDATE SKIP LOCKED` en Postgres): una réplica que arranca solo retoma las de una réplica muerta.

## Registro de entregas (secret key)

```bash
# Un webhook
curl "{BASE_URL}/api/v1/webhooks/{id}/deliveries?status=failed&page=0&size=20" \
  -H "X-API-Key: {secret_key}"

# Toda la app (webhook_id opcional)
curl "{BASE_URL}/api/v1/webhooks/deliveries?event_type=accounts.user.signup&webhook_id={id}" \
  -H "X-API-Key: {secret_key}"
```

Cada ítem: `id`, `webhook_id`, `app_id`, `event_id` (= `X-Webhook-Id`), `event_type`, `status` (`pending` | `delivered` | `failed` | `blocked`), `blocked_reason` (solo en `blocked`: `insecure_scheme` | `blocked_destination`, igual que `last_error`; sin respuesta ni reintentos), `attempts`, `last_status_code` (`0` = sin respuesta HTTP), `last_error`, `last_response_body` (respuesta del receptor en el último intento, 2xx o no, ≤ 2048 bytes UTF-8), `last_duration_ms` (`0` = no salió ninguno), `created_at`, `updated_at`, `finished_at` (los strings vacíos se omiten). Recientes primero; paginación en `meta.pagination`. Filtros: `status`, `event_type` (exacto) y, en el de la app, `webhook_id` (UUID; uno de otra app devuelve lista vacía). No guarda el cuerpo del evento una vez terminada la entrega; las terminadas se borran a los 30 días. Los envíos de prueba no entran. Errores: `404 webhooks.deliveries.not_found` (solo por webhook), `422 dto.validate.ListDeliveriesQuery`.

---

## Eventos que se emiten

| Código | Cuándo | `data` (lo principal) |
|--------|--------|------|
| `accounts.user.signup` | Registro completado (correo, OAuth, magic link, código por correo o testers) | `user`, `auth`, `roles` |
| `accounts.user.created` | El backend crea un usuario (`POST /api/v1/users`) | `user` (`id`, `user_name`, `name`, `role`, `is_test`) |
| `accounts.user.verified` | El usuario demostró su correo (activación, set-password, `verify-email` admin) | `user_id`, `login_method_id`, `source` |
| `accounts.user.updated` | Cambió el rol o la metadata | `user_id`, `changes`, `metadata_keys` (solo claves) |
| `accounts.user.locked` | Bloqueo progresivo de una cuenta existente | `user_id`, `lock_seconds`, `locked_until` |
| `accounts.user.email_changed` | Cambio de correo confirmado | `email_change.old_email` / `new_email` |
| `accounts.user.deleted` | Usuario eliminado (solo si el webhook se suscribe) | ver abajo |
| `accounts.user.password_reset` | Terminó una recuperación de contraseña (`reset-confirm` o `reset/set-password`); no sale en el cambio con sesión | `user` (`id`, `email`), `reason`, `changed_at`, `ip` |
| `accounts.auth.login` | Un login abrió una sesión nueva (no el refresh) | `method`, `geo`, `session` |
| `accounts.auth.login_failed` | Login rechazado antes de abrir sesión | `reason` |
| `accounts.auth.logout` | El usuario cerró la sesión; llega además de `session.revoked` | `reason` |
| `accounts.auth.method_added` | Un usuario existente ganó un método de login (correo u OAuth enlazado) | `user_id`, `method`, `reason` |
| `accounts.session.created` | Un login abrió una sesión | `session_id`, `user_id`, `method` |
| `accounts.session.revoked` | Toda revocación de una sesión | `reason` |
| `accounts.oauth.login` | Login con un proveedor (además de `auth.login`) | `provider`, `platform` |
| `accounts.oauth.linked` | Identidad OAuth enlazada a un usuario existente | `user_id`, `provider` |
| `accounts.role.created` / `.deleted` | Alta y baja de un rol | `role` |
| `accounts.role.assigned` | Cambio de rol de un usuario | `user_id`, `role`, `previous_role` |
| `accounts.policy.created` / `.updated` / `.deleted` | Cambios de policies | `policy` |
| `accounts.apikey.created` / `.rotated` / `.revoked` | Generar, rotar, desactivar o borrar una key (nunca su material) | `api_key` (`id`, `name`), `reason` |
| `accounts.app.updated` / `.deleted` | Cambios de la app / baja | `app` |
| `accounts.behavior.changed` | Cualquier escritura 2xx en `/api/v1/app-behaviors/*` (nunca la config) | `route`, `behavior` |
| `accounts.security.mfa_enrollment_started` / `.mfa_enabled` / `.mfa_disabled` / `.mfa_backup_codes_regenerated` | Ciclo del segundo factor (nunca secretos ni códigos) | `user_id`, `method` |
| `accounts.security.password_changed` | Contraseña cambiada, recuperada o fijada por el backend | `user_id`, `reason` |
| `accounts.security.suspicious_activity` | Refresh token reutilizado (la sesión se revoca) | `user_id`, `session_id`, `kind` |
| `accounts.testers.batch_created` / `.job_finished` | Lote de testers / fin de un trabajo | `batch_id`, `count` / `job_id`, `status`, `result` |
| `accounts.mcp.*` (7) | MCP Connect | ver mcp-connect.md |

Catálogo completo con `emitted`: `GET /api/v1/webhooks/events`. El resto (por ejemplo `accounts.session.refreshed` o `accounts.organization.*`) está **reservado**: no llega.

---

## Payload de `accounts.user.signup`

```json
{
  "type": "accounts.user.signup",
  "source": "tester",
  "app_id": "…",
  "data": {
    "user": {
      "id": "…",
      "name": "qa_1",
      "email": "qa_1@getfoundathyon.mock",
      "is_test": true,
      "expires_at": "2026-09-30T18:00:00Z"
    },
    "auth": { "id": "…", "method": "email", "is_verify": true, "source": "tester" },
    "roles": ["default"]
  }
}
```

- `data.user.is_test` y `data.user.expires_at` van **siempre** (`false` / `null` para una persona).
- `data.auth.source: "tester"` solo cuando el usuario nació por el módulo de testers; un lote de N dispara N eventos.
- Filtra por `is_test` para no contar testers como altas reales. Ver [testers.md](testers.md).

---

## Payload de `accounts.user.deleted`

```json
{
  "id": "…",
  "type": "accounts.user.deleted",
  "source": "accounts",
  "created_at": "2026-09-23T18:00:00Z",
  "app_id": "…",
  "data": {
    "user": { "id": "…", "email": "qa_7@getfoundathyon.mock", "name": "…", "is_test": true },
    "deleted_at": "2026-09-23T18:00:00Z",
    "initiated_by": "admin"
  }
}
```

- `initiated_by`: `admin` (secret key: `DELETE /users/{id}`, testers y sus trabajos), `user` (`DELETE /users/me`), `api` (otro origen).
- El usuario ya no existe al recibirlo: usa `data.user.id` para borrar lo tuyo; `email` es su primer correo (o el del login social).
- Firmado igual que el alta (ver [Verificar la firma](#verificar-la-firma-obligatorio-en-el-receptor)).

---

## Payload de `accounts.user.password_reset`

```json
{
  "id": "…",
  "type": "accounts.user.password_reset",
  "source": "accounts",
  "created_at": "2026-10-23T12:30:00Z",
  "app_id": "…",
  "data": {
    "user": { "id": "…", "email": "ana@example.com" },
    "reason": "password_reset",
    "changed_at": "2026-10-23T12:30:00Z",
    "ip": "203.0.113.7"
  }
}
```

- Nunca lleva la contraseña ni el código. Úsalo para cerrar sesiones propias o avisar a soporte.

---

## Payload de `accounts.auth.login`

Cada login que **abre una sesión nueva** (entrega un access token y un refresh token) envía `accounts.auth.login` a los webhooks activos **suscritos** a ese evento (ninguno por default). Sale una sola vez por login, después de guardar la sesión y firmar sus tokens.

```json
{
  "id": "7f3a…",
  "specversion": "1.0",
  "type": "accounts.auth.login",
  "version": "1.0",
  "source": "accounts",
  "created_at": "2026-10-01T10:00:00Z",
  "triggered_by": { "ip": "203.0.113.9", "user_agent": "Mozilla/5.0 …" },
  "app_id": "9c1a27be-2f83-481f-aecc-db5c99c5b6c2",
  "data": {
    "session": {
      "id": "0b0c3f2e-5d6a-4c1b-9e8f-7a6b5c4d3e2f",
      "login_method_id": "…",
      "device_name": "iPhone de Ana",
      "user_agent": "AccountsApp/2.1 (iOS 18)",
      "ip": "203.0.113.9",
      "created_at": "2026-10-01T10:00:00Z",
      "expires_at": "2026-10-31T10:00:00Z"
    },
    "user": { "id": "52f213ab-612b-4e22-a2d0-3315a23cb8f3", "email": "ana@example.com" },
    "method": "oauth",
    "provider": "google",
    "platform": "web",
    "is_new_user": false,
    "geo": { "country_code": "MX", "country_name": "Mexico", "region": "Jalisco", "city": "Guadalajara", "source": "database" }
  },
  "context": { "environment": "production", "trace_id": "…" }
}
```

| `method` | Endpoint | `is_new_user` |
|---|---|---|
| `password` | `POST /api/v1/emails/signin`, `POST /api/v1/emails/login` cuando entra con contraseña y el login que hace `POST /api/v1/emails/reset/set-password` | `false` |
| `email_password_signup` | `POST /api/v1/emails/signup` cuando la app no pide verificación y el registro devuelve tokens | `true` |
| `activation` | `POST /api/v1/emails/activate` y `POST /api/v1/emails/activate/v2/set-password` (Pro) | `true` |
| `magic_link` | `POST /api/v1/emails/magic-link/claim` | `true` cuando el canje es el alta (la misma regla que `accounts.user.signup`) |
| `email_code` | `POST /api/v1/emails/email-code/claim` | `true` cuando el canje es el alta (la misma regla que `accounts.user.signup`) |
| `oauth` | El callback web de un proveedor (`GET /api/v1/oauth/{callback_key}`), con redirect o en el popup de los componentes embebidos | `true` si el callback creó al usuario |
| `native_oauth` | `POST /api/v1/auth/social` | `true` si la petición creó al usuario |

- `provider` (`google`, `apple`, `github`, `microsoft`) y `platform` (`web`, `ios`, `android`…) solo vienen en los logins `oauth` y `native_oauth`.
- `data.user.email` es el correo con el que entró; puede llegar vacío en un login OAuth cuyo proveedor no lo entregó (Apple en logins posteriores).
- `data.session` es la sesión recién abierta: el mismo `id` que llega después en `accounts.session.revoked` cuando se cierre. `expires_at` es cuándo vence su refresh token.
- `triggered_by` es la petición del login.
- En un alta llegan **dos** eventos: `accounts.user.signup` y `accounts.auth.login` con `is_new_user: true`, cada uno con su `id`. **El orden de llegada no está garantizado**: no supongas que el alta llega antes.
- La lista de `method` puede crecer: trata un valor desconocido como un login más.
- `data.geo` es la ubicación aproximada de la IP de la sesión (IP Geolocation by DB-IP). `country_code` es `"XX"` si no se pudo ubicar; `source` es `database`, `headers` (Cloudflare de confianza) o `none`.

**No envían `accounts.auth.login`:**

- El refresh (`GET /api/v1/refresh-jwt`), con o sin rotación: no abre una sesión, renueva la que hay.
- El token directo de un [tester](testers.md) (`POST /api/v1/testers/{id}/token`): esa sesión la pide el backend de la app con su secret key, no un login del usuario.
- MCP Connect (`POST /o/{app_id}/oauth/token`): las conexiones de un asistente tienen sus propios eventos `accounts.mcp.*`.
- Un login que falla o que el límite de sesiones rechaza (`409 sessions.limit_reached`).

---

## Payload de `accounts.auth.login_failed`

Sale cuando un login se rechaza antes de crear nada: el bloqueo regional (`geo_access`, Pro) o, en las dos ediciones, el signin con contraseña (contraseña mala, correo sin cuenta o cuenta bloqueada por intentos):

```json
{
  "id": "…",
  "type": "accounts.auth.login_failed",
  "source": "accounts",
  "triggered_by": { "ip": "8.8.8.8", "user_agent": "Mozilla/5.0 …" },
  "app_id": "…",
  "data": {
    "reason": "geo_blocked",
    "block_reason": "country_not_allowed",
    "method": "oauth",
    "provider": "google",
    "ip": "8.8.8.8",
    "geo": { "country_code": "US", "country_name": "United States", "region": "California", "city": "Mountain View", "source": "database" },
    "user": { "id": "", "email": "alice@example.com" }
  }
}
```

- `reason`: `geo_blocked` (con `block_reason`: `country_not_allowed` o `unknown_country`), `bad_password`, `unknown_account` (`user.id` vacío) o `rate_limited` (la cuenta estaba bloqueada; no se miró la contraseña). Los tres últimos llevan `method: "password"`.
- `reason: "mfa_failed"`: el primer factor pasó y el código TOTP o de respaldo se rechazó (o el `mfa_token` agotó sus intentos); `method` es el del login original (`password`, `oauth`, `magic_link`…). Con `MFA_FAILURE_MAX` fallos del usuario sale `rate_limited`. Ver [mfa.md](mfa.md).
- `reason: "account_not_verified"` (contraseña correcta, correo sin verificar), `"oauth_failed"` (`method` `oauth` o `native_oauth`, con `provider`: código o `id_token` inválido, proveedor caído, `state` rechazado), `"link_invalid"` (`method: "magic_link"`: desconocido, vencido, ya usado o abierto desde otra IP o navegador) y `"code_invalid"` (`method: "email_code"`: equivocado, vencido, ya usado o reemplazado; sin intentos sale `rate_limited`). Estos tres últimos no llevan `user`.
- `provider` solo en OAuth; `user` solo si el flujo ya conocía el usuario o el correo.
- Cada signin rechazado manda uno: en una ráfaga llegan tantos como intentos (acotados por el límite por IP).

---

## Payload de `accounts.session.revoked` y `accounts.auth.logout`

Los dos llevan la misma `data`; `accounts.auth.logout` sale solo cuando la sesión la cerró el usuario, con **su propio `id`** (no lo deduplica contra el de `session.revoked`).

```json
{
  "id": "5d2e…",
  "specversion": "1.0",
  "type": "accounts.session.revoked",
  "version": "1.0",
  "source": "accounts",
  "created_at": "2026-09-26T09:00:00Z",
  "triggered_by": { "ip": "203.0.113.9", "user_agent": "Mozilla/5.0 …" },
  "app_id": "9c1a27be-2f83-481f-aecc-db5c99c5b6c2",
  "data": {
    "session": {
      "id": "0b0c3f2e-5d6a-4c1b-9e8f-7a6b5c4d3e2f",
      "login_method_id": "…",
      "device_name": "iPhone de Ana",
      "user_agent": "AccountsApp/2.1 (iOS 18)",
      "ip": "198.51.100.23",
      "created_at": "2026-09-25T10:00:00Z",
      "last_used_at": "2026-09-25T18:30:00Z"
    },
    "user": { "id": "52f213ab-612b-4e22-a2d0-3315a23cb8f3" },
    "reason": "logout",
    "revoked_at": "2026-09-26T09:00:00Z"
  },
  "context": { "environment": "production", "trace_id": "…" }
}
```

| `reason` | Cuándo | También `accounts.auth.logout` |
|---|---|---|
| `logout` | El cliente cerró su sesión: `POST /api/v1/logout` | Sí |
| `revoked_by_user` | El usuario cerró una de sus sesiones: `DELETE /api/v1/users/me/sessions/{id}` | Sí |
| `revoked_by_app` | El backend de la app la revocó con la secret key: `POST /api/v1/revoke-refresh` o `DELETE /api/v1/revoke-refresh/{id}` | No: Accounts no sabe si el usuario lo pidió |
| `reuse_detected` | Con la rotación activa, alguien presentó un refresh token ya usado | No |
| `idle_timeout` | La sesión pasó el timeout de inactividad de la app | No |

- `data.session` es la foto de la sesión: el dispositivo, el user-agent y la IP del login que la abrió, y su último uso. Las sesiones abiertas antes de que existieran esos datos llegan con ellos vacíos.
- `triggered_by` es la petición que la revocó. En un `reuse_detected` es la que presentó el token ya usado, que puede ser el dueño o quien tenía la copia.
- La lista de `reason` puede crecer: trata un valor desconocido como una revocación más.
- Borrar un usuario revoca sus sesiones sin enviar `accounts.session.revoked`: el aviso es `accounts.user.deleted`. Una sesión que vence por su `exp` tampoco envía nada, porque nadie la revoca.

Sesiones, rotación y logout en [tokens.md](tokens.md).

---

## Integración típica

```
Cliente → Accounts (signup/signin)
Accounts → Event bus interno
Accounts → POST tu-webhook-url (async)
Tu backend → procesa evento (analytics, CRM, etc.)
```

Los webhooks **no reemplazan** el manejo de tokens en el cliente.

---

## Auth

| Endpoint | Auth |
|----------|------|
| `GET /webhooks/events` | Ninguna |
| `GET/POST/PATCH/DELETE /webhooks` | Secret key |
| `POST /webhooks/{id}/test` | Secret key |
| `GET /webhooks/{id}/deliveries` | Secret key |
| `GET /webhooks/deliveries` | Secret key |

Ver bodies exactos en [openapi.json](../assets/openapi.json).
