# Setup — despliegue y configuración

## `{BASE_URL}`

Todas las rutas de este skill usan `{BASE_URL}`:

```
{BASE_URL} = protocolo + host + puerto + ROOT_PATH
```

Ejemplos:

| Entorno | ROOT_PATH | BASE_URL |
|---------|-----------|----------|
| Docker local | `/accounts` | `http://localhost:8000/accounts` |
| Sin ROOT_PATH | `` | `http://localhost:8080` |
| Producción | `/accounts` | `https://api.tudominio.com/accounts` |

## Docker Compose mínimo

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: authify
    ports:
      - "5441:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  accounts:
    image: foundathyon/accounts:latest
    ports:
      - "8000:8000"
    environment:
      PORT: 8000
      ROOT_PATH: /accounts
      ADMIN_API_KEY: secret
      POSTGRES_DSN: postgresql://postgres:secret@db:5432/authify
      DB_SCHEMA: accounts
      ENGINE_DB: POSTGRESQL
    depends_on:
      db:
        condition: service_healthy
```

## Variables de entorno clave (servidor Accounts)

| Variable | Descripción |
|----------|-------------|
| `PORT` | Puerto HTTP (ej. 8000) |
| `ROOT_PATH` | Prefijo de rutas (ej. `/accounts`) |
| `POSTGRES_DSN` | Conexión PostgreSQL |
| `DB_SCHEMA` | Schema (ej. `accounts`) |
| `ADMIN_API_KEY` | Key admin sistema (`GET /v1/apps`) |
| `PRIVATE_KEY_JWT` / `PUBLIC_KEY_JWT` | Par RSA para firmar JWT |
| `REFRESH_EXPIRE` | TTL refresh token |
| `EMAIL_NOTIFICATIONS_ACTIVE` | Envío de emails (activate, reset) |

## Variables en tu app consumidora

```env
ACCOUNTS_BASE_URL=http://localhost:8000/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...
ACCOUNTS_SECRET_KEY=sk_live_...
```

## Documentación interactiva (runtime)

Con la API levantada:

```
{BASE_URL}/docs/index.html
```

Swagger UI generado desde el código Go.

## Health check

```bash
curl "{BASE_URL}/health"
```

## Al crear una app automáticamente se provisiona

- Par de API keys (publishable + secret)
- Rol `default`
- Behavior `email_auth` en modo simple (sin verificación de email)

Esto permite signup/signin inmediato sin config admin adicional.
