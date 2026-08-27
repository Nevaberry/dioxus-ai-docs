# Login and management

## Allow outbound traffic from Cloud

Cloud instances use region-specific static source addresses for outbound LDAP, OIDC/OAuth, SAML, SMTP, HTTP-provider, and Action traffic. Allowlist only the address for the instance region:

```text
Switzerland   34.65.158.196
Europe        34.107.19.72
United States 34.69.146.246
Australia     34.87.243.23
```

## Model administration and projects

### Assign administrator memberships, not application roles

Administrative rights are memberships on an instance, organization, project, or granted project. They are separate from application roles. `IAM_LOGIN_CLIENT` is the narrowly scoped instance role for a custom Login UI. Self-hosters can replace built-in role-to-permission mappings under `InternalAuthZ`.

```text
instance: IAM_OWNER, IAM_OWNER_VIEWER, IAM_ORG_MANAGER, IAM_USER_MANAGER,
          IAM_ADMIN_IMPERSONATOR, IAM_END_USER_IMPERSONATOR, IAM_LOGIN_CLIENT
organization: ORG_OWNER, ORG_OWNER_VIEWER, ORG_USER_MANAGER,
              ORG_USER_PERMISSION_EDITOR, ORG_PROJECT_PERMISSION_EDITOR,
              ORG_PROJECT_CREATOR, ORG_ADMIN_IMPERSONATOR, ORG_END_USER_IMPERSONATOR
project: PROJECT_OWNER, PROJECT_OWNER_VIEWER, PROJECT_OWNER_GLOBAL,
         PROJECT_OWNER_VIEWER_GLOBAL
granted project: PROJECT_GRANT_OWNER
```

```yaml
InternalAuthZ:
  RolePermissionMappings:
    - Role: IAM_OWNER
      Permissions: [iam.read, iam.write]
```

### Respect organization and domain invariants

A user belongs to exactly one organization and cannot be moved. The same email can identify users in different organizations; a verified domain belongs to only one organization. Without login-name suffixing, usernames are instance-global. With suffixing, verified domains add aliases and the primary domain controls displayed login and `preferred_username`. Claiming a domain can rename a conflicting global user's login. Keep DNS verification records because ZITADEL periodically rechecks them.

### Distinguish projects, grants, and gates

All applications in a project share its roles. A project grant exposes selected roles to another organization, whose administrators can assign them but cannot view or change application settings. Project policy can require any role assignment, require the user's organization to hold a grant, or assert roles. Do not repurpose the automatically created `ZITADEL` project; it protects Console and API access.

Project creation can include members. User-grant listing can filter multiple users with `InUserIDs`, and current role-assignment updates correctly remove adjacent roles.

### Choose project-controlled branding

Branding can use instance defaults, force the project-owning organization's policy for the whole login, or start with project branding and switch to the discovered user's organization. The last mode is the usual private-label B2B choice because a granted organization's users retain their own policy and branding after discovery.

## Configure applications and Login selection

### Set redirects and token behavior

Application type is immutable. Outside Development Mode, redirect URIs must match exactly and use HTTPS. Development Mode permits insecure redirects and glob terms `*`, `/**/`, `?`, `[class]`, and `{alt1,alt2}`; `**` is required between path separators and IPv6 brackets must be escaped, for example `http://\[::1\]:80`. Native applications also support HTTPS loopback addresses, bare `http://localhost`, and current native custom protocol schemes.

Per-application settings choose opaque or JWT access tokens, roles or user information in ID tokens, clock skew, and CORS origins. Applications can be looked up by OIDC client ID or SAML entity ID. Caller-provided OIDC application IDs are honored.

### Resolve Login V2 precedence

The per-application **Use new login UI** switch matters only while the instance Login V2 feature is disabled. The instance feature forces all applications onto V2; an empty custom base URL chooses built-in `/ui/v2/login`. A custom base URL can point either mode at a separately hosted UI. Login V2 is the default for new customers.

### Apply inherited settings and discovery

Instance settings are organization defaults. Feature values are `Enabled`, `Disabled`, or `Inherit`. Login policy can disable email or phone login, use domain discovery to route an unknown login name to an organization IdP, or defer unknown-user disclosure until the password step. Without auth-request context, the default redirect URI is used and initially points to `/ui/console/`.

`allowUsernamePassword` has been renamed `allowLocalAuthentication`; the Login UI must also respect password-complexity settings. Primary authentication methods are checked during user discovery, and identity-provider registration flows no longer depend on `loginSettings.allowRegister`.

## Apply authentication policy

### Track recency, expiry, and lockout independently

Login policy has separate lifetimes for password checks, external-login checks, MFA initialization, second-factor checks, and multifactor checks. MFA-init lifetime zero suppresses setup prompts; MFA enforcement can be limited to locally authenticated users. Password and `(T)OTP` lockouts have separate maxima where zero disables lockout and an administrator must unlock the account. Password expiry does not send the configured advance warning by itself.

MFA checks ignore enrolled methods that are not ready. Multi-method session validation accounts for several authentication methods. A user-verified passkey satisfies MFA. If forced MFA exposes no factor, Login falls back to email verification.

### Respect deactivation and enrollment authorization

Login V2 blocks users from deactivated organizations. Require authentication before WebAuthn/U2F and TOTP/OTP enrollment, enforce permission checks before issuing passkey enrollment codes, and require the MFA prompt step before 2FA enrollment.

## Deliver notifications

### Activate one provider per channel

Multiple SMTP, SMS, or HTTP providers can be configured per channel, but only the active provider sends. Generic SMTP in Console supports plain authentication; the API supports XOAUTH2, and current SMTP configurations may use OAuth, passwordless authentication, or no authentication. SMTPUTF8 addresses are accepted.

HTTP providers are created and activated separately and receive resolved content rather than only a template ID.

```text
POST /admin/v1/sms/http                 POST /admin/v1/email/http
POST /admin/v1/sms/{id}/_activate       POST /admin/v1/email/{id}/_activate
payload = { contextInfo, templateData, args }
```

HTTP providers can have signing keys. Avoid duplicate SMTP configurations.

### Understand feature restrictions

When public organization registration is restricted, `GET /ui/login/register/org` returns 404 and POST returns 409. `AllowedLanguages` filters discovery's `ui_locales_supported`, Login rendering, and notifications. Custom text may be prepared for a supported but currently disallowed language before enabling it.

## Provision users with SCIM

### Isolate provisioning domains

Set `urn:zitadel:scim:provisioningDomain` as service-account metadata to isolate one provisioner's `externalId` values. ZITADEL uses a namespaced user-metadata key and falls back to the unscoped key when the service account has no provisioning domain.

```text
service-account metadata: urn:zitadel:scim:provisioningDomain = customer-a
user metadata:            urn:zitadel:scim:customer-a:externalId = upstream-123
fallback:                 urn:zitadel:scim:externalId = upstream-123
```

### Map SCIM contacts and attributes

Only the primary email and phone are stored; both are verified by default. `displayName` wins over `name.formatted`; `name.givenName`, `name.familyName`, and at least one email are required. Other attributes are stored under `urn:zitadel:scim:*` metadata, with multivalued structures serialized as JSON. Configure defaults with `SCIM.EmailVerified` and `SCIM.PhoneVerified`. SCIM email objects expose `type`, and a metadata setting can ignore a random creation password.

## Create users and deliver verification

`POST /v2/users/human` can atomically accept caller-chosen user ID, profile, password with `changeRequired`, and email. Mark email verified, choose `sendCode` with a URL template, or use `returnCode` for custom delivery. Automatic email verification can be disabled. A registration UI should read `SettingsService.GetLoginSettings` and `GetPasswordComplexitySettings` rather than hard-code methods or rules.

```json
{"userId":"<id>","username":"ada","email":{"email":"ada@example.com","returnCode":{}},"password":{"password":"...","changeRequired":false}}
```

Invite delivery sends a code only when email is unverified. Current generators support invite codes, multiple live-code replacement, recovery after all methods are removed, and expiry based on code creation time. Invite and verification resends preserve OIDC or SAML context and reject duplicate verification.

## Manage Web Keys

### Select an algorithm

`POST /v2/web_keys` with `{}` generates RSA-2048/SHA-256 (`RS256`). Generator settings also support RSA-3072/4096 with SHA-384/512, ECDSA `ES256`/`ES384`/`ES512`, and Ed25519 reported as `EdDSA`. Ed25519 is the only EdDSA curve; verifiers must support its SHA-512 behavior and inspect `crv` rather than infer curve from `alg`.

### Rotate without invalidating tokens

Only one Web Key is active; activation deactivates the previous key. Initial and inactive public keys remain in JWKS. Only non-active keys can be deleted, and deletion immediately invalidates tokens and long-lived `id_token_hint` values signed by the key.

1. Create the next key.
2. Wait at least the JWKS cache age plus client refresh time.
3. Activate the next key.
4. Retain the old key through relevant token and hint lifetimes.
5. Delete it only afterward.

```text
POST   /v2/web_keys
POST   /v2/web_keys/{next-id}/_activate
DELETE /v2/web_keys/{retired-id}
```

JWKS defaults to `Cache-Control: max-age=300, must-revalidate`. Self-hosters configure `OIDC.JWKSCacheControlMaxAge` or `ZITADEL_OIDC_JWKSCACHECONTROLMAXAGE`; zero produces `no-store`.

## Build a custom Login UI

### Meet the proxy contract

A custom Login backend needs a service-account PAT with `IAM_LOGIN_CLIENT`, HTTPS, and a trusted instance domain. Proxy `/.well-known/*`, `/oauth/*`, and `/oidc/*`, identifying both public and instance hosts. Custom request headers can be configured by environment and empty values remove a header.

```http
x-zitadel-public-host: login.example.com
x-zitadel-instance-host: tenant.zitadel.cloud
```

The reference Login avoids auto-submitting one-time codes on page load so link scanners do not consume them; `NEXT_PUBLIC_AUTO_SUBMIT_CODE=true` explicitly opts in. Browser OTP flows must not request the code through `returnCode`.

### Preserve session tokens and lifetimes

A Session API session accumulates checked factors with `verifiedAt`; the client decides which factors and recency suffice. Every create or update may return a replacement opaque token, so retain only the latest. Supplying `lifetime` recalculates expiration from every update; omitting it makes a non-expiring session. Expired sessions cannot be updated. A session token is not an OAuth access token and cannot be introspected.

```json
{"checks":{"user":{"loginName":"ada@example.com"}},"lifetime":"18000.000000000s"}
```

### Complete OIDC, SAML, and device requests

For OIDC, proxy authorization, load `GET /v2/oidc/auth_requests/{id}`, complete Session API checks, and use `IAM_LOGIN_CLIENT` to POST the latest session ID and token. Redirect to returned `callbackUrl`; also proxy token, userinfo, introspection, discovery, and end-session endpoints.

```json
{"session":{"sessionId":"<session-id>","sessionToken":"<latest-token>"}}
```

For SAML, load and POST `/v2/saml/saml_requests/{id}`. Redirect binding returns a completed URL; POST binding returns ACS URL, `RelayState`, and `SAMLResponse` for browser form-posting. For device flow, proxy `/oauth/v2/device_authorization`, load `/v2/oidc/device_authorization/{user_code}`, authenticate, then POST the session or denial to `/v2/oidc/device_authorization/{request-id}`.

### Complete an external identity-provider intent

Start with `POST /v2/idp_intents` using provider ID and success/failure URLs, follow the provider URL, then retrieve via `POST /v2/idp_intents/{intent-id}` and its one-use token. The result may include `login_hint` and a refresh token. Check a linked user ID together with `idpIntent` when creating a session; otherwise create a user with `idpLinks` or link an authenticated existing user. Externally authenticated sessions can register passkeys, including native-app links.

### Enroll and check MFA

TOTP enrollment uses `/v2/users/{id}/totp` then `/verify`. SMS OTP needs a verified phone before `/otp_sms`; email OTP uses an already verified email before `/otp_email`. For authentication, create a checked-user session with `otpSms` or `otpEmail` challenge (`returnCode: false` sends; `true` returns), then PATCH the matching code.

```json
{"checks":{"user":{"loginName":"ada@example.com"}},"challenges":{"otpEmail":{"returnCode":false}}}
```

```json
{"checks":{"otpEmail":{"code":"323764"}}}
```

Recovery codes are supported MFA and become active when added. SMS OTP in Login V1 has a country-code selector from version 4.10.1.

### Register and use passkeys

Create `/v2/users/{id}/passkeys/registration_link` with a sent template or returned code, then start `/passkeys` with optional code and platform, cross-platform, or unrestricted authenticator choice. Verify the browser credential at `/passkeys/{passkey-id}`.

For login, create a checked-user session with a `webAuthN` challenge whose domain is the Login UI relying-party domain and verification is `REQUIRED`, then PATCH the browser assertion. Moving Login to an unrelated domain strands existing domain-bound credentials.

```json
{"checks":{"user":{"loginName":"ada@example.com"}},"challenges":{"webAuthN":{"domain":"login.example.com","userVerificationRequirement":"USER_VERIFICATION_REQUIREMENT_REQUIRED"}}}
```

### Reset or change passwords

`POST /v2/users/{id}/password_reset` accepts `sendLink` with URL template or `returnCode`. Complete with `POST /v2/users/{id}/password`, passing `newPassword` and `verificationCode`; supplying current password performs an authenticated change. User deletion or deactivation terminates sessions.

```json
{"newPassword":{"password":"<new-password>","changeRequired":false},"verificationCode":"<code>"}
```
