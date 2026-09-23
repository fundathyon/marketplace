# Tokens — validación, refresh y revocación

## Validar tokens

| Endpoint | Token en Authorization |
|----------|------------------------|
| `GET /api/v1/validate-access` | access token |
| `GET /api/v1/validate-refresh` | refresh token |

```bash
curl -X GET "{BASE_URL}/api/v1/validate-access" \
  -H "Authorization: Bearer {access_token}"
```

Respuesta 200:

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "is_valid": true,
    "entity_type": "oauth"
  }
}
```

401 si inválido o expirado.

---

## Refrescar access token

`GET /api/v1/refresh-jwt` — intercambia refresh válido por nuevo access. El refresh enviado **sigue válido**.

```bash
curl -X GET "{BASE_URL}/api/v1/refresh-jwt" \
  -H "X-API-Key: {publishable_key}" \
  -H "Authorization: Bearer {refresh_token}"
```

Respuesta 201:

```json
{
  "success": true,
  "status_code": 201,
  "data": {
    "jwt": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

Errores:

| HTTP | Causa | Acción |
|------|-------|--------|
| 401 | Refresh inválido/expirado | Re-login |
| 404 | Refresh revocado en DB | Re-login |
| 403 | `testers.expired`: el usuario es un tester caducado | Revivirlo con `PATCH /api/v1/testers/{id}/expiry` y volver a iniciar sesión |

---

## Información del usuario

```bash
curl -X GET "{BASE_URL}/api/v1/jwt/info" \
  -H "Authorization: Bearer {refresh_token}"
```

---

## Revocar refresh (logout servidor)

Requiere **secret key** — operación desde tu backend:

```bash
# Por token JWT
curl -X POST "{BASE_URL}/api/v1/revoke-refresh" \
  -H "X-API-Key: {secret_key}" \
  -H "Authorization: Bearer {refresh_token}"

# Por ID del claim del refresh token
curl -X DELETE "{BASE_URL}/api/v1/revoke-refresh/{token_id}" \
  -H "X-API-Key: {secret_key}"
```

Respuesta 200:

```json
{
  "success": true,
  "data": { "revoked": true, "id": "..." }
}
```

---

## Patrón cliente (refresh automático)

```typescript
async function withAuth<T>(fn: (token: string) => Promise<T>): Promise<T> {
  try {
    return await fn(accessToken);
  } catch (e) {
    if (e.status === 401 && refreshToken) {
      const res = await fetch(`${BASE_URL}/api/v1/refresh-jwt`, {
        headers: {
          "X-API-Key": publishableKey,
          Authorization: `Bearer ${refreshToken}`,
        },
      });
      if (!res.ok) throw new SessionExpiredError();
      const { data } = await res.json();
      accessToken = data.jwt ?? data.access_token;
      return await fn(accessToken);
    }
    throw e;
  }
}
```

---

## Resumen

| Acción | Método | Endpoint | Auth |
|--------|--------|----------|------|
| Validar access | GET | `/api/v1/validate-access` | Bearer access |
| Validar refresh | GET | `/api/v1/validate-refresh` | Bearer refresh |
| Nuevo access | GET | `/api/v1/refresh-jwt` | Public + Bearer refresh |
| Info usuario | GET | `/api/v1/jwt/info` | Bearer refresh |
| Revocar | POST | `/api/v1/revoke-refresh` | Secret + Bearer refresh |
| Revocar por ID | DELETE | `/api/v1/revoke-refresh/:id` | Secret |

## JWT

- Firmados con **RSA** (claves configuradas en el servidor)
- Access: corta duración
- Refresh: larga duración; persistido en DB con `id` claim
- **Testers:** el `exp` del access y del refresh nunca pasa del `expires_at` del tester, aunque la app emita tokens más largos. No asumas la vida configurada; lee `exp`. Ver [testers.md](testers.md)
- Ver claims en payload JWT decodificado (base64)
