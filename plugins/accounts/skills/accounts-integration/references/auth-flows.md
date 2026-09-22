# Árbol de decisión — flujos de autenticación

Usa este documento para elegir endpoints **antes** de escribir código.

## Variables

- `{BASE_URL}` = host + `ROOT_PATH` (ej. `http://localhost:8000/accounts`)
- Todas las rutas email/OAuth de cliente requieren `X-API-Key: publishable_key`

---

## 1. Email + contraseña

```
¿Un solo formulario email/password?
├─ SÍ → POST {BASE_URL}/api/v1/emails/login
│        (detecta signup vs signin según usuario existente)
└─ NO → flujos explícitos
         ├─ Registro → POST /api/v1/emails/signup
         │   ├─ behavior verification OFF
         │   │   └─ Usuario activo → POST /api/v1/emails/signin
         │   └─ behavior verification ON
         │       ├─ Signup crea usuario pendiente
         │       ├─ Usuario recibe código por email
         │       ├─ POST /api/v1/emails/activate { email, code }
         │       └─ Luego POST /api/v1/emails/signin
         └─ Login → POST /api/v1/emails/signin
             └─ Si login requiere verificación extra
                 └─ POST /api/v1/emails/signin/resend-code
```

### Signup body mínimo

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "default"
}
```

Campos opcionales: `user_name`, `metadata` (si metadata schema está activo).

---

## 2. Magic link (passwordless)

Requiere behavior magic link activado en la app.

```
POST /api/v1/emails/magic-link/request  → envía enlace/código
POST /api/v1/emails/magic-link/claim    → intercambia token por sesión
```

Guía completa: [magic-link.md](magic-link.md)

---

## 2b. Código de acceso por correo (passwordless, email OTP)

Requiere behavior `email_code` activado en la app. Misma familia que el magic link: el código para escribirlo en la misma pantalla, el enlace para abrir en otro dispositivo. Sirve para entrar y para crear la cuenta (`auto_signup`).

```
POST /api/v1/emails/email-code/request  { email }                 → 200 { challenge_id, expires_in }
POST /api/v1/emails/email-code/claim    { challenge_id, code }    → tokens + user.is_new
```

Guía completa: [email-code.md](./email-code.md)

---

## 3. OAuth web (redirect)

```
1. GET {BASE_URL}/api/v1/oauths/link?provider=google&redirect_uri=...
   Header: X-API-Key (public)
   → URL de autorización del proveedor

2. Usuario autoriza → redirect a callback de Accounts
   GET {BASE_URL}/api/v1/oauth/{callback_key}?code=...&state=...
   (sin API key — redirect del proveedor)

3. Respuesta incluye tokens o redirige a tu app con tokens
```

Config admin (secret key): `POST /api/v1/oauth-configs`

Detalle: [oauth.md](oauth.md)

---

## 4. OAuth native SDK (Apple / Google Sign-In)

```
Frontend obtiene id_token del SDK nativo
→ POST {BASE_URL}/api/v1/auth/social
  Header: X-API-Key (public)
  Body: { provider, id_token, ... }
```

Audiences nativas se configuran con secret key en `/api/v1/oauth-configs/{id}/audiences`.

Detalle: [oauth.md](oauth.md)

---

## 5. Ciclo de vida de sesión

```
Signin/OAuth → access_token + refresh_token

Llamadas API protegidas:
  Authorization: Bearer {access_token}

Access expirado:
  GET /api/v1/refresh-jwt
  Authorization: Bearer {refresh_token}
  X-API-Key: {publishable_key}

Refresh inválido (401):
  → Re-login (signin u OAuth)

Logout en dispositivo (servidor):
  POST /api/v1/revoke-refresh
  X-API-Key: {secret_key}
  Authorization: Bearer {refresh_token}
```

Detalle: [tokens.md](tokens.md)

---

## 6. Reset de contraseña

```
POST /api/v1/emails/reset              → solicita código
POST /api/v1/emails/reset/validate-code
POST /api/v1/emails/reset/set-password → con JWT temporal
```

Alternativa legacy: `reset-confirm`

---

## Tabla behavior → impacto

| Behavior / config | Efecto en integración |
|-------------------|----------------------|
| `verification.enabled = false` | Signup → signin directo |
| `verification.enabled = true` | Signup → activate → signin |
| Password policy | Validar antes de submit; errores `emails.validation.weak_password` |
| Magic link activo | Ofrecer flujo passwordless por enlace |
| Email code activo | Ofrecer flujo passwordless por código (misma pantalla) |
| OAuth config activo | Mostrar botones sociales + redirect o native |
| Metadata schema | Signup/signin puede requerir `metadata` |

Consultar behavior: endpoints admin con secret key en `/api/v1/app-behaviors`.
