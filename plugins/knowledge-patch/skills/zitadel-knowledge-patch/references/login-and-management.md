# Login and management

- [Cloud egress allowlisting](#cloud-egress-allowlisting)
- [Administrator memberships and custom roles](#administrator-memberships-and-custom-roles)
- [Application redirect and token settings](#application-redirect-and-token-settings)
- [Login V2 selection precedence](#login-v2-selection-precedence)
- [Settings inheritance and login discovery](#settings-inheritance-and-login-discovery)
- [Authentication recency and lockout policy](#authentication-recency-and-lockout-policy)
- [Organization user and domain invariants](#organization-user-and-domain-invariants)
- [Project grants and authentication gates](#project-grants-and-authentication-gates)
- [Project-controlled branding](#project-controlled-branding)
- [Notification-provider activation and payloads](#notification-provider-activation-and-payloads)
- [Feature-restriction effects](#feature-restriction-effects)
- [SCIM provisioning domains](#scim-provisioning-domains)
- [SCIM contact and attribute mapping](#scim-contact-and-attribute-mapping)
- [User creation and verification delivery](#user-creation-and-verification-delivery)
- [Web Key algorithms and creation defaults](#web-key-algorithms-and-creation-defaults)
- [Safe Web Key rotation](#safe-web-key-rotation)
- [Self-hosted Login proxy contract](#self-hosted-login-proxy-contract)
- [Session state and lifetime contract](#session-state-and-lifetime-contract)
- [OIDC handoff from a custom Login UI](#oidc-handoff-from-a-custom-login-ui)
- [SAML handoff from a custom Login UI](#saml-handoff-from-a-custom-login-ui)
- [Device authorization in a custom Login UI](#device-authorization-in-a-custom-login-ui)
- [External identity-provider intents](#external-identity-provider-intents)
- [MFA enrollment and Session API challenges](#mfa-enrollment-and-session-api-challenges)
- [Passkey registration and login](#passkey-registration-and-login)
- [Password reset and password change](#password-reset-and-password-change)

## Cloud egress allowlisting

ZITADEL Cloud uses region-specific static source addresses for outbound LDAP, OIDC/OAuth, SAML, SMTP, HTTP-provider, and Action traffic. Allowlist only the address for the instance's region:

```text
Switzerland    34.65.158.196
Europe         34.107.19.72
United States  34.69.146.246
Australia      34.87.243.23
```

## Administrator memberships and custom roles

Administrative rights are memberships on an instance, organization, project, or granted project, separate from application roles; `IAM_LOGIN_CLIENT` is the narrowly named instance role for a custom Login UI. Self-hosters can replace the built-in role-to-permission mappings under `InternalAuthZ`.

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

## Application redirect and token settings

An application's type cannot be changed after creation, and outside Development Mode redirect URIs must match exactly and use HTTPS. Development Mode permits insecure redirects and glob terms `*`, `/**/`, `?`, `[class]`, and `{alt1,alt2}`, with `**` required between path separators and IPv6 brackets escaped as in `http://\[::1\]:80`. Per-application settings also select opaque versus JWT access tokens, user roles or user information in the ID token, clock skew, and additional CORS origins.

## Login V2 selection precedence

The per-application **Use new login UI** switch matters only while the instance Login V2 feature is disabled; the instance feature forces every application onto V2, while an empty custom base URL selects the built-in `/ui/v2/login`. A custom base URL can point either mode at a separately hosted Login UI.

## Settings inheritance and login discovery

Instance settings are defaults that organizations can override, and feature values are `Enabled`, `Disabled`, or `Inherit`. Login policy can independently disable email or phone login, route an unknown login name to an organization's IdP through domain discovery, or defer unknown-user disclosure until the password step. When auth-request context is missing, the default redirect URI is used and initially points to `/ui/console/`.

## Authentication recency and lockout policy

Login policy has separate lifetimes for password checks, external-login checks, MFA initialization, second-factor checks, and multifactor login checks; an MFA-init lifetime of zero suppresses the setup prompt, and MFA enforcement can be limited to locally authenticated users. Password and `(T)OTP` lockouts have independent attempt maxima where zero disables lockout and an administrator must unlock the account, while password expiry does not itself send the configured advance warning.

## Organization user and domain invariants

A user belongs to exactly one organization and cannot be moved, the same email may identify users in different organizations, and a verified domain can belong to only one organization. Without login-name suffixing usernames are instance-global; with suffixing, verified domains add login aliases and the primary organization domain controls the displayed login and `preferred_username`, while claiming a domain can rename a conflicting global user's login and DNS verification records must remain for periodic rechecks.

## Project grants and authentication gates

All applications in a project share its roles. A project grant exposes only selected roles to another organization, whose administrators can assign those roles to their own users but cannot view or change application settings. Project policy can require any role assignment, require the user's organization to have a project grant, or assert roles. Do not repurpose the automatically created `ZITADEL` project because it protects Console and the APIs.

## Project-controlled branding

Project branding mode can use instance defaults, enforce the project-owning organization's policy for the whole login, or start with project branding and switch to the discovered user's organization. The last mode is the usual private-label B2B behavior because a granted organization's users retain their own login policy and branding after discovery.

## Notification-provider activation and payloads

Multiple SMTP, SMS, or HTTP providers may be configured per channel, but only the active provider delivers messages. SMTP supports plain, XOAUTH/XOAuth2, and unauthenticated configurations; OAuth settings are exposed in Console. HTTP providers are created and activated separately and receive the resolved content rather than only a template identifier.

```text
POST /admin/v1/sms/http                 POST /admin/v1/email/http
POST /admin/v1/sms/{id}/_activate       POST /admin/v1/email/{id}/_activate
payload = { contextInfo, templateData, args }
```

## Feature-restriction effects

When public organization registration is restricted, `GET /ui/login/register/org` returns 404 and its POST returns 409. `AllowedLanguages` also filters discovery's `ui_locales_supported`, Login rendering, and notification rendering, although custom texts may be prepared for a supported but currently disallowed language before enabling it.

## SCIM provisioning domains

Set `urn:zitadel:scim:provisioningDomain` as service-account metadata to isolate one provisioner's `externalId` values from another. ZITADEL stores the value at the namespaced metadata key, falling back to the unscoped key when the service account has no provisioning domain.

```text
service-account metadata: urn:zitadel:scim:provisioningDomain = customer-a
user metadata:            urn:zitadel:scim:customer-a:externalId = upstream-123
fallback:                 urn:zitadel:scim:externalId = upstream-123
```

## SCIM contact and attribute mapping

Only the primary SCIM email and phone are stored, both are considered verified by default, and `displayName` wins over `name.formatted`; `name.givenName`, `name.familyName`, and at least one email are additionally required. Attributes without native fields are stored under `urn:zitadel:scim:*` user metadata, with multivalued structures serialized as JSON. Configure the verification defaults with `SCIM.EmailVerified` and `SCIM.PhoneVerified`.

## User creation and verification delivery

`POST /v2/users/human` can atomically accept a caller-chosen user ID, profile, password plus `changeRequired`, and email; mark the email verified or choose `sendCode` with a URL template versus `returnCode` for custom delivery. A registration UI should read `SettingsService.GetLoginSettings` and `GetPasswordComplexitySettings` rather than hard-code the enabled methods or password rules.

```json
{"userId":"<id>","username":"ada","email":{"email":"ada@example.com","returnCode":{}},"password":{"password":"...","changeRequired":false}}
```

## Web Key algorithms and creation defaults

`POST /v2/web_keys` with `{}` generates RSA-2048 with SHA-256 (`RS256`); generator settings also support RSA-3072/4096 with SHA-384/512, ECDSA for `ES256`/`ES384`/`ES512`, and Ed25519 reported as `EdDSA`. Ed25519 is the only supported EdDSA curve, so verifiers must support its SHA-512 behavior and inspect `crv` rather than infer the curve from `alg` alone.

## Safe Web Key rotation

Only one Web Key is active, activation deactivates the previous key, and initial plus inactive public keys remain in JWKS. Only non-active keys can be deleted, and deletion immediately invalidates tokens and long-lived `id_token_hint` values signed by that key. Create the next key first, wait at least the JWKS cache age plus client refresh time, activate it, and retain the old key through relevant token and hint lifetimes.

```text
POST   /v2/web_keys
POST   /v2/web_keys/{next-id}/_activate
DELETE /v2/web_keys/{retired-id}
```

JWKS responses default to `Cache-Control: max-age=300, must-revalidate`; self-hosters set `OIDC.JWKSCacheControlMaxAge` or `ZITADEL_OIDC_JWKSCACHECONTROLMAXAGE`, with zero producing `no-store`.

## Self-hosted Login proxy contract

A custom Login backend needs a service-account PAT with `IAM_LOGIN_CLIENT`, HTTPS, and its host registered as an instance trusted domain; its proxy forwards `/.well-known/*`, `/oauth/*`, and `/oidc/*` while identifying both public and instance hosts. The reference Login does not auto-submit one-time codes on page load to avoid email-link scanners consuming them, with `NEXT_PUBLIC_AUTO_SUBMIT_CODE=true` as the explicit opt-in.

```http
x-zitadel-public-host: login.example.com
x-zitadel-instance-host: tenant.zitadel.cloud
```

## Session state and lifetime contract

A Session API session accumulates checked factors with `verifiedAt` timestamps, but the client must decide which factors and recency are sufficient. Every create or update can return a replacement opaque session token, so retain only the latest token. Supplying `lifetime` recalculates expiration from each update, omitting it creates a non-expiring session, and an expired session is rejected and cannot be updated. A session token is not an OAuth access token and cannot be introspected as one.

```json
{"checks":{"user":{"loginName":"ada@example.com"}},"lifetime":"18000.000000000s"}
```

## OIDC handoff from a custom Login UI

Proxy the authorization request, load the resulting ID with `GET /v2/oidc/auth_requests/{id}`, perform the required Session API checks, then use an `IAM_LOGIN_CLIENT` credential to POST the latest session ID and token to that auth-request resource. Use the response's `callbackUrl` for the browser redirect. The custom host must also proxy token, userinfo, introspection, discovery, and end-session endpoints.

```json
POST /v2/oidc/auth_requests/{id}
{"session":{"sessionId":"<session-id>","sessionToken":"<latest-token>"}}
```

## SAML handoff from a custom Login UI

The equivalent SAML bridge loads `GET /v2/saml/saml_requests/{id}` and POSTs the latest session to the same resource after authentication. Its result is binding-specific: redirect binding supplies a completed URL, while POST binding supplies the ACS URL plus `RelayState` and `SAMLResponse` fields that the browser must form-post.

## Device authorization in a custom Login UI

Proxy `/oauth/v2/device_authorization`, present its `verification_uri` and code, then load `GET /v2/oidc/device_authorization/{user_code}` and authenticate a session. POST that session or a denial to `/v2/oidc/device_authorization/{request-id}` so the device's token polling can complete.

## External identity-provider intents

Start an external login with `POST /v2/idp_intents` using the provider ID and success/failure URLs, follow the returned provider URL, then retrieve the result with `POST /v2/idp_intents/{intent-id}` and its one-time intent token. A returned linked user ID can be checked together with `idpIntent` when creating a session; otherwise use the returned external subject to create a user with `idpLinks` or explicitly add a link to an authenticated existing user.

## MFA enrollment and Session API challenges

TOTP enrollment uses `/v2/users/{id}/totp` followed by `/verify`; SMS OTP requires a verified phone before `/otp_sms`, while email OTP uses the already verified email before `/otp_email`. For authentication, create a checked-user session with an `otpSms` or `otpEmail` challenge (`returnCode: false` sends it and `true` returns it), then PATCH the session with the matching code check.

```json
{"checks":{"user":{"loginName":"ada@example.com"}},"challenges":{"otpEmail":{"returnCode":false}}}
```

```json
{"checks":{"otpEmail":{"code":"323764"}}}
```

## Passkey registration and login

Passkey enrollment can first create `/v2/users/{id}/passkeys/registration_link` with either a sent link template or returned code, then start `/passkeys` with the optional code and platform, cross-platform, or unrestricted authenticator choice before verifying the browser credential at `/passkeys/{passkey-id}`. Login creates a checked-user session with a `webAuthN` challenge whose domain is the Login UI's relying-party domain and whose verification requirement is `REQUIRED`, then PATCHes the browser assertion into that session. Moving Login to an unrelated domain therefore strands existing domain-bound credentials.

```json
{"checks":{"user":{"loginName":"ada@example.com"}},"challenges":{"webAuthN":{"domain":"login.example.com","userVerificationRequirement":"USER_VERIFICATION_REQUIREMENT_REQUIRED"}}}
```

## Password reset and password change

`POST /v2/users/{id}/password_reset` accepts either `sendLink` with a customizable URL template or `returnCode` for delivery by the caller. Complete the reset with `POST /v2/users/{id}/password`, passing `newPassword` and `verificationCode`; the same operation performs an authenticated password change when the current password is supplied instead.

```json
{"newPassword":{"password":"<new-password>","changeRequired":false},"verificationCode":"<code>"}
```
