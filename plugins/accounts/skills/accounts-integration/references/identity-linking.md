# Enlace de identidades por correo (`identity_linking`)

Community y Pro. Decide si dos identidades con el mismo correo (OAuth + correo, o dos OAuth) son el mismo usuario.

## Regla base (siempre)

Una identidad OAuth **nunca** se enlaza a un usuario existente si el proveedor no verificó el correo de forma fiable; se crea un usuario aparte (el login no falla).

| Proveedor | Verificado cuando |
|-----------|-------------------|
| Google / Apple | `email_verified` del proveedor |
| Microsoft | `id_token` con claim opcional `xms_edov: true` (mismo `oid`, `aud` = client id). Configurarlo en Entra → Token configuration → ID → `xms_edov` + `email` |
| GitHub | correo primario **y** verificado de `/user/emails` |

Si el usuario existente es OAuth, también su proveedor tiene que haberlo verificado.

## Config (secret key)

```http
GET /api/v1/app-behaviors/identity-linking
PUT /api/v1/app-behaviors/identity-linking
{"mode": "link_with_proof" | "separate"}
```

Respuesta `data`: `{app_id, mode, updated_at?}`. Sin fila: `link_with_proof`. Modo inválido: `400 identity_linking.invalid_mode`.

## Modos

| Flujo | `link_with_proof` (default) | `separate` |
|-------|-----------------------------|------------|
| OAuth web / popup / nativo | enlaza si está verificado | usuario aparte |
| Signup, verificación **off**, choca con OAuth | `201` **sin tokens**; enlaza con `POST /api/v1/emails/activate` + código | usuario nuevo con sus tokens |
| Signup, verificación on | pendiente del código, enlaza al activar | usuario nuevo pendiente del código |
| Magic link / código por correo | se cuelga del OAuth verificado | identidad de correo propia |

En los dos casos de "usuario aparte" el `user_name`, si ya está ocupado, pasa a `valor#xxxxxxxx` (determinista).

## Para integradores

- Tras `POST /api/v1/emails/signup` **no asumas tokens** aunque la verificación esté apagada: si `data.access_token` falta, pide el código y llama a `/activate`.
- `NATIVE_AUTH_AUTO_LINK_BY_EMAIL=false` (instancia) fuerza `separate` en todas las apps; `/auth/social` ya no responde `409 auth.social.email_already_linked`.
- `503 identity_linking.lookup_error`: reintenta.
