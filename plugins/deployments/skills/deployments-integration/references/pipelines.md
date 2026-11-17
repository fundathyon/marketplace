# CI Pipelines

Vuelve al índice: [SKILL.md](../SKILL.md).

Cada archivo `.foundathyon/pipelines/*.yml` del repositorio es un pipeline.
Un run reserva un Docker-in-Docker aislado con los recursos que pida el
pipeline, y cada job corre en un contenedor dentro de él.

## Activarlo

1. En el panel, enlaza el repositorio de GitHub a la organización (instalando
   la GitHub App de Foundathyon) y crea una **app** para él.
2. En la app, activa sus pipelines y los eventos que escucha.
3. Crea las variables y secretos que el YAML usa (organización, app o entorno
   de la app).
4. Empuja un tag que cumpla el patrón de `on.tags`.

Hoy **solo los tags** lanzan pipelines. `push` y `pull_request` son válidos en
el YAML y lanzarán runs cuando el panel los habilite.

## Claves del pipeline

| Clave | Qué es | Ejemplo |
| --- | --- | --- |
| `name` | Nombre del pipeline | `release` |
| `on` | Disparadores. Ver abajo | |
| `timeout` | Tiempo máximo del run | `30m` |
| `resources.cpu` | CPU del run: número o milésimas | `2`, `500m` |
| `resources.memory` | Memoria del run (`GB` se lee como GiB) | `4GB` |
| `concurrency` | Runs simultáneos de este pipeline (sin valor: sin límite propio) | `1` |
| `priority` | `low`, `normal` o `high`. Sin valor: la del evento (tag alta, push normal, PR baja) | `high` |
| `labels` | Etiquetas libres | `[release]` |
| `env` | Variables para todos los jobs | `NODE_ENV: production` |
| `permissions` | Permisos del token de GitHub de los jobs: `contents`, `pull_requests`, `issues`, `checks`, `statuses` con `read`, `write` o `none`. Por defecto, `contents: read` | `contents: read` |
| `imports` | Jobs y valores de otro repositorio: `repository`, `ref`, `path` | |
| `jobs` | Los jobs, en el orden del archivo | |

## Disparadores (`on`)

```yaml
on:
  tags: ["v*"]                 # disponible hoy
  push:                        # se acepta; aún no lanza runs
    branches: [main]
  pull_request:                # se acepta; aún no lanza runs
    branches: [main]
    types: [opened, synchronize, reopened]   # también ready_for_review
  manual:                      # el botón «Ejecutar pipeline»
    inputs:
      - name: environment
        type: choice           # string, choice o boolean
        options: [staging, production]
        default: staging
        required: true
```

`tags`, si se declara, no puede estar vacío. Sin patrones en `branches`,
cualquier rama.

## Claves de un job (`jobs.<nombre>`)

| Clave | Qué es |
| --- | --- |
| `image` | Imagen del contenedor del job |
| `commands` | Lista de comandos de shell, en orden; el primero que falla corta el job |
| `needs` | Jobs que tienen que terminar antes: `[test, lint]` |
| `env` | Variables del job |
| `environment` | Entorno de la app cuyas variables y secretos usa el job, con su política de ramas |
| `permissions` | Reemplazan las del pipeline para este job |
| `docker` | `true` le da un daemon de Docker propio en `DOCKER_HOST`. Solo para construir imágenes |
| `services` | Contenedores auxiliares en la red del run: `name`, `image`, `env` (una base de datos para tests) |
| `artifacts` | Rutas que el job conserva |
| `if` | Condición para ejecutar el job |
| `retry` | Reintentos del job si falla |

## Expresiones y variables

| Escribes | Obtienes |
| --- | --- |
| `${{ vars.NOMBRE }}` | Una variable del panel |
| `${{ secrets.NOMBRE }}` | Un secreto del panel; se oculta en los logs |
| `$FD_SHA` | El commit del run |
| `$FD_REF_NAME` | El tag o la rama (`v1.2.0`) |
| `$FD_REPOSITORY` | `owner/repo` en GitHub |

El prefijo `FD_` está reservado: no lo uses en tus variables ni secretos.

## Tests con una base de datos

```yaml
jobs:
  test:
    image: golang:1.25
    services:
      - name: postgres
        image: postgres:17
        env:
          POSTGRES_PASSWORD: test
    env:
      DATABASE_URL: postgres://postgres:test@postgres:5432/postgres?sslmode=disable
    commands:
      - go test ./...
```

## Seguir un run

En el panel, la organización → CI muestra los runs con sus logs en vivo, y
permite cancelarlos o relanzarlos. El panel también valida un pipeline antes
de que corra: úsalo cuando el YAML cambie.
