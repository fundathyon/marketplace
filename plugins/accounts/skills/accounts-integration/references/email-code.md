# Código de acceso por correo (Email OTP) — passwordless

Requiere behavior **email_code** activado en la app (admin con secret key). Es la estrategia hermana del [magic link](./magic-link.md): el usuario teclea su correo, recibe un **código corto** (6 dígitos por default) y lo escribe en la misma pantalla. Sirve para **entrar y para crear la cuenta**: si el correo no existe y `auto_signup` está activo, la cuenta se crea sola.

## Concepto clave

```
Pantalla login → POST /email-code/request { email }
              ← 200 { challenge_id, expires_in }      (siempre 200, exista o no el correo)
Correo        → "482913 es tu código de {app}"
Misma pestaña → POST /email-code/claim { challenge_id, code }
              ← 200/201 { access_token, refresh_token, user: { id, email, is_new } }
```

- El `challenge_id` lo devuelve `/request` y **se guarda en la pestaña** (memoria o sessionStorage); el canje lo exige. Así un código corto no se puede adivinar sin conocer además un identificador aleatorio de 122 bits.
- El código tiene **intentos limitados** (`max_verify_attempts`, default 5): al agotarlos hay que pedir otro.
- Pedir un código nuevo **deja sin efecto el anterior** (`single_active_code`).
- Cuándo usar cada uno: **código** para escribirlo en la misma pantalla (móvil, kiosco, registro a un evento); **magic link** para abrir en otro dispositivo.

---

## Activar (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/email-code/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "enabled": true,
    "auto_signup": true,
    "code_size": 6,
    "code_type": "numeric",
    "ttl_seconds": 600,
    "max_verify_attempts": 5,
    "resend_cooldown_seconds": 60,
    "email_branding": { "from_name": "Mi App", "subject": "Tu código de acceso" }
  }'
```

Todos los campos son opcionales; el endpoint hace merge y `enabled` se asume `true` en la primera activación. También se puede editar con `PUT /api/v1/app-behaviors/:id` dentro de `config.email_code`.

| Campo | Default | Rango / valores |
|-------|---------|-----------------|
| `enabled` | `true` al activar | bool |
| `auto_signup` | `true` | bool — crear la cuenta si el correo es nuevo |
| `code_size` | `6` | 4–12 |
| `code_type` | `numeric` | `numeric` · `alphanumeric` (mayúsculas + dígitos, sin 0/O/1/I/L; el canje acepta minúsculas) · `alphanumeric_special` (lo anterior + `#$%&*+-=?@!`) |
| `code_strategy` | `random` | `random` · `fixed` (solo entornos de prueba: local, development, staging, qa, test) |
| `fixed_code` | — | obligatorio con `fixed`; debe medir `code_size` y usar el alfabeto de `code_type` |
| `ttl_seconds` | `600` | 60–3600 |
| `max_verify_attempts` | `5` | 1–20 — intentos fallidos por código antes de invalidarlo |
| `window_seconds` / `max_attempts_per_window` | `600` / `5` | envíos por correo por ventana |
| `resend_cooldown_seconds` | `60` | 0–3600 — espera mínima entre dos envíos al mismo correo |
| `single_active_code` | `true` | bool — un código nuevo invalida el anterior |
| `bind_to_ip` / `bind_to_user_agent` | `false` | bool — el canje debe venir de la misma IP / User-Agent |
| `email_branding` | plantilla | `from_name`, `subject`, `logo_url`. El asunto admite `{app_name}` y `{otp_code}`: `"{otp_code} es tu código de {app_name}"` da un asunto al estilo Luma |

---

## Request — enviar código

```bash
curl -X POST "{BASE_URL}/api/v1/emails/email-code/request" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "email": "user@example.com" }'
```

Respuesta (siempre 200, exista o no el correo):

```json
{ "success": true, "status_code": 200, "data": { "challenge_id": "2f7c1e9a-…", "expires_in": 600 } }
```

- `422 email_code.disabled` → activar el behavior
- `429 email_code.cooldown` → esperar `resend_cooldown_seconds`
- `429 email_code.rate_limit_exceeded` → demasiados envíos en la ventana

---

## Claim — canjear código

```bash
curl -X POST "{BASE_URL}/api/v1/emails/email-code/claim" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{ "challenge_id": "2f7c1e9a-…", "code": "482913" }'
```

Respuesta: `access_token`, `refresh_token`, `user.is_new` (`true` y HTTP **201** cuando la cuenta se creó o entró por primera vez; `false` y **200** cuando ya existía). Guardar los tokens en storage seguro.

`user.is_new = true` también dispara el webhook `accounts.user.signup`: la cuenta se anuncia en el primer canje, no al pedir el código.

| HTTP | `scope` | Qué hacer |
|------|---------|-----------|
| 401 | `email_code.invalid` | Código equivocado (o challenge desconocido). `error.meta.remaining_attempts` dice cuántos quedan |
| 401 | `email_code.attempts_exceeded` | Intentos agotados: pedir un código nuevo |
| 401 | `email_code.expired` | Venció: pedir uno nuevo |
| 401 | `email_code.superseded` | Se pidió otro después: usar el más reciente |
| 401 | `email_code.already_used` | Ya se canjeó |
| 401 | `email_code.binding_mismatch` | Otra IP / User-Agent (solo con binding activo) |
| 422 | `email_code.disabled` | Estrategia apagada |

---

## Flujo frontend

```typescript
// 1. Pantalla login: pedir el código y guardar el challenge en la pestaña
const req = await fetch(`${BASE_URL}/api/v1/emails/email-code/request`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-API-Key": pk },
  body: JSON.stringify({ email }),
});
const { data: { challenge_id, expires_in } } = await req.json();
sessionStorage.setItem("email_code_challenge", challenge_id);
// Mostrar "Revisa tu correo" + 6 casillas + "reenviar" deshabilitado unos segundos

// 2. Misma pantalla: canjear
const res = await fetch(`${BASE_URL}/api/v1/emails/email-code/claim`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-API-Key": pk },
  body: JSON.stringify({ challenge_id: sessionStorage.getItem("email_code_challenge"), code }),
});
const body = await res.json();
if (!body.success) {
  if (body.error.scope === "email_code.invalid") showError(`Código incorrecto, quedan ${body.error.meta.remaining_attempts}`);
  else if (["email_code.attempts_exceeded", "email_code.expired", "email_code.superseded"].includes(body.error.scope)) askForNewCode();
  return;
}
saveSession(body.data.access_token, body.data.refresh_token);
router.push(body.data.user.is_new ? "/welcome" : "/dashboard");
```

UX recomendada: casillas numéricas, teclado numérico en móvil, pegar el código completo, enviar solo al completar, mostrar "vence en N min", y no cerrar la pestaña (el challenge vive ahí).

Ver [behaviors.md](./behaviors.md) y [error-scopes.md](./error-scopes.md).
