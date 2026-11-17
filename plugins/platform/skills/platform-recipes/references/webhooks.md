# Verificar un webhook de Foundathyon

Vuelve al índice: [SKILL.md](../SKILL.md).

Los webhooks de Foundathyon (los de Accounts y los que reparte la plataforma)
llegan como `POST` con el evento en JSON y firmados con el secret del
webhook. El catálogo de eventos de Accounts y su configuración están en
`references/webhooks.md` de `accounts-integration`.

## Cabeceras

| Cabecera | Qué es |
| --- | --- |
| `X-Webhook-Id` | Id del evento |
| `X-Webhook-Delivery-Id` | Id de la entrega; igual en todos sus reintentos. **Clave de idempotencia** |
| `Idempotency-Key` | El mismo valor que `X-Webhook-Delivery-Id` |
| `X-Webhook-Timestamp` | Segundos Unix del intento |
| `X-Webhook-Signature` | `v1=<hex>`: HMAC-SHA256 con el secret sobre `<id>.<timestamp>.<cuerpo crudo>`. Puede traer varias firmas separadas por comas; acepta si alguna coincide |

## Pasos

1. Lee el **cuerpo crudo**, antes de parsear JSON.
2. Rechaza si `X-Webhook-Timestamp` se aleja más de 5 minutos de tu reloj.
3. Calcula `HMAC-SHA256(secret, id + "." + timestamp + "." + body)` en hex y
   compáralo en tiempo constante con cada `v1=` de la cabecera.
4. Si ya procesaste ese `X-Webhook-Delivery-Id`, responde `2xx` sin repetir.
5. Responde `2xx` enseguida y haz el trabajo pesado en segundo plano.

```ts
import { createHmac, timingSafeEqual } from "node:crypto";

export function verifyFoundathyonWebhook(req, res, next) {
  const id = req.get("x-webhook-id") ?? "";
  const timestamp = req.get("x-webhook-timestamp") ?? "";
  const header = req.get("x-webhook-signature") ?? "";
  const body: Buffer = req.body; // express.raw()

  if (Math.abs(Date.now() / 1000 - Number(timestamp)) > 300) return res.sendStatus(400);

  const expected = createHmac("sha256", process.env.FOUNDATHYON_WEBHOOK_SECRET!)
    .update(`${id}.${timestamp}.`)
    .update(body)
    .digest();
  const valid = header.split(",").some((part) => {
    const [version, hex] = part.trim().split("=");
    if (version !== "v1" || !hex) return false;
    const got = Buffer.from(hex, "hex");
    return got.length === expected.length && timingSafeEqual(got, expected);
  });
  if (!valid) return res.sendStatus(401);
  next();
}
```

## No hagas

- Comparar la firma con `===`.
- Confiar en la cabecera obsoleta `X-Webhook-Secret` (secret en claro).
- Parsear el JSON antes de verificar: cambia los bytes y rompe la firma.
- Tardar en responder: los reintentos se acumulan.
