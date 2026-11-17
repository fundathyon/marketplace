# Límites del plan y errores

Vuelve al índice: [SKILL.md](../SKILL.md).

Los límites son **de la organización**: el número de jobs y los minutos suman
todos sus servicios de Cron jobs. Si una cifra no coincide con la del panel
(**Plan y facturación**, **Uso**), manda la del panel.

| Límite | Free | Starter | Pro | Enterprise |
| --- | --- | --- | --- | --- |
| Jobs | 5 | 25 | 200 | Sin límite |
| Intervalo mínimo entre ejecuciones | 15 min | 5 min | 1 min | 1 min |
| Timeout máximo | 30 s | 2 min | 10 min | 1 h |
| Minutos de ejecución al mes | 100 | 500 | 3.000 | Sin límite |

## Minutos

- Cuentan el tiempo de cada intento que se ejecuta, reintentos incluidos. El
  mes es el mes natural en UTC.
- **Free**: al llegar a los minutos incluidos se pausan las ejecuciones de
  todos los servicios de Cron jobs de la organización hasta el mes siguiente
  o hasta subir de plan.
- **Starter y Pro**: nunca se pausan; el excedente se mide con su precio por
  minuto en **Uso**.

Un endpoint que responde en 300 ms gasta mucho menos que uno que tarda 25 s:
responder rápido también ahorra minutos.

## Al crear o editar un job

Crear un job por encima del límite, con un horario más frecuente que el
intervalo mínimo o con un timeout mayor que el máximo se rechaza con `402` y
`error.scope` `plan.limit_exceeded`:

```json
{
  "success": false,
  "status_code": 402,
  "error": {
    "code": 402,
    "message": "…",
    "scope": "plan.limit_exceeded",
    "meta": { "limit_key": "max_cron_jobs", "limit": 5, "used": 5 }
  },
  "trace_id": "…"
}
```

| `error.meta.limit_key` | Qué se pasó | Qué proponer |
| --- | --- | --- |
| `max_cron_jobs` | Número de jobs de la organización | Agrupar trabajos en un endpoint, borrar jobs que no se usan o subir de plan |
| `min_cron_interval_sec` | Horario más frecuente que el mínimo | Un horario menos frecuente, o lotes más grandes por ejecución |
| `max_cron_timeout_sec` | Timeout mayor que el máximo | Un endpoint más rápido (lotes, encolar) o subir de plan |

Un job creado sin timeout recibe el máximo del plan. Un timeout de `0` no es
válido.

## Agrupar jobs

Con pocos jobs en el plan, un endpoint puede despachar varias tareas que
comparten horario:

```ts
// POST /internal/cron/hourly  →  un solo job "0 * * * *"
await Promise.allSettled([cleanupSessions(), refreshCaches(), retryFailedEmails()]);
```

Si alguna falla, responde un status de error para que el job reintente, y
asegúrate de que las que sí terminaron son idempotentes.
