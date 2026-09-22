# Guía para agentes — marketplace

Este repositorio es la fuente pública de las skills de integración de
Foundathyon. Cada skill se instala en Claude Code, Cursor, Codex y GitHub
Copilot — por el marketplace de cada agente o copiando la carpeta — así que
tiene que funcionar en todos, y un manifiesto roto rompe la instalación para
todos.

## Comandos canónicos

Desde la raíz del repositorio:

```sh
python3 scripts/validate.py                 # catálogo, manifiestos y skills
python3 -m unittest discover tests          # el validador contra sí mismo
claude plugin validate . --strict           # cómo lo lee Claude Code
uvx --from 'git+https://github.com/agentskills/agentskills#subdirectory=skills-ref' \
  skills-ref validate plugins/<plugin>/skills/<skill>   # el validador del estándar
```

Los cuatro corren en CI en cada pull request. Para probar una skill de verdad
antes de mezclar, instálala desde este checkout en un repositorio de prueba:

```
/plugin marketplace add /ruta/a/marketplace
/plugin install <plugin>@foundathyon
```

## La fuente de verdad no está aquí

Cada skill se genera en el repositorio de su servicio y se copia aquí. Para
`accounts` es `fundathyon/accounts` → `.agents/accounts-integration/`,
regenerada con `make sync-integration-docs`. **Edita la skill allí**, no aquí:
un cambio hecho solo en este repositorio desaparece en la siguiente copia.

Lo único que vive solo aquí son los manifiestos, el README y este archivo.

## Añadir un servicio

Un plugin es la unidad que instala un agente; uno por servicio. Una skill es
lo que el agente lee; una por plugin salvo que de verdad haga falta más.

1. **Crear las carpetas**, con la skill en el layout del estándar:

   ```text
   plugins/<servicio>/plugin.json
   plugins/<servicio>/.claude-plugin/plugin.json
   plugins/<servicio>/skills/<servicio>-integration/
     SKILL.md            índice y reglas — lo primero que lee el agente
     references/         la documentación por flujo, un archivo por tema
     assets/             contratos y datos: openapi.json, esquemas
   ```

2. **Escribir el frontmatter** — solo campos del estándar, para que lo lean
   todos los agentes:

   ```yaml
   ---
   name: <servicio>-integration   # = su carpeta: a-z, 0-9, guiones simples, ≤ 64
   description: <qué hace, y luego "Usar para …" — hasta 1024 caracteres>
   metadata:
     version: "0.1.0"             # entre comillas, o YAML lo lee como número
   ---
   ```

   La `description` es todo lo que el agente ve antes de elegir la skill: di
   qué hace y en qué situaciones aplica. El nombre lleva el servicio delante
   para que nunca choque con la skill de otro.

3. **Escribir los manifiestos.** `plugin.json` sigue Agent Plugins 1.0 — copia
   el `$schema` tal cual de `plugins/accounts/plugin.json`. Los dos manifiestos
   llevan el mismo `name`, `version` y `description`.

4. **Listar el plugin** en `.claude-plugin/marketplace.json`, con `source` en
   string relativo (`"./plugins/<servicio>"`), `category` y `version`. Codex
   ignora cualquier otro tipo de `source`.

5. **Validar**, y añadir la fila a la tabla del README.

## Skills que funcionan en todos los agentes

- `SKILL.md` por debajo de 500 líneas: los pasos y las reglas. El detalle va en
  `references/`, enlazado con ruta relativa. El agente carga `SKILL.md` entero
  al activar la skill y las referencias solo cuando las necesita.
- Todo enlace relativo, en cualquier `.md` de la skill, tiene que resolver
  dentro de la skill: cada agente la instala en un sitio distinto.
- Scripts solo con biblioteca estándar (Python 3 o sh POSIX), con `--json`
  cuando un agente vaya a leer su salida, y código de salida distinto de cero al
  fallar.
- Nada de frontmatter específico de un agente (`allowed-tools`, `model`…) salvo
  que la skill lo necesite de verdad: los demás lo ignoran o lo leen distinto.
- **Sin secretos, URLs internas, marcas viejas ni datos personales.** El
  repositorio es público y la skill se copia en muchas máquinas. El validador
  detiene credenciales con forma real; los dominios de ejemplo son
  `example.com`.

## Cambiar una skill

- Sube la versión — versionado semántico — en `SKILL.md`, en los dos
  `plugin.json` y en la entrada del `marketplace.json`. El validador falla si
  no concuerdan.
- El nombre de una skill es su identidad en todas las máquinas donde está
  instalada; renombrarla es una skill nueva más la retirada de la vieja.
- Los cambios de una skill y los de sus manifiestos van en el mismo pull
  request.

## Commits

Conventional Commits en inglés, firmados, sin coautoría de agentes:
`feat(accounts): …`, `fix(marketplace): …`, `docs(readme): …`.
