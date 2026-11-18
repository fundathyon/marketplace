---
name: monitoring-integration
description: >-
  Prepara una app para Foundathyon Monitoring, health checks HTTP programados
  con alertas cuando un endpoint cae y cuando vuelve. Usar cuando el usuario
  quiere saber si su API o su web está caída, añade un endpoint /health o
  /ready, decide qué debe comprobar un health check, configura la frecuencia,
  el status esperado o el timeout de un check, o pregunta por alertas,
  incidentes o disponibilidad (uptime) en Foundathyon.
metadata:
  version: "0.1.0"
  status: "preview"
---

# Foundathyon Monitoring

Monitoring comprueba endpoints HTTP con la frecuencia que elijas y avisa
cuando uno cae y cuando se recupera. Guarda el status y el tiempo de
respuesta de cada comprobación, la línea de tiempo de cada incidente y la
disponibilidad de cada endpoint.

## Estado: preview — lee esto primero

- **Monitoring todavía no está disponible** en la plataforma. En **Uso** de
  la organización aparece con los límites que tendrá el plan, sin consumo.
- No hay API pública ni configuración que se pueda crear hoy. No generes
  código que llame a una API de Monitoring ni inventes sus rutas, campos o
  webhooks de alertas.
- Lo que sí puede hacer el agente desde ya, y es lo que cubre esta skill:
  **dejar la app lista** con endpoints de salud bien diseñados, y entregar al
  usuario la configuración de cada check para cuando el producto abra.

## Cómo funciona un check

Cada health check vigila un endpoint. Defines la **frecuencia**, el **status
esperado** y el **timeout**; un check que no recibe ese status a tiempo cuenta
como fallo. Un fallo abre un incidente y una alerta; la recuperación lo cierra
con otra alerta.

## Qué hace el agente con esta skill

1. **Añade los endpoints de salud** a la app: [references/health-endpoints.md](references/health-endpoints.md).
2. **Propone qué vigilar** y con qué configuración: [references/check-plan.md](references/check-plan.md).

## Reglas que nunca debes violar

| Regla | Detalle |
| --- | --- |
| Público y barato | El endpoint que vigila Monitoring es público (o protegido con un token en cabecera) y responde en milisegundos: no carga la base de datos ni llama a terceros lentos en cada comprobación |
| Status, no texto | El check decide por el status HTTP: `200` si está bien, `503` si no. Nunca `200` con `{"status":"down"}` |
| Sin datos internos | La respuesta pública no revela versiones de dependencias, hosts, cadenas de conexión ni trazas de error |
| Liveness frente a readiness | `/health` dice si el proceso vive; `/ready` si puede atender (dependencias críticas). Vigila `/ready` para alertar de caídas reales |
| Timeouts propios | Cada dependencia que comprueba `/ready` tiene su timeout, más corto que el del check |
| Fuera del rate limit | El endpoint de salud no cuenta para el rate limit de usuarios ni exige sesión |
| No inventar | Si el usuario pide integrar alertas, webhooks o una API de Monitoring, explícale que aún no está disponible |

## Happy path

```ts
// Express
app.get("/health", (_req, res) => res.status(200).json({ status: "ok" }));

app.get("/ready", async (_req, res) => {
  const checks = await Promise.allSettled([
    withTimeout(db.query("select 1"), 1000),
    withTimeout(cache.ping(), 500),
  ]);
  const ok = checks.every((c) => c.status === "fulfilled");
  res.status(ok ? 200 : 503).json({ status: ok ? "ok" : "unavailable" });
});
```

Check propuesto:

| Campo | Valor |
| --- | --- |
| URL | `https://api.example.com/ready` |
| Frecuencia | La más corta que permita el plan para producción |
| Status esperado | `200` |
| Timeout | 5 s |

## Checklist de entrega

- [ ] `/health` y `/ready` añadidos, rápidos y sin datos internos
- [ ] Dependencias críticas en `/ready`, cada una con timeout
- [ ] Excluidos de sesión, CSRF y rate limit de usuarios
- [ ] Lista de checks propuestos entregada al usuario
- [ ] El usuario sabe que Monitoring aún no está disponible para activarlos
