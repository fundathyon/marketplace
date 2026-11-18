# Container Registry

Vuelve al índice: [SKILL.md](../SKILL.md).

Un registry de Docker privado por organización, con `docker login`, `push` y
`pull` de siempre.

## Acceso

| Dato | Valor |
| --- | --- |
| Host | El del registry de la organización, en el panel. Cópialo, no lo adivines |
| Usuario | El slug de la organización |
| Contraseña | Un token `fdr_…` creado en el panel |

```sh
echo "$REGISTRY_TOKEN" | docker login "$REGISTRY_HOST" -u "$REGISTRY_USER" --password-stdin
docker push "$REGISTRY_HOST/<namespace>/<repositorio>:v1.2.0"
```

## Namespaces y repositorios

- Las imágenes se organizan en **namespaces**: `<namespace>/<repositorio>`.
  Un namespace por producto o equipo (`billing/api`, `billing/worker`).
- Los namespaces y los repositorios se gestionan en el panel, donde también
  se ven los tags, se bloquea un tag para que no se borre y se borran
  imágenes.

## Tokens

| Permiso | Para |
| --- | --- |
| Escritura | El pipeline que construye y sube. Limítalo a los repositorios que sube |
| Lectura | Quien solo baja imágenes: un entorno que despliega, otro equipo |

- Cada token tiene descripción, permiso, repositorios y caducidad en días.
  Pon caducidad y rótalo antes de que venza.
- El valor se muestra una sola vez al crearlo: guárdalo directamente como
  secreto de CI (`REGISTRY_TOKEN`), nunca en el repositorio.
- Un token filtrado se borra en el panel y se crea otro.

## Buenas prácticas de imagen

- Construye con `docker buildx build --push` y una plataforma explícita
  (`--platform linux/amd64`).
- Secretos de build con `--secret id=…,env=…`, nunca `--build-arg`.
- Tag inmutable por release (`$FD_REF_NAME`); evita depender de `latest`.
- Labels OCI `source`, `revision` y `version` para saber de dónde sale cada
  imagen.

## Espacio

El espacio del registry cuenta en **Uso** de la organización, con la cuota
de su plan. Borra imágenes viejas que nadie despliega; bloquea los tags que
no se pueden perder.
