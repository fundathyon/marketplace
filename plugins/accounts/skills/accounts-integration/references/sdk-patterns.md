# Patrones SDK — frontend y backend

## Separación de responsabilidades

```
┌─────────────┐     pk_live      ┌──────────────┐
│   Frontend  │ ───────────────► │   Accounts   │
│  (web/móvil)│ ◄── JWT/refresh ─│     API      │
└─────────────┘                  └──────────────┘
       │                                  ▲
       │                                  │ sk_live
┌──────▼──────┐                           │
│   Backend   │ ──────────────────────────┘
│  (tu API)   │   admin, revoke, webhooks
└─────────────┘
```

---

## Variables de entorno

```env
# Frontend (.env público)
NEXT_PUBLIC_ACCOUNTS_BASE_URL=https://api.example.com/accounts
NEXT_PUBLIC_ACCOUNTS_PK=pk_live_...

# Backend (.env secreto)
ACCOUNTS_BASE_URL=https://api.example.com/accounts
ACCOUNTS_SK=sk_live_...
```

---

## Cliente HTTP tipado (TypeScript)

```typescript
const BASE = process.env.NEXT_PUBLIC_ACCOUNTS_BASE_URL!;
const PK = process.env.NEXT_PUBLIC_ACCOUNTS_PK!;

async function signin(email: string, password: string) {
  const res = await fetch(`${BASE}/api/v1/emails/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": PK },
    body: JSON.stringify({ email, password }),
  });
  const body = await res.json();
  if (!body.success) throw new AccountsError(body.error);
  return {
    accessToken: body.data.access_token ?? body.data.jwt,
    refreshToken: body.data.refresh_token,
  };
}
```

---

## Almacenamiento de sesión

| Token | Web recomendado | Móvil |
|-------|-----------------|-------|
| Access | Memoria o sessionStorage | Keychain/Keystore |
| Refresh | HttpOnly cookie (vía BFF) o secure storage | Secure storage |

Evitar refresh en localStorage si hay riesgo XSS.

---

## Backend-for-frontend (BFF)

Opcional: tu backend proxya refresh y revoke:

```
Browser → tu-api/refresh → Accounts /refresh-jwt (pk + refresh)
Browser ← HttpOnly cookie ← tu-api
```

Ventaja: refresh token nunca en JS del browser.

---

## Validación JWT en tu API

Opción A — validar localmente con clave pública RSA de Accounts.

Opción B — delegar:

```bash
curl "{ACCOUNTS_BASE_URL}/api/v1/validate-access" \
  -H "Authorization: Bearer {token}"
```

---

## Manejo de errores

Siempre parsear `error.scope`:

```typescript
class AccountsError extends Error {
  constructor(public error: { scope: string; message: string }) {
    super(error.message);
  }
}
```

Ver [error-scopes.md](error-scopes.md).

---

## Checklist integración frontend

- [ ] `ACCOUNTS_BASE_URL` incluye ROOT_PATH
- [ ] Solo `pk_live` en bundle frontend
- [ ] Refresh antes de expiry o en 401
- [ ] Flujo activate si verification ON
- [ ] OAuth redirect URIs registradas
- [ ] Magic link: claim en POST, no JWT en URL
