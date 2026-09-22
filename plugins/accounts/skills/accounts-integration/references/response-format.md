# Formato de respuestas API

Todas las respuestas siguen el envelope estándar.

## Respuesta exitosa

```json
{
  "success": true,
  "status_code": 200,
  "data": { },
  "trace_id": "uuid-opcional"
}
```

`data` varía por endpoint. Signin típico:

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 3600
  }
}
```

Campos de token equivalentes:

| Campo | Significado |
|-------|-------------|
| `access_token` | JWT de acceso |
| `jwt` | Mismo que access_token (algunos endpoints) |
| `refresh_token` | JWT para renovar sesión |

## Respuesta de error

```json
{
  "success": false,
  "status_code": 409,
  "error": {
    "message": "The email address is already registered in this application",
    "scope": "emails.signup.email_already_exists",
    "details": {}
  },
  "trace_id": "uuid-opcional"
}
```

## Reglas para integradores

1. Comprobar `success` además del HTTP status
2. Usar `error.scope` para lógica de UI (ver [error-scopes.md](error-scopes.md))
3. Loguear `trace_id` en soporte/debug
4. No parsear `message` para lógica — puede cambiar; `scope` es estable

## Códigos HTTP habituales

| Código | Significado típico |
|--------|-------------------|
| 200 | OK |
| 201 | Creado (app, refresh token nuevo) |
| 400 | Body inválido |
| 401 | Auth inválida (key, credenciales, token) |
| 403 | Prohibido (cuenta inactiva, app disabled) |
| 404 | Recurso no encontrado |
| 409 | Conflicto (email duplicado, ya activo) |
| 422 | Validación (password débil, metadata) |
| 500 | Error interno |

## Paginación (listados admin)

Algunos endpoints admin devuelven listas paginadas con query params:

```
?page=0&size=10&offset=0
```

Consultar [openapi.json](../assets/openapi.json) por endpoint.
