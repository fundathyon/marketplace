# marketplace

Skills de integración de Foundathyon para agentes de código. Un repositorio, una
copia de cada skill, instalable como **plugin en Claude Code** y como carpeta en
**Cursor**, **Codex**, **GitHub Copilot** y cualquier otro agente que lea el
estándar abierto [Agent Skills](https://agentskills.io).

Una skill le da al asistente las rutas, headers y formato de respuesta reales de
un servicio de Foundathyon, para que el código de integración que escriba no sea
inventado.

## Skills disponibles

| Skill | Plugin | Qué hace | Versión |
| --- | --- | --- | --- |
| [`accounts-integration`](plugins/accounts/skills/accounts-integration/SKILL.md) | `accounts` | Integra Foundathyon Accounts: signup, signin, refresh token, OAuth, magic link, webhooks, roles y behaviors | 0.1.0 |

## Instalar

### Claude Code — como plugin

Un solo comando, dentro de Claude Code (no en la terminal):

```
/plugin install accounts --marketplace fundathyon/marketplace
```

Requiere Claude Code v2.1.275 o posterior. En versiones anteriores, en dos pasos:

```
/plugin marketplace add fundathyon/marketplace
/plugin install accounts@foundathyon
```

Al instalar eliges el alcance: **user** (todos tus proyectos), **project**
(queda en el `.claude/settings.json` del repo, para todo el equipo) o **local**
(solo tú, solo este repo).

Para que un equipo lo tenga sin pedirle nada a nadie, declara el marketplace en
el `.claude/settings.json` del repo del cliente:

```json
{
  "extraKnownMarketplaces": {
    "foundathyon": {
      "source": { "source": "github", "repo": "fundathyon/marketplace" }
    }
  },
  "enabledPlugins": ["accounts@foundathyon"]
}
```

> [!IMPORTANT]
> Claude Code trae el auto-update **desactivado** por defecto en marketplaces de
> terceros como este. Actívalo en `/plugin` → **Marketplaces** → **Enable
> auto-update**, o actualiza a mano con `/plugin update accounts`. Una skill
> vieja genera código contra rutas que ya no existen.

### Cursor, Codex, Copilot y demás — copiando la carpeta

Estos agentes no instalan plugins de Claude Code, pero sí leen el formato Agent
Skills. `~/.agents/skills/` es la ruta que leen Cursor, Codex y Copilot a la vez,
así que una sola copia cubre los tres:

```sh
git clone https://github.com/fundathyon/marketplace
mkdir -p ~/.agents/skills
cp -r marketplace/plugins/accounts/skills/accounts-integration ~/.agents/skills/
```

Rutas por agente, si prefieres ser explícito:

| Agente | En un repositorio | Para tu usuario |
| --- | --- | --- |
| Cursor, Codex, Copilot | `.agents/skills/<skill>` | `~/.agents/skills/<skill>` |
| Claude Code | `.claude/skills/<skill>` | `~/.claude/skills/<skill>` |
| Cursor (ruta propia) | `.cursor/skills/<skill>` | `~/.cursor/skills/<skill>` |

Cursor además lee `.claude/skills/` y `.codex/skills/` por compatibilidad, así
que no hace falta duplicar la carpeta por agente.

Instalada dentro de un repositorio, la skill se commitea con el código: la
tienen tus compañeros y también los agentes en la nube.

## Usar

Pídele la integración y nombra la skill:

```
Integra login con email, signup y refresh token usando Foundathyon Accounts.
BASE_URL en ACCOUNTS_BASE_URL, publishable key en env.
Usa la skill accounts-integration.
```

Nombrar el flujo ayuda: *magic link* lleva al agente a `magic-link.md`,
*webhooks* a `webhooks.md`. El agente carga solo los archivos que ese flujo
necesita — así funciona la divulgación progresiva del estándar.

Define las credenciales en tu proyecto, con la secret key **solo** en el backend:

```sh
ACCOUNTS_BASE_URL=https://foundathyon.com/services/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...
ACCOUNTS_SECRET_KEY=sk_live_...        # solo backend
```

## Estructura

```text
.claude-plugin/
  marketplace.json                    catálogo: qué plugins existen y dónde
plugins/
  accounts/                           un plugin = un servicio
    plugin.json                       manifiesto Agent Plugins 1.0
    .claude-plugin/plugin.json        el mismo manifiesto, donde lo lee Claude Code
    skills/
      accounts-integration/           una skill = una carpeta con SKILL.md
        SKILL.md                      índice y reglas; lo que el agente lee primero
        references/                   la documentación por flujo, un archivo por tema
        assets/openapi.json           el contrato HTTP, machine-readable
```

Tres niveles, y conviene no confundirlos:

- **El marketplace** es el catálogo. Solo `marketplace.json`: no contiene código,
  apunta a los plugins con un `source` relativo.
- **El plugin** es la unidad que instala un agente. Uno por servicio. Puede
  llevar skills, comandos, hooks y servidores MCP.
- **La skill** es lo que el agente lee. Una carpeta con `SKILL.md` en la raíz,
  el detalle en `references/` y los contratos en `assets/`, según el
  [estándar Agent Skills](https://agentskills.io/specification). El agente carga
  `SKILL.md` al activarla y las referencias solo cuando el flujo las pide.

Los dos `plugin.json` llevan el mismo `name`, `version` y `description`, y la
entrada del `marketplace.json` repite la `version`. Si no concuerdan, la
validación falla.

## Añadir un servicio

Hoy solo está `accounts`. Cada servicio nuevo de Foundathyon entra como un
plugin más, sin tocar los existentes. Para `payments`, por ejemplo:

**1. Crear las carpetas.** El `name` de la skill debe ser igual al nombre de su
carpeta — lo exige el estándar.

```text
plugins/payments/plugin.json
plugins/payments/.claude-plugin/plugin.json
plugins/payments/skills/payments-integration/SKILL.md
plugins/payments/skills/payments-integration/references/   documentación por flujo
plugins/payments/skills/payments-integration/assets/       openapi.json y otros contratos
```

**2. Escribir el frontmatter.** Solo campos del estándar, para que lo lean todos
los agentes:

```yaml
---
name: payments-integration
description: >-
  Documentación completa y autocontenida de Foundathyon Payments. Usar para
  integrar cobros, suscripciones, reembolsos y webhooks de pago.
metadata:
  version: "0.1.0"
---
```

La `description` es lo único que el agente ve antes de decidir si abre la skill:
di qué hace y en qué situaciones aplica. Máximo 1024 caracteres.

**3. Listar el plugin** en `.claude-plugin/marketplace.json`, con `source`
relativo en string, `category` y `version`:

```json
{
  "name": "payments",
  "source": "./plugins/payments",
  "description": "Integra Foundathyon Payments: cobros, suscripciones, reembolsos y webhooks.",
  "version": "0.1.0",
  "category": "integration",
  "keywords": ["payments", "suscripciones", "webhooks", "foundathyon"]
}
```

Codex ignora cualquier otro tipo de `source`, así que siempre relativo.

**4. Validar y documentar.** Añade la fila a la tabla de arriba. CI corre lo
mismo en cada pull request; el detalle está en [AGENTS.md](AGENTS.md).

```sh
python3 scripts/validate.py          # catálogo, manifiestos y skills
claude plugin validate . --strict    # como lo lee Claude Code
```

## Cuando un servicio tenga MCP

Un plugin no se limita a skills: puede declarar un servidor **MCP**, y así es
como los plugins de integración del marketplace oficial (GitHub, Stripe,
Supabase, Sentry) conectan su servicio sin que el usuario configure nada.

Cuando Accounts tenga servidor MCP, entra en el **mismo** `plugins/accounts/` —
no en un repositorio nuevo. La skill enseña a integrar la API; el MCP deja que
el agente la llame. Se complementan, y el cliente sigue instalando un plugin.

## Versionado

Versionado semántico. Al cambiar una skill hay que subir la versión en el
`SKILL.md`, en los dos `plugin.json` y en la entrada del `marketplace.json`: la
validación falla si no concuerdan.

El nombre de una skill es su identidad en todas las máquinas donde está
instalada. Renombrarla es publicar una nueva y retirar la vieja.

## Reglas para skills que funcionan en todos los agentes

- `SKILL.md` por debajo de 500 líneas: los pasos y las reglas. El detalle va en
  `references/`, enlazado con ruta relativa; los contratos y datos, en `assets/`.
- Nombra los archivos del bundle relativos a la carpeta de la skill: cada agente
  la instala en un sitio distinto.
- Nada de frontmatter específico de un agente (`allowed-tools`, `model`…) salvo
  que la skill lo necesite de verdad: los demás lo ignoran o lo leen distinto.
- **Sin secretos, URLs internas, marcas viejas ni datos personales.** Este
  repositorio es público y la skill se copia en muchas máquinas. El validador
  detiene credenciales con forma real; los dominios de ejemplo son `example.com`.

## De dónde vienen las skills

Cada skill se genera en el repositorio de su servicio y se copia aquí — el
servicio es la fuente de verdad. Para Accounts es `.agents/accounts-integration/`,
regenerada desde el contrato OpenAPI con `make sync-integration-docs`. Edita la
skill allí, no aquí.

La documentación para humanos del mismo contenido está en
[docs.foundathyon.com](https://docs.foundathyon.com/es/plataforma/ai-skills).
