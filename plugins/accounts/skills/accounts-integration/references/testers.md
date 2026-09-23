# Usuarios de prueba (testers)

Cuentas de prueba que **Accounts fabrica** para poblar datos sin abrir buzones: se crean en lote con la **secret key**, tienen contraseña descargable, caducan solas y nunca se mezclan con personas reales. **Todo desde backend o scripts**: ningún endpoint de aquí se llama con la publishable key.

---

## Modelo

- Un tester es un **usuario normal** con `is_test: true` y `expires_at` (fecha o `null`). Entra por los mismos `POST /api/v1/emails/signin`, `GET /api/v1/refresh-jwt`, `validate-access` y `jwt/info` que una persona.
- Correo: `<user_name>@getfoundathyon.mock`. **Dominio reservado**: ningún correo sale hacia él, y los flujos públicos lo rechazan (ver abajo).
- Nace **verificado** y con rol **`default` fijo**.
- `status` calculado: `expired` si `expires_at` ya pasó, `active` en otro caso.
- Contraseña **derivada** (`HMAC` de `SECRET_PASSWORD`, app y correo), cumple la política de la app; solo se guarda su hash. Se recupera cuando quieras con `/credentials`.

---

## 1. Activar (una vez por app)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/testers/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{}'
```

Nodo `email_auth.testers: {"enabled": false}` por default. Apagado → todo `/api/v1/testers/*` responde `422 testers.disabled`. `{"enabled": false}` apaga la fábrica; los testers existentes siguen entrando.

---

## 2. Crear

`ttl` obligatorio: `15m | 30m | 1h | 2h | 1w | 1mo | never`.

```bash
# Uno (user_name y name opcionales; sin user_name → nombre realista)
curl -X POST "{BASE_URL}/api/v1/testers" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"user_name": "juanito", "ttl": "1h"}'

# Lote (1–200, todo o nada)
curl -X POST "{BASE_URL}/api/v1/testers/bulk" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"count": 20, "mode": "pattern", "pattern": "qa_{n}", "ttl": "1w"}'
# mode: "realistic" genera nombres coherentes; "pattern" exige {n}
```

Respuesta 201 (en lote, `data` es una lista de esto). **La contraseña solo viaja aquí y en `/credentials`**:

```json
{
  "data": {
    "user_id": "…", "user_name": "juanito", "name": "juanito",
    "email": "juanito@getfoundathyon.mock", "password": "Kq7!mZ2x…",
    "expires_at": "2026-09-23T19:00:00Z", "status": "active"
  }
}
```

`user_name`: minúsculas, dígitos, `.`, `_`, `-`, hasta 64. Repetido → `409 testers.username_taken` con `error.meta.user_names`; en modo `pattern` no se crea ninguno.

---

## 3. Credenciales

```bash
curl "{BASE_URL}/api/v1/testers/credentials" -H "X-API-Key: {secret_key}"              # JSON
curl "{BASE_URL}/api/v1/testers/credentials?format=csv" -H "X-API-Key: {secret_key}"   # CSV adjunto
curl "{BASE_URL}/api/v1/testers/{id}/credentials" -H "X-API-Key: {secret_key}"         # uno
```

CSV: `user_id,user_name,name,email,password,expires_at,status`.

Tras **rotar `SECRET_PASSWORD`** o cambiar la política de contraseñas de la app, las derivadas dejan de coincidir con los hashes (signin → 401). Arreglo, por app:

```bash
curl -X POST "{BASE_URL}/api/v1/testers/regenerate" -H "X-API-Key: {secret_key}"
# → { "data": { "regenerated": N } }
```

---

## 4. Iniciar sesión

- **UI / e2e:** `POST /api/v1/emails/signin` (publishable key) con correo y contraseña de `/credentials`. Igual que una persona.
- **CI / scripts:** token directo, sin contraseña, mismo par que el signin:

```bash
curl -X POST "{BASE_URL}/api/v1/testers/{id}/token" -H "X-API-Key: {secret_key}"
# → { "data": { "access_token": "eyJ…", "refresh_token": "eyJ…" } }
```

---

## 5. Vigencia

- Caducado → `403 testers.expired` en signin (después de validar la contraseña), `refresh-jwt` y `/token`. **Sigue existiendo y listado** con `status: "expired"`; nada se borra solo.
- El `exp` de todo access y refresh token de un tester es `≤ expires_at`, aunque la app emita tokens más largos. Un cliente no debe asumir la vida configurada de la app.
- Alargar o revivir (cuenta desde ahora; las sesiones viejas no reviven):

```bash
curl -X PATCH "{BASE_URL}/api/v1/testers/{id}/expiry" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"ttl": "1w"}'
```

---

## 6. Listar y borrar

```bash
curl "{BASE_URL}/api/v1/testers?status=expired&page=0&size=50" -H "X-API-Key: {secret_key}"
curl "{BASE_URL}/api/v1/users?is_test=true" -H "X-API-Key: {secret_key}"   # solo testers; false = solo personas

curl -X DELETE "{BASE_URL}/api/v1/testers/{id}" -H "X-API-Key: {secret_key}"                        # {deleted: 1}
curl -X DELETE "{BASE_URL}/api/v1/testers?status=expired&confirm=true" -H "X-API-Key: {secret_key}"  # {deleted: N}
```

`/testers` devuelve `status` y `ttl_remaining` (segundos) por elemento, paginado (`meta.pagination`). Los valores `null` se omiten de la respuesta: un tester `never` llega sin `expires_at` ni `ttl_remaining`. Sin `confirm=true` → `422 testers.confirm_required`. Cada borrado es en cascada y publica `user.deleted`.

---

## 7. Flujos públicos y el dominio reservado

| Flujo | Con `@getfoundathyon.mock` |
|---|---|
| `POST /emails/signup` (con o sin verificación), `POST /pending-registrations`, login social | `422 emails.reserved_domain` |
| `POST /emails/magic-link/request`, `/emails/email-code/request` | 200 uniforme, no crea ni envía nada |
| Allowlist / blocklist de la app | No aplican: el tester entra igual |
| `POST /users/{id}/set-password`, `/emails/reset`, `/reset-confirm`, `/reset/validate-code` | `409 testers.password_managed` |
| `PATCH /users/{id}/role` | `409 testers.role_locked` |

`set-password` y `role` responden con la envoltura antigua: el scope viene en `errors[0].scope`.

---

## 8. Webhook

`accounts.user.signup` lleva en todas las altas `data.user.is_test` y `data.user.expires_at`; en las de testers, además, `data.auth.source: "tester"`. Un lote de N dispara N eventos. Úsalo para marcar y limpiar en tu sistema lo que nació como prueba. Ver [webhooks.md](webhooks.md).

---

## Errores

| Scope | HTTP | Acción |
|-------|------|--------|
| `testers.disabled` | 422 | Activar `email_auth.testers` |
| `testers.username_taken` | 409 | Otro nombre/patrón (`error.meta.user_names`) |
| `testers.not_found` | 404 | El id no es un tester de la app |
| `testers.expired` | 403 | `PATCH /testers/{id}/expiry` |
| `testers.password_managed` | 409 | Usar `/credentials`, no cambiar la contraseña |
| `testers.role_locked` | 409 | El rol es siempre `default` |
| `testers.confirm_required` | 422 | Añadir `confirm=true` |
| `testers.password_policy` | 422 | La política de la app no se puede cumplir |
| `emails.reserved_domain` | 422 | Dominio de testers en un flujo público |

## Reglas para agentes

1. Nunca uses la secret key en frontend: los testers se crean y se leen desde backend, CI o scripts.
2. No persistas contraseñas de testers en tu código: pídelas a `/credentials` cuando las necesites.
3. Para seeds, prefiere `bulk` + `/token`; para probar la UI de login, `signin` con la contraseña descargada.
4. Filtra `is_test` (o escucha `data.user.is_test` en el webhook) para no mezclar testers con métricas reales.
