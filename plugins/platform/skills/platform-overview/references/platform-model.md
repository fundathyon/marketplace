# Modelo de la plataforma

Vuelve al índice: [SKILL.md](../SKILL.md).

## Tres niveles

| Nivel | Qué es | Contiene | Se gestiona en |
| --- | --- | --- | --- |
| Organización | La empresa o el equipo | Proyectos, miembros, plan y uso, registry, variables y secretos de CI | Miembros, Plan y facturación, Uso, ajustes |
| Proyecto | Un producto o un entorno (*Producción*, *Staging*, el nombre de la app) | Servicios | Alta de servicios y ajustes del proyecto |
| Servicio | Una instancia de un producto, independiente y con su propia configuración | Lo del producto. En Accounts: apps, API keys, usuarios, roles, behaviors, plantillas, OAuth, webhooks. En Cron jobs: jobs, secretos, ejecuciones | Su propia sección en el panel, o su API |

Un proyecto puede tener varios servicios del mismo producto (por ejemplo, dos
Accounts para dos apps distintas). Cada uno se configura por separado.

## Primer servicio, paso a paso

1. Crear la cuenta de la plataforma en el panel y verificar el correo. Es la
   cuenta del equipo, no un usuario de la app.
2. Onboarding: nombre de la organización e invitaciones opcionales.
3. Crear un proyecto.
4. En el proyecto, añadir un servicio y elegir el producto. Para Accounts, el
   origen **Crear nuevo** aprovisiona la app con un rol por defecto, el
   registro por correo con la verificación apagada y un par de keys
   **Initial API Keys** con acceso total.
5. Copiar las keys del servicio a las variables de entorno del entorno que
   corresponde.

Si no aparece la opción de añadir servicios, no se está dentro de un
proyecto. Si no se pueden crear más proyectos o servicios, es el límite del
plan: **Uso** de la organización.

## Entornos

Usa **un proyecto por entorno**. Cada proyecto tiene sus propios servicios y,
por tanto, sus propias keys, usuarios y datos.

| Entorno | Proyecto | Variables |
| --- | --- | --- |
| Producción | *Producción* | Las keys de los servicios de ese proyecto, en el gestor de secretos de producción |
| Staging | *Staging* | Las de su proyecto, nunca las de producción |
| Local | El de staging, o uno *Desarrollo* | `.env` local, fuera del repositorio |

Para pruebas automáticas contra Accounts usa los testers
(`@getfoundathyon.mock`), no usuarios reales: lo explica `accounts-integration`.

## Miembros frente a usuarios

| | Miembros de la organización | Usuarios de la app |
| --- | --- | --- |
| Quiénes son | El equipo que desarrolla y administra | Las personas que usan el producto |
| Dónde entran | Al panel de Foundathyon | A la aplicación del cliente |
| Dónde se gestionan | Organización → **Miembros** | Servicio Accounts → **Users** |
| Roles | `owner` (todo, incluida facturación), `admin` (proyectos y servicios, sin facturación), Developer (el de por defecto al invitar), Editor, Viewer | Los que defina la app en Accounts |

Algunas acciones de la organización, como editar las variables de CI, solo
las pueden hacer `owner` y `admin`. Gestionar el plan es cosa del `owner`.

## Panel y API

Casi todo lo que se configura en un servicio se puede hacer en el panel o
por API. El panel es la vía visual; la API, la de automatizar. Cuando el
usuario pida "configurarlo por código", usa la API del producto que documenta
su skill; si su skill no la documenta, dirige al panel.
