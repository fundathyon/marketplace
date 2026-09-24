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

### Lotes grandes: trabajos (recomendado)

`/bulk` responde al terminar (un lote grande topa con el timeout del proxy). Un trabajo responde **202** al instante y avanza en el servidor:

```bash
curl -X POST "{BASE_URL}/api/v1/testers/jobs" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "action": "create", "n_start": 1, "count": 150, "ttl": "1w",
    "fields": {
      "email":     {"mode": "pattern", "pattern": "qa_{n:03}"},
      "user_name": {"mode": "mock", "kind": "first_last"},
      "name":      {"mode": "mock", "kind": "full_name"},
      "metadata":  {"team": {"mode": "fixed", "value": "QA"}}
    },
    "retry": {"attempts": 3, "backoff_seconds": 2}
  }'
# → 202 { "data": { "job_id": "…", "status": "queued" } }

# Polling hasta status succeeded | failed | interrupted
curl "{BASE_URL}/api/v1/testers/jobs/{job_id}" -H "X-API-Key: {secret_key}"
# → { "data": { "status": "running", "total": 150, "done": 60, "params": {…, "seed": 48213},
#               "result": { "created": 60, "created_ids": […], "skipped": 0, "skipped_items": [],
#                           "notified": 58, "notify_pending": 2, "notify_failed": 0 } } }
```

- Campos: `email` (solo parte local; dominio fijo), `user_name`, `name`, `metadata.<key>`. `mode`: `pattern` (`{n}` o `{n:0W}` obligatorio), `mock` (`kind` de `GET /testers/mock-kinds`, determinista por `seed`+`n`, nombres de México; `email` y `user_name` salen sin número y solo si ya existen se les agrega `n` al final) o `fixed` (`name`/metadata; en `email`/`user_name` solo con `count: 1`, y ese tester no guarda `test_seq`). Defaults: `user_name` mock `first_last`, `name` mock `full_name`, `email` = `user_name`.
- `POST /testers/preview` con el mismo cuerpo → `{seed, n_start, count, items[5]}` (`email` completo); manda esa `seed` al trabajo para obtener lo mismo.
- Un `user_name`/correo existente se salta (`result.skipped`); un tester que agota `retry.attempts` detiene el trabajo (`failed`, `failed_item: {n, error}`) sin revertir: relanzar el mismo rango completa lo que falta.
- Tandas: cada tester de un trabajo `create` guarda `test_batch` = id del trabajo (los de un `/testers/bulk` comparten uno). `GET /testers/batches` → `{batches: [{batch, created_at, count, active, expired}], unbatched}`; `batch=<tanda>` (o `none`) acota `GET /testers`, `GET /testers/credentials` y `target.filter.batch`.
- Cada tester numerado guarda su `n` en `test_seq`; `GET /testers?n_from=&n_to=&q=` filtra por rango y texto.
- Masivos: `{"action": "delete", "confirm": true, "target": …}` y `{"action": "set_expiry", "ttl": "1mo", "target": …}`; `target` = exactamente uno de `{"ids": […]}`, `{"all": true}`, `{"filter": {"status", "n_from", "n_to", "q"}}` (≤ 1000 testers).
- Hasta 2 trabajos corren a la vez por proceso; un reinicio deja el trabajo `interrupted`.

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

`/testers` devuelve `status`, `ttl_remaining` (segundos) y `test_seq` por elemento, acepta `n_from`, `n_to` y `q`, ordena con `order_by` (`created_at`, `test_seq`, `user_name`, `name`, `expires_at`; vacíos al final) y `order` (`asc`/`desc`), paginado (`meta.pagination`); `offset` pide filas exactas de ese orden y manda sobre `page`. Los valores `null` se omiten de la respuesta: un tester `never` llega sin `expires_at` ni `ttl_remaining`. Sin `confirm=true` → `422 testers.confirm_required`. Cada borrado es en cascada y publica `user.deleted`.

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

`accounts.user.signup` lleva en todas las altas `data.user.is_test` y `data.user.expires_at`; en las de testers, además, `data.auth.source: "tester"`. Un lote de N dispara N eventos, en la cola del webhook. Borrar testers envía `accounts.user.deleted` con `initiated_by: "admin"` a los webhooks suscritos. Úsalo para marcar y limpiar en tu sistema lo que nació como prueba. Ver [webhooks.md](webhooks.md).

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
| `testers.confirm_required` | 422 | Añadir `confirm=true` (o `"confirm": true` en un trabajo `delete`) |
| `testers.invalid_input` | 422 | Cuerpo de trabajo/preview inválido: plantilla sin `{n}`, `count` 1–1000, `target` |
| `testers.job_not_found` | 404 | El id no es un trabajo de la app |
| `testers.password_policy` | 422 | La política de la app no se puede cumplir |
| `emails.reserved_domain` | 422 | Dominio de testers en un flujo público |

## Reglas para agentes

1. Nunca uses la secret key en frontend: los testers se crean y se leen desde backend, CI o scripts.
2. No persistas contraseñas de testers en tu código: pídelas a `/credentials` cuando las necesites.
3. Para seeds, prefiere un trabajo `create` (con polling) + `/token`; para probar la UI de login, `signin` con la contraseña descargada.
4. Filtra `is_test` (o escucha `data.user.is_test` en el webhook) para no mezclar testers con métricas reales.
