# Usuarios — endpoints

## Verificar si email existe

```bash
curl -X POST "{BASE_URL}/api/v1/users/exist" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "email": "user@example.com" }'
```

Útil antes de signup/login unificado.

---

## Crear usuario (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/users" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "email": "...", "role_id": "...", ... }'
```

---

## Eliminar cuenta propia

```bash
curl -X DELETE "{BASE_URL}/api/v1/users/me" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}"
```

---

## Eliminar usuario (admin o self)

```bash
# Por JWT autenticado — alias de /api/v1/users/me.
# Exige también la publishable key: sin ella responde 401.
curl -X DELETE "{BASE_URL}/api/v1/users" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}"

# Por ID (admin secret)
curl -X DELETE "{BASE_URL}/api/v1/users/{user_id}" \
  -H "X-API-Key: {secret_key}"
```

> `DELETE /api/v1/users` y `DELETE /api/v1/users/me` son el mismo camino: borran
> la cuenta del dueño del access token y sólo si pertenece a la app de la
> publishable key. Para código nuevo usa `/me`.

---

## Actualizar rol (admin)

```bash
curl -X PATCH "{BASE_URL}/api/v1/users/{user_id}/role" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "role": "admin" }'
```

Sobre un usuario de prueba (tester) responde `409 testers.role_locked`: su rol es siempre `default`. Lo mismo con `POST /api/v1/users/{user_id}/set-password` → `409 testers.password_managed`. Ambos devuelven el scope en `errors[0].scope`.

---

## Metadata de usuario

JSON dinámico por implementador (requiere metadata schema activo):

```bash
# Propio usuario
curl -X PATCH "{BASE_URL}/api/v1/users/me/metadata" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{ "metadata": { "phone": "+34600...", "company": "Acme" } }'

# Admin por user ID
curl -X PATCH "{BASE_URL}/api/v1/users/{user_id}/metadata" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "metadata": { "plan": "pro" } }'
```

### Metadata en el access_token (Pro)

`GET`/`PUT /api/v1/user-metadata-policy` (secret key) decide qué claves de primer nivel viajan como claims: `{"enabled": bool, "allowed_keys": [...], "include_user_writable": bool}`.

- `include_user_writable: true` → llegan las claves permitidas las haya escrito quien sea (comportamiento de siempre; las políticas que ya existían lo conservan).
- `include_user_writable: false` → solo las claves cuyo valor actual escribió el backend con la **secret key** (`PATCH /users/{id}/metadata`, `POST /users`, testers). **Default de una política nueva.** Lo que escribe el usuario (`PATCH /users/me/metadata`, metadata de signup/login nativo) no llega al JWT; si el usuario sobrescribe una clave del backend, deja de llegar hasta que el backend la reescriba.
- Sin el campo en el `PUT` se conserva el valor guardado. La respuesta de los endpoints de metadata no cambia.
- Nunca confíes en un claim de metadata para autorizar si la política tiene `include_user_writable: true`.

---

## Cambio de email

### 1. Solicitar cambio

```bash
curl -X POST "{BASE_URL}/api/v1/users/change-email/request" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}" \
  -d '{ "new_email": "nuevo@example.com" }'
```

### 2. Confirmar con código

```bash
curl -X POST "{BASE_URL}/api/v1/users/change-email/confirm" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}" \
  -d '{ "code": "123456" }'
```

---

## Listar y buscar usuarios

Requiere **secret key** con `users:read` (o `X-Admin-API-Key`; ahí `app_id` en el query acota a una app y, sin él, busca en todas las apps de la instancia). Con la secret key la app es siempre la de la key: el `app_id` del query se ignora. Una key que no resuelve a ninguna app → `401 tenant.app_unresolved` (nunca "todas las apps").

```bash
# Todos (como siempre)
curl "{BASE_URL}/api/v1/users?page=0&size=20" -H "X-API-Key: {secret_key}"

# Solo testers / solo personas
curl "{BASE_URL}/api/v1/users?is_test=true"  -H "X-API-Key: {secret_key}"
curl "{BASE_URL}/api/v1/users?is_test=false" -H "X-API-Key: {secret_key}"

# Búsqueda (patrón Criteria): todos los filtros se combinan con AND
curl -G "{BASE_URL}/api/v1/users" -H "X-API-Key: {secret_key}" \
  --data-urlencode "q=ana" \
  --data-urlencode "verified=true" \
  --data-urlencode "created_from=2026-01-01" \
  --data-urlencode "sort=-last_login,email" \
  --data-urlencode "size=50"
```

Sintaxis: `campo=valor` usa el operador por defecto del campo; `campo[operador]=valor` uno explícito (codifica los corchetes: `email%5Bcontains%5D=@acme.com`). Un `?q=` vacío es "sin filtro".

| Param | Tipo | Operadores | Qué filtra |
|---|---|---|---|
| `q` | texto (≤ 100) | `contains` | correo (de email o de su identidad OAuth), `user_name` y `name` |
| `email` | texto | `eq` (def.), `contains` | correo de email u OAuth |
| `user_name`, `name` | texto | `eq` (def.), `contains` | |
| `role` | texto | `eq` | nombre del rol |
| `role_id` | id | `eq` | |
| `verified` | bool | `eq` | `true`: algún método de login verificado; `false`: ninguno |
| `mfa_enabled` | bool | `eq` | TOTP activo |
| `provider` | token | `eq` | `email` o la plataforma OAuth (`google`, `apple`, `microsoft`, `github`, …) |
| `is_test` | bool | `eq` | testers / personas |
| `created_at` | fecha | `gte`, `lte` | alias `created_from` / `created_to` |
| `last_login` | fecha | `gte`, `lte` | último login exitoso del historial (`login_events`, sujeto a `LOGIN_EVENTS_RETENTION_DAYS`); alias `last_login_from` / `last_login_to` |

- Texto: sin distinguir mayúsculas (también acentos y ñ); `%` y `_` se buscan literalmente.
- Fechas: RFC 3339 o `YYYY-MM-DD` (UTC); con `lte`/`_to` una fecha sin hora incluye el día entero.
- `sort`: `created_at` (por defecto), `email`, `last_login`, `user_name`, `name`; `-` delante es descendente; hasta 3 separados por coma. Los vacíos (sin correo, sin login) van al final.
- `page` (desde 0) y `size` (por defecto 10, máximo 100; uno mayor se recorta).
- Un param desconocido **sin** corchetes se ignora (como siempre). Un campo u operador fuera de la lista, un valor mal formado, un param repetido o un `sort` no permitido → `422 users.list.invalid_filter` / `users.list.invalid_sort` con `error.meta.field` (el param). `page`/`size` inválidos siguen en `400 users.list.invalid_pagination` e `is_test` en `400 users.list.invalid_is_test`.

Cada usuario lleva `is_test`, `expires_at` y `status` (`active` | `expired`, calculado). La respuesta omite los valores `null`: una persona llega sin `expires_at`. Nunca incluye contraseñas ni el secreto TOTP. Los testers se gestionan en [testers.md](testers.md).

## Ver un usuario

```bash
curl "{BASE_URL}/api/v1/users/{user_id}" -H "X-API-Key: {secret_key}"
```

Misma forma que cada elemento del listado (rol, `login_methods`, `is_test`, `status`). Scope `users:read`. Un id de otra app, inexistente o que no es un UUID responde igual: `404 users.get.not_found`. Igual que el listado: con secret key manda la key (una key sin app → `401 tenant.app_unresolved`); con `X-Admin-API-Key`, `app_id` acota a una app y sin él lee el usuario de cualquier app. Un fallo de base de datos es `500 users.get.error` (reintentable), nunca un 404.

---

## Sesiones activas

Dónde tiene el usuario la sesión abierta (dispositivo, IP, user-agent, último uso) y cerrar la que no reconoce:

```bash
# Las propias (la de este access token trae current: true)
curl "{BASE_URL}/api/v1/users/me/sessions" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}"

curl -X DELETE "{BASE_URL}/api/v1/users/me/sessions/{session_id}" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {access_token}"

# Las de un usuario, desde el backend
curl "{BASE_URL}/api/v1/users/{user_id}/sessions" -H "X-API-Key: {secret_key}"
```

Formato, rotación de refresh tokens y logout desde el cliente en [tokens.md](tokens.md).
