# Entornos y variables

Vuelve al índice: [SKILL.md](../SKILL.md).

## Un proyecto por entorno

Cada entorno es un proyecto de Foundathyon con sus propios servicios. Las
keys, los usuarios, los jobs y los datos no se comparten entre entornos.

| Entorno | Proyecto | De dónde salen las variables |
| --- | --- | --- |
| Local | Staging, o uno *Desarrollo* | `.env` local, en `.gitignore` |
| Staging | *Staging* | El gestor de secretos de staging |
| Producción | *Producción* | El gestor de secretos de producción |
| CI | La organización | Variables y secretos de CI en el panel |

## Nombres de variables

El prefijo es el producto. El mismo nombre en todos los entornos; cambia el
valor.

```env
# Accounts
ACCOUNTS_BASE_URL=https://foundathyon.com/services/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...      # se puede exponer al cliente
ACCOUNTS_SECRET_KEY=sk_live_...           # solo backend

# Webhooks de Foundathyon
FOUNDATHYON_WEBHOOK_SECRET=...            # solo backend

# Cron jobs: lo que verifica /internal/cron/*
CRON_JOBS_TOKEN=...                       # solo backend; mismo valor en el secreto de cada job
```

En frameworks que exponen variables al navegador por prefijo
(`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`), solo la publishable key y la URL
base llevan ese prefijo. Nunca una secret key ni un token.

## `.env.example`

Commitea un `.env.example` con todos los nombres y valores vacíos o de
ejemplo, y valida al arrancar que los obligatorios existen.

## Rotación

| Qué | Dónde se rota | Pasos |
| --- | --- | --- |
| Secret key de Accounts | Servicio Accounts → API keys | Crear la nueva, desplegarla, revocar la vieja |
| `CRON_JOBS_TOKEN` | Tu backend y el secreto de cada job | Aceptar temporalmente el viejo y el nuevo en el endpoint, actualizar los jobs, quitar el viejo |
| Secret de un webhook | Configuración del webhook | La firma puede traer varias; acepta el viejo y el nuevo durante el cambio |
| Token del registry | Registry de la organización | Crear el nuevo, actualizar `secrets.REGISTRY_TOKEN`, borrar el viejo |
