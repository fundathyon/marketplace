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

## Listar usuarios

Requiere **secret key** (o `X-Admin-API-Key` + `app_id` en el query).

```bash
# Todos (como siempre)
curl "{BASE_URL}/api/v1/users?page=0&size=20" -H "X-API-Key: {secret_key}"

# Solo testers / solo personas
curl "{BASE_URL}/api/v1/users?is_test=true"  -H "X-API-Key: {secret_key}"
curl "{BASE_URL}/api/v1/users?is_test=false" -H "X-API-Key: {secret_key}"
```

Cada usuario lleva `is_test`, `expires_at` y `status` (`active` | `expired`, calculado). La respuesta omite los valores `null`: una persona llega sin `expires_at`. Un `is_test` distinto de `true`/`false` → `400 users.list.invalid_is_test`. Nunca incluye contraseñas. Los testers se gestionan en [testers.md](testers.md).
