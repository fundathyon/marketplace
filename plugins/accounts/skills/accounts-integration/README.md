# Foundathon Accounts — skill portable

**Documentación completa autocontenida** para integrar Accounts desde cualquier proyecto con Cursor o Claude Code.

No necesitas clonar el repo de accounts: copia esta carpeta y listo.

---

## Contenido del bundle

| Archivo | Descripción |
|---------|-------------|
| `SKILL.md` | Entrada principal — índice y reglas |
| `quickstart.md` | Flujo mínimo en 5 minutos |
| `setup.md` | Docker, env vars, BASE_URL |
| `api-keys-and-auth.md` | Tipos de auth y matriz |
| `response-format.md` | JSON success/error |
| `auth-flows.md` | Árbol de decisión |
| `email-auth.md` | Signup, signin, activate, reset |
| `tokens.md` | Refresh, validate, revoke |
| `oauth.md` | Web redirect + native SDK |
| `magic-link.md` | Passwordless |
| `behaviors.md` | Config que cambia flujos |
| `users.md` | Usuarios, metadata, change-email |
| `roles-policies.md` | RBAC admin |
| `webhooks.md` | Eventos HTTP |
| `endpoints-reference.md` | Tabla completa endpoints |
| `error-scopes.md` | Errores por scope |
| `sdk-patterns.md` | Patrones frontend/backend |
| `openapi.json` | Contrato HTTP (Swagger 2.0) |

---

## Instalar en Cursor

```bash
# Global — disponible en todos tus proyectos
cp -r accounts-integration ~/.cursor/skills/

# Por proyecto
cp -r accounts-integration /tu-proyecto/.cursor/skills/
```

Cursor descubre el skill por `description` en el frontmatter de `SKILL.md`.

---

## Instalar en Claude Code

```bash
# Global
cp -r accounts-integration ~/.claude/skills/

# Por proyecto
cp -r accounts-integration /tu-proyecto/.claude/skills/
```

Claude Code también lee `CLAUDE.md` del proyecto si lo añades (opcional).

---

## Variables en tu proyecto consumidor

```env
ACCOUNTS_BASE_URL=https://api.tudominio.com/accounts
ACCOUNTS_PUBLISHABLE_KEY=pk_live_...
ACCOUNTS_SECRET_KEY=sk_live_...        # solo backend
```

---

## Actualizar desde repo accounts

Si mantienes el repo fuente:

```bash
make sync-openapi        # actualiza openapi.json en el bundle
make sync-agent-skills   # copia bundle → .cursor y .claude
```

Editar siempre en `.agents/accounts-integration/` en el repo accounts.

---

## Prompt de ejemplo

> Integra login con email, signup y refresh token usando Foundathon Accounts.
> BASE_URL=https://api.example.com/accounts, PK en env.
> Usa el skill accounts-integration.

El agente debe leer los `.md` de este folder antes de generar código.
