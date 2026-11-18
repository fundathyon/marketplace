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

## 1b. Segundo factor (cualquier flujo que emite tokens)

Behavior `mfa` (Community y Pro; default `optional` en los cinco flujos). Signin, signup sin verificación, activate, magic link, código por correo, OAuth web/popup y nativo pueden responder **el paso en vez de los tokens**:

```
¿La respuesta trae mfa_required o mfa_enrollment_required?
├─ NO → access_token + refresh_token como siempre
├─ mfa_required: true (usuario con TOTP)
│   └─ POST /api/v1/mfa/verify { mfa_token, method: "totp" | "backup_code", code }
│       → 200 access_token + refresh_token
└─ mfa_enrollment_required: true (mode required, usuario sin TOTP)
    ├─ POST /api/v1/mfa/enroll/start   { mfa_token }        → secret, url, qr_image
    └─ POST /api/v1/mfa/enroll/confirm { mfa_token, code }  → tokens + backup_codes (10, una vez)
```

`mfa_token`: un solo uso, 5 min, 5 códigos. `401 mfa.invalid_token` o `429 mfa.too_many_attempts` → volver a iniciar sesión. Testers exentos. Guía completa: [mfa.md](mfa.md)

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

## 2c. Componentes embebidos (Pro)

Sin construir formularios: un `<script src="{BASE_URL}/ui/v1/accounts.js" data-publishable-key="…">` y `<accounts-sign-in>` en tu página hacen los flujos de arriba (contraseña + activación, código, magic link de vuelta a la página, OAuth por popup, signup y reset) según lo que la app tenga activo. Requiere el behavior `embedded_auth` con el origen de tu página en `allowed_origins`. Tu frontend pide el token con `Accounts.getToken()` y tu backend verifica el JWT como siempre.

Guía completa: [embedded-auth.md](./embedded-auth.md)

---

## 3. OAuth web (redirect)

```
1. GET {BASE_URL}/api/v1/oauths/link?provider=google&platform=web&redirect_url=...
   Header: X-API-Key (public)
   → data: URL de inicio del flujo en Accounts (…/oauth/{callback_key}/start?…)

2. El navegador NAVEGA a esa URL (no XHR)
   → Accounts deja una cookie que ata el login a ese navegador
   → 302 al proveedor con un state de un solo uso y PKCE

3. Usuario autoriza → redirect a callback de Accounts
   GET {BASE_URL}/api/v1/oauth/{callback_key}?code=...&state=...
   (sin API key — redirect del proveedor; necesita la cookie del paso 2)

4. 302 a tu app con access_token, refresh_token y provider en la query
   (con segundo factor pendiente: mfa_required=true | mfa_enrollment_required=true,
    mfa_token, mfa_methods y provider — sin tokens; completa con /api/v1/mfa/*)
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
  → guarda access_token y refresh_token de la respuesta
    (con la rotación activa el refresh es nuevo)

Refresh inválido (401):
  → Re-login (signin u OAuth)

Logout desde el cliente (SPA, app móvil):
  POST /api/v1/logout
  Authorization: Bearer {refresh_token}

Logout desde el servidor:
  POST /api/v1/revoke-refresh
  X-API-Key: {secret_key}
  Authorization: Bearer {refresh_token}

Sesiones activas del usuario:
  GET /api/v1/users/me/sessions
  X-API-Key: {publishable_key}
  Authorization: Bearer {access_token}
```

Detalle: [tokens.md](tokens.md)

---

## 6. Reset de contraseña

```
POST /api/v1/emails/reset              → solicita código (200 genérico exista o no la cuenta)
POST /api/v1/emails/reset/validate-code
POST /api/v1/emails/reset/set-password → con JWT temporal; devuelve data.login (sesión)
                                         o 200 sin data.login (contraseña cambiada, hay que hacer signin)
```

Alternativa legacy: `reset-confirm` (email + código + contraseña, nunca devuelve tokens).

En los dos: código y token de un solo uso, código de 10 minutos por defecto,
política de `email_auth` (`422 emails.validation.weak_password`) y, con
`password.policy.check_breached`, `400 password.breached`, sin gastar el
código. Al terminar se cierran sesiones según `session_security` /
`tokens.revocation.on_password_reset`, sale el correo `password_changed_notice`
y el webhook `accounts.user.password_reset`.

---

## Tabla behavior → impacto

| Behavior / config | Efecto en integración |
|-------------------|----------------------|
| `verification.enabled = false` | Signup → signin directo |
| `verification.enabled = true` | Signup → activate → signin |
| Correo de un usuario OAuth + `identity_linking: link_with_proof` | Signup **sin tokens** aunque `verification` esté apagada → activate con el código (enlaza) — ver [identity-linking.md](identity-linking.md) |
| Password policy | Validar antes de submit; errores `emails.validation.weak_password` (signup, activación, reset, cambio y set-password de admin) |
| `password.policy.check_breached = true` (apps nuevas) | Contraseñas filtradas → `400 password.breached`; fail-open si Have I Been Pwned no responde |
| `mfa` `optional` (default) | Usuarios con TOTP activo reciben `mfa_required` en vez de tokens → `/api/v1/mfa/verify` |
| `mfa` `required` | Todos: sin TOTP → `mfa_enrollment_required` → `/api/v1/mfa/enroll/*` |
| Magic link activo | Ofrecer flujo passwordless por enlace |
| Email code activo | Ofrecer flujo passwordless por código (misma pantalla) |
| OAuth config activo | Mostrar botones sociales + redirect o native |
| Metadata schema | Signup/signin puede requerir `metadata` |
| `embedded_auth` (Pro) | Componentes web en las páginas de `allowed_origins`; estrategias = guardadas ∩ disponibles |

Consultar behavior: endpoints admin con secret key en `/api/v1/app-behaviors`.
