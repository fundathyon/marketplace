# Tokens — refresh, sesiones, validación y revocación

Cada login (email, magic link, código, OAuth, token directo de testers) abre una **sesión**: una fila que respalda al refresh token. Su id viaja en el claim `id` del refresh token y en el claim `sid` de los access tokens que emite.

## Validar tokens

| Endpoint | Token en Authorization |
|----------|------------------------|
| `GET /api/v1/validate-access` | access token |
| `GET /api/v1/validate-refresh` | refresh token |

```bash
curl -X GET "{BASE_URL}/api/v1/validate-access" \
  -H "Authorization: Bearer {access_token}"
```

Respuesta 200:

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "is_valid": true,
    "entity_type": "oauth"
  }
}
```

401 si inválido o expirado, y `401 refresh_tokens.validate.revoked` si su sesión ya se cerró (logout, revocación, cambio de contraseña, usuario borrado): la denylist por sesión. La verificación solo local con el JWKS no ve eso hasta el `exp` (ver [session-security.md](session-security.md)). `validate-refresh` también responde 401 con `refresh_tokens.validate_refresh.rotated` para un refresh token reemplazado por la rotación y `refresh_tokens.validate_refresh.idle_timeout` para una sesión inactiva; validar nunca revoca.

---

## Refrescar access token

`GET /api/v1/refresh-jwt` — intercambia el refresh por un access nuevo. **Guarda siempre el `refresh_token` de la respuesta**:

- Sin rotación (el default de toda app): es el mismo que enviaste, que sigue válido.
- Con rotación (la app la enciende, ver abajo): es uno nuevo y el anterior queda usado.

```bash
curl -X GET "{BASE_URL}/api/v1/refresh-jwt" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {refresh_token}"
```

Respuesta 201:

```json
{
  "success": true,
  "status_code": 201,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

Errores:

| HTTP | `error.scope` | Causa | Acción |
|------|---------------|-------|--------|
| 401 | `refresh_tokens.create.failed_to_validate_token` | Refresh inválido/expirado | Re-login |
| 401 | `refresh_tokens.create.revoked` | Sesión revocada (logout, revocación, reuso) | Re-login |
| 401 | `refresh_tokens.create.reuse_detected` | Se presentó un refresh token ya usado: la sesión se revocó | Re-login; es la señal de que alguien más tenía una copia |
| 401 | `refresh_tokens.create.idle_timeout` | La sesión pasó el timeout de inactividad de la app | Re-login |
| 404 | `refresh_tokens.create.refresh_token_not_found` | La sesión no existe | Re-login |
| 403 | `testers.expired` | El usuario es un tester caducado | Revivirlo con `PATCH /api/v1/testers/{id}/expiry` y volver a iniciar sesión |

### Rotación de refresh tokens (opt-in por app)

> Las **apps nuevas** nacen con la rotación encendida por el behavior `session_security` (`refresh_rotation: true`); las que ya existían conservan lo que tenían. Ver [session-security.md](session-security.md).

Con la rotación encendida, cada refresh devuelve un refresh token nuevo (claim `gen` = generación siguiente) y el anterior deja de servir. Si un refresh token ya usado vuelve a aparecer, Accounts revoca la sesión entera (`reuse_detected`): el ladrón y la víctima tienen que volver a iniciar sesión, y el robo queda registrado.

- **Gracia**: durante `reuse_interval_seconds` (30 por defecto) tras rotar, el token anterior todavía recibe la generación vigente, sin revocar nada. Cubre dos pestañas o un reintento de red que refrescan a la vez. No distingue clientes: alguien con una copia que refresque en los mismos segundos que el dueño tampoco dispara el reuso (queda en el log como `authentication.succeeded`, `reason=refresh_token_grace`, en WARN si llega desde otra IP que la rotación). `reuse_interval_seconds: 0` cierra ese hueco a cambio de que dos refresh concurrentes revoquen la sesión: serializa el refresh en el cliente.
- **Vida**: la rotación nunca alarga la sesión. El token nuevo vence cuando vencía el primero (`REFRESH_EXPIRE`, 30 días por defecto, desde el login).
- **Inactividad**: con `idle_timeout_seconds`, una sesión que pasa ese tiempo sin refrescar se cierra en su siguiente refresh (`idle_timeout`). Aplica con o sin rotación, y nunca es menos del doble de la vida del access token: un cliente activo refresca cuando vence el suyo.

Se configura desde el backend de la app (secret key). En **Pro** vive en el nodo `sessions` del behavior `tokens` (ver más abajo). La ruta de siempre sigue funcionando pero está **deprecada**: escribe en los dos sitios. En **Community** vive en el nodo `sessions` del behavior `email_auth`:

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/sessions/activate" \
  -H "X-API-Key: {secret_key}" \
  -H "Content-Type: application/json" \
  -d '{"refresh_rotation": true, "reuse_interval_seconds": 30, "idle_timeout_seconds": 1209600}'
```

| Campo | Default | Rango |
|-------|---------|-------|
| `refresh_rotation` | `false` en el nodo | bool |
| `reuse_interval_seconds` | 30 | 0–300 |
| `idle_timeout_seconds` | 0 (sin límite) | 0, o 3600–31536000 y al menos el doble de la vida del access token (`422 app_behaviors.activate_sessions.idle_timeout_too_short`) |

Los campos que no mandas conservan su valor: mandar solo `idle_timeout_seconds` no enciende la rotación. Un body vacío, `{}`, la enciende.

**Antes de encenderla**, todos tus clientes tienen que guardar el `refresh_token` de cada respuesta de `refresh-jwt`. Uno que siga reutilizando el del login perdería la sesión en su segundo refresh.

### Behavior `tokens` (Pro)

Una sola config por app para los tokens y las sesiones. Siempre está activo y no se desactiva. Lo que no configuras se **hereda**: una app que nunca lo tocó se comporta como antes.

```bash
curl "{BASE_URL}/api/v1/app-behaviors/tokens" -H "X-API-Key: {secret_key}"   # config guardada + effective

curl -X PUT "{BASE_URL}/api/v1/app-behaviors/tokens" \
  -H "X-API-Key: {secret_key}" -H "Content-Type: application/json" \
  -d '{
    "lifetimes":  {"access_token_seconds": 900, "refresh_token_seconds": 2592000, "activation_token_seconds": 900, "password_reset_token_seconds": 900},
    "sessions":   {"refresh_rotation": true, "reuse_interval_seconds": 30, "idle_timeout_seconds": 1209600},
    "limits":     {"max_sessions_per_user": 5, "on_limit": "revoke_oldest"},
    "revocation": {"on_password_change": "others", "on_password_reset": "all", "on_email_change": "others"}
  }'
```

`PUT` reemplaza la config completa. Error: `422 app_behaviors.tokens.invalid_config`.

| Campo | Rango | Si falta / 0 |
|-------|-------|--------------|
| `lifetimes.access_token_seconds` | 300–86400 | hereda (`JWT_EXPIRE`) |
| `lifetimes.refresh_token_seconds` | 3600–31536000, mayor que el access | hereda (`REFRESH_EXPIRE`) |
| `lifetimes.activation_token_seconds` | 300–86400 | 900 |
| `lifetimes.password_reset_token_seconds` | 300–7200 | 900 |
| `sessions.*` | como en la tabla de arriba; la inactividad además menor que la vida de la sesión | nodo de `email_auth` |
| `limits.max_sessions_per_user` | 1–100 | 0 = sin límite |
| `limits.on_limit` | `revoke_oldest` (cierra la sesión menos usada) · `reject` (`409 sessions.limit_reached` en el login nuevo) | — |
| `revocation.on_password_change` / `on_email_change` | `all` · `others` (conserva la sesión que hace el cambio) · `none` | `none` |
| `revocation.on_password_reset` | `all` · `none` | `none` |

- **Límite de sesiones:** aplica a todos los logins (email, código, magic link, OAuth). Los testers no tienen límite. Cada sesión cerrada sale en el webhook `accounts.session.revoked` con `reason` igual a `session_limit`.
- **Revocación:** las sesiones cerradas por un cambio de credenciales salen con `reason` igual a `password_change`, `password_reset` o `email_change`. Los access tokens ya emitidos valen hasta su `exp`.

### Cambiar la contraseña (usuario con sesión)

```bash
curl -X POST "{BASE_URL}/api/v1/users/me/password" \
  -H "X-API-Key: {publishable_key}" -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"current_password": "…", "new_password": "…"}'
# 200 {"changed": true, "revoked_sessions": 1}
```

- **Contraseña nueva:** tiene que cumplir la política de `email_auth`.
- **Revocación:** cierra sesiones según `revocation.on_password_change`; con `others` conserva la del access token.
- **Errores:**
  - `401 users.change_password.invalid_current_password`
  - `422 users.change_password.weak_password` y `422 users.change_password.same_password`
  - `409 users.change_password.no_password`: cuenta sin contraseña; se fija con el reset.
  - `409 testers.password_managed`

---

## Cerrar sesión desde el cliente

`POST /api/v1/logout` con el refresh token. **No lleva API key**: tener el refresh token prueba que la sesión es tuya, así que una SPA o una app móvil pueden cerrar su propia sesión.

```bash
curl -X POST "{BASE_URL}/api/v1/logout" \
  -H "Authorization: Bearer {refresh_token}"
```

Respuesta 200: `{ "data": { "revoked": true, "id": "<id de la sesión>" } }`. Repetirlo responde 200 igual.

Un 401 (`refresh_tokens.logout.token`, `refresh_tokens.logout.missing_token`) significa que el refresh token ya no es válido: borra tus tokens de todos modos. Los access tokens ya emitidos siguen valiendo hasta su `exp`.

---

## Sesiones activas

Cada sesión guarda la IP, el user-agent y el nombre de dispositivo del login, y cuándo se usó por última vez. El nombre lo declara el cliente con el header opcional **`X-Device-Name`** en el login (`"iPhone de Ana"`, máx. 100 caracteres).

### Las del propio usuario

```bash
# Listar (la de este access token viene con current: true)
curl -X GET "{BASE_URL}/api/v1/users/me/sessions?page=0&size=20" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}"

# Cerrar una
curl -X DELETE "{BASE_URL}/api/v1/users/me/sessions/{session_id}" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}"
```

Una sesión de otro usuario o de otra app responde 404 `sessions.revoke.not_found`.

### Las de un usuario, desde el backend

```bash
curl -X GET "{BASE_URL}/api/v1/users/{user_id}/sessions" \
  -H "X-API-Key: {secret_key}"
```

Se revoca una con `DELETE /api/v1/revoke-refresh/{session_id}`.

Cada sesión del listado:

```json
{
  "id": "0b...",
  "current": true,
  "login_method_id": "...",
  "device_name": "iPhone de Ana",
  "user_agent": "AccountsApp/2.1 (iOS 18)",
  "ip": "198.51.100.23",
  "last_ip": "198.51.100.40",
  "country_code": "MX",
  "region": "Jalisco",
  "city": "Guadalajara",
  "geo_source": "database",
  "last_country_code": "US",
  "created_at": "2026-09-25T10:00:00Z",
  "last_used_at": "2026-09-25T18:30:00Z",
  "expires_at": "2026-10-25T10:00:00Z"
}
```

`country_code`, `region` y `city` son la ubicación aproximada de `ip` (IP Geolocation by DB-IP; `"XX"` si no se pudo ubicar) y `geo_source` de dónde salió (`database`, `headers` o `none`); `last_country_code` solo aparece cuando `last_ip` es distinta. Cada refresh desde otra IP queda además como `ip_changed` en el [historial de logins](login-security.md).

Paginación en `meta.pagination`. Un listado vacío no trae `data`. `last_used_at` tiene precisión de un minuto. Las sesiones abiertas antes de esta versión no tienen dispositivo, IP ni user-agent, y `last_used_at` aparece desde su primer refresh.

---

## Webhooks de sesión

Cada revocación sale como `accounts.session.revoked` (motivo en `data.reason`) a los webhooks suscritos; cuando la cerró el propio usuario, también `accounts.auth.logout`. Un reuso detectado es `reason: reuse_detected`, con la petición que presentó el token en `triggered_by`: suscríbete para enterarte en tu backend. Cada login que abre una sesión sale como `accounts.auth.login` (el refresh no). Payload en [webhooks.md](webhooks.md).

---

## Información del usuario

```bash
curl -X GET "{BASE_URL}/api/v1/jwt/info" \
  -H "Authorization: Bearer {access_token}"
```

---

## Revocar desde el backend (secret key)

```bash
# Por token JWT
curl -X POST "{BASE_URL}/api/v1/revoke-refresh" \
  -H "X-API-Key: {secret_key}" \
  -H "Authorization: Bearer {refresh_token}"

# Por id de la sesión (claim id del refresh, sid del access, id del listado)
curl -X DELETE "{BASE_URL}/api/v1/revoke-refresh/{session_id}" \
  -H "X-API-Key: {secret_key}"
```

Respuesta 200:

```json
{
  "success": true,
  "data": { "revoked": true, "id": "..." }
}
```

---

## Patrón cliente (refresh automático)

```typescript
async function withAuth<T>(fn: (token: string) => Promise<T>): Promise<T> {
  try {
    return await fn(accessToken);
  } catch (e) {
    if (e.status === 401 && refreshToken) {
      const res = await fetch(`${BASE_URL}/api/v1/refresh-jwt`, {
        headers: {
          "X-API-Key": publishableKey,
          Authorization: `Bearer ${refreshToken}`,
        },
      });
      if (!res.ok) throw new SessionExpiredError();
      const { data } = await res.json();
      accessToken = data.access_token ?? data.jwt;
      refreshToken = data.refresh_token; // siempre: con rotación es uno nuevo
      return await fn(accessToken);
    }
    throw e;
  }
}

async function logout() {
  await fetch(`${BASE_URL}/api/v1/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${refreshToken}` },
  }).catch(() => {});
  accessToken = refreshToken = undefined; // también si respondió 401
}
```

Con la rotación encendida, si varias pestañas comparten la sesión, guarda el refresh token en un almacenamiento compartido (no en memoria por pestaña) y serializa el refresh: la gracia cubre carreras de segundos, no un token viejo guardado por horas.

---

## Resumen

| Acción | Método | Endpoint | Auth |
|--------|--------|----------|------|
| Validar access | GET | `/api/v1/validate-access` | Bearer access |
| Validar refresh | GET | `/api/v1/validate-refresh` | Bearer refresh |
| Nuevo access | GET | `/api/v1/refresh-jwt` | Public + Bearer refresh |
| Cerrar sesión | POST | `/api/v1/logout` | Bearer refresh |
| Mis sesiones | GET | `/api/v1/users/me/sessions` | Public + Bearer access |
| Cerrar una de mis sesiones | DELETE | `/api/v1/users/me/sessions/:id` | Public + Bearer access |
| Sesiones de un usuario | GET | `/api/v1/users/:id/sessions` | Secret |
| Configurar rotación/inactividad | POST | `/api/v1/app-behaviors/email/sessions/activate` | Secret |
| Info usuario | GET | `/api/v1/jwt/info` | Bearer access |
| Revocar | POST | `/api/v1/revoke-refresh` | Secret + Bearer refresh |
| Revocar por ID | DELETE | `/api/v1/revoke-refresh/:id` | Secret |

## JWT

- Firmados con **RS256**. La llave depende de la edición:
  - **Pro:** cada app tiene su propio par RSA. Todos sus tokens —access, refresh, activación y reset— se firman y se verifican solo con él; la llave global del servidor no abre nada. La pública de la app se obtiene con `GET /api/v1/system/public-key-jwt` y la secret key de la app (también está en `jwt_public_keys`). Los tokens internos llevan el claim `app_id`.
  - **Community:** una sola llave global (`PRIVATE_KEY_JWT` / `PUBLIC_KEY_JWT`).
- Access: corta duración; lleva `sid`, el id de su sesión (los emitidos antes de esta versión no lo traen)
- Access: lleva `role`, el nombre del rol del usuario en la app (siempre sale de la base, nunca de la metadata; se omite si no tiene rol). Con `JWT_PERMISSIONS_CLAIM=true` también `permissions`: los `"resource:action"` que el rol tiene permitidos. Refleja el rol al emitirse: para una decisión al día usa `POST /api/v1/authorize` — ver [roles-policies.md](roles-policies.md)
- La pública de una app también está en `GET /api/v1/jwks/{app_id}` (JWKS, sin auth; global en Community)
- Con segundo factor pendiente el login no emite ningún token hasta `/api/v1/mfa/*` — ver [mfa.md](mfa.md)
- Refresh: larga duración; persistido en DB con `id` claim; con rotación, `gen` es su generación (sin `gen` = 0)
- **Testers:** el `exp` del access y del refresh nunca pasa del `expires_at` del tester, aunque la app emita tokens más largos. No asumas la vida configurada; lee `exp`. Ver [testers.md](testers.md)
- Ver claims en payload JWT decodificado (base64)
