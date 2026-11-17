# Error scopes — referencia completa

Implementar manejo por **`error.scope`**, no solo HTTP status.

Formato: ver [response-format.md](response-format.md)

---

## Apps

| Scope | HTTP | Acción |
|-------|------|--------|
| `apps.create.limit_reached` | 403 | Límite edition; no reintentar |
| `apps.create.invalid_data` | 400 | Validar body |
| `apps.create.internal_error` | 500 | Reintentar / soporte |
| `apps.list.unauthorized` | 401 | Revisar Admin API Key |
| `apps.list.invalid_pagination` | 400 | Corregir page/size |
| `apps.tenant_ref.invalid` | 400 | Operador: `tenant_ref` debe ser 1–64 caracteres `[A-Za-z0-9._:-]` |
| `apps.not_found` | 404 | Operador: `PUT /v1/apps/{id}/tenant` sobre una app inexistente o dada de baja |

---

## Signup

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.signup.email_already_exists` | 409 | → signin o reset password |
| `emails.validation.weak_password` | 422 | Mostrar reglas password (también en reset-confirm, reset/set-password, activación y set-password de admin) |
| `password.breached` | 400 | La contraseña aparece en una filtración (app con `password.policy.check_breached`): pedir otra. Mismo scope en signup, reset, cambio de contraseña y set-password de admin |
| `dto.validate.SignUpDTO` | 422 | Email con formato inválido o campo que falta: el `message` dice cuál |
| `emails.signup.app_not_found` | 404 | Revisar API key |
| `auth.apikey.invalid` | 401 | Revisar publishable_key / entorno |
| `emails.reserved_domain` | 422 | `@getfoundathyon.mock` es de los testers (también en pending-registrations y login social) |

---

## Resend código (signup)

| Scope | HTTP | Acción |
|-------|------|--------|
| (ninguno) | 201 | Respuesta genérica **exista o no la cuenta**, esté activa o ya haya pedido 5 códigos: «If an account is pending activation…». No usar para decidir signup/signin |
| `auth.rate_limited` | 429 | Tope por cuenta o por IP: esperar `error.meta.retry_after_seconds` / `Retry-After` |

> Desde 0.14.0 desaparecen `emails.resend.user_not_found` (404), `emails.resend.already_active` (409) y `emails.resend.rate_limited` (429): ya no se puede saber por esta ruta si un correo tiene cuenta.

---

## Signin

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.signin.invalid_credentials` | 401 | «Email o contraseña incorrectos». Sale igual si el correo no tiene cuenta: no distinguir |
| `emails.signin.error_email_not_verified` | 401 | Contraseña correcta, cuenta sin activar → activate / resend-code |
| `auth.rate_limited` | 429 | Cuenta bloqueada por contraseñas fallidas (1, 5, 15 min) o IP sobre su límite: esperar `error.meta.retry_after_seconds` / `Retry-After`. Sale igual exista o no la cuenta |
| `testers.expired` | 403 | Usuario de prueba caducado: revivirlo (ver Testers) |

> Desde 0.14.0 desaparecen `emails.signin.error_email_not_found` (404) y `emails.signin.error_invalid_password` (401). Quien mapeaba el 404 a «no existe la cuenta, regístrate» tiene que mostrar el mensaje genérico.

---

## Códigos de verificación (activación, reset, cambio de correo, registro)

Cada código admite **5 intentos**, contando el correcto. Un código equivocado
responde el error de siempre del flujo con `error.meta.remaining_attempts`; el
último intento equivocado lo bloquea con un scope propio y desde ahí ni el
código correcto sirve: hay que pedir otro. Pedir uno nuevo invalida los
anteriores, y cada usuario puede pedir hasta 5 por tipo cada 15 minutos (429).

## Activate

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.activate.error_invalid_code` | 400 | Reintentar; `error.meta.remaining_attempts` dice cuántos quedan |
| `emails.activate.error_too_many_attempts` | 400 | Código bloqueado: resend-code |
| `emails.activate.error_code_expired` | 400 | resend-code |
| `emails.activate.error_code_not_found` | 404 | resend-code |

## Activate v2 (Pro)

| Scope | HTTP | Acción |
|-------|------|--------|
| `emails.activate_v2.error_code_not_valid` | 400 | Reintentar; `error.meta.remaining_attempts` |
| `emails.activate_v2.error_too_many_attempts` | 400 | El backend crea un registro nuevo |
| `emails.activate_v2.error_pending_registration_not_found` | 404 | No hay registro con ese correo en la app |
| `emails.activate_v2.error_code_not_found` | 404 | El código ya se usó |

---

## Reset password

| Scope | HTTP | Acción |
|-------|------|--------|
| (ninguno) | 200 | `POST /reset` responde siempre el mismo 200 genérico, exista o no la cuenta o haya pedido ya 5 códigos (entonces no sale ninguno) |
| `auth.rate_limited` | 429 | Tope por cuenta o por IP antes de buscar la cuenta: esperar `Retry-After` |
| `emails.confirm_password.error_code_not_valid` | 401 | Reintentar; `error.meta.remaining_attempts` |
| `emails.confirm_password.error_too_many_attempts` | 401 | Código bloqueado: pedir otro reset |
| `emails.confirm_password.error_code_not_found` | 404 | Código reemplazado o ya usado: pedir otro reset |
| `emails.validation.weak_password` / `password.breached` | 422 / 400 | La contraseña nueva no vale: pedir otra; el código o el token **no** se gastan |
| `emails.set_password_from_reset.error_token_already_used` | 401 | Token de reset ya usado (un solo uso): empezar de nuevo |

`reset-confirm` y `reset/validate-code` comparten los intentos del código, y en
`validate-code` también cuenta la validación correcta. Un código vencido (10
minutos por defecto) responde `401 emails.confirm_password.error_code_not_valid`.

`reset/set-password` responde 200 **sin `data.login`** cuando la contraseña
cambió pero no se pudo abrir la sesión (p. ej. cuenta bloqueada por intentos):
mandar al login, no tratarlo como error.

## Cambio de correo

| Scope | HTTP | Acción |
|-------|------|--------|
| `users.change_email.rate_limited` | 429 | Ya pidió 5 códigos en 15 minutos: esperar |
| `users.change_email.code_not_valid` | 401 | Reintentar; `error.meta.remaining_attempts` |
| `users.change_email.too_many_attempts` | 401 | Código bloqueado: pedir el cambio de nuevo |
| `users.change_email.code_not_found` | 404 | Código vencido, usado o reemplazado |

---

## Tokens

| Situación | HTTP | Acción |
|-----------|------|--------|
| Access inválido/expirado | 401 | → refresh-jwt |
| Refresh inválido (`refresh_tokens.create.failed_to_validate_token`) | 401 | → re-login |
| Refresh revocado (`refresh_tokens.create.revoked`) | 401 | → re-login |
| Sesión inexistente (`refresh_tokens.create.refresh_token_not_found`) | 404 | → re-login |
| `refresh_tokens.create.reuse_detected` | 401 | Se usó un refresh token ya rotado: la sesión se revocó. → re-login |
| `refresh_tokens.create.idle_timeout` | 401 | Sesión inactiva más del timeout de la app. → re-login |
| `refresh_tokens.validate_refresh.rotated` | 401 | El refresh fue reemplazado por la rotación; usa el último que recibiste |
| `refresh_tokens.logout.token` / `.missing_token` | 401 | El refresh ya no es válido: borra los tokens igual |
| `refresh_tokens.logout.not_found` | 404 | La sesión no existe: borra los tokens igual |
| `sessions.list.invalid_token` / `sessions.revoke.invalid_token` | 401 | → refresh-jwt y reintentar |
| `sessions.revoke.not_found` | 404 | La sesión no existe o no es del usuario |
| `app_behaviors.activate_sessions.behavior_not_found` | 404 | La app no tiene behavior `email_auth` |
| `app_behaviors.activate_sessions.idle_timeout_too_short` | 422 | `idle_timeout_seconds` menor que el doble de la vida del access token de la app |
| `testers.expired` | 403 | Dueño tester caducado: re-login no basta, hay que revivirlo |
| `refresh_tokens.validate.revoked` | 401 | (`/validate-access`) La sesión del access token se cerró → re-login |
| `refresh_tokens.validate.lookup_error` | 503 | No se pudo consultar la sesión → reintenta |

---

## OAuth

| Situación | HTTP | Acción |
|-----------|------|--------|
| Provider no config | 404/422 | Configurar oauth-configs |
| Redirect mismatch | 400 | Añadir redirect URL |
| Token inválido (native) | 401 | Revisar id_token / audiences |
| `auth.social.nonce_required` | 401 | La config del proveedor tiene `require_nonce`: pedir `POST /api/v1/auth/social/nonce`, pasarlo al SDK y mandarlo en `nonce` |
| `auth.social.nonce_mismatch` | 401 | El claim `nonce` del id_token no es el nonce enviado ni su SHA-256 hex (o el token no trae nonce) → revisar qué se le pasó al SDK |
| `auth.social.nonce_invalid` | 401 | Nonce desconocido, de otra app, vencido (10 min) o ya usado → pedir uno nuevo y repetir el login |
| `auth.social.nonce_error` | 500 | Accounts no pudo emitir o verificar el nonce → reintentar |
| `oauth.exchange.invalid_code` | 400 | Code desconocido o de otra app → re-login |
| `oauth.exchange.code_used` | 400 | Code ya canjeado; su sesión se revocó → re-login |
| `oauth.exchange.code_expired` | 400 | Code de más de 60 s → re-login |
| `oauth.exchange.redirect_mismatch` | 400 | `redirect_uri` no es el del code |
| `oauth.exchange.validation` | 400 | Falta `code` |
| `session_security.lookup_error` | 503 | El callback no pudo leer el behavior → reintenta el login |

## Seguridad de sesiones (`session_security`)

| Situación | HTTP | Acción |
|-----------|------|--------|
| `session_security.invalid_field` | 400 | Campo desconocido o cuerpo no objeto (`error.meta.field`) |
| `session_security.invalid_value` | 400 | Valor inválido (`error.meta.field`) |
| `app_behaviors.create.use_session_security_endpoint` / `app_behaviors.update.use_session_security_endpoint` | 422 | Usa `PUT /api/v1/app-behaviors/session-security` |

---

## Magic link

| Situación | HTTP | Acción |
|-----------|------|--------|
| Strategy disabled | 422 | Activar behavior |
| Token usado/expirado | 401 | Nuevo request |

---

## Código de acceso por correo

| Scope | HTTP | Acción |
|-------|------|--------|
| `email_code.disabled` | 422 | Activar behavior |
| `email_code.cooldown` | 429 | Esperar `resend_cooldown_seconds` y reintentar (se cuenta por correo: sale igual exista o no la cuenta) |
| `email_code.rate_limit_exceeded` | 429 | Esperar la ventana |
| `email_code.invalid` | 401 | Código equivocado; `error.meta.remaining_attempts` dice cuántos quedan |
| `email_code.attempts_exceeded` | 401 | Intentos agotados: pedir código nuevo |
| `email_code.expired` / `email_code.superseded` / `email_code.already_used` | 401 | Pedir código nuevo |
| `email_code.binding_mismatch` | 401 | Canjear desde la misma IP / navegador |

---

## Embedded Auth (Pro)

Solo en peticiones del componente (cabeceras `X-Accounts-*`) y en sus endpoints. Ver [embedded-auth.md](embedded-auth.md).

| Scope | HTTP | Acción |
|-------|------|--------|
| `embedded_auth.origin.not_allowed` | 403 | Añadir el origen exacto de la página a `allowed_origins` |
| `embedded_auth.disabled` | 403 | Configurar el behavior con ≥1 origen (o la fila está inactiva) |
| `embedded_auth.publishable_key.required` | 401 | Mandar la publishable key (`data-publishable-key`) |
| `embedded_auth.lookup_error` | 503 | Reintentar; base de datos caída |
| `embedded_auth.unavailable` | 503 | Resolver del gate sin registrar: revisar el despliegue |
| `embedded_auth.redirect.not_allowed` | 403 | Registrar la página del magic link en `redirect_urls` |
| `embedded_auth.redirect.check_error` | 500 | Reintentar |
| `embedded_auth.oauth.provider_not_allowed` | 403 | Habilitar el proveedor y listarlo en `strategies.oauth` |
| `embedded_auth.magic_link.challenge_required` | 422 | Mandar `code_challenge` (base64url SHA-256 del verifier, 43) junto al `redirect_url` |
| `embedded_auth.oauth.nonce_required` | 400 | Añadir `&nonce=` (base64url, 22–64) a la `start_url` del popup |
| `app_behaviors.embedded_auth.invalid_config` | 422 | Corregir los campos del mensaje (`campo: error; …`) |
| `app_behaviors.embedded_auth.read_error` / `app_behaviors.embedded_auth.save_error` | 500 | Reintentar |
| `app_behaviors.update.use_embedded_auth_endpoint` / `app_behaviors.create.use_embedded_auth_endpoint` | 422 | Usar `PUT /api/v1/app-behaviors/embedded-auth` |

---

## Webhooks: destino de la URL

| Scope | HTTP | Acción |
|-------|------|--------|
| `webhooks.url.insecure_scheme` | 422 | La `url` no es `https` (alta, `PATCH` con `url` o prueba de un webhook antiguo). Usar https |
| `webhooks.url.blocked_destination` | 422 | El host es o resuelve a una IP no pública (loopback, privada, link-local/metadata, CGNAT, ULA, multicast, IPv4 mapeada) o es un nombre reservado (`localhost`, `*.internal`, `*.local`, sin punto). Usar un host público |
| `webhooks.url.unresolvable_host` | 422 | El host no resuelve. Revisar el nombre / DNS |
| `webhooks.url.invalid_url` | 422 | La `url` no tiene esquema o host |

> Desde 0.15.0. Una entrega bloqueada no es un error HTTP: queda en el registro con `status: "blocked"` y `blocked_reason`.

---

## Límites contra fuerza bruta

| Scope | HTTP | Acción |
|-------|------|--------|
| `auth.rate_limited` | 429 | Signin con cuenta bloqueada, o demasiadas peticiones por IP (60/min por endpoint) o por cuenta (10 cada 15 min en reset, resend, magic link, código). `error.meta.retry_after_seconds` + `Retry-After`. No reintentar antes |
| `api_keys.rate_limited` | 429 | Demasiadas secret keys inválidas desde la IP o para el `key_id` (10 cada 5 min). Revisar la secret configurada |
| `api_keys.verifier_busy` | 503 | Secret key del formato anterior sin turno para verificarse; reintentar tras `Retry-After: 1` (pasa una sola vez por clave: luego queda en HMAC) |

---

## Scopes de secret keys (revisión 21)

| Scope | HTTP | Acción |
|-------|------|--------|
| `api_keys.scope_denied` | 403 | La secret key no tiene el scope de la ruta; `error.meta.required_scope` dice cuál (`"*"` si la ruta solo admite poder total). Darle el scope con `PATCH /api/v1/api-keys/{id}` |
| `api_keys.scope_escalation` | 403 | La key quiso crear, rotar, editar, desactivar o borrar otra con scopes que ella no tiene; `error.meta.missing_scopes` |
| `api_keys.last_full_access_key` | 409 | Quitarle `"*"` a la última key activa con `"*"` de la app; darle `"*"` a otra primero |
| `api_keys.invalid_scopes` | 400 | `scopes` con más de 64, con uno fuera del catálogo (`error.meta.invalid_scope`) o vacío en `PATCH`; en `generate`, omitirlo (o `[]`) es `"*"` |
| `api_keys.update.not_found` / `api_keys.get.not_found` | 404 | La key no es de la app, está dada de baja o no existe |
| `api_keys.update.name_taken` | 409 | Otra key de la app ya usa ese nombre |

---

## Aislamiento de tenants

| Scope | HTTP | Acción |
|-------|------|--------|
| `tenant.app_unresolved` | 401 | La key (secret o publishable) no resuelve a una app válida y la ruta se corta antes del handler. Una key sana nunca lo provoca: generar una key nueva para la app o revisar la fila de la key con el operador |
| `tenant.app_required` | 400 | Un servicio acotado a una app recibió un `app_id` vacío (segundo cinturón detrás del anterior). No debería verse desde un cliente; reportarlo con el `trace_id` |

---

## Planes y cuotas (`quota.*`)

Solo con `ENTITLEMENTS_URL` y en apps con `tenant_ref`. Ver [plans-and-quotas.md](plans-and-quotas.md). Los logins nunca los reciben.

| Scope | HTTP | Acción |
|-------|------|--------|
| `quota.users_exceeded` | 403 | La organización llegó a `max_accounts_users` de su plan (`error.meta.limit`, `error.meta.current` solo con secret key). Magic link y código por correo no lo devuelven: responden su 200 genérico. Mostrar "límite de usuarios alcanzado" y no reintentar; se libera al subir de plan o borrar usuarios |
| `quota.tenant_read_only` | 403 | Plan impagado vencido, suspendido o cancelado (`error.meta.status`): altas nuevas y mutaciones administrativas con secret key cerradas. Los `GET`, los logins y las revocaciones siguen. No reintentar |
| `entitlements.not_found` / `entitlements.disabled` / `entitlements.provider_unavailable` | 404 / 409 / 502 | Rutas de operador `/api/v1/system/entitlements/*` |

---

## Límites del servidor HTTP

| Scope | HTTP | Acción |
|-------|------|--------|
| `http.request.body_too_large` | 413 | El cuerpo pasa del límite de la instancia (`error.meta.max_bytes`; 1 MiB por defecto, 4 MiB en las plantillas de correo). Achicar el payload; no reintentar igual |

---

## Bloqueo regional e historial de logins

Ver [login-security.md](login-security.md).

| Scope | HTTP | Acción |
|-------|------|--------|
| `geo_access.country_not_allowed` | 403 | Login desde un país no permitido; el país detectado viene en `error.meta.country_code` (y `country_name`). No reintentar |
| `geo_access.unknown_country` | 403 | No se pudo ubicar la IP (`error.meta.country_code: "XX"`) y la app pide `unknown_country: deny` |
| `geo_access.lookup_error` | 503 | Reintentar; no se pudo leer la política |
| `app_behaviors.geo_access.invalid_config` | 422 | Corregir los campos de `error.meta.errors` (`mode`, `countries[i]`, `unknown_country`) |
| `app_behaviors.geo_access.read_error` / `app_behaviors.geo_access.save_error` | 500 | Reintentar |
| `app_behaviors.update.use_geo_access_endpoint` / `app_behaviors.create.use_geo_access_endpoint` | 422 | Usar `PUT /api/v1/app-behaviors/geo-access` |
| `dto.validate.ListLoginEventsQuery` | 422 | Corregir `page`, `size`, `country` (ISO2 o `XX`), `type`, `method`, `from`/`to` (RFC 3339) |
| `dto.validate.LoginEventsSummaryQuery` | 422 | `from`/`to` RFC 3339 y `from` ≤ `to` |
| `login_events.list.error` / `login_events.summary.error` | 500 | Reintentar |
| `audit.query.invalid_filter` | 400 | Corregir el filtro de `error.meta.field` (`action`, `actor_id`, `resource_type`, `resource_id`, `result`, `from`/`to` RFC 3339 con `from` < `to`, `limit` 1..200) |
| `audit.query.invalid_cursor` | 400 | Usar el `next_cursor` tal cual lo devolvió la API |
| `audit.query.local_store_disabled` | 404 | La instancia corre con `AUDIT_LOCAL_STORE=false`: el audit log está en core |
| `audit.query.failed` | 500 | Reintentar |

---

## Idioma de los correos (`email_locale`)

Ver [email-locale.md](email-locale.md).

| Scope | HTTP | Acción |
|-------|------|--------|
| `email_locale.invalid_locale` | 400 | `default_locale` debe ser una etiqueta BCP 47 (`es`, `es-MX`) o `""` |
| `app_behaviors.email_locale.read_error` / `app_behaviors.email_locale.save_error` | 500 | Reintentar |

---

## Enlace de identidades (`identity_linking`)

Ver [identity-linking.md](identity-linking.md).

| Scope | HTTP | Acción |
|-------|------|--------|
| `identity_linking.invalid_mode` | 400 | `mode` debe ser `link_with_proof` o `separate` |
| `identity_linking.lookup_error` | 503 | Reintentar; no se pudo leer la política (no se enlazó ni creó nada) |
| `app_behaviors.identity_linking.read_error` / `app_behaviors.identity_linking.save_error` | 500 | Reintentar |
| `app_behaviors.update.use_identity_linking_endpoint` / `app_behaviors.create.use_identity_linking_endpoint` | 422 | Usar `PUT /api/v1/app-behaviors/identity-linking` |

---

## Testers (usuarios de prueba)

| Scope | HTTP | Acción |
|-------|------|--------|
| `testers.disabled` | 422 | Activar `email_auth.testers` |
| `testers.username_taken` | 409 | Otro `user_name`/patrón; lista en `error.meta.user_names` |
| `testers.not_found` | 404 | El id no es un tester de la app |
| `testers.expired` | 403 | `PATCH /api/v1/testers/{id}/expiry` y volver a iniciar sesión |
| `testers.password_managed` | 409 | Contraseña derivada: leerla de `/credentials`, no cambiarla (set-password, reset, reset-confirm, reset/validate-code) |
| `testers.role_locked` | 409 | El rol de un tester es siempre `default` |
| `testers.confirm_required` | 422 | Añadir `confirm=true` al borrado en lote (`"confirm": true` en un trabajo `delete`) |
| `testers.job_not_found` | 404 | El id no es un trabajo de la app |
| `testers.password_policy` | 422 | La política de contraseñas de la app no se puede cumplir |
| `testers.invalid_input` / `dto.validate.*` | 422 | Corregir `ttl`, `mode`, `pattern` (debe llevar `{n}` o `{n:0W}`), `count` (1–1000), `target` (exactamente uno de `ids`, `all`, `filter`; ≤ 1000 testers), `status`… |
| `testers.lookup_error`, `testers.error_saving`, `testers.error_hashing_password`, `testers.error_generating_tokens` | 500 | Reintentar; loguear `trace_id` |
| `users.list.invalid_is_test` | 400 | `is_test` solo admite `true`/`false` |

`POST /users/{id}/set-password` y `PATCH /users/{id}/role` devuelven el scope en `errors[0].scope` (envoltura antigua).

---

## Segundo factor (MFA)

| Scope | HTTP | Acción |
|-------|------|--------|
| `mfa.invalid_code` | 401 | Código equivocado; mostrar `error.meta.attempts_remaining` |
| `mfa.invalid_token` | 401 | `mfa_token` desconocido, vencido, usado o de otra app → volver a iniciar sesión |
| `mfa.too_many_attempts` | 429 | El `mfa_token` agotó sus intentos → volver a iniciar sesión |
| `mfa.invalid_method` | 400 | `method` debe ser `totp` o `backup_code` |
| `mfa.enrollment_required` | 409 | Token de enrolamiento usado en `/mfa/verify` → `/mfa/enroll/start` |
| `mfa.already_enrolled` | 409 | Token de verificación usado en `/mfa/enroll/*` (o el usuario ya tiene TOTP) → `/mfa/verify` |
| `mfa.enrollment_not_started` | 409 | `enroll/confirm` antes de `enroll/start` |
| `mfa.lookup_error` | 503 | No se pudo leer el behavior, el usuario o el paso; el login falla cerrado. Reintentar |
| `mfa.internal_error` | 500 | Reintentar / soporte |
| `mfa.invalid_mode` | 400 | `PUT /app-behaviors/mfa`: `off`, `optional` o `required` |
| `mfa.invalid_flow` | 400 | `PUT /app-behaviors/mfa`: flujo desconocido |
| `app_behaviors.mfa.read_error` / `app_behaviors.mfa.save_error` | 500 | Reintentar |
| `app_behaviors.create.use_mfa_endpoint` / `app_behaviors.update.use_mfa_endpoint` | 422 | Usar `/api/v1/app-behaviors/mfa` |
| `security_limits.out_of_range` | 400 | `PUT /app-behaviors/security-limits`: valor fuera de rango; `error.meta {field, min, max}` |
| `security_limits.invalid_field` | 400 | `PUT /app-behaviors/security-limits`: campo desconocido o de tipo equivocado; `error.meta.field` |
| `security_limits.invalid_durations` | 400 | `lockout.durations_sec`: 1 a 5 valores no decrecientes |
| `app_behaviors.security_limits.read_error` / `app_behaviors.security_limits.save_error` | 500 | Reintentar |
| `app_behaviors.create.use_security_limits_endpoint` / `app_behaviors.update.use_security_limits_endpoint` | 422 | Usar `/api/v1/app-behaviors/security-limits` |
| `auth.rate_limited` | 429 | `MFA_FAILURE_MAX` fallos del usuario o límite por IP; `Retry-After` |
| `client.mfa_required` / `client.mfa_enrollment_required` | — | Solo en el navegador (Embedded Auth): `MfaRequiredError` con `challenge`; completar con `Accounts.mfa.*` |

## TOTP del usuario

| Scope | HTTP | Acción |
|-------|------|--------|
| `totp.setup.already_enabled` | 409 | Ya tiene TOTP |
| `totp.verify.not_configured` | 400 | Llamar `/totp/setup` primero |
| `totp.verify.invalid_code` / `totp.disable.invalid_code` | 401 | Código equivocado |
| `totp.setup.invalid_token` / `totp.verify.invalid_token` / `totp.disable.invalid_token` | 401 | Access token inválido |
| `totp.qr.not_configured` | 404 | No hay secreto pendiente → `/totp/setup` |
| `totp.qr.already_enabled` | 409 | TOTP ya activo: no hay QR que mostrar |
| `totp.backup_codes.invalid_code` | 401 | Código TOTP equivocado al regenerar |
| `totp.backup_codes.totp_not_enabled` | 409 | Activar TOTP primero |
| `totp.backup_codes.unavailable` | 503 | Reintentar |

## Policies y autorización

| Scope | HTTP | Acción |
|-------|------|--------|
| `policies.update.validation` | 400 | Campo vacío o `effect` distinto de `allow`/`deny` |
| `policies.update.not_found` / `policies.delete.not_found` | 404 | No existe en la app |
| `policies.update.already_exists` | 409 | Ya hay una policy con ese `(resource, action, effect)` |
| `role_policies.remove.not_found` | 404 | El rol no tiene esa policy |
| `authorize.validation` | 400 | Falta `action`/`resource`, o no mandaste exactamente uno de `user_id` / `access_token` |
| `authorize.invalid_token` | 401 | `access_token` inválido, vencido o de otra app |
| `authorize.user_not_found` | 404 | El usuario no existe en la app |
| `authorize.lookup_error` | 503 | Reintentar |

---

## Patrón implementación

```typescript
function handleScope(scope: string): UiAction {
  const map: Record<string, UiAction> = {
    "emails.signup.email_already_exists": { type: "redirect", to: "/login" },
    "emails.validation.weak_password": { type: "field-error", field: "password" },
    "password.breached": { type: "field-error", field: "password" },
    "emails.signin.invalid_credentials": { type: "toast", msg: "Credenciales inválidas" },
    "emails.signin.account_inactive": { type: "activate-flow" },
    "auth.apikey.invalid": { type: "config-error" },
  };
  return map[scope] ?? { type: "generic" };
}
```

---

## MCP Connect

| Scope | HTTP | Acción |
|-------|------|--------|
| `mcp_resources.invalid_resource_url` / `invalid_login_url` / `invalid_access_ttl` | 422 | Corregir el campo |
| `mcp_resources.duplicate_resource_url` | 409 | La app ya registró esa URL |
| `mcp_resources.invalid_scope_key` / `duplicate_scope_key` / `invalid_scope_label` / `unknown_role` | 422 | Corregir la lista de scopes |
| `mcp_resources.not_found` | 404 | No existe o es de otra app |
| `mcp_resources.verify.blocked_destination` | 422 | La URL del MCP resuelve a una red privada |
| `oauth_clients.not_found` | 404 | client_id desconocido |
| `oauth_clients.invalid_redirect_uris` / `redirect_domain_not_allowed` | 422 | Corregir redirect_uris o `allowed_redirect_domains` |
| `mcp_authorization.not_found` | 404 | Solicitud desconocida o de otra app |
| `mcp_authorization.expired` | 410 | Pasaron 10 min; el asistente reinicia |
| `mcp_authorization.approve.user_token_invalid` | 401 | `user_token` no es un access token vigente de esta app |
| `mcp_authorization.approve.scope_not_requested` | 422 | Solo se pueden quitar scopes |
| `mcp_authorization.approve.scope_not_allowed_for_user` | 422 | El rol de la persona no cubre ese scope |
| `mcp_authorization.approve.scope_required` | 422 | Para «no» usa deny |
| `mcp_authorization.approve.not_pending` / `deny.not_pending` | 409 | Ya resuelta; no hay segundo código |
| `mcp_connections.not_found` | 404 | No existe, es de otra app o de otra persona |
| `mcp_connections.me.missing_token` / `me.invalid_token` | 401 | Re-login |

Las rutas `/o/{app_id}/oauth/*` no usan scopes: responden errores OAuth (`invalid_request`, `invalid_client`, `invalid_grant`, `invalid_scope`, `invalid_target`, `unsupported_grant_type`, `access_denied`).

---

## Reglas

1. No usar `error.message` para branching — puede cambiar
2. Loguear `trace_id` en errores 5xx
3. 401 en refresh → siempre re-login, no loop infinito
4. Mensajes genéricos en credenciales (seguridad)
