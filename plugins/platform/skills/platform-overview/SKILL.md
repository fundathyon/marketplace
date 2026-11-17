---
name: platform-overview
description: >-
  Mapa de la plataforma Foundathyon como conjunto: qué productos hay (Accounts,
  Cron jobs, Monitoring, Deployments con CI Pipelines y Container Registry),
  cuál usar para cada necesidad, cómo se organiza (organización, proyecto,
  servicio), planes y límites (402 plan.limit_exceeded, 403 quota.*), API keys
  y entornos, y qué plugin del marketplace instalar para cada producto. Usar
  cuando el usuario empieza con Foundathyon, pregunta qué producto le sirve,
  combina varios productos, organiza entornos (producción, staging), choca
  con un límite del plan o pide algo de un producto cuya skill no está
  instalada.
metadata:
  version: "0.1.0"
  status: "stable"
---

# Foundathyon — la plataforma como conjunto

Foundathyon da los módulos que todo producto acaba construyendo igual:
autenticación, jobs programados, health checks, CI, registry de imágenes y
despliegues. Se aprovisionan desde el panel y se integran por su API.

Esta skill es el mapa. **La integración de cada producto vive en su propia
skill**: cuando el usuario pide algo de un producto, usa la skill de ese
producto; si no está instalada, dile qué plugin instalar (tabla de abajo) en
vez de inventar rutas.

## Productos

| Producto | Para qué | Plugin | Skill | Estado |
| --- | --- | --- | --- | --- |
| Accounts | Login y usuarios de tu app: email, códigos, magic link, OAuth, MFA, roles, tokens, webhooks | `accounts` | `accounts-integration` | estable |
| Cron jobs | Llamadas HTTP programadas a tu API, con reintentos, secretos e historial | `cron-jobs` | `cron-jobs-integration` | preview: disponible, se configura en el panel |
| Monitoring | Health checks HTTP con alertas de caída y recuperación | `monitoring` | `monitoring-integration` | preview: aún no disponible |
| Deployments, CI Pipelines y Container Registry | Del commit a producción: pipelines YAML, imágenes privadas, releases inmutables | `deployments` | `deployments-integration` | preview: Pipelines (por tag) y Registry disponibles; Deployments en preparación |
| La plataforma | Este mapa y las recetas que combinan productos | `platform` | `platform-overview`, `platform-recipes` | estable |

**Estado `preview`**: el producto no está completo o su API pública todavía
cambia. Su skill dice qué está confirmado y qué no; no completes lo que falta
con suposiciones. Hoy **solo Accounts tiene una API pública con API keys**;
los demás productos se configuran en el panel.

Instalar un plugin:

```text
/plugin install <plugin>@foundathyon                          # Claude Code
curl -fsSL https://raw.githubusercontent.com/fundathyon/marketplace/main/scripts/install.sh | sh -s -- <plugin>
                                                              # Cursor, Codex, Copilot
```

## Qué producto usar

| El usuario necesita… | Usa |
| --- | --- |
| Registro, login, sesiones, recuperar contraseña, OAuth, 2FA, roles de sus usuarios | Accounts |
| Que algo ocurra a una hora o cada cierto tiempo (limpiezas, resúmenes, facturación, sincronizaciones) | Cron jobs: Foundathyon llama a un endpoint de su API |
| Saber cuándo su API o su web se cae y cuándo vuelve | Monitoring |
| Construir, guardar imágenes y desplegar su app o su base de datos | Deployments (con CI Pipelines y Container Registry) |
| Reaccionar en su backend a lo que pasa en Accounts (alta de usuario, login, cambio de rol) | Webhooks de Accounts, en `accounts-integration` |
| Varias de las anteriores juntas | `platform-recipes` |

Cron jobs **no ejecuta código del usuario**: llama por HTTP a una URL pública
suya. Si el usuario quiere "un worker", la respuesta es un endpoint protegido
en su API más un job que lo llame. Lo explica `platform-recipes`.

## Cómo se organiza

```text
Organización           la empresa o el equipo: miembros, plan y uso
└── Proyecto           un producto o un entorno (Producción, Staging…)
    └── Servicio       una instancia de un producto, p. ej. Accounts
```

- **El servicio es lo que se integra por API.** Cada uno tiene su propia
  configuración y sus propias keys.
- **Un proyecto por entorno** (Producción, Staging): servicios y keys
  separados, sin usuarios ni datos compartidos.
- El Container Registry y las variables de CI son **de la organización**, no
  de un proyecto.
- **Miembros** (el equipo, entran al panel de Foundathyon, roles `owner`,
  `admin`, Developer, Editor, Viewer) **no son usuarios de la app** (los
  gestiona Accounts, con sus propios roles). Nunca los mezcles.

Detalle: [references/platform-model.md](references/platform-model.md).

## Reglas que nunca debes violar

| Regla | Detalle |
| --- | --- |
| Secret keys solo en el servidor | `sk_live_…` y cualquier token de escritura (registry, CI) nunca van a código de navegador ni de apps móviles, ni a un repositorio |
| Keys por entorno | Cada entorno lee las suyas de variables de entorno; nada de keys en el código |
| Envelope común | Las APIs responden `{ success, status_code, data?, meta?, error?: { code, message, scope, meta? }, trace_id? }`. Decide por `error.scope`, nunca por `message`, y guarda el `trace_id` |
| Límites del plan | Son de la organización. Un `402` con `error.scope` `plan.limit_exceeded` (crear por encima de un límite) o un `403 quota.*` en Accounts no se reintenta: muestra el motivo y que se resuelve subiendo de plan |
| El panel manda | Si una cifra de límites o precios de una skill no coincide con la del panel (**Plan y facturación**, **Uso**), manda la del panel |
| No inventar | Si una ruta, campo o comportamiento no está en la skill del producto, dilo y remite a la documentación; no lo supongas |

Planes, límites y errores: [references/plans-and-limits.md](references/plans-and-limits.md).

## Documentación para agentes

Para lo que no esté en una skill, la documentación pública está pensada para
leerse desde un agente:

| URL | Contenido |
| --- | --- |
| `https://docs.foundathyon.com/es/<producto>/llms-full.txt` | Todo un producto en un archivo (`en` para inglés) |
| `https://docs.foundathyon.com/es/<producto>/llms.txt` | El índice de sus páginas |
| `https://docs.foundathyon.com/es/<producto>/<página>.md` | Una página en Markdown |

`<producto>` es `accounts`, `cron-jobs`, `monitoring`, `deployments`,
`pipelines`, `registry` o `get-started`. Pasa solo el producto que se está
integrando.

## Variables de entorno

Una convención para todos los productos: el nombre del producto como
prefijo, y nada de keys en el código.

```env
# Accounts
ACCOUNTS_BASE_URL=https://foundathyon.com/services/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...      # cliente
ACCOUNTS_SECRET_KEY=sk_live_...           # solo backend

# Endpoints que llama Cron jobs: el token que verifica tu API
CRON_JOBS_TOKEN=...                       # solo backend; el mismo valor va en el secreto del job
```

## Checklist al empezar un proyecto

- [ ] Organización y un proyecto por entorno creados en el panel
- [ ] Un servicio por producto en cada proyecto
- [ ] Keys de cada entorno en sus variables de entorno, secret keys solo en el servidor
- [ ] La skill de cada producto que se integra, instalada
- [ ] Errores manejados por `error.scope`, con el `trace_id` en los logs
- [ ] Límites del plan revisados en **Uso** antes de lanzar
