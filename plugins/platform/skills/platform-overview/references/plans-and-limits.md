# Planes, límites y errores

Vuelve al índice: [SKILL.md](../SKILL.md).

El plan es **de la organización**: todos sus proyectos y servicios comparten
el mismo plan y suman al mismo consumo. Cambiar de plan afecta a todos.

## Planes

| Plan | Qué es |
| --- | --- |
| Free | Para empezar sin tarjeta, con límites fijos |
| Starter | De pago, mensual o anual |
| Pro | De pago, mensual o anual |
| Enterprise | Por contrato |

Los precios y las cifras vigentes están en el panel, en **Plan y
facturación**; cambian con el tiempo. Un código **Early Access** da a la
organización los límites y funciones de un plan de pago sin costo mientras
sigue en Free.

## Qué cuenta en **Uso**

| Producto | Qué cuenta |
| --- | --- |
| Plataforma | Proyectos, servicios, miembros, solicitudes API del mes, espacio del Container Registry |
| Accounts | Usuarios registrados, usuarios activos del mes (MAU), servicios de Accounts, API keys, roles, webhooks, proveedores OAuth |
| Cron jobs | Minutos de ejecución del mes y número de jobs |
| Monitoring | Aún sin consumo: muestra los límites que tendrá el plan |

## Límites fijos y medidos

- **Fijos** (casi todos): al llegar, crear algo más se rechaza hasta subir de
  plan.
- **Medidos** en Starter y Pro: usuarios de Accounts y minutos de cron.
  Pasado lo incluido siguen funcionando y **Uso** muestra el excedente. En
  Free son fijos: se bloquean los registros nuevos y se pausan las
  ejecuciones de cron hasta el mes siguiente.

## Cómo llegan al código

| Respuesta | Producto | Qué significa | Qué hacer |
| --- | --- | --- | --- |
| `402` · `plan.limit_exceeded` | Plataforma, Cron jobs | Crear por encima de un límite del plan (jobs, intervalo mínimo, timeout máximo, proyectos…) | No reintentar. Mostrar qué límite y que se resuelve subiendo de plan |
| `403` · `quota.users_exceeded` | Accounts | La organización llegó a su techo de usuarios | Bloquear el alta con un mensaje propio; los logins nunca se bloquean |
| `403` · `quota.*_exceeded` | Accounts | Techo de API keys, roles, webhooks u OAuth | No reintentar |
| `403` · `quota.feature_not_in_plan` | Accounts | Función de un plan superior (Embedded Auth, bloqueo por país…) | Ocultar o desactivar la función |
| `403` · `quota.tenant_read_only` | Accounts | La organización está en solo lectura | Permitir lecturas y logins; deshabilitar escrituras |

Detalle de Accounts: `references/plans-and-quotas.md` de `accounts-integration`.

## Antes de lanzar

- Revisa **Uso** frente a lo que esperas consumir el primer mes.
- Si un límite fijo va a quedarse corto, sube de plan antes de llegar.
- Registra el `trace_id` de cualquier `402` o `403 quota.*` para soporte.
