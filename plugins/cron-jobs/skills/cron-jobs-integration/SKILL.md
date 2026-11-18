---
name: cron-jobs-integration
description: >-
  Integra Foundathyon Cron jobs, llamadas HTTP programadas a la API del
  usuario con reintentos, secretos e historial. Usar cuando el usuario quiere
  que algo ocurra a una hora o cada cierto tiempo (limpiezas, resúmenes por
  correo, facturación, sincronizaciones), necesita un worker o tarea en
  background, escribe el endpoint que llamará un cron job, lo protege con un
  token, configura el horario, la zona horaria, los reintentos o el timeout de
  un job, interpreta una ejecución fallida o choca con 402
  plan.limit_exceeded al crear un job.
metadata:
  version: "0.1.0"
  status: "preview"
---

# Foundathyon Cron jobs

Cron jobs **llama por HTTP a una URL pública de la API del usuario** con la
frecuencia que elija, reintenta las llamadas que fallan y guarda cada
ejecución. No ejecuta código del usuario: el trabajo lo hace su endpoint.

## Estado: preview — lee esto primero

- **Los jobs se crean y se gestionan en el panel** de Foundathyon (proyecto →
  servicio de tipo Crons → **Jobs**). Hoy **no hay una API pública con API
  key** para crear jobs desde el código del usuario. No generes clientes HTTP
  ni scripts que creen jobs: escribe el endpoint y di qué configurar en el
  panel.
- Lo que sí está confirmado, y es lo que esta skill cubre: cómo se comporta
  un job (horario, reintentos, timeout, secretos, ejecuciones) y los límites
  del plan.

## Qué hace el agente con esta skill

1. **Escribe el endpoint** que llamará el job, en el backend del usuario:
   protegido, idempotente y rápido. Patrones por framework en
   [references/endpoint-patterns.md](references/endpoint-patterns.md).
2. **Le da al usuario la configuración del job**, campo por campo, para
   copiarla en el panel: [references/job-config.md](references/job-config.md).
3. **Revisa los límites del plan** antes de proponer un horario o un timeout:
   [references/limits-and-errors.md](references/limits-and-errors.md).

## Reglas que nunca debes violar

| Regla | Detalle |
| --- | --- |
| URL pública | El job solo llama a `http`/`https` públicos. `localhost`, redes privadas y endpoints de metadatos de la nube están bloqueados. Para probar en local, usa un túnel o el entorno de staging |
| Endpoint protegido | El endpoint exige un token en una cabecera (`Authorization: Bearer …`), comparado en tiempo constante. En el job, la cabecera usa el secreto: `Bearer {{secrets.CRON_JOBS_TOKEN}}`. Nunca el token en claro en la URL ni en el job |
| Idempotente | La entrega es **al menos una vez**: hay reintentos (hasta 10), reenvíos manuales de ejecuciones fallidas y la opción de ejecutar una vez al volver de una ejecución perdida. Ejecutar dos veces el mismo trabajo no debe duplicar efectos (correos, cobros) |
| Rápido | Responde antes del timeout del job, que tiene un máximo por plan (30 s en Free). Si el trabajo es largo, encólalo o procésalo por lotes y responde enseguida |
| Status exacto | La ejecución es correcta solo si la respuesta trae **exactamente** el status esperado del job (200 si no se cambia). Si el endpoint responde `202` o `204`, ese número va en el job |
| Sin solapes | Un job no arranca mientras su ejecución anterior siga en curso. No hace falta un lock para eso; sí para el mismo trabajo lanzado desde otro sitio |
| Zona horaria | El horario se lee en la zona horaria del job (UTC por defecto). Escríbela siempre de forma explícita, con nombre IANA (`Europe/Madrid`, `America/Mexico_City`) |
| Errores honestos | Un fallo real responde un status distinto del esperado para que el job lo reintente; un "no había nada que hacer" responde el esperado |

## Happy path

Endpoint (Express; otros frameworks en las referencias):

```ts
import { timingSafeEqual } from "node:crypto";

function authorized(header: string | undefined): boolean {
  const expected = Buffer.from(`Bearer ${process.env.CRON_JOBS_TOKEN}`);
  const received = Buffer.from(header ?? "");
  return received.length === expected.length && timingSafeEqual(received, expected);
}

app.post("/internal/cron/cleanup-sessions", async (req, res) => {
  if (!authorized(req.get("authorization"))) return res.sendStatus(401);
  const deleted = await deleteExpiredSessions({ olderThanHours: 24, batch: 1000 }); // idempotente
  res.status(200).json({ deleted });
});
```

Job en el panel:

| Campo | Valor |
| --- | --- |
| Nombre | `cleanup-sessions` |
| Método y URL | `POST https://api.example.com/internal/cron/cleanup-sessions` |
| Cabeceras | `Authorization: Bearer {{secrets.CRON_JOBS_TOKEN}}` |
| Secreto | `CRON_JOBS_TOKEN` = el mismo valor que la variable del backend |
| Horario | `0 3 * * *` (todos los días a las 03:00) |
| Zona horaria | `Europe/Madrid` |
| Status esperado | `200` |
| Timeout | 25 s, por debajo del máximo del plan |
| Reintentos | 3 |
| Ejecución perdida | Saltarla |

## Anti-patrones

- Generar código que llame a una "API de crons" con una API key: hoy no existe
- Poner el token en la query string o en claro en las cabeceras del job
- Usar `localhost` o una IP privada como URL del job
- Un endpoint que hace todo el trabajo de golpe y supera el timeout
- Un endpoint que manda correos o cobra sin comprobar si ya lo hizo
- Responder `200` cuando el trabajo falló (el job no lo reintentará)
- Un horario más frecuente que el intervalo mínimo del plan
- Omitir la zona horaria y descubrir que "a las 9" era a las 9 UTC

## Checklist de entrega

- [ ] Endpoint con token en cabecera, comparado en tiempo constante, y `CRON_JOBS_TOKEN` solo en el backend
- [ ] Trabajo idempotente y por lotes, que termina antes del timeout
- [ ] Status de éxito del endpoint = status esperado del job
- [ ] Configuración del job entregada al usuario, con zona horaria explícita
- [ ] Horario y timeout dentro de los límites de su plan
- [ ] El usuario sabe dónde ver las ejecuciones: servicio Crons → **Ejecuciones**
