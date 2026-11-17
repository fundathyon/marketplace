# Roles y políticas (RBAC)

Autorización granular por app (Community y Pro). Requiere **secret key** en todos los endpoints de gestión y en `/authorize`.

## Conceptos

| Entidad | Descripción |
|---------|-------------|
| **Role** | Rol de usuario (ej. `default`, `admin`) |
| **Policy** | Regla allow/deny sobre recurso + acción |
| **Role-Policy** | Asignación de policies a roles |

El `role` en signup referencia un rol de la app.

---

## Roles

```bash
# Listar
curl "{BASE_URL}/api/v1/roles" \
  -H "X-API-Key: {secret_key}"

# Crear
curl -X POST "{BASE_URL}/api/v1/roles" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "name": "editor", "description": "..." }'

# Actualizar
curl -X PATCH "{BASE_URL}/api/v1/roles/{id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "name": "editor-v2" }'

# Eliminar
curl -X DELETE "{BASE_URL}/api/v1/roles/{id}" \
  -H "X-API-Key: {secret_key}"
```

---

## Políticas

Una policy es `(resource, action, effect)` de la app; `effect` es `allow` o `deny`. `name`, `resource`, `action` y `effect` son obligatorios en el alta.

```bash
# Listar (page, size hasta 100, offset)
curl "{BASE_URL}/api/v1/policies?page=0&size=100" \
  -H "X-API-Key: {secret_key}"

# Crear (409 si ya existe el mismo resource/action/effect)
curl -X POST "{BASE_URL}/api/v1/policies" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "name": "create_posts",
    "description": "Crear posts",
    "resource": "posts",
    "action": "create",
    "effect": "allow"
  }'

# Editar: mismos campos que el alta, todos opcionales (solo cambia los que llegan)
curl -X PATCH "{BASE_URL}/api/v1/policies/{id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "effect": "deny" }'
# 400 policies.update.validation · 404 policies.update.not_found · 409 policies.update.already_exists

# Borrar (definitivo; la quita de todos los roles)
curl -X DELETE "{BASE_URL}/api/v1/policies/{id}" \
  -H "X-API-Key: {secret_key}"
# 404 policies.delete.not_found
```

---

## Asignar policy a role

```bash
curl -X POST "{BASE_URL}/api/v1/role-policies" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "role_id": "...",
    "policy_id": "..."
  }'

# Ver policies de un rol → {role, policies: [policy completa…]} (lista vacía si no tiene)
curl "{BASE_URL}/api/v1/role-policies/{role_id}" \
  -H "X-API-Key: {secret_key}"

# Quitar una policy de un rol (la policy sigue existiendo)
curl -X DELETE "{BASE_URL}/api/v1/role-policies/{role_id}/{policy_id}" \
  -H "X-API-Key: {secret_key}"
# 200 {role_id, policy_id, removed} · 404 role_policies.remove.not_found
```

`/api/v1/role-policies` es la ruta canónica; `/api/v1/role_policies` queda como alias con los mismos handlers.

---

## Claim `role` en el access token

Todo access token lleva `role` con el **nombre** del rol del usuario en la app (sale de la base; un `role` en la metadata del usuario se descarta; se omite si el usuario no tiene rol). Con `JWT_PERMISSIONS_CLAIM=true` (default `false`) lleva además `permissions`: los `"resource:action"` que el rol tiene permitidos (allow sin un deny igual). El claim refleja el rol **cuando se emitió el token**.

---

## `POST /api/v1/authorize` (decisión autoritativa)

```bash
curl -X POST "{BASE_URL}/api/v1/authorize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "user_id": "…", "action": "delete", "resource": "invoices" }'
# o { "access_token": "eyJ…", "action": …, "resource": … }  (exactamente uno de los dos)
```

```json
{ "success": true, "status_code": 200,
  "data": { "allowed": false, "role": "editor", "matched_policy_id": "…", "effect": "deny" } }
```

- Evalúa las policies del **rol actual** del usuario (de la base, no del claim).
- `resource` y `action` se comparan exactos (sin comodines).
- Un `deny` que coincide gana sobre cualquier `allow`; sin coincidencia se deniega (`allowed: false`, `matched_policy_id: null`, `effect: null`).
- Con `access_token`, el token se verifica con la llave y la audiencia de la app.
- Errores: `400 authorize.validation`, `401 authorize.invalid_token`, `404 authorize.user_not_found`, `503 authorize.lookup_error`.

---

## Verificador Go para tu backend (`authz`)

Módulo aparte `github.com/fundathyon/accounts/authz` (solo stdlib + `fd_auth`):

```go
client, err := authz.New(authz.Config{
    BaseURL:   "https://api.example.com/accounts", // host + ROOT_PATH
    Issuer:    "https://api.example.com/accounts", // JWT_ISSUER de Accounts
    AppID:     appID,
    SecretKey: os.Getenv("ACCOUNTS_SECRET_KEY"),   // solo para Authorize
})
claims, err := client.Verify(ctx, r.Header.Get("Authorization")) // 401 / 503
if !claims.HasRole("admin") { /* 403 */ }
d, err := client.Authorize(ctx, authz.Request{AccessToken: token, Action: "delete", Resource: "invoices"})
```

`Verify` valida RS256 contra `GET {BASE_URL}/api/v1/jwks/{app_id}` (público, cacheado; global en Community, de la app en Pro), `typ at+jwt`, `iss`, `aud` = app, `exp` y `nbf`. `HasRole` usa el claim sin red; `HasPermission` solo con `JWT_PERMISSIONS_CLAIM=true`; `Authorize` llama `/api/v1/authorize`.

---

## Uso en integración

1. Al crear app → rol `default` ya existe
2. Signup con `"role": "default"`
3. Chequeos rápidos: claim `role` del access token (verifica el JWT primero)
4. Decisiones sensibles o con el rol al día: `POST /api/v1/authorize` desde tu backend (secret key)

Ver JWT claims en [tokens.md](tokens.md) y [openapi.json](../assets/openapi.json).
