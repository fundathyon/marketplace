# Idioma de los correos transaccionales (`email_locale`)

Community y Pro. Aplica a los correos de activación (signup y reenvío), reset de
contraseña, magic link, código por correo, cambio de correo y aviso de
contraseña cambiada.

## Cómo se elige el idioma

Cada correo prueba esta cadena, del más específico al menos, y usa la primera
plantilla que exista (en Pro primero las de la app en toda la cadena y después
las globales, así una app que solo personalizó su plantilla `en` la sigue
recibiendo aunque exista una global en el idioma pedido):

1. `locale` del body de la petición que lo origina (`POST /api/v1/emails/signup`,
   `/signup/resend-code`, `/reset`, `/magic-link/request`, `/email-code/request`).
2. La cabecera `Accept-Language` de esa petición (la etiqueta de mayor `q`).
3. El idioma guardado del usuario: el que trajo su signup (body o cabecera).
4. El `default_locale` de la app (behavior `email_locale`, opt-in).
5. `en`.

Cada paso va de lo regional a lo general: `es-MX` prueba `es-mx` y luego `es`.
Los locales se normalizan a minúsculas con `-` (`pt_BR` → `pt-br`). Un `locale`
sin forma de BCP 47 se ignora (nunca da 4xx). Las plantillas embebidas y los
temas están en inglés: llegar a `en` sin plantilla propia usa el tema.

**Compatibilidad:** una app sin plantillas en otros idiomas recibe exactamente
el mismo correo que antes. Para mandar en español, crea la plantilla `es` con
`PUT /api/v1/email-templates/{id}` (`"locale": "es"`).

```bash
curl -X POST "{BASE_URL}/api/v1/emails/signup" \
  -H "X-API-Key: {publishable_key}" -H "Content-Type: application/json" \
  -H "Accept-Language: es-MX,es;q=0.9" \
  -d '{"email": "ana@example.com", "password": "SecurePass123!", "locale": "es-MX"}'
```

## Idioma por defecto de la app

```bash
curl "{BASE_URL}/api/v1/app-behaviors/email-locale" -H "X-API-Key: {secret_key}"
# {"data": {"app_id": "...", "effective_default_locale": "en"}}

curl -X PUT "{BASE_URL}/api/v1/app-behaviors/email-locale" \
  -H "X-API-Key: {secret_key}" -H "Content-Type: application/json" \
  -d '{"default_locale": "es"}'
# {"data": {"app_id": "...", "default_locale": "es", "effective_default_locale": "es", "updated_at": "..."}}
```

- Sin fila no hay default (correos en `en`, como siempre); `GET` no crea nada.
- `"default_locale": ""` lo vacía.
- Scopes: `behaviors:read` / `behaviors:write`.
- Errores: `400 email_locale.invalid_locale`, `500 app_behaviors.email_locale.read_error` / `save_error`.

## Entrega

Los correos salen tras el commit por el outbox. Con `EMAIL_ASYNC_DELIVERY=true`
(default) la respuesta no espera al proveedor. Un fallo temporal (red, timeout,
4xx SMTP, 408/429/5xx de Mailgun) se reintenta con backoff; uno permanente no.
Un reintento nunca repite un correo que ya salió: cada envío queda en
`email_deliveries` con la llave evento + plantilla y el `Message-ID` sale de esa
misma llave. Para el cliente nada cambia: las respuestas de los endpoints son
las de siempre.
