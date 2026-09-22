# Behaviors — configuración por app

Los **behaviors** cambian cómo responden los endpoints sin cambiar las rutas. Siempre verificar la config de la app antes de implementar auth.

## Qué es un behavior

Config JSON por app que activa/desactiva funcionalidades:

- Verificación de email en signup/signin
- Política de contraseñas
- Magic link
- OAuth providers
- Metadata schema en signup
- Notificaciones email

## Behavior principal: `email_auth`

Al crear app (`POST /v1/apps`) se crea email_auth en modo **simple**:

```json
{
  "verification": { "enabled": false }
}
```

### verification.enabled

| Valor | Signup | Signin |
|-------|--------|--------|
| `false` | Usuario activo al instante | Directo |
| `true` | Envía código por email | Requiere activate previo |

### Password policy (ejemplo)

```json
{
  "password": {
    "min_length": 8,
    "min_uppercase": 1,
    "min_lowercase": 1,
    "min_numbers": 1,
    "min_special": 1
  }
}
```

Errores: `emails.validation.weak_password`

---

## Activar verificación email (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/verification/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{}'
```

Desactivar:

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/verification/deactivate" \
  -H "X-API-Key: {secret_key}"
```

---

## Magic link (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/magic-link/activate" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "enabled": true }'
```

Ver [magic-link.md](./magic-link.md).

---

## Metadata schema (admin)

Permite campos JSON dinámicos en signup:

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/metadata-schema/activate" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "schema": {
      "phone": { "type": "string", "required": true }
    }
  }'
```

Signup entonces requiere `metadata: { "phone": "+34..." }`.

---

## CRUD behaviors (admin)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/app-behaviors` | Listar |
| GET | `/api/v1/app-behaviors/:id` | Por ID |
| POST | `/api/v1/app-behaviors` | Crear |
| PUT | `/api/v1/app-behaviors/:id` | Actualizar |
| GET | `/api/v1/app-behaviors/available` | Tipos disponibles |
| GET | `/api/v1/app-behaviors/examples/:code` | Ejemplo de config |

Todas requieren **secret key**.

---

## Regla para agentes

Si el usuario no especifica la config:

1. Preguntar si verification está ON
2. O implementar ambos caminos (signup → check response → activate si aplica)
3. Documentar qué behavior asumiste

Ver [auth-flows.md](./auth-flows.md).
