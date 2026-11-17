---
name: platform-recipes
description: >-
  Recetas que combinan varios productos de Foundathyon en una misma app:
  un SaaS con login (Accounts), tareas programadas (Cron jobs), endpoints de
  salud (Monitoring) y despliegue por tag (CI Pipelines y Registry); cómo
  separar en la API las rutas de usuarios (JWT de Accounts), las de Cron jobs
  (token) y las de webhooks (firma); verificar webhooks de Foundathyon;
  entornos y variables; y el checklist antes de producción. Usar cuando el
  usuario monta un proyecto nuevo sobre Foundathyon, integra más de un
  producto, organiza su backend para varios productos o prepara el
  lanzamiento.
metadata:
  version: "0.1.0"
  status: "stable"
---

# Recetas de la plataforma

Cada receta combina productos. El detalle de cada producto está en su skill;
aquí está cómo encajan. Si falta la skill de un producto, dile al usuario qué
plugin instalar (lo lista `platform-overview`).

| Receta | Productos | Detalle |
| --- | --- | --- |
| SaaS desde cero | Accounts, Cron jobs, Monitoring, CI Pipelines | [references/saas-starter.md](references/saas-starter.md) |
| Tres tipos de llamada entrante en la misma API | Accounts, Cron jobs, webhooks | Abajo |
| Verificar un webhook de Foundathyon | Accounts y los webhooks de la plataforma | [references/webhooks.md](references/webhooks.md) |
| Entornos y variables | Todos | [references/environments.md](references/environments.md) |
| Antes de producción | Todos | Abajo |

## Tres tipos de llamada entrante

Una API integrada con Foundathyon recibe tres tipos de llamada, y cada una se
autentica de una forma distinta. **No las mezcles en un mismo middleware.**

| Quién llama | Prefijo sugerido | Cómo se autentica | Skill |
| --- | --- | --- | --- |
| Tus usuarios (web, móvil) | `/api/…` | `Authorization: Bearer <access_token>` de Accounts, verificado con JWKS o `/validate-access` | `accounts-integration` |
| Cron jobs | `/internal/cron/…` | `Authorization: Bearer <CRON_JOBS_TOKEN>`, comparado en tiempo constante | `cron-jobs-integration` |
| Webhooks de Foundathyon | `/webhooks/foundathyon` | Firma `X-Webhook-Signature` sobre el cuerpo crudo | [references/webhooks.md](references/webhooks.md) |
| Monitoring | `/health`, `/ready` | Sin sesión; respuesta mínima | `monitoring-integration` |

```ts
// Express: un router por tipo de llamada
app.use("/api", requireAccountsJwt, userRoutes);
app.use("/internal/cron", requireCronToken, cronRoutes);
app.post("/webhooks/foundathyon", express.raw({ type: "application/json" }), verifyFoundathyonWebhook, onEvent);
app.get("/health", health);
app.get("/ready", ready);
```

- El receptor de webhooks lee el **cuerpo crudo**: un `express.json()`
  global delante rompe la firma.
- Las rutas de cron y de webhooks quedan fuera de CSRF y de la sesión, pero
  nunca sin autenticación.
- Un `access_token` de usuario nunca abre `/internal/cron`, y el token de
  cron nunca abre `/api`.

## Antes de producción

- [ ] Un proyecto **Producción** separado del de staging, con sus propios servicios y keys
- [ ] Secret keys y tokens solo en el gestor de secretos del backend; nada en el repositorio
- [ ] Accounts: refresh con rotación, logout, MFA y errores por `error.scope` (checklist de `accounts-integration`)
- [ ] Accounts: verificación de correo y política de contraseña decididas en sus behaviors
- [ ] Webhooks: firma verificada, idempotencia por `X-Webhook-Delivery-Id`, respuesta `2xx` rápida
- [ ] Cron jobs: endpoints idempotentes, dentro del timeout del plan, con zona horaria explícita
- [ ] `/health` y `/ready` desplegados y la lista de checks preparada
- [ ] Pipeline por tag que construye y sube la imagen; ningún secreto en `build-arg`
- [ ] **Uso** revisado frente al consumo esperado del primer mes; plan elegido
- [ ] `trace_id` de las respuestas de error en los logs, para soporte
