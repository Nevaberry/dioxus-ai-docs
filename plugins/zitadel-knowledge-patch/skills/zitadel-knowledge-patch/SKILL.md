---
name: zitadel-knowledge-patch
description: "Zitadel IAM changes since training cutoff (latest: v4.13) — V2 ConnectRPC APIs, Actions V2 webhooks, Session API custom login, Login V2 Next.js, token exchange GA, new language SDKs. Load before working with Zitadel."
version: "4.13"
license: MIT
metadata:
  author: Nevaberry
---

# Zitadel v3+ Knowledge Patch

Claude's baseline knowledge covers Zitadel v2.x: basic OIDC/OAuth2, gRPC API v1, and event sourcing architecture. This patch covers v3.0 through v4.13 — the complete API v2 migration, Actions V2, Login V2, and new SDK ecosystem.

## Index

| Topic | Reference | Key Content |
|-------|-----------|-------------|
| Version History | [version-history.md](references/version-history.md) | v3→v4 breaking changes, V2 API GA timeline, v5 preview |
| OIDC & OAuth2 | [oidc-oauth2.md](references/oidc-oauth2.md) | Reserved scopes, claims, grant types, key formats, logout |
| Actions V1 | [actions-v1.md](references/actions-v1.md) | JavaScript flows, triggers, built-in modules, setClaim gotchas |
| Actions V2 | [actions-v2.md](references/actions-v2.md) | Targets, executions, payloads, JWT/JWE signing, error forwarding |
| Session API & Login | [session-api-custom-login.md](references/session-api-custom-login.md) | Session checks/challenges, OIDC proxy, Login V2, passkeys |
| Identity Providers | [identity-providers.md](references/identity-providers.md) | 15+ IdP types, LDAP, JWT IdP, SAML, org-level scoping |
| API & Services | [api-services.md](references/api-services.md) | V2 service catalog, ConnectRPC, RBAC roles, event API |
| Self-Hosting | [self-hosting.md](references/self-hosting.md) | v4 architecture, Helm, Docker, caching, DB schema, quotas |
| Migration | [migration.md](references/migration.md) | Import/export, password hashes, JIT patterns, zitadel-tools |
| SDKs & Terraform | [sdks-terraform.md](references/sdks-terraform.md) | Go SDK v3, new language SDKs, OIDC lib, Terraform v2.11 |

---

## V2 API Service Catalog (Quick Reference)

All v2 APIs use gRPC with ConnectRPC. HTTP/JSON available via `/v2/` prefix.

| Service | gRPC Path Prefix |
|---------|-----------------|
| UserService | `/zitadel.user.v2.UserService/` |
| SessionService | `/zitadel.session.v2.SessionService/` |
| OrganizationService | `/zitadel.org.v2.OrganizationService/` |
| InstanceService | `/zitadel.instance.v2.InstanceService/` |
| ProjectService | `/zitadel.project.v2.ProjectService/` |
| ApplicationService | `/zitadel.application.v2.ApplicationService/` |
| IdentityProviderService | `/zitadel.idp.v2.IdentityProviderService/` |
| GroupService | `/zitadel.group.v2.GroupService/` |
| SettingsService | `/zitadel.settings.v2.SettingsService/` |
| FeatureService | `/zitadel.feature.v2.FeatureService/` |
| AuthorizationService | `/zitadel.authorization.v2.AuthorizationService/` |
| ActionService | `/zitadel.action.v2.ActionService/` |
| WebKeyService | `/zitadel.webkey.v2.WebKeyService/` |
| OIDCService | `/zitadel.oidc.v2.OIDCService/` |
| SAMLService | `/zitadel.saml.v2.SAMLService/` |

## Zitadel Reserved Scopes (Quick Reference)

| Scope | Purpose |
|-------|---------|
| `urn:zitadel:iam:org:project:role:{rolekey}` | Request specific role claim |
| `urn:zitadel:iam:org:projects:roles` | Roles for ALL audience projects |
| `urn:zitadel:iam:org:id:{id}` | Enforce org membership by ID |
| `urn:zitadel:iam:org:domain:primary:{domain}` | Enforce org by domain; show org branding/IdPs |
| `urn:zitadel:iam:org:project:id:{projectid}:aud` | Add project to token audience |
| `urn:zitadel:iam:org:project:id:zitadel:aud` | Required for calling Zitadel APIs with user tokens |
| `urn:zitadel:iam:user:metadata` | Include user metadata (base64 encoded) |
| `urn:zitadel:iam:user:resourceowner` | Include user's org info in token |
| `urn:zitadel:iam:org:idp:id:{idp_id}` | Skip login UI, redirect to IdP |
| `urn:zitadel:iam:org:roles:id:{orgID}` | Filter roles to specific org IDs |

## Critical Gotchas

### Token Introspection Requires Audience Scope
For introspection to return `active: true`, the token **must** have been requested with `urn:zitadel:iam:org:project:id:{projectid}:aud`. Without it, introspection returns `active: false`.

### ID Token Missing Claims When Access Token Present
When `response_type=code`, the `id_token` does **NOT** contain profile/email/phone/address claims (per OIDC Core spec). Use userinfo or introspection endpoint. Override with `id_token_userinfo_assertion` app setting.

### setClaim() Does NOT Overwrite (Actions V1)
`setClaim(key, value)` silently logs instead of overwriting if the key exists. Keys with `urn:zitadel:iam` prefix are silently ignored.

### Actions V2 Feature Flag: Executions Always Run
Toggling the Actions feature flag off does NOT stop running executions. The only way to stop an execution is to delete it.

### Service Accounts Default to Opaque Tokens
Service accounts get opaque tokens by default, not JWTs. Change in account settings if local JWT validation is needed.

## v5 Breaking Changes Preview

**Actions V1 removed** — migrate to Actions V2 (targets + executions).
**Login V1 removed** — Login V2 (Next.js/Session API) becomes the only option.
**All V1 APIs removed** — migrate to V2 resource-based APIs.

Any code using V1 Management/Admin/Auth APIs, Actions V1, or Login V1 templates **must migrate before v5**.

## V4 Terminology Renames

| Old Term (V1 APIs) | New Term (V2 APIs) |
|---------------------|-------------------|
| User Grant / Authorization | **Role Assignment** |
| Members / Memberships | **Administrators** |
| IAM | **Instance** |

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

## Key JSON Formats

**Application key** (`private_key_jwt` client auth) — JWT uses `clientId` as `iss`/`sub`:
```json
{ "type": "application", "keyId": "...", "key": "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----", "clientId": "78366401571920522@acme", "appId": "..." }
```

**Service account key** (JWT profile grant) — JWT uses `userId` as `iss`/`sub`:
```json
{ "type": "serviceaccount", "keyId": "...", "key": "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----", "userId": "78366401571647008" }
```

Both require `kid` = `keyId` in JWT header. See [oidc-oauth2.md](references/oidc-oauth2.md) for full details.

## Actions V2 Target Types (Quick Reference)

| Type | API Field | Behavior |
|------|-----------|----------|
| **Webhook** | `restWebhook` | Fire-and-forget — status checked, response body ignored |
| **Call** | `restCall` | Status AND response processed — enables request/response manipulation |
| **Async** | `restAsync` | Neither checked — runs in parallel |

All support `interruptOnError: true`. See [actions-v2.md](references/actions-v2.md) for payloads and signing.

## Session API Checks (Quick Reference)

The Session API (`SessionService`) uses progressive authentication with checks and challenges:

| Check | Field | Value |
|-------|-------|-------|
| User | `user` | `{ "loginName": "..." }` or `{ "userId": "..." }` |
| Password | `password` | `{ "password": "..." }` |
| TOTP | `totp` | `{ "code": "123456" }` |
| OTP SMS | `otpSms` | `{ "code": "..." }` |
| OTP Email | `otpEmail` | `{ "code": "..." }` |
| WebAuthN | `webAuthN` | `{ "credentialAssertionData": {...} }` |
| IdP Intent | `idpIntent` | `{ "idpIntentId": "...", "idpIntentToken": "..." }` |

Multiple checks can be combined in one request. See [session-api-custom-login.md](references/session-api-custom-login.md) for challenges and full flow.

## RBAC Roles (Quick Reference)

**Instance-level:** `IAM_OWNER` (full), `IAM_OWNER_VIEWER` (read-only), `IAM_ORG_MANAGER`, `IAM_USER_MANAGER`, `IAM_ADMIN_IMPERSONATOR`, `IAM_END_USER_IMPERSONATOR`, `IAM_LOGIN_CLIENT` (custom login UI).

**Organization-level:** `ORG_OWNER`, `ORG_USER_MANAGER`, `ORG_USER_PERMISSION_EDITOR`, `ORG_PROJECT_PERMISSION_EDITOR`, `ORG_PROJECT_CREATOR`.

See [api-services.md](references/api-services.md) for full RBAC reference.

## Single Domain Architecture

Everything runs under one domain (`{instance}.zitadel.cloud` or custom) — OIDC issuer, all APIs, Console, and Login UI. "Instance not found" errors typically mean the domain isn't configured correctly.

**UI paths:** `/ui/console/` (admin), `/ui/v2/login` (Login V2, Next.js), `/ui/login/` (Login V1, legacy).

**Debug endpoints:** `/debug/ready` (readiness), `/debug/healthz` (liveness), `/debug/metrics` (Prometheus).

## V2 API GA Promotion Timeline

| Version | Service Promoted to GA |
|---------|----------------------|
| v4.0 | Actions V2, Caches V2 |
| v4.5 | Application Service, Permission Service |
| v4.6 | Project Service, Authorization Service, Instance Service |
| v4.7 | Organization API |
| v4.11 | Token Exchange, Back-Channel Logout |
| v4.13 | WebKeys V2 |

When targeting a specific version, check whether the V2 API you need is GA or still v2beta.

## SDK Quick Reference

| Language | Package | Auth Methods |
|----------|---------|-------------|
| Go | `github.com/zitadel/zitadel-go/v3` (v3.28.0) | JWT Profile, Client Credentials, PAT |
| .NET | `Zitadel.Api` (NuGet) | PAT, Service Account JWT |
| Python | `zitadel-client` (pip, beta) | Private Key JWT, Client Credentials, PAT |
| Java | `io.github.zitadel:client` (Maven, beta) | Private Key JWT, Client Credentials, PAT |
| Node.js | `@zitadel/zitadel-node` (GitHub Packages) | Private Key JWT, Client Credentials, PAT |
| PHP | `zitadel/client` (Composer, beta) | Private Key JWT, Client Credentials, PAT |
| Ruby | `zitadel-client` (gem, beta) | Private Key JWT, Client Credentials, PAT |

Terraform provider: `zitadel/zitadel` v2.11.0. See [sdks-terraform.md](references/sdks-terraform.md) for code examples.

---

See [version-history.md](references/version-history.md) for the complete v3→v4 changelog.
