# Session API & Custom Login UI

## Session API: Progressive Authentication Model

The Session API (`SessionService`) is the foundation for custom login UIs. Sessions are created and progressively updated with "checks" (authentication factors) and "challenges" (factor requests). Each create/update returns a `sessionId` and opaque `sessionToken` — always use the latest token.

**Checks** (verify a factor):
- `user` — `{ "loginName": "..." }` or `{ "userId": "..." }`
- `password` — `{ "password": "..." }`
- `totp` — `{ "code": "123456" }`
- `otpSms` — `{ "code": "..." }`
- `otpEmail` — `{ "code": "..." }`
- `webAuthN` — `{ "credentialAssertionData": {...} }` (passkey/U2F response)
- `idpIntent` — `{ "idpIntentId": "...", "idpIntentToken": "..." }`

**Challenges** (request a factor):
- `webAuthN` — `{ "domain": "login.example.com", "userVerificationRequirement": "..." }` — returns `publicKeyCredentialRequestOptions`
- `otpSms` — `{ "returnCode": false }` — triggers SMS (or returns code if `true`)
- `otpEmail` — `{ "returnCode": false }` — triggers email (or returns code if `true`)

Multiple checks can be combined in one request. Sessions track which factors are verified and when (`factors.{type}.verifiedAt`).

## Session Lifetime and Expiration

```json
{ "lifetime": "18000.000000000s" }
```
Each update with `lifetime` recalculates `expirationDate` from that point. Sessions without `lifetime` never expire. Expired sessions are automatically rejected.

## Login V2 Activation Methods

1. **Per-application**: Enable in app settings in Console, optionally set custom base URL
2. **Instance-wide**: Enable `loginV2` feature via `FeatureService.SetInstanceFeatures`

On Zitadel Cloud, empty base URL defaults to `${CUSTOM_DOMAIN}/ui/v2/login`.

## Login V2 Custom Text

**Cannot** be customized through Management Console. Use Settings V2 API:
```
PUT /v2/settings/hosted_login/translation
```
Reference keys from `apps/login/locales/en.json` in the Zitadel repo. Send only override keys — Login V2 merges with defaults.

## Login V2 Known Limitations

- Generic JWT IDP
- LDAP IDP
- Device Authorization Grants
- Force MFA on externally authenticated users
- Passkey/U2F setup (domain-bound — if login runs on different domain than Console, passkeys won't work across both; use a subdomain like `login.myinstance.zitadel.cloud`)

## Login V2 Self-Hosted Deployment

1. Create service account with PAT
2. Grant `IAM_LOGIN_CLIENT` role (instance-level)
3. Set env vars: `PAT`, `ZITADEL_API_URL` (no trailing slash)
4. Add login UI domain to **Trusted Domains**
5. External IdP redirect URL: `${CUSTOM_DOMAIN}/idps/callback`
6. Optional: `EMAIL_VERIFICATION=true`

## OIDC Proxy Architecture for Custom Login

The custom Login app acts as an OIDC proxy. Middleware rewrites `/.well-known/*`, `/oauth/*`, `/oidc/*` to Zitadel backend. Required proxy headers:
- `x-zitadel-public-host` — host of your login UI
- `x-zitadel-instance-host` — host of your Zitadel instance

Login domain must be a **Trusted Domain** and use HTTPS.

## Login App Service Account

Authenticates using PAT with `IAM_LOGIN_CLIENT` role. Required for:
- Reading instance/org policies and settings
- Finalizing auth requests (`CreateCallback`, `CreateResponse`)
- Finalizing device authorization requests

Env vars: `ZITADEL_API_URL`, `ZITADEL_SERVICE_USER_ID`, `ZITADEL_SERVICE_USER_TOKEN`.

## OIDCService V2: Custom Login Flow

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /v2/oidc/auth_requests/{id}` | GetAuthRequest | Retrieve parsed auth request |
| `POST /v2/oidc/auth_requests/{id}` | CreateCallback | Finalize with session → returns `callbackUrl` |
| `GET /v2/oidc/device_authorization/{userCode}` | GetDeviceAuthorizationRequest | Get device auth by user code |
| `POST /v2/oidc/device_authorization/{id}` | AuthorizeOrDenyDeviceAuthorization | Approve/deny device auth |

**OIDC flow**: app → `login.example.com/oauth/v2/authorize` (proxied) → Zitadel redirects to `login.example.com/login?authRequest=V2_{id}` → login UI fetches auth request → authenticates via Session API → `CreateCallback` → redirects to app's `callbackUrl`.

## SAMLService V2: Custom Login SAML Flow

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /v2/saml/saml_requests/{id}` | GetSAMLRequest | Retrieve parsed SAML request |
| `POST /v2/saml/saml_requests/{id}` | CreateResponse | Finalize with session |

CreateResponse returns:
- **POST binding**: `{ "url": "...", "binding": { "post": { "relayState": "...", "samlResponse": "base64..." } } }`
- **Redirect binding**: `{ "url": "...?RelayState=...&SAMLResponse=...", "binding": { "redirect": {} } }`

## IdP Intent Flow (External Login)

1. **Start**: `POST /v2/idp_intents` with `{ "idpId": "...", "urls": { "successUrl": "...", "failureUrl": "..." } }` → returns `authUrl`
2. **User authenticates** → callback at `/idps/callback` (V2) or `/ui/login/login/externalidp/callback` (V1) → redirects to success/failure URL with `intentID`, `token`, `userID`
3. **Retrieve**: `POST /v2/idp_intents/{intentId}` with token → returns provider info

Then either:
- **Login**: Session with `idpIntent` check
- **Register**: `POST /v2/users/human` with `idpLinks: [{ idpId, userId, userName }]`
- **Link**: `POST /v2/users/users/{userId}/links` with `{ "idpLink": { idpId, userId, userName } }`

## WebAuthN: U2F vs Passkey

The `webAuthN` challenge is used for both. The difference is `userVerificationRequirement`:
- **Passkey**: `USER_VERIFICATION_REQUIREMENT_REQUIRED` — user must provide PIN/biometric
- **U2F**: `USER_VERIFICATION_REQUIREMENT_DISCOURAGED` — no PIN required

## Passkey Registration

Two paths:
1. **Link-based** (any device): `POST /v2/users/{userId}/passkeys/registration_link` with `sendLink` or `returnCode`. URL template supports `{{.UserID}}`, `{{.OrgID}}`, `{{.CodeID}}`, `{{.Code}}`.
2. **Direct** (current device): `POST /v2/users/{userId}/passkeys` → returns `publicKeyCredentialCreationOptions`.

Verify: `POST /v2/users/{userId}/passkeys/{passkeyId}` with `publicKeyCredential` and `passkeyName`.

## Email Link Scanner Protection

Enterprise email scanners pre-fetch URLs and consume one-time codes. Automatic code submission on page load is **disabled by default**. Enable with `NEXT_PUBLIC_AUTO_SUBMIT_CODE=true` if scanners are not a concern.
