# Foundathyon Accounts — skill portable

**Documentación completa y autocontenida** para integrar Accounts desde
cualquier proyecto con Claude Code, Cursor, Codex o GitHub Copilot.

No necesitas clonar el repo de accounts: el skill se publica en el
marketplace público de Foundathyon,
[fundathyon/marketplace](https://github.com/fundathyon/marketplace), como el
plugin `accounts`.

---

## Contenido del bundle

El agente carga `SKILL.md` (reglas, happy path e índice) y después solo la
guía del flujo que le pides.

<!-- skill-index:start — generado desde SKILL.md con make skill-index; no editar a mano -->

| Archivo | Cuándo leerlo |
|---------|---------------|
| [`SKILL.md`](SKILL.md) | Siempre primero: reglas, happy path e índice |
| [`references/quickstart.md`](references/quickstart.md) | Primer contacto, flujo mínimo app → signup → signin |
| [`references/setup.md`](references/setup.md) | Docker, variables de entorno, `{BASE_URL}` |
| [`references/api-keys-and-auth.md`](references/api-keys-and-auth.md) | Tipos de auth, matriz por endpoint, scopes de las secret keys (catálogo, `403 api_keys.scope_denied`, sin escalada) |
| [`references/response-format.md`](references/response-format.md) | Formato JSON success/error; qué errores llegan con message genérico (5xx, seguridad) y por qué hay que guardar el `trace_id` |
| [`references/auth-flows.md`](references/auth-flows.md) | Árbol de decisión de flujos |
| [`references/email-auth.md`](references/email-auth.md) | Signup, signin, activate, reset, login unificado |
| [`references/tokens.md`](references/tokens.md) | Refresh (y rotación), logout desde el cliente, sesiones activas, validate, revoke, jwt/info |
| [`references/oauth.md`](references/oauth.md) | OAuth web redirect y native SDK |
| [`references/magic-link.md`](references/magic-link.md) | Autenticación passwordless por enlace |
| [`references/email-code.md`](references/email-code.md) | Autenticación passwordless por código (email OTP): entrar y crear cuenta con un código |
| [`references/embedded-auth.md`](references/embedded-auth.md) | Componentes web (Pro): `<script>` + `<accounts-sign-in>`…, `Accounts.getToken()`, behavior `embedded_auth` (`allowed_origins`), cabeceras `X-Accounts-*`, verificar el JWT en el backend |
| [`references/behaviors.md`](references/behaviors.md) | Config por app que cambia los flujos |
| [`references/users.md`](references/users.md) | CRUD usuario, búsqueda (Criteria: `q`, filtros, `sort`), `GET /users/{id}`, metadata, change-email |
| [`references/testers.md`](references/testers.md) | Usuarios de prueba: crear en lote, credenciales, vigencia, token directo, borrado |
| [`references/roles-policies.md`](references/roles-policies.md) | RBAC: roles, policies (alta, edición, borrado), asignación a roles, claim `role`, `POST /api/v1/authorize`, JWKS y verificador Go (`authz`) |
| [`references/mfa.md`](references/mfa.md) | Segundo factor: behavior `mfa`, respuesta `mfa_required` / `mfa_enrollment_required` en los logins, `/api/v1/mfa/*`, TOTP del usuario y códigos de respaldo |
| [`references/security-limits.md`](references/security-limits.md) | Límites de seguridad por app (`security_limits`, Community y Pro): rate limit por IP y cuenta, bloqueo progresivo, secret keys inválidas y MFA dentro de rangos fijos sobre los defaults de la instancia; `PUT` parcial, `null` = default |
| [`references/session-security.md`](references/session-security.md) | Seguridad de sesiones (`session_security`, Community y Pro): entrega de tokens del login OAuth web por `code` (`POST /api/v1/oauth/exchange`) o por query, rotación del refresh, revocación al cambiar la contraseña, denylist de access tokens; apps existentes sin cambios, apps nuevas en modo seguro |
| [`references/mcp-connect.md`](references/mcp-connect.md) | Login OAuth 2.1 para servidores MCP: registrar el recurso, configurar el servidor MCP, construir la página de conexión, conexiones |
| [`references/email-locale.md`](references/email-locale.md) | Idioma de los correos transaccionales (`email_locale`, Community y Pro): campo `locale` del body, `Accept-Language`, idioma guardado del usuario, `default_locale` de la app y `en`; reintentos sin correos duplicados |
| [`references/identity-linking.md`](references/identity-linking.md) | Enlace de identidades por correo (`identity_linking`, Community y Pro): regla de correo verificado (Microsoft `xms_edov`, GitHub primario verificado), modos `link_with_proof`/`separate`, signup sin tokens hasta el código |
| [`references/login-security.md`](references/login-security.md) | Historial de logins (`/api/v1/login-events`, resumen por país, `ip_changed`) y bloqueo regional por país (Pro, `geo_access`): config, 403 `geo_access.*`, webhook `accounts.auth.login_failed`, `TRUSTED_PROXIES` |
| [`references/plans-and-quotas.md`](references/plans-and-quotas.md) | Planes y cuotas por organización (`tenant_ref`, operador): techo `max_accounts_users` en toda alta (overage en planes de pago), techos de API keys/roles/webhooks/OAuth (`403 quota.*_exceeded`), funciones Pro (`403 quota.feature_not_in_plan`), MAU, `accounts.entitlement.limited`, uso por tenant, retención por plan, modo de solo lectura (`403 quota.tenant_read_only`); los logins nunca se bloquean; `ENTITLEMENTS_*` |
| [`references/metrics.md`](references/metrics.md) | Métricas del dashboard con secret key: `GET /api/v1/metrics/{overview,users,logins,webhooks,usage}`, `from`/`to`/`interval`/`tz`, activos nuevos/reactivados/retenidos, fallos por motivo, top IPs, entregas de webhooks y uso del plan; campos null o vacíos no viajan; `metrics.query.*` |
| [`references/audit-log.md`](references/audit-log.md) | Audit log de las acciones administrativas (secret key / admin key): `GET /api/v1/audit-logs` con filtros de core y cursor, forma del evento `fd_audit`, `changes` redactado, `via=core`, `AUDIT_*` |
| [`references/webhooks.md`](references/webhooks.md) | Eventos HTTP hacia tu backend: verificar la firma, los 43 eventos que se emiten (usuarios, sesiones, identidades, roles, API keys, MFA, testers…), garantías del outbox, registro de entregas |
| [`references/endpoints-reference.md`](references/endpoints-reference.md) | Tabla completa de endpoints |
| [`references/error-scopes.md`](references/error-scopes.md) | Errores por `scope` con la acción sugerida, por flujo |
| [`references/error-catalog.md`](references/error-catalog.md) | Catálogo completo de `error.scope`, generado desde el código: status y si el message es descriptivo o genérico |
| [`references/sdk-patterns.md`](references/sdk-patterns.md) | Patrones frontend/backend |
| [`assets/openapi.json`](assets/openapi.json) | Contrato HTTP machine-readable (Swagger 2.0) |

<!-- skill-index:end -->

---

## Instalar

### Claude Code

Dentro de Claude Code:

```text
/plugin marketplace add fundathyon/marketplace
/plugin install accounts@foundathyon
/plugin install platform@foundathyon   # opcional: el mapa de toda la plataforma
```

### Cursor, Codex y GitHub Copilot

Los tres leen `~/.agents/skills/`:

```bash
curl -fsSL https://raw.githubusercontent.com/fundathyon/marketplace/main/scripts/install.sh \
  | sh -s -- accounts
```

Para un solo repositorio, añade `--dest .agents/skills`: el skill se commitea
con el código y lo tiene todo el equipo.

---

## Variables en tu proyecto consumidor

```env
ACCOUNTS_BASE_URL=https://foundathyon.com/services/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...
ACCOUNTS_SECRET_KEY=sk_live_...        # solo backend
```

---

## Mantener el skill (repo accounts)

La fuente de verdad es `.agents/accounts-integration/` en este repo. Edita
siempre aquí: `.claude/skills/` y `.cursor/skills/` son copias, y el
marketplace copia esta carpeta.

```bash
make sync-integration-docs   # swagger, openapi, catálogo de errores, índice y copias
make skill-index             # solo el índice de este README, desde la tabla de SKILL.md
make sync-agent-skills       # solo las copias de .claude/ y .cursor/
```

Al añadir una guía, ponla en la tabla de `SKILL.md`, regenera y menciónala en
el `llms.txt` de la raíz. Los tests de `internal/common/agentskill` fallan si
una guía no está indexada, si el índice o las copias no están al día, o si el
`description` pasa de 1024 caracteres (el límite que aplica el marketplace).

Para publicar, sube `metadata.version` en `SKILL.md` y copia la carpeta a
`plugins/accounts/skills/accounts-integration/` del marketplace, con la misma
versión en sus manifiestos.

---

## Prompt de ejemplo

> Integra login con email, signup y refresh token usando Foundathyon Accounts.
> BASE_URL en ACCOUNTS_BASE_URL, publishable key en env.
> Usa el skill accounts-integration.
