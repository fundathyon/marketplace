# Behaviors — configuración por app

Los **behaviors** cambian cómo responden los endpoints sin cambiar las rutas. Siempre verificar la config de la app antes de implementar auth.

## Qué es un behavior

Config JSON por app que activa/desactiva funcionalidades:

- Verificación de email en signup/signin
- Política de contraseñas
- Magic link
- Código de acceso por correo (email OTP)
- Usuarios de prueba (testers)
- OAuth providers
- Metadata schema en signup
- Notificaciones email
- Segundo factor (`mfa`)
- Límites de seguridad (`security_limits`)
- Seguridad de sesiones (`session_security`)

## Behavior principal: `email_auth`

Al crear app (`POST /v1/apps`) se crea email_auth en modo **simple**:

```json
{
  "verification": { "enabled": false }
}
```

### verification.enabled

| Valor | Signup | Signin |
|-------|--------|--------|
| `false` | Usuario activo al instante | Directo |
| `true` | Envía código por email | Requiere activate previo |

### Password policy (ejemplo)

```json
{
  "password": {
    "min_length": 8,
    "min_uppercase": 1,
    "min_lowercase": 1,
    "min_numbers": 1,
    "min_special": 1
  }
}
```

Errores: `emails.validation.weak_password`

---

## Activar verificación email (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/verification/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{}'
```

Desactivar:

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/verification/deactivate" \
  -H "X-API-Key: {secret_key}"
```

---

## Magic link (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/magic-link/activate" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "enabled": true }'
```

Ver [magic-link.md](magic-link.md).

---

## Código de acceso por correo (admin)

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/email-code/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{ "enabled": true, "code_size": 6, "code_type": "numeric", "ttl_seconds": 600, "max_verify_attempts": 5 }'
```

Configurable por app: largo (4–12) y alfabeto del código, vigencia (60–3600 s), intentos por código (1–20), cooldown de reenvío, envíos por ventana, `auto_signup`, un solo código activo, binding a IP/User-Agent y branding del correo. Ver [email-code.md](./email-code.md).

---

## Testers (admin)

Gate del módulo de usuarios de prueba (`email_auth.testers`, apagado por default):

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/testers/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{}'
```

```json
{ "testers": { "enabled": true } }
```

Apagado → `/api/v1/testers/*` responde `422 testers.disabled`; los testers ya creados siguen entrando. `{"enabled": false}` lo apaga. La contraseña derivada de los testers sigue la política `password` de este mismo behavior: si la cambias, llama `POST /api/v1/testers/regenerate`. Ver [testers.md](testers.md).

---

## Sesiones: rotación de refresh tokens e inactividad (admin)

Nodo `email_auth.sessions`, apagado por default (también en las apps nuevas):

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/sessions/activate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {secret_key}" \
  -d '{"refresh_rotation": true}'
```

```json
{ "sessions": { "refresh_rotation": true, "reuse_interval_seconds": 30, "idle_timeout_seconds": 0 } }
```

- `refresh_rotation`: cada refresh devuelve un refresh token nuevo; reutilizar uno ya usado revoca la sesión (`refresh_tokens.create.reuse_detected`).
- `reuse_interval_seconds` (0–300, default 30): gracia para dos refresh concurrentes con el mismo token; 0 es el modo estricto.
- `idle_timeout_seconds` (0 = sin límite, o 3600–31536000, y al menos el doble de la vida del access token): cierra la sesión que pasa ese tiempo sin refrescar, con o sin rotación.

Los campos que no mandas conservan su valor: mandar solo los números no enciende la rotación. Un body vacío, `{}`, la enciende. Aplica al siguiente refresh de cualquier sesión. **Enciende la rotación solo cuando todos tus clientes guarden el `refresh_token` de cada respuesta de `refresh-jwt`.** Ver [tokens.md](tokens.md).

---

## Metadata schema (admin)

Permite campos JSON dinámicos en signup:

```bash
curl -X POST "{BASE_URL}/api/v1/app-behaviors/email/metadata-schema/activate" \
  -H "X-API-Key: {secret_key}" \
  -d '{
    "schema": {
      "phone": { "type": "string", "required": true }
    }
  }'
```

Signup entonces requiere `metadata: { "phone": "+34..." }`.

---

## Embedded Auth (admin, Pro)

El behavior `embedded_auth` configura los componentes web de login: `allowed_origins`, `redirect_urls` del magic link, `strategies` y `branding`. Solo se lee y escribe con `GET`/`PUT /api/v1/app-behaviors/embedded-auth` (secret key); la fila se crea con el primer `PUT` y las rutas genéricas la rechazan (`422 app_behaviors.update.use_embedded_auth_endpoint`). Ver [embedded-auth.md](embedded-auth.md).

---

## Enlace de identidades (admin, Community y Pro)

El behavior `email_locale` (`{"default_locale": "es"}`) es el idioma por defecto de los correos transaccionales cuando ni la petición (`locale` del body o `Accept-Language`) ni el usuario traen uno. Solo con `GET`/`PUT /api/v1/app-behaviors/email-locale` (secret key); sin fila, `en`. Ver [email-locale.md](email-locale.md).

El behavior `identity_linking` (`{"mode": "link_with_proof" | "separate"}`) decide si identidades con el mismo correo se enlazan. Solo con `GET`/`PUT /api/v1/app-behaviors/identity-linking` (secret key); sin fila, `link_with_proof`. En `link_with_proof` un signup que choca con un usuario OAuth exige el código aunque `verification.enabled` sea `false`. Ver [identity-linking.md](identity-linking.md).

---

## Segundo factor (admin, Community y Pro)

El behavior `mfa` (`{"mode": "off" | "optional" | "required", "flows": [...]}`) decide cuándo un login pide el código TOTP. Solo con `GET`/`PUT /api/v1/app-behaviors/mfa` (secret key); sin fila, `optional` en `password`, `oauth`, `native`, `magic_link` y `email_code`: **los usuarios con TOTP activo reciben `mfa_required` en vez de tokens**. `required` obliga a todos (quien no tiene TOTP se enrola en el login). Errores `400 mfa.invalid_mode` / `mfa.invalid_flow`; las rutas genéricas lo rechazan (`422 app_behaviors.*.use_mfa_endpoint`). Testers exentos. Ver [mfa.md](mfa.md).

---

## Límites de seguridad (admin, Community y Pro)

El behavior `security_limits` ajusta por app los límites contra fuerza bruta (`rate_limit`, `lockout`, `api_keys`, `mfa`) dentro de rangos fijos; las variables de entorno son el default. Solo con `GET`/`PUT /api/v1/app-behaviors/security-limits` (secret key). `PUT` parcial: `null` vuelve al default, `{}` no cambia nada. Errores `400 security_limits.out_of_range` (`error.meta {field, min, max}`), `security_limits.invalid_field`, `security_limits.invalid_durations`; las rutas genéricas lo rechazan (`422 app_behaviors.*.use_security_limits_endpoint`). Ver [security-limits.md](security-limits.md).

El behavior `session_security` decide la entrega de tokens del login OAuth web (`query` | `code`), la rotación del refresh y la revocación de sesiones al cambiar la contraseña. Solo con `GET`/`PUT /api/v1/app-behaviors/session-security` (secret key), `PUT` parcial. Las apps existentes tienen la fila con su comportamiento de antes; una app sin fila usa `defaults_for_new_apps` (`code`, `true`, `true`). Ver [session-security.md](session-security.md).

---

## CRUD behaviors (admin)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/app-behaviors` | Listar |
| GET | `/api/v1/app-behaviors/:id` | Por ID |
| POST | `/api/v1/app-behaviors` | Crear |
| PUT | `/api/v1/app-behaviors/:id` | Actualizar |
| GET | `/api/v1/app-behaviors/available` | Tipos disponibles |
| GET | `/api/v1/app-behaviors/examples/:code` | Ejemplo de config |

Todas requieren **secret key**.

---

## Regla para agentes

Si el usuario no especifica la config:

1. Preguntar si verification está ON
2. O implementar ambos caminos (signup → check response → activate si aplica)
3. Manejar siempre `mfa_required` / `mfa_enrollment_required` en las respuestas de login (el default `optional` lo activa para usuarios con TOTP)
4. Documentar qué behavior asumiste

Ver [auth-flows.md](auth-flows.md).
