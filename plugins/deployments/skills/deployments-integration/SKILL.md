---
name: deployments-integration
description: >-
  Lleva el código de un repositorio a producción con Foundathyon: CI
  Pipelines (archivos YAML en .foundathyon/pipelines que corren cada job en
  su propio Docker), Container Registry privado de la organización (docker
  login con token fdr_, namespaces, tokens de lectura o escritura) y
  Deployments (releases inmutables por digest, en preparación). Usar cuando
  el usuario escribe o corrige un pipeline de Foundathyon, construye y sube
  una imagen al registry, usa variables o secretos de CI (vars, secrets),
  dispara un pipeline con un tag, o pregunta cómo desplegar su app o su base
  de datos en Foundathyon.
metadata:
  version: "0.1.0"
  status: "preview"
---

# Foundathyon Deployments, CI Pipelines y Container Registry

El camino del commit a producción, en tres piezas:

```text
tag en GitHub ──▶ CI Pipelines ──▶ Container Registry ──▶ Deployments
                  .foundathyon/     imagen por digest      release inmutable
                  pipelines/*.yml
```

## Estado: preview — lee esto primero

| Pieza | Estado | Qué puede hacer el agente |
| --- | --- | --- |
| CI Pipelines | Disponible. **Hoy solo disparan los tags**; `push` y `pull_request` se aceptan en el YAML pero el panel los marca como no disponibles todavía | Escribir y corregir pipelines: [references/pipelines.md](references/pipelines.md) |
| Container Registry | Disponible | Login, build y push desde un pipeline; tokens y namespaces: [references/registry.md](references/registry.md) |
| Deployments | **En preparación**: no hay releases, estrategias ni bases de datos que configurar todavía | Dejar la app lista (imagen reproducible, configuración por variables de entorno): [references/deployments.md](references/deployments.md) |

No inventes campos del YAML, rutas de API ni comandos de despliegue que no
estén en las referencias. Si el usuario pide algo que no está, dilo.

## Cómo se organiza

- Los pipelines **viven en el repositorio** del usuario, en
  `.foundathyon/pipelines/*.yml`, y cambian con el código.
- El repositorio de GitHub se enlaza a la organización como una **app** en el
  panel; ahí se activan sus pipelines.
- **Variables y secretos** se guardan en el panel, a nivel de organización,
  de app o de entorno de la app, y el YAML los lee como `${{ vars.X }}` y
  `${{ secrets.X }}`. Editar los de la organización es cosa de `owner` y
  `admin`.
- El **registry es de la organización**: todos sus proyectos comparten el
  mismo. Su espacio cuenta en **Uso**.

## Reglas que nunca debes violar

| Regla | Detalle |
| --- | --- |
| Secretos fuera del YAML | Todo token va en `${{ secrets.X }}`, guardado en el panel. Nunca en el YAML, en el Dockerfile ni en un `build-arg` (queda en el historial de la imagen): usa `--secret` de BuildKit |
| Prefijo `FD_` reservado | Las variables `FD_*` las pone la plataforma (`FD_SHA`, `FD_REF_NAME`, `FD_REPOSITORY`). No declares variables ni secretos con ese prefijo |
| Login sin eco | `echo "$REGISTRY_TOKEN" \| docker login "$REGISTRY" -u "$REGISTRY_USER" --password-stdin`, nunca `-p` |
| Token mínimo | Un token del registry con permiso de escritura solo sobre los repositorios que el pipeline sube; de lectura para quien solo baja |
| Imagen trazable | Etiqueta con el tag del release (`$FD_REF_NAME`) y añade las labels OCI `source`, `revision` y `version`. Lo que se despliega se fija por digest, no por tag |
| Docker solo si hace falta | `docker: true` solo en los jobs que construyen imágenes |
| Host del registry | Cópialo del panel (Registry de la organización). No lo adivines |

## Happy path: construir y subir una imagen con cada tag

```yaml
# .foundathyon/pipelines/release.yml
name: release

on:
  tags: ["v*.*.*"]

timeout: 30m
resources:
  cpu: 2
  memory: 4GB

jobs:
  test:
    image: node:22
    commands:
      - npm ci
      - npm test

  image:
    needs: [test]
    image: docker:28-cli
    docker: true
    env:
      REGISTRY: ${{ vars.REGISTRY_HOST }}
      IMAGE: ${{ vars.REGISTRY_HOST }}/my-namespace/my-api
      REGISTRY_USER: ${{ vars.REGISTRY_USER }}
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
    commands:
      - echo "$REGISTRY_TOKEN" | docker login "$REGISTRY" -u "$REGISTRY_USER" --password-stdin
      - >-
        docker buildx build --push --platform linux/amd64
        --label org.opencontainers.image.source="https://github.com/$FD_REPOSITORY"
        --label org.opencontainers.image.revision="$FD_SHA"
        --label org.opencontainers.image.version="$FD_REF_NAME"
        -t "$IMAGE:$FD_REF_NAME" .
```

En el panel: `vars.REGISTRY_HOST` (el host del registry de la organización),
`vars.REGISTRY_USER` (el slug de la organización) y `secrets.REGISTRY_TOKEN`
(un token `fdr_` con escritura sobre `my-namespace/*`). Se publica con
`git tag v1.2.0 && git push origin v1.2.0`.

## Checklist de entrega

- [ ] Pipeline en `.foundathyon/pipelines/`, disparado por tag
- [ ] Jobs con `needs` en el orden correcto y `docker: true` solo donde se construye
- [ ] Ningún secreto en el YAML ni en `build-arg`; nada con prefijo `FD_`
- [ ] Variables y secretos que el usuario debe crear en el panel, listados
- [ ] Imagen etiquetada con `$FD_REF_NAME` y labels OCI
- [ ] Si pidió desplegar: explicado que Deployments está en preparación y la app lista para él
