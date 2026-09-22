# Magic link — autenticación passwordless

Requiere behavior **magic link** activado en la app (admin con secret key).

## Concepto clave

El click del email **no** entrega JWT en la URL. Entrega un **token corto de un solo uso** que el frontend canjea por JWT vía POST.

```
Email click → tu página /auth/verify?token=RAW
           → POST /magic-link/claim { token: RAW }
           → JSON con access_token + refresh_token
```

**Por qué:** JWTs en URL se filtran en logs, history y scanners de email.

---

## Activar magic link (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/magic-link/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "enabled": true }'
```

Config adicional en behavior `email_auth` (redirect paths, TTL, etc.).

---

## Request — enviar enlace

Usuario ingresa email en tu UI:

```bash
curl -X POST "{BASE_URL}/api/v1/emails/magic-link/request" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "email": "user@example.com",
    "redirect_path": "/dashboard"
  }'
```

- Si magic link **disabled** → 422
- Email enviado con enlace que apunta a tu frontend + token raw

---

## Claim — canjear token

Tu página `/auth/verify` lee `token` de query params:

```bash
curl -X POST "{BASE_URL}/api/v1/emails/magic-link/claim" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {publishable_key}" \
  -d '{
    "token": "raw_token_from_email_url"
  }'
```

Respuesta: `access_token`, `refresh_token` — guardar en storage seguro, **nunca** en URL.

Luego redirigir a `redirect_path`.

---

## Flujo frontend

```typescript
// 1. Pantalla login
await fetch(`${BASE_URL}/api/v1/emails/magic-link/request`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-API-Key": pk },
  body: JSON.stringify({ email, redirect_path: "/dashboard" }),
});

// 2. Página /auth/verify
const raw = new URLSearchParams(location.search).get("token");
const res = await fetch(`${BASE_URL}/api/v1/emails/magic-link/claim`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-API-Key": pk },
  body: JSON.stringify({ token: raw }),
});
const { data } = await res.json();
saveSession(data.access_token, data.refresh_token);
router.push("/dashboard");
```

---

## Errores

| HTTP | Causa |
|------|-------|
| 422 | Magic link no activo |
| 400/401 | Token inválido, expirado o ya usado |
| 404 | Email no encontrado (según config) |

Ver [behaviors.md](behaviors.md).
