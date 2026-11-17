# Deployments (en preparación)

Vuelve al índice: [SKILL.md](../SKILL.md).

Deployments pondrá en marcha apps y bases de datos con releases inmutables.
**Todavía no está disponible**: no hay releases, estrategias, bases de datos
ni URLs que configurar. No generes comandos, APIs ni archivos de despliegue
de Foundathyon.

## Lo que traerá

| Capacidad | Qué dará |
| --- | --- |
| Disparadores | Despliegues con un tag o un push, con un patrón como `v*` |
| Releases inmutables | Cada release fijado por el digest de la imagen |
| Estrategias | Rolling, blue/green, canary y progresiva |
| Configuración | Variables de entorno y archivos de configuración montados en el contenedor |
| Recursos | Límites de CPU y memoria, y réplicas |
| Operación | Apagar y encender una app sin perder su release |
| Ubicación | Placement por región |
| Acceso | Una URL pública por app |
| Bases de datos | Postgres, MySQL, MariaDB, MongoDB y Redis |

Las imágenes saldrán del Container Registry de la organización, donde las
dejan los CI Pipelines.

## Dejar la app lista desde hoy

Lo que hagas ahora sirve tal cual cuando Deployments abra:

- [ ] **Una imagen por release**, construida por un pipeline con cada tag y
      subida al registry ([pipelines.md](pipelines.md), [registry.md](registry.md))
- [ ] **Configuración solo por variables de entorno**: nada de hosts, keys ni
      URLs en la imagen. Las keys de Accounts y el token de Cron jobs entran
      por entorno
- [ ] **Escucha en el puerto de `PORT`** y en `0.0.0.0`
- [ ] **`/health` y `/ready`** para que una estrategia sin caída sepa cuándo
      la versión nueva puede recibir tráfico (lo explica la skill
      `monitoring-integration`)
- [ ] **Apagado ordenado** con `SIGTERM`: deja de aceptar peticiones,
      termina las que tiene y cierra conexiones
- [ ] **Sin estado en el contenedor**: archivos subidos y sesiones fuera de
      su disco
- [ ] **Migraciones compatibles hacia atrás**: con rolling o blue/green
      conviven dos versiones; añade columnas antes de usarlas y bórralas
      después
- [ ] **Logs a stdout/stderr**, una línea JSON por evento
