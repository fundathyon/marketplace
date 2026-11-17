# SaaS desde cero

Vuelve al índice: [SKILL.md](../SKILL.md).

Una app con login, un resumen diario por correo, limpieza nocturna, endpoints
de salud y release por tag. Pasos en orden; cada uno dice qué skill usar.

## 1. En el panel

1. Organización y dos proyectos: **Staging** y **Producción**.
2. En cada proyecto, un servicio **Accounts** y un servicio **Crons**.
3. Copia las keys de Accounts de cada proyecto a las variables de su entorno.
4. Genera un `CRON_JOBS_TOKEN` distinto por entorno (por ejemplo
   `openssl rand -hex 32`) y guárdalo en las variables del backend.

## 2. Login (`accounts-integration`)

- Frontend: signup, signin, refresh con rotación y logout con la publishable
  key.
- Backend: middleware que verifica el `access_token` en las rutas `/api`.
- Decide en los behaviors si hay verificación de correo y MFA; el código
  tiene que manejar `mfa_required` y la activación aunque hoy estén apagados.

## 3. Reaccionar a las altas (`accounts-integration`, webhooks)

- Un webhook de Accounts hacia `/webhooks/foundathyon` crea el perfil de la
  app cuando llega el alta del usuario. Verificación: [webhooks.md](webhooks.md).
- Así el perfil existe aunque el usuario cierre la pestaña tras registrarse.

## 4. Tareas programadas (`cron-jobs-integration`)

| Job | Endpoint | Horario | Zona |
| --- | --- | --- | --- |
| Resumen diario | `POST /internal/cron/daily-digest` | `0 8 * * *` | la del negocio |
| Limpieza | `POST /internal/cron/cleanup` | `0 3 * * *` | la del negocio |

Los dos con `Authorization: Bearer {{secrets.CRON_JOBS_TOKEN}}`, idempotentes
y por lotes. En Free solo hay 5 jobs y 15 minutos de intervalo mínimo.

## 5. Salud (`monitoring-integration`)

- `/health` y `/ready` (base de datos con timeout).
- Lista de checks para cuando Monitoring esté disponible.

## 6. Release (`deployments-integration`)

- `.foundathyon/pipelines/release.yml`: tests y, después, imagen al registry
  con cada tag `v*.*.*`.
- Variables y secretos del pipeline en el panel.
- Mientras Deployments está en preparación, la imagen se despliega donde el
  usuario ya despliega.

## Estructura de un backend Node

```text
src/
  auth/accounts.ts          cliente de Accounts, verificación del JWT
  routes/api/…              rutas de usuarios (JWT)
  routes/internal/cron/…    endpoints de Cron jobs (token)
  routes/webhooks.ts        receptor de webhooks (firma, cuerpo crudo)
  routes/health.ts          /health y /ready
  config.ts                 lee y valida las variables al arrancar
.foundathyon/pipelines/release.yml
```

`config.ts` falla al arrancar si falta una variable obligatoria: mejor un
despliegue que no arranca que uno que falla en la primera petición.
