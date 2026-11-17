# Endpoints de salud

Vuelve al índice: [SKILL.md](../SKILL.md).

## Qué expone cada uno

| Endpoint | Pregunta | Comprueba | Responde |
| --- | --- | --- | --- |
| `/health` | ¿Vive el proceso? | Nada externo | Siempre `200` mientras el proceso atienda |
| `/ready` | ¿Puede atender peticiones reales? | Dependencias **críticas**: base de datos, caché si es imprescindible | `200` si todas responden, `503` si alguna no |

No metas en `/ready` dependencias opcionales (un proveedor de analítica, un
servicio de correo con cola): su caída no impide atender y abriría
incidentes falsos.

## Respuesta

```json
{ "status": "ok" }
```

Mínima. Si quieres detalle por dependencia para tu equipo, ponlo detrás de un
token y en otro endpoint (`/internal/health/details`), no en el público.

## Go (net/http)

```go
mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"status":"ok"}`))
})

mux.HandleFunc("GET /ready", func(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), time.Second)
	defer cancel()
	w.Header().Set("Content-Type", "application/json")
	if err := db.PingContext(ctx); err != nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		w.Write([]byte(`{"status":"unavailable"}`))
		return
	}
	w.Write([]byte(`{"status":"ok"}`))
})
```

## Next.js (App Router)

```ts
// app/api/health/route.ts
export const dynamic = "force-dynamic";
export function GET() {
  return Response.json({ status: "ok" });
}
```

Para una web estática o un frontend, vigila la propia página principal (`/`)
o un `/api/health` así: el check confirma que el despliegue responde.

## Python (FastAPI)

```python
@app.get("/ready")
async def ready():
    try:
        await asyncio.wait_for(db.execute("select 1"), timeout=1)
    except Exception:
        return JSONResponse({"status": "unavailable"}, status_code=503)
    return {"status": "ok"}
```

## Errores comunes

| Error | Consecuencia |
| --- | --- |
| `/ready` sin timeout en la consulta | El check agota su timeout y se lee como caída aunque la base esté lenta, no caída |
| Consultas pesadas en cada check | Carga constante en la base de datos |
| El endpoint exige sesión de usuario | El check siempre falla con `401` |
| Responder `200` con un cuerpo que dice "down" | El check nunca detecta la caída |
| El balanceador responde por la app caída | Vigila la URL pública real, no la del balanceador |
