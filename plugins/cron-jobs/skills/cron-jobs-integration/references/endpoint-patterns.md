# El endpoint que llama el job

Vuelve al índice: [SKILL.md](../SKILL.md).

Todos los patrones cumplen lo mismo: token en `Authorization` comparado en
tiempo constante, trabajo idempotente y por lotes, y respuesta antes del
timeout. `CRON_JOBS_TOKEN` vive solo en el backend; el job lo manda como
`Authorization: Bearer {{secrets.CRON_JOBS_TOKEN}}`.

Pon estos endpoints bajo un prefijo propio (`/internal/cron/…`) para
excluirlos de la sesión de usuario, del CSRF y del rate limit de usuarios,
pero **no** de la autenticación por token.

## Next.js (App Router)

```ts
// app/api/cron/daily-digest/route.ts
import { timingSafeEqual } from "node:crypto";

export const dynamic = "force-dynamic";

function authorized(request: Request): boolean {
  const expected = Buffer.from(`Bearer ${process.env.CRON_JOBS_TOKEN ?? ""}`);
  const received = Buffer.from(request.headers.get("authorization") ?? "");
  return received.length === expected.length && timingSafeEqual(received, expected);
}

export async function POST(request: Request) {
  if (!process.env.CRON_JOBS_TOKEN || !authorized(request)) {
    return new Response(null, { status: 401 });
  }
  const sent = await sendPendingDigests({ limit: 200 }); // marca cada envío
  return Response.json({ sent });
}
```

## Go (net/http)

```go
func cronAuth(next http.Handler) http.Handler {
	expected := []byte("Bearer " + os.Getenv("CRON_JOBS_TOKEN"))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		got := []byte(r.Header.Get("Authorization"))
		if len(expected) == len("Bearer ") || subtle.ConstantTimeCompare(got, expected) != 1 {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r)
	})
}

mux.Handle("POST /internal/cron/cleanup-sessions", cronAuth(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 20*time.Second) // por debajo del timeout del job
	defer cancel()
	n, err := sessions.DeleteExpired(ctx, 1000)
	if err != nil {
		http.Error(w, "cleanup failed", http.StatusInternalServerError) // el job reintenta
		return
	}
	json.NewEncoder(w).Encode(map[string]int{"deleted": n})
})))
```

## Python (FastAPI)

```python
import hmac, os
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

def check(authorization: str | None) -> None:
    expected = f"Bearer {os.environ['CRON_JOBS_TOKEN']}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401)

@app.post("/internal/cron/sync-invoices")
async def sync_invoices(authorization: str | None = Header(default=None)):
    check(authorization)
    synced = await sync_pending_invoices(limit=500)
    return {"synced": synced}
```

## Idempotencia

La entrega es al menos una vez. Diseña el trabajo para que repetirlo no
duplique efectos:

| Trabajo | Cómo hacerlo idempotente |
| --- | --- |
| Borrar caducados | Ya lo es: "borra lo caducado" no borra dos veces |
| Enviar un resumen diario | Guarda `(usuario, fecha)` enviado con una restricción única antes de enviar; si ya existe, sáltalo |
| Cobrar o facturar | Usa la clave de idempotencia del proveedor de pagos, derivada del periodo (`invoice-2026-11-user-42`) |
| Sincronizar con un tercero | Procesa por "pendiente desde" con un cursor guardado, y avanza el cursor al confirmar |

## Trabajo largo

Si el trabajo no cabe en el timeout:

1. **Por lotes**: cada ejecución procesa un lote acotado (por ejemplo 500
   registros) y el horario es lo bastante frecuente para vaciar la cola.
2. **Encolar**: el endpoint mete el trabajo en una cola propia y responde
   `202`. Pon `202` como status esperado en el job. El fallo del trabajo
   encolado ya no lo ve el job: vigílalo en tu cola.

## Probar

- En local, el job no llega a `localhost`. Prueba el endpoint con `curl` y el
  token, y el job contra staging o un túnel público.
- Después de crear el job, **Ejecutar ahora** y mira la respuesta en
  **Ejecuciones**.

```sh
curl -i -X POST https://api.example.com/internal/cron/cleanup-sessions \
  -H "Authorization: Bearer $CRON_JOBS_TOKEN"
```
