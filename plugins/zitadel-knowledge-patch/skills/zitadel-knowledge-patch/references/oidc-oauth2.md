# OIDC & OAuth2

## Reserved Scopes (Complete Reference)

| Scope | Purpose |
|-------|---------|
| `urn:zitadel:iam:org:project:role:{rolekey}` | Request specific role in `urn:zitadel:iam:org:project:roles` claim |
| `urn:zitadel:iam:org:projects:roles` | Roles for ALL audience projects (as `urn:zitadel:iam:org:project:{projectid}:roles`) |
| `urn:zitadel:iam:org:id:{id}` | Enforce org membership by ID; shows org branding/IdPs |
| `urn:zitadel:iam:org:domain:primary:{domainname}` | Enforce org by domain; suffix username with domain |
| `urn:zitadel:iam:org:roles:id:{orgID}` | Filter returned roles to specific org IDs (repeatable) |
| `urn:zitadel:iam:org:project:id:{projectid}:aud` | Add project to access token audience |
| `urn:zitadel:iam:org:project:id:zitadel:aud` | Add Zitadel's project to audience (required for Zitadel API calls) |
| `urn:zitadel:iam:user:metadata` | Include user metadata in token (values are **base64 encoded**) |
| `urn:zitadel:iam:user:resourceowner` | Include user's org id, name, and primary_domain in token |
| `urn:zitadel:iam:org:idp:id:{idp_id}` | Skip login UI, redirect directly to specified IdP |

## Roles Claim Structure

Roles nest org info under each role key:
```json
{
  "urn:zitadel:iam:org:project:roles": {
    "admin": {
      "178204173316174381": "acme.ch",
      "209358103284843523": "partner.ch"
    },
    "viewer": {
      "178204173316174381": "acme.ch"
    }
  }
}
```
Each role maps org IDs to primary domains. Use `urn:zitadel:iam:org:roles:id:{orgID}` scope to filter which orgs appear.

## ID Token Claims Gotcha

When an `access_token` is issued alongside the `id_token` (i.e., `response_type=code`), the `id_token` does **NOT** contain `profile`, `email`, `phone`, or `address` claims — per OIDC Core 1.0 spec. Retrieve from `userinfo_endpoint` or `introspection_endpoint`. Override by enabling `id_token_userinfo_assertion` ("User Info inside ID Token" in Console) on the application.

## Key JSON Formats: Application vs Service Account

**Application key** (`private_key_jwt` client auth):
```json
{
  "type": "application",
  "keyId": "81693565968962154",
  "key": "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----",
  "clientId": "78366401571920522@acme",
  "appId": "78366403256846242"
}
```
JWT: `clientId` as both `iss` and `sub`. Header must include `kid` = `keyId`.

**Service account key** (JWT profile grant):
```json
{
  "type": "serviceaccount",
  "keyId": "81693565968772648",
  "key": "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----",
  "userId": "78366401571647008"
}
```
JWT: `userId` as both `iss` and `sub`. Header must include `kid` = `keyId`.

## End Session: `logout_hint` Parameter (Login V2 Only)

The `end_session_endpoint` accepts `logout_hint` (valid login name) to pre-select which user to log out. **Only supported with Login UI V2**.

```
GET ${CUSTOM_DOMAIN}/oidc/v1/end_session
    ?id_token_hint={id_token}
    &post_logout_redirect_uri=https://app.example.com/logged_out
    &state=random_string
```
Must send either `id_token_hint` or `client_id` if `post_logout_redirect_uris` are configured.

## `form_post` Response Mode

Zitadel supports `response_mode=form_post` — serves JavaScript that POSTs response parameters to the `redirect_uri`. Useful for server-side apps that need authorization code via POST.

## Supported Grant Types

| Grant Type | Supported |
|-----------|-----------|
| Authorization Code (+ PKCE) | Yes |
| Client Credentials | Yes |
| Implicit | Yes |
| JWT Profile | Yes |
| Refresh Token | Yes |
| Token Exchange (RFC 8693) | Yes (GA since v4.11) |
| Device Authorization (RFC 8628) | Yes |
| Resource Owner Password | **No** |
| SAML 2.0 Profile | **No** |

## Organization Scope for OIDC Requests

Pre-select an organization:
```
urn:zitadel:iam:org:domain:primary:{domainname}
```
Forces registration to that org and shows its branding + configured IdPs.

## `prompt=create` for Registration

Direct users to registration form instead of login:
```
/oauth/v2/authorize?...&prompt=create&scope=openid urn:zitadel:iam:org:id:{orgId}
```

## Session Cookie Behavior

Zitadel uses a server-side session model with a user-agent cookie. All sessions on the same browser share one cookie. Account Picker shows all previously authenticated accounts. Deleting the cookie loses the session association.

## SAML: SP-Initiated Only

Zitadel supports **only SP-initiated** SAML flow. IdP-initiated SAML is not supported.
- SSO endpoint: `${CUSTOM_DOMAIN}/saml/v2/SSO`
- Metadata: `${CUSTOM_DOMAIN}/saml/v2/metadata`

## Web Keys API: Full Key Lifecycle

Manages OIDC signing keys (JWTs). Lifecycle: create → activate → deactivate → delete.

**Supported algorithms:**
| Generator | Algorithms | Config |
|-----------|-----------|--------|
| RSA | RS256 (default), RS384, RS512 | `bits`: 2048/3072/4096, `hasher`: SHA256/384/512 |
| ECDSA | ES256, ES384, ES512 | `curve`: P256/P384/P512 |
| ED25519 | EdDSA (ed25519 only) | No config needed |

**Key states:** `STATE_INITIAL` → `STATE_ACTIVE` → `STATE_INACTIVE`

**Activation rules:**
- Only one active key per instance
- Activating auto-deactivates previous key
- Delay activation for JWKS cache propagation
- Active keys cannot be deleted; keep deactivated keys until signed tokens expire

**JWKS endpoint:** `${CUSTOM_DOMAIN}/oauth/v2/keys`
```yaml
OIDC:
  JWKSCacheControlMaxAge: 5m # default; set to 0 for no-store
```
Env var: `ZITADEL_OIDC_JWKSCACHECONTROLMAXAGE`

When `web_key` feature is first enabled, two key pairs auto-created with one activated.

## Development Mode Redirect URI Glob Patterns

When dev mode is enabled on an OIDC app:

| Pattern | Meaning |
|---------|---------|
| `*` | Any sequence of non-path-separator characters |
| `/**/` | Zero or more directories |
| `?` | Any single non-path-separator character |
| `[class]` | Character class (e.g., `[a-z]`) |
| `{alt1,...}` | Alternatives |

IPv6 URIs require escaped brackets: `http://\[::1\]:80`. Double stars must be surrounded by path separators.

## Project Authentication Settings

Three project-level settings control auth behavior:

1. **Assert Roles on Authentication**: Include roles in userinfo responses
2. **Check Role Assignment on Authentication**: Deny login if user has NO roles for this project
3. **Check for Project on Authentication**: Deny login if user's org lacks a grant for this project

Critical for B2B access control patterns.
