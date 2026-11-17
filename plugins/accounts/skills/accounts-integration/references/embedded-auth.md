# Embedded Auth (Pro) — componentes web de login

**Solo edición Pro.** La instancia sirve un script (`{BASE_URL}/ui/v1/accounts.js`) con custom elements (`<accounts-sign-in>`, `<accounts-sign-up>`, `<accounts-reset-password>`, `<accounts-user-button>`) que hacen login, registro, reset y la sesión del navegador contra las rutas de siempre. En Community `/ui/v1/*`, `/api/v1/embedded-auth/config` y `/embedded-start` dan 404 y las cabeceras `X-Accounts-*` se ignoran (`GET /health` → `edition`).

## Concepto clave

```
Admin (secret key) → PUT /api/v1/app-behaviors/embedded-auth   { allowed_origins, strategies, branding… }
Página             → <script src="{BASE_URL}/ui/v1/accounts.js" data-publishable-key="pk_…">
                     <accounts-sign-in after-sign-in-url="/dashboard">
Componente         → rutas de siempre con X-Accounts-Client + X-Accounts-Publishable-Key
Gate de Accounts   → valida pk + app habilitada + Origin ∈ allowed_origins → copia pk a X-API-Key
Tu frontend        → const token = await Accounts.getToken()  → fetch(tu API, Authorization: Bearer token)
Tu backend         → verifica el JWT RS256 con la llave de la app (public-key-jwt + secret key)
```

- **Sin `X-Accounts-*` nada cambia**: curl, móvil, servidores y SPAs actuales reciben las mismas respuestas y el `cors.Default()` de siempre.
- El componente **nunca** manda `X-API-Key` ni `Authorization`: manda `X-Accounts-Publishable-Key` y `X-Accounts-Authorization: Bearer <token>`, y el gate los traduce tras validar el origen (así el preflight nunca concede cabeceras en las que confían las rutas existentes).
- La publishable key es pública; lo que impide su uso desde otra página es `allowed_origins`. La **secret key nunca** va en el navegador.

---

## Configurar el behavior (admin, secret key)

La fila `embedded_auth` se crea con el primer `PUT` (no al crear la app). `GET` sin fila devuelve la config por defecto y no crea nada.

```bash
curl -X PUT "{BASE_URL}/api/v1/app-behaviors/embedded-auth" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: {secret_key}" \
  -d '{
    "allowed_origins": ["https://miapp.com", "http://localhost:5173"],
    "redirect_urls": ["https://miapp.com/login"],
    "strategies": { "password": true, "email_code": true, "magic_link": true, "oauth": ["google"] },
    "branding": { "name": "Mi App", "logo_url": "", "accent": "neutral", "theme": "system", "layout": "card", "locale": "es" },
    "hide_branding": false
  }'
```

Respuesta (`GET` y `PUT`): `{ id?, app_id, config, effective: { enabled, strategies }, available: { password, email_code, magic_link, oauth[] }, created_at, updated_at }`. Los campos vacíos se omiten del JSON (trátalos como `[]`/`""`).

| Campo | Regla |
|-------|-------|
| `allowed_origins` | 1–20; `scheme://host[:port]` sin ruta/query/fragmento/usuario/comodines; `https` salvo `localhost`, `127.0.0.1`, `[::1]`; se guardan en minúsculas sin puerto por defecto; duplicados → 422 |
| `redirect_urls` | 0–20; URL absoluta http(s) sin fragmento ni usuario; su origen debe estar en `allowed_origins`; match exacto tras normalizar. El componente manda `location.origin + location.pathname` → registrar **sin query** |
| `strategies.password` | requiere `email_auth` activo |
| `strategies.email_code` / `magic_link` | requieren el nodo habilitado en `email_auth`; `magic_link` además ≥1 `redirect_url` |
| `strategies.oauth` | proveedores en minúsculas, únicos, configurados y habilitados en `oauth-configs` |
| `branding` | `name` ≤ 80; `logo_url` https (http solo localhost); `theme` system\|light\|dark; `layout` card\|split; `locale` es\|en; `accent` `"neutral"` o `{hue 0–360, l 0.30–0.80, c 0–0.37}` (default naranja `{45, 0.56, 0.17}`) |
| `hide_branding` | oculta "Protegido por Foundathyon Accounts" |

- Al menos una estrategia. `PUT` reemplaza la config **entera**.
- `effective.enabled` = fila existe ∧ activa ∧ ≥1 origen válido. `effective.strategies` = guardadas ∩ disponibles hoy.
- `PUT /api/v1/app-behaviors/{id}` sobre la fila → `422 app_behaviors.update.use_embedded_auth_endpoint`; `POST /app-behaviors` o `/simple` con `embedded_auth` → `422 app_behaviors.create.use_embedded_auth_endpoint`.
- Sin interruptor explícito: para cortar, deja solo un origen que no uses (p. ej. `http://localhost:1`) o marca la fila `is_active = false` (→ `403 embedded_auth.disabled`).

---

## Página (HTML)

```html
<script src="{BASE_URL}/ui/v1/accounts.js" data-publishable-key="{publishable_key}" defer></script>

<accounts-sign-in after-sign-in-url="/dashboard" sign-up-url="/registro"></accounts-sign-in>
<accounts-user-button after-sign-out-url="/"></accounts-user-button>
```

- Script **clásico** (no `type="module"`): deduce `{BASE_URL}` de su `src` quitando `/ui/v1/accounts.js` (conserva `ROOT_PATH`). Override: `data-base-url`, o `Accounts.load({ publishableKey, baseUrl, persistence, locale })`.
- `data-persistence`: `local` (default) | `session` | `memory` — dónde vive el refresh token. El access token siempre en memoria.

| Atributo | Elementos | Valores |
|----------|-----------|---------|
| `after-sign-in-url` / `after-sign-up-url` / `after-sign-out-url` | según elemento | URL tras el evento |
| `sign-in-url` / `sign-up-url` / `reset-password-url` | sign-in, sign-up, reset, user-button | enlaces; sin ellos el flujo cambia en el lugar |
| `locale` | todos | `es` \| `en` |
| `theme` | todos | `system` \| `light` \| `dark` |
| `accent` | todos | `neutral` o `hue,l,c` |
| `layout` | sign-in, sign-up, reset | `card` \| `split` (`<div slot="brand">`) |
| `mode` | sign-in, sign-up, reset | `inline` \| `modal` (`open()`/`close()`) |
| `strategies` | sign-in, sign-up | solo **restringe**: `password`, `email_code`, `magic_link`, `oauth` o proveedor |

Estilos: variables `--fdn-*` sobre el elemento y `::part()` (`card`, `input`, `button`, `button-primary`, `alert`, `otp`, `requirements`, `requirement`, …). Precedencia de tema/acento: atributo (u opción de `openSignIn`) > `Accounts.setAppearance()` > `data-fdn-theme`/`data-fdn-product` de la página > `branding` > default (idioma y layout igual, sin el paso de la página).

Contraseña nueva (sign-up y reset): con `signup.password_policy` en la config el componente lista los requisitos bajo el campo (`aria-describedby`), los marca mientras se escribe con las reglas del servidor (largo en bytes, Lu/Ll/Nd, `special_chars` o cualquier símbolo) y en un `422 emails.validation.weak_password` muestra los que faltan; sin ella, "Mínimo N caracteres" de `password_min_length`.

---

## API de JavaScript

```js
await Accounts.ready;                         // status: 'unknown' | 'signed-in' | 'signed-out'
Accounts.user;                                 // { id, appId, sessionId, method, email?, claims } | null
const token = await Accounts.getToken();       // refresca si quedan < 30 s; null sin sesión
Accounts.on('signed-in', ({ user }) => {});
Accounts.on('signed-out', ({ reason, scope, fromOtherTab }) => {}); // reason: signed-out|expired|revoked|replaced
Accounts.on('error', ({ error }) => console.warn(error.scope));
Accounts.openSignIn({ afterSignInUrl: '/dashboard' });                // modal
Accounts.openSignUp({ theme: 'dark', accent: 'neutral', locale: 'en', layout: 'card' }); // misma semántica que los atributos
Accounts.setAppearance({ theme: 'dark', locale: 'en' }); // default de la página: elementos sin atributo y modales, en vivo; null/'' borra una clave, setAppearance(null) todo
await Accounts.signOut();                                             // POST /api/v1/logout + avisa a otras pestañas

// Sin componentes
await Accounts.signIn.password(email, password);
const { challengeId } = await Accounts.signIn.emailCode.request(email);
await Accounts.signIn.emailCode.verify(challengeId, code);
await Accounts.signIn.magicLink.request(email);   // vuelve a esta página con ?accounts_ticket
button.onclick = () => Accounts.signIn.oauth('google'); // popup: llamar directo en el click
const r = await Accounts.signUp.password(email, password); // r.status: 'complete' | 'needs_verification'
await Accounts.activate(email, code);
await Accounts.resetPassword.request(email);
const { token: t } = await Accounts.resetPassword.validateCode(email, code);
await Accounts.resetPassword.setPassword(t, newPassword);

// Segundo factor (behavior mfa): cualquier login de arriba puede rechazar con el paso
try { await Accounts.signIn.password(email, password); }
catch (e) {
  if (e.scope === 'client.mfa_required') {               // MfaRequiredError, e.challenge
    await Accounts.mfa.verify(e.challenge, code);          // o { method: 'backup_code' }
  } else if (e.scope === 'client.mfa_enrollment_required') {
    const { qrImage, secret, url } = await Accounts.mfa.enroll.start(e.challenge);
    const { user, backupCodes } = await Accounts.mfa.enroll.confirm(e.challenge, code);
  } else throw e;
}
```

Segundo factor en los componentes: cualquier estrategia que abre sesión (contraseña, código, magic link —también el canjeado al cargar—, OAuth, signup sin verificación, activación, reset) muestra el paso en vez de terminar: `mfa` (6 dígitos, auto-submit; "Usar un código de respaldo" si `methods` lo incluye), `mfa-backup`, `mfa-enroll` (QR solo si es `data:image/…` + clave manual + primer código) y `mfa-backup-codes` (10 códigos una vez, "Continuar"). `mfa.invalid_code` muestra los intentos (`meta.attempts_remaining`); `mfa.invalid_token` / `mfa.too_many_attempts` solo ofrecen volver a iniciar sesión. Un `MfaRequiredError` no se emite como `accounts:error`. Ver [mfa.md](mfa.md).

Eventos DOM en `document`: `accounts:signed-in`, `accounts:signed-out`, `accounts:error` (`detail.error.scope`). Cada elemento también despacha `accounts:error` con `{ error, flow, step }`; el modal emite `accounts:close` (`reason`: `dismiss` | `signed-in`). Errores: `AccountsError { scope, status, code, message, serverMessage, meta, traceId }`.

Sesión: refresh serializado entre pestañas (Web Lock `accounts:<pk>:refresh` + `BroadcastChannel` `accounts:<pk>`), persiste el refresh nuevo antes de difundirlo (seguro con rotación). Scopes terminales → `signed-out`; red/5xx → conserva la sesión y reintenta.

---

## Backend: verificar el JWT

```js
import { importSPKI, jwtVerify } from 'jose';

// Pro: secret key en X-API-KEY; la respuesta es JSON y el PEM viene en data.
const res = await fetch(`${ACCOUNTS_BASE_URL}/api/v1/system/public-key-jwt`, {
  headers: { 'X-API-KEY': ACCOUNTS_SECRET_KEY },
});
const { data: pem } = await res.json();
const key = await importSPKI(pem, 'RS256');

const { payload } = await jwtVerify(token, key, {
  algorithms: ['RS256'],
  typ: 'at+jwt',
  audience: ACCOUNTS_APP_ID,                          // aud = app_id
  issuer: ACCOUNTS_JWT_ISSUER ?? 'foundathyon-accounts', // JWT_ISSUER de la instancia
});
// payload.sub = user_id
```

`public-key-jwt` **no** es público ni texto plano: sin secret key → `401 public_key_jwt.api_key_required`. Pídelo en el servidor, una vez, y cachéalo.

---

## Magic link embebido

Con `X-Accounts-Client`, `POST /api/v1/emails/magic-link/request` acepta `redirect_url` (debe ser exactamente una de `redirect_urls`) y entonces **exige** `code_challenge` (estilo PKCE, ata el link al navegador que lo pidió):

```text
verifier       = base64url(32 bytes aleatorios) sin relleno (43)   → localStorage "accounts:<pk>:ml" = [{v, t}] (más nuevo primero, máx 3, < 1 h)
code_challenge = base64url(SHA-256(utf8(verifier))) sin relleno (43, ^[A-Za-z0-9_-]{43}$)   → en el body junto a email y redirect_url
correo         = redirect_url?accounts_ticket=R
token_hash     = hash(D),  D = hex_minúsculas(HMAC-SHA256(key = utf8(code_challenge), msg = utf8(R)))  (64)
canje          = POST /api/v1/emails/magic-link/claim { "token": D }   (endpoint sin cambios; R en claro → 401 magic_link.not_found)
```

Sin `code_challenge` válido → `422 embedded_auth.magic_link.challenge_required`, sin efectos (antes de buscar/crear identidad y del rate limit; después del check de `redirect_url`). El script saca el ticket con `replaceState` y prueba cada `verifier` guardado (más nuevo primero): `magic_link.not_found` pasa al siguiente, otro error corta. **Sin `verifier` no canjea** y muestra `client.magic_link_other_browser` ("Abre el enlace en el mismo navegador donde lo pediste"): compromiso documentado, el link embebido solo funciona en el mismo navegador/perfil. `redirect_base_url` no hace falta. Si la página ya tiene sesión, `<accounts-sign-in>` pide confirmar antes de canjear. Sin la cabecera, en Community, sin `redirect_url` o si no es string → `redirect_url` y `code_challenge` se ignoran y el link se canjea con el token del correo, como antes.

## OAuth por popup

La config pública da `strategies.oauth[].start_url` (= `callback_uri` + `/embedded-start`, en el host del callback). El componente genera por intento `nonce = base64url(32 bytes)` (43) y un nombre de ventana aleatorio, y abre `start_url?origin=<location.origin>&nonce=<nonce>` en el click. `/embedded-start` exige `nonce` `^[A-Za-z0-9_-]{22,64}$` (si no, `400 embedded_auth.oauth.nonce_required`, comprobado después de config/política/proveedor/origen) y lo guarda con el origen validado en el valor de la cookie `HttpOnly` del flujo. El callback redirige a `{prefijo}/ui/v1/oauth-callback.html#status=ok|error&provider&access_token&refresh_token&error&message&origin&nonce` (ya no existe `origins`); con segundo factor pendiente `status=mfa_required|mfa_enrollment_required` con `mfa_token` y `mfa_methods`, sin tokens. La página hace **un** `postMessage({type:"accounts:oauth:result", status, provider, access_token, refresh_token, error, message, mfa_token, mfa_methods, nonce}, origin)` y se cierra (sin `origin`/`nonce` válidos no envía nada). El componente solo acepta `event.source === popup && event.origin === new URL(start_url).origin && data.nonce === nonce`. Requisitos: proveedor habilitado y en `strategies.oauth`; proxy que sirva `{ROOT_PATH}/ui/v1/*` en el host del callback; **la página anfitriona no debe mandar `Cross-Origin-Opener-Policy: same-origin`** (usa `same-origin-allow-popups` o nada).

---

## Endpoints

| Método | Ruta | Auth | Notas |
|--------|------|------|-------|
| GET | `/api/v1/app-behaviors/embedded-auth` | Secret | config + effective + available; no crea fila |
| PUT | `/api/v1/app-behaviors/embedded-auth` | Secret | reemplaza la config; crea la fila |
| GET | `/api/v1/embedded-auth/config` | Public (o cabeceras del componente) | estrategias efectivas, `start_url`, `signup{enabled, verification_required, code_size, code_type, password_min_length, password_policy?{min_length, min_uppercase, min_lowercase, min_digits, min_special, special_chars[]}}` (`password_policy` se omite sin política), branding; `no-store` |
| GET | `/api/v1/oauth/:callback_key/embedded-start?origin=&nonce=` | — (navegación del popup) | 302 al proveedor + cookie |
| GET, HEAD | `/ui/v1/:file` | — | `accounts.js`, `oauth-callback.html`, `oauth-callback.js`, `manifest.json` (HEAD: mismos headers y status, sin cuerpo) |

## Error scopes

| Scope | HTTP | Acción |
|-------|------|--------|
| `embedded_auth.origin.not_allowed` | 403 | Añadir el origen exacto a `allowed_origins` |
| `embedded_auth.disabled` | 403 | `PUT` del behavior con ≥1 origen (o fila inactiva) |
| `embedded_auth.publishable_key.required` | 401 | Falta `data-publishable-key` / `Accounts.load` |
| `auth.apikey.invalid` | 401 | Publishable key inválida |
| `embedded_auth.lookup_error` | 503 | Reintentar (base caída) |
| `embedded_auth.unavailable` | 503 | Resolver sin registrar (despliegue) |
| `embedded_auth.redirect.not_allowed` | 403 | Registrar la página en `redirect_urls` |
| `embedded_auth.redirect.check_error` | 500 | Reintentar |
| `embedded_auth.magic_link.challenge_required` | 422 | Mandar `code_challenge` (base64url SHA-256 del verifier, 43) con el `redirect_url` |
| `embedded_auth.oauth.nonce_required` | 400 | Añadir `&nonce=` (base64url 22–64) a la `start_url` |
| `embedded_auth.oauth.provider_not_allowed` | 403 | Habilitar el proveedor y listarlo en `strategies.oauth` |
| `app_behaviors.embedded_auth.invalid_config` | 422 | Corregir `campo: error; …` |
| `app_behaviors.embedded_auth.read_error` / `save_error` | 500 | Reintentar |
| `app_behaviors.update.use_embedded_auth_endpoint` / `app_behaviors.create.use_embedded_auth_endpoint` | 422 | Usar `PUT /app-behaviors/embedded-auth` |
| `client.network_error` | 0 | Casi siempre CORS: Community, proxy o cabeceras `X-Accounts-*` filtradas |
| `client.popup_blocked` / `popup_closed` / `popup_timeout` | 0 | Permitir popups / reintentar |
| `client.magic_link_other_browser` | 0 | Abrir el enlace en el navegador donde se pidió |
| `client.crypto_unavailable` | 0 | El navegador no tiene WebCrypto |
| `client.mfa_required` / `client.mfa_enrollment_required` | — | No es un fallo: `MfaRequiredError` con `challenge` → `Accounts.mfa.*` (los componentes lo hacen solos) |
| `mfa.invalid_code` / `mfa.invalid_token` / `mfa.too_many_attempts` | 401/401/429 | Ver [mfa.md](mfa.md) |

## Fuera de alcance (v1)

Sin rate limiting en el gate, sin modo cookie (refresh en `HttpOnly`), sin wrappers React/Vue ni npm, sin fallback de redirección si el popup se bloquea. Reset requiere códigos de 6 caracteres (contrato de `/reset`). El magic link embebido solo se canjea en el mismo navegador donde se pidió.

## Anti-patrones

- Mandar `X-API-Key` o `Authorization` desde el navegador "para ayudar" al componente.
- Poner la secret key en la página o llamar a `public-key-jwt` desde el navegador.
- Registrar `https://miapp.com/` con ruta en `allowed_origins`, o comodines.
- Registrar la `redirect_url` con query cuando el componente manda `origin + pathname`.
- Guardar el access token en tu propio storage: pídelo con `Accounts.getToken()` antes de cada llamada.
- Servir la página con `Cross-Origin-Opener-Policy: same-origin` y esperar que funcione OAuth.
