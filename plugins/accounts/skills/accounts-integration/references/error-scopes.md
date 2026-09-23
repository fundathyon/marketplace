# Error scopes — referencia completa

Implementar manejo por **`error.scope`**, no solo HTTP status.

Formato: ver [response-format.md](response-format.md)

---

## Apps

| Scope | HTTP | Acción |
|-------|------|--------|
| `apps.create.limit_reached` | 403 | Límite edition; no reintentar |
| `apps.create.name_conflict` | 409 | Otro nombre de app |
| `apps.create.invalid_data` | 400 | Validar body |
| `apps.create.internal_error` | 500 | Reintentar / soporte |
| `apps.list.unauthorized` | 401 | Revisar Admin API Key |
| `apps.list.invalid_pagination` | 400 | Corregir page/size |

---

## Signup

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.signup.email_already_exists` | 409 | → signin o reset password |
| `emails.validation.weak_password` | 422 | Mostrar reglas password |
| `emails.validation.invalid_email` | 422 | Corregir email |
| `emails.signup.app_not_found` | 404 | Revisar API key |
| `auth.apikey.invalid` | 401 | Revisar publishable_key / entorno |
| `emails.reserved_domain` | 422 | `@getfoundathyon.mock` es de los testers (también en pending-registrations y login social) |

---

## Resend código (signup)

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.resend.user_not_found` | 404 | → signup |
| `emails.resend.already_active` | 409 | → signin |

---

## Signin

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.signin.invalid_credentials` | 401 | Mensaje genérico |
| `emails.signin.account_locked` | 403 | Bloqueo temporal |
| `emails.signin.account_inactive` | 403 | → activate / resend-code |
| `emails.signin.app_disabled` | 403 | Error config app |
| `testers.expired` | 403 | Usuario de prueba caducado: revivirlo (ver Testers) |

---

## Activate

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.activate.invalid_code` | 400 | Reintentar código |
| `emails.activate.code_expired` | 400 | resend-code |
| `emails.activate.user_not_found` | 404 | → signup |
| `emails.activate.already_active` | 409 | → signin |

---

## Reset password

| Scope | HTTP | Acción |
|-------|------|--------|
| Código inválido | 400 | Reintentar |
| Código expirado | 400 | Nuevo reset |
| Usuario no encontrado | 404 | Mensaje genérico (no revelar) |

---

## Tokens

| Situación | HTTP | Acción |
|-----------|------|--------|
| Access inválido/expirado | 401 | → refresh-jwt |
| Refresh inválido | 401 | → re-login |
| Refresh revocado | 404 | → re-login |
| `testers.expired` | 403 | Dueño tester caducado: re-login no basta, hay que revivirlo |

---

## OAuth

| Situación | HTTP | Acción |
|-----------|------|--------|
| Provider no config | 404/422 | Configurar oauth-configs |
| Redirect mismatch | 400 | Añadir redirect URL |
| Token inválido (native) | 401 | Revisar id_token / audiences |

---

## Magic link

| Situación | HTTP | Acción |
|-----------|------|--------|
| Strategy disabled | 422 | Activar behavior |
| Token usado/expirado | 401 | Nuevo request |

---

## Código de acceso por correo

| Scope | HTTP | Acción |
|-------|------|--------|
| `email_code.disabled` | 422 | Activar behavior |
| `email_code.cooldown` | 429 | Esperar `resend_cooldown_seconds` y reintentar |
| `email_code.rate_limit_exceeded` | 429 | Esperar la ventana |
| `email_code.invalid` | 401 | Código equivocado; `error.meta.remaining_attempts` dice cuántos quedan |
| `email_code.attempts_exceeded` | 401 | Intentos agotados: pedir código nuevo |
| `email_code.expired` / `email_code.superseded` / `email_code.already_used` | 401 | Pedir código nuevo |
| `email_code.binding_mismatch` | 401 | Canjear desde la misma IP / navegador |

---

## Testers (usuarios de prueba)

| Scope | HTTP | Acción |
|-------|------|--------|
| `testers.disabled` | 422 | Activar `email_auth.testers` |
| `testers.username_taken` | 409 | Otro `user_name`/patrón; lista en `error.meta.user_names` |
| `testers.not_found` | 404 | El id no es un tester de la app |
| `testers.expired` | 403 | `PATCH /api/v1/testers/{id}/expiry` y volver a iniciar sesión |
| `testers.password_managed` | 409 | Contraseña derivada: leerla de `/credentials`, no cambiarla (set-password, reset, reset-confirm, reset/validate-code) |
| `testers.role_locked` | 409 | El rol de un tester es siempre `default` |
| `testers.confirm_required` | 422 | Añadir `confirm=true` al borrado en lote |
| `testers.password_policy` | 422 | La política de contraseñas de la app no se puede cumplir |
| `testers.invalid_input` / `dto.validate.*` | 422 | Corregir `ttl`, `mode`, `pattern`, `status`… |
| `testers.lookup_error`, `testers.error_saving`, `testers.error_hashing_password`, `testers.error_generating_tokens` | 500 | Reintentar; loguear `trace_id` |
| `users.list.invalid_is_test` | 400 | `is_test` solo admite `true`/`false` |

`POST /users/{id}/set-password` y `PATCH /users/{id}/role` devuelven el scope en `errors[0].scope` (envoltura antigua).

---

## Patrón implementación

```typescript
function handleScope(scope: string): UiAction {
  const map: Record<string, UiAction> = {
    "emails.signup.email_already_exists": { type: "redirect", to: "/login" },
    "emails.validation.weak_password": { type: "field-error", field: "password" },
    "emails.signin.invalid_credentials": { type: "toast", msg: "Credenciales inválidas" },
    "emails.signin.account_inactive": { type: "activate-flow" },
    "auth.apikey.invalid": { type: "config-error" },
  };
  return map[scope] ?? { type: "generic" };
}
```

---

## Reglas

1. No usar `error.message` para branching — puede cambiar
2. Loguear `trace_id` en errores 5xx
3. 401 en refresh → siempre re-login, no loop infinito
4. Mensajes genéricos en credenciales (seguridad)
