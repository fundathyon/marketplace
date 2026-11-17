# Qué vigilar

Vuelve al índice: [SKILL.md](../SKILL.md).

Entrega al usuario una tabla de checks como esta, para crearlos cuando
Monitoring esté disponible. Ordénala por lo que más duele si cae.

| Qué | URL | Status esperado | Timeout | Por qué |
| --- | --- | --- | --- | --- |
| API | `https://api.example.com/ready` | `200` | 5 s | Si cae, cae todo el producto |
| Web | `https://example.com/` | `200` | 10 s | Lo primero que ve un usuario |
| Receptor de webhooks | `https://api.example.com/health` | `200` | 5 s | Si cae, se acumulan reintentos de los webhooks |
| Endpoints de Cron jobs | No los vigiles con checks: el historial de ejecuciones del job ya dice si fallan | — | — | Evita alertas duplicadas |

## Frecuencia

- Producción: la más corta que permita el plan para la API y la web.
- Staging: una frecuencia más baja basta.
- El número de checks (monitores) tendrá un límite por plan, visible en
  **Uso**: prioriza la tabla de arriba.

## Hasta que esté disponible

Si el usuario necesita vigilancia ya, puede usar un servicio externo con los
mismos endpoints. Los endpoints no cambian al pasar a Foundathyon Monitoring.
