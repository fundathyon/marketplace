# Roles y políticas (RBAC)

Autorización granular por app. Requiere **secret key** en todos los endpoints.

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

```bash
# Listar
curl "{BASE_URL}/api/v1/policies" \
  -H "X-API-Key: {secret_key}"

# Crear
curl -X POST "{BASE_URL}/api/v1/policies" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "resource": "posts",
    "action": "create",
    "effect": "allow"
  }'
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

# Ver policies de un rol
curl "{BASE_URL}/api/v1/role-policies/{role_id}" \
  -H "X-API-Key: {secret_key}"
```

---

## Uso en integración

1. Al crear app → rol `default` ya existe
2. Signup con `"role": "default"`
3. Tu app evalúa permisos según el rol del JWT/usuario
4. Accounts gestiona roles; **tu app** implementa enforcement de policies o usa el rol como claim

Ver JWT claims en [tokens.md](tokens.md) y [openapi.json](../assets/openapi.json).
