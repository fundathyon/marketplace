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
    "code": 409,
    "message": "The email address is already registered in this application",
    "scope": "emails.signup.email_already_exists",
    "meta": {}
  },
  "trace_id": "4f2a1c9b7e6d5a3f8b0c2d4e6f1a3b5c"
}
```

`error.meta` es opcional: datos estructurados (`retry_after_seconds`,
`remaining_attempts`, `missing_scopes`, errores por campo…).

### Errores delicados: message genérico

La API no devuelve detalles internos. El `scope` y el `status_code` no cambian
nunca; solo el texto:

| Caso | `error.message` | `error.meta` |
|------|-----------------|--------------|
| Cualquier 5xx | `Internal server error` (500) o `Service temporarily unavailable. Try again later.` (502/503/504) | Solo `retry_after_seconds` |
| 4xx de seguridad o interno (p. ej. `api_key_not_found`, `refresh_tokens.info.get_user`) | El genérico del status (`Unauthorized`, `Invalid request`…) | Solo `retry_after_seconds` |
| 4xx de validación o negocio | Descriptivo, tal cual | El de siempre |

Un 4xx descriptivo cuyo texto delataría detalle interno (SQL, rutas, stack)
también sale genérico. El detalle queda en los logs del servidor con el
`trace_id`: es lo que hay que mandar a soporte. Qué caso aplica a cada scope:
[error-catalog.md](error-catalog.md) (generado desde el código).

## Reglas para integradores

1. Comprobar `success` además del HTTP status
2. Usar `error.scope` para lógica de UI (ver [error-scopes.md](error-scopes.md) y [error-catalog.md](error-catalog.md))
3. Loguear `trace_id` en soporte/debug
4. No parsear `message` para lógica — puede cambiar; `scope` es estable
5. En un 5xx, mostrar un mensaje propio: el `message` es genérico a propósito

## Códigos HTTP habituales

| Código | Significado típico |
|--------|-------------------|
| 200 | OK |
| 201 | Creado (app, refresh token nuevo) |
| 400 | Body inválido |
| 401 | Auth inválida (key, credenciales, token) |
| 403 | Prohibido (cuenta inactiva, app disabled) |
| 404 | Recurso no encontrado |
| 409 | Conflicto (email duplicado) |
| 422 | Validación (password débil, metadata) |
| 500 | Error interno (message genérico; detalle en logs por `trace_id`) |

## Paginación (listados admin)

Algunos endpoints admin devuelven listas paginadas con query params:

```
?page=0&size=10&offset=0
```

Consultar [openapi.json](../assets/openapi.json) por endpoint.
