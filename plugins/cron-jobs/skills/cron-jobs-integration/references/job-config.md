# Configuración de un job

Vuelve al índice: [SKILL.md](../SKILL.md).

Los jobs se crean en el panel: proyecto → servicio de tipo **Crons** →
**Jobs**. Entrega al usuario cada campo con su valor. Entre paréntesis, el
nombre interno del campo, por si aparece en mensajes de error o en la salida
de una ejecución.

## Campos del job

| Campo | Qué es | Valores |
| --- | --- | --- |
| Nombre (`name`) y descripción (`description`) | Para reconocerlo | Texto. Usa un nombre en kebab-case que diga qué hace |
| Activo (`enabled`) | Si se ejecuta según su horario | Sí por defecto. Desactivar no lo borra ni borra su historial |
| Método (`http_config.method`) | | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| URL (`http_config.url`) | Lo que se llama | `http` o `https` público. Admite `{{secrets.NOMBRE}}` |
| Cabeceras (`http_config.headers`) | | Pares nombre/valor. Admiten `{{secrets.NOMBRE}}` |
| Cuerpo (`http_config.body`) | | Texto (por ejemplo JSON). Admite `{{secrets.NOMBRE}}`. Si es JSON, añade `Content-Type: application/json` |
| Status esperado (`http_config.expected_status`) | La única respuesta que cuenta como éxito | 200 por defecto. Debe coincidir exactamente |
| Seguir redirecciones (`http_config.follow_redirects`) | | Mejor apuntar directamente a la URL final |
| Horario (`schedule`) | Cuándo | Una frecuencia predefinida o una expresión cron de 5 campos: minuto hora día-del-mes mes día-de-la-semana |
| Zona horaria (`timezone`) | En qué zona se lee el horario | Nombre IANA. UTC por defecto |
| Timeout (`timeout`) | Segundos que espera la respuesta | Hasta el máximo del plan. Sin valor, recibe el máximo |
| Reintentos (`max_retries`) | Intentos extra tras un fallo | 0 a 10 |
| Espera entre reintentos (`retry_delay`) | Base del backoff, en segundos | Cada espera dobla la anterior, con algo de azar, hasta 1 hora |
| Ejecución perdida (`misfire_policy`) | Qué hacer si una ejecución no pudo lanzarse a su hora | `skip` (saltarla, por defecto) o `run_once` (ejecutarla una vez al volver) |

## Expresiones cron

| Expresión | Cuándo |
| --- | --- |
| `*/15 * * * *` | Cada 15 minutos (el mínimo de Free) |
| `0 * * * *` | Cada hora en punto |
| `0 3 * * *` | Todos los días a las 03:00 |
| `0 9 * * 1-5` | De lunes a viernes a las 09:00 |
| `0 0 1 * *` | El día 1 de cada mes a medianoche |

Elige horas valle para trabajos pesados y evita que varios jobs pesados
coincidan en el mismo minuto.

## Secretos

- Cada job tiene sus secretos: valores cifrados que se usan como
  `{{secrets.NOMBRE}}` en la URL, las cabeceras o el cuerpo.
- No se vuelven a mostrar después de guardarlos y se ocultan en la salida de
  las ejecuciones. Para cambiar uno, se sobrescribe.
- Convención: `CRON_JOBS_TOKEN` para el token que verifica el endpoint. Si el
  backend tiene varios endpoints de cron, un único token para todos basta; uno
  por job si quieres revocarlos por separado.

## Control manual

- **Ejecutar ahora**: lanza el job fuera de su horario. Úsalo para probar
  después de configurarlo.
- **Reenviar** una ejecución fallida definitiva: la vuelve a lanzar. Por eso
  el endpoint debe ser idempotente.

## Ejecuciones

Cada ejecución guarda estado, origen, duración, intento y la respuesta
recibida. Se ven en el servicio → **Ejecuciones**, con filtros por job y por
estado.

| Estado | Significa |
| --- | --- |
| `pending`, `queued` | Esperando a lanzarse |
| `running` | En curso |
| `success` | Llegó el status esperado |
| `failed` | Llegó otro status o hubo un error de red; se reintenta si quedan intentos |
| `timeout` | No respondió dentro del timeout |
| `interrupted` | Se cortó (por ejemplo, un reinicio de la plataforma) |

| Origen | Significa |
| --- | --- |
| `scheduled` | Su horario |
| `manual` | Ejecutar ahora |
| `misfire` | Ejecución perdida recuperada con `run_once` |
| `redrive` | Reenvío de una ejecución fallida |

Una ejecución que agota sus intentos, o que pasa 24 horas sin terminar, queda
como fallida definitiva.

## Diagnosticar una ejecución fallida

| Síntoma | Causa probable | Arreglo |
| --- | --- | --- |
| `401`/`403` en la respuesta | El secreto del job y la variable del backend no coinciden | Sobrescribe el secreto con el valor actual |
| `timeout` | El endpoint hace demasiado trabajo | Lotes más pequeños o encolar y responder enseguida |
| Status `202` o `204` marcado como fallo | El status esperado sigue en 200 | Pon el status real en el job |
| Error de conexión inmediato | URL privada, `localhost` o DNS que no resuelve públicamente | URL pública |
| Efectos duplicados | Reintentos o reenvíos sobre un endpoint no idempotente | Haz el trabajo idempotente |

## Auditoría

El servicio registra quién cambió qué: jobs, secretos, ejecuciones manuales y
reenvíos. Los valores de secretos y cabeceras nunca se registran.
