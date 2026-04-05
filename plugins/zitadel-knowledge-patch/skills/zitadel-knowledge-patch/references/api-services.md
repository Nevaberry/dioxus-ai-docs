# API & Services

## V2 API Service Catalog

All v2 APIs use gRPC with ConnectRPC. HTTP/JSON via REST transcoding at `/v2/` prefix. Legacy `/v2beta/` kept for backward compat.

| Service | gRPC Path Prefix | Purpose |
|---------|-----------------|---------|
| UserService | `/zitadel.user.v2.UserService/` | Manage users and auth methods |
| SessionService | `/zitadel.session.v2.SessionService/` | Create/manage user sessions |
| OrganizationService | `/zitadel.org.v2.OrganizationService/` | Manage organizations |
| InstanceService | `/zitadel.instance.v2.InstanceService/` | Manage Zitadel instance |
| ProjectService | `/zitadel.project.v2.ProjectService/` | Manage projects and grants |
| ApplicationService | `/zitadel.application.v2.ApplicationService/` | Manage OIDC, SAML, API apps |
| IdentityProviderService | `/zitadel.idp.v2.IdentityProviderService/` | Manage identity providers |
| GroupService | `/zitadel.group.v2.GroupService/` | Manage user groups |
| SettingsService | `/zitadel.settings.v2.SettingsService/` | Read login/instance settings |
| FeatureService | `/zitadel.feature.v2.FeatureService/` | Manage feature flags |
| AuthorizationService | `/zitadel.authorization.v2.AuthorizationService/` | Check/manage permissions |
| ActionService | `/zitadel.action.v2.ActionService/` | Manage targets and executions |
| WebKeyService | `/zitadel.webkey.v2.WebKeyService/` | Manage OIDC signing keys |
| OIDCService | `/zitadel.oidc.v2.OIDCService/` | OIDC auth flows (custom login) |
| SAMLService | `/zitadel.saml.v2.SAMLService/` | SAML auth flows (custom login) |

## ConnectRPC Protocol Options

Clients can use:
- **Native gRPC** (HTTP/2, binary protobuf)
- **gRPC-Web** (HTTP/1.1 compatible)
- **Connect protocol** (simple HTTP POST with JSON or protobuf)

Existing v1 gRPC + REST gateway endpoints are unaffected.

## V1 Management API: Organization Targeting

`x-zitadel-orgid` request header determines target organization. Falls back to authenticated user's org if omitted. Essential for service accounts managing resources across multiple orgs.

## Debug Endpoints

| Endpoint | Purpose | Kubernetes Probe |
|----------|---------|-----------------|
| `/debug/ready` | Ready to accept traffic | `readinessProbe` |
| `/debug/healthz` | Process alive | `livenessProbe` |
| `/debug/metrics` | OpenTelemetry metrics (Prometheus) | N/A |

Metrics enabled by default, can be disabled. Helm chart includes `ServiceMonitor` CRD support.

## UI Path Prefixes

- `/ui/console/` — Management Console (Angular admin UI)
- `/ui/v2/login` — Login UI v2 (Next.js, separate container in self-hosted)
- `/ui/login/` — Login UI v1 (legacy, built into Zitadel binary)

## Single Domain Architecture

Everything runs under one domain (`{instance}.zitadel.cloud` or custom). This domain is:
- OIDC issuer
- Base URL for all gRPC and REST APIs
- Console and Login UI host

"Instance not found" errors = domain not configured. See: `https://zitadel.com/docs/self-hosting/manage/custom-domain`

## Service Accounts & Token Introspection

### Terminology
"Service Account" is the official term (replaces "Machine User", "Service User", "Technical Account").

### Opaque Tokens by Default
Service accounts receive **opaque** tokens by default, not JWTs. Change in account settings for local JWT validation.

### Token Introspection: Audience Scope Required
**Critical**: Token must have been requested with `urn:zitadel:iam:org:project:id:{projectid}:aud`. Without it, introspection returns `active: false`.

### Introspection Auth Methods

**1. Private Key JWT (recommended):**
```bash
curl --request POST \
  --url https://$DOMAIN/oauth/v2/introspect \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer \
  --data client_assertion=$SIGNED_JWT \
  --data token=$ACCESS_TOKEN
```
Uses **application key** (type `"application"`) with `clientId` as `iss`/`sub`.

**2. Basic Auth:**
```bash
curl --request POST \
  --url https://$DOMAIN/oauth/v2/introspect \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --header 'Authorization: Basic $BASE64_CLIENT_ID_SECRET' \
  --data token=$ACCESS_TOKEN
```

### Service Account JWT Bearer Grant
```bash
curl --request POST \
  --url https://$DOMAIN/oauth/v2/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer \
  --data scope='openid urn:zitadel:iam:org:project:id:zitadel:aud' \
  --data assertion=$SIGNED_JWT
```
Uses **service account key** (type `"serviceaccount"`) with `userId` as `iss`/`sub`.

## Event API: Querying Audit Events

`POST /admin/v1/events/_search` — requires `IAM_OWNER_VIEWER` or `IAM_OWNER`.

Key event types:
```
oidc_session.added, oidc_session.access_token.added
oidc_session.refresh_token.added, oidc_session.refresh_token.renewed
saml_session.added, saml_session.saml_response.added
user.human.password.check.failed
user.mfa.otp.check.failed
user.human.mfa.u2f.token.check.failed
user.human.passwordless.token.check.failed
```

List types: `POST /admin/v1/events/types/_search`
List aggregates: `POST /admin/v1/aggregates/types/_search`

```bash
curl -X POST "${DOMAIN}/admin/v1/events/_search" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"asc": false, "limit": 1000, "creation_date": "2023-02-01T10:00:00Z", "aggregate_types": ["user"]}'
```

## System API (Self-Hosted)

`/system/v1/` — operates across all instances. Auth uses self-signed JWTs (not OAuth2):

```yaml
SystemAPIUsers:
  - system-user-1:
      Path: /system-user-1.pub # or KeyData: <base64>
      Memberships:
        - MemberType: System
          Roles: ["SYSTEM_OWNER", "IAM_OWNER"]
        - MemberType: IAM
          Roles: "IAM_OWNER"
          AggregateID: "123456789012345678" # restrict to instance
        - MemberType: Organization
          Roles: "ORG_OWNER"
          AggregateID: "123456789012345678" # restrict to org
```
JWT payload: `iss`/`sub` = user ID, `aud` = instance domain. No memberships = full `SYSTEM_OWNER`.

## Complete RBAC Role Reference

**Instance-level (prefix `IAM_`):**

| Role | Key | Purpose |
|------|-----|---------|
| Instance Owner | `IAM_OWNER` | Full instance + all orgs |
| Instance Owner Viewer | `IAM_OWNER_VIEWER` | Read-only across instance |
| Instance Org Manager | `IAM_ORG_MANAGER` | Manage all orgs |
| Instance User Manager | `IAM_USER_MANAGER` | Manage all users/authorizations |
| Instance Admin Impersonator | `IAM_ADMIN_IMPERSONATOR` | Impersonate admin + end users |
| Instance Impersonator | `IAM_END_USER_IMPERSONATOR` | Impersonate end users |
| Instance Login Client | `IAM_LOGIN_CLIENT` | Custom Login UI permissions |

**Organization-level (prefix `ORG_`):**

| Role | Key | Purpose |
|------|-----|---------|
| Org Owner | `ORG_OWNER` | Full org management |
| Org User Manager | `ORG_USER_MANAGER` | Manage org users/authorizations |
| Org User Permission Editor | `ORG_USER_PERMISSION_EDITOR` | User grants only |
| Org Project Permission Editor | `ORG_PROJECT_PERMISSION_EDITOR` | Grant projects to other orgs |
| Org Project Creator | `ORG_PROJECT_CREATOR` | Create/manage projects |

Self-hosted: Custom roles via `InternalAuthZ.RolePermissionMappings` in config YAML.

## HTTP Webhook Notification Providers

Beyond Twilio/SMTP, Zitadel supports HTTP webhooks for custom message delivery:

```json
{
  "contextInfo": {
    "eventType": "user.human.initialization.code.added",
    "provider": { "id": "285181292935381355", "description": "test" },
    "recipientEmailAddress": "user@example.com"
  },
  "templateData": {
    "title": "...", "subject": "...", "greeting": "...",
    "text": "...", "url": "...", "buttonText": "...",
    "primaryColor": "#5469d4", "backgroundColor": "#fafafa",
    "fontColor": "#000000", "fontFamily": "..."
  },
  "args": {
    "code": "0M53RF", "userName": "Username",
    "firstName": "GivenName", "lastName": "FamilyName",
    "verifiedEmail": "user@example.com", "loginNames": ["Username"]
  }
}
```

```bash
# Email HTTP provider
POST /admin/v1/email/http {"endpoint": "https://relay.example.com/provider"}
POST /admin/v1/email/:id/_activate

# SMS HTTP provider
POST /admin/v1/sms/http {"endpoint": "https://relay.example.com/provider"}
POST /admin/v1/sms/:id/_activate
```

## Feature Restrictions API

- **Disallow public org registrations**: `/ui/login/register/org` returns 404/409. Only `IAM_OWNER` can create orgs.
- **AllowedLanguages**: Restricts languages in OIDC discovery `ui_locales_supported`, login UI, and notifications.

Configure via `SetRestrictions` Admin API or `DefaultInstance.Restrictions` in self-hosted config.

## SCIM v2.0 Provisioning

Implements `urn:ietf:params:scim:schemas:core:2.0:User` (no Groups).

**Provisioning domains** scope `externalId` handling. Set via service account metadata:
- Key: `urn:zitadel:scim:provisioningDomain`, Value: domain name
- With domain: stored as `urn:zitadel:scim:{domain}:externalId`
- Without domain: stored as `urn:zitadel:scim:externalId`

Key mappings:
- `username` → `username`, `name.familyName/givenName` → profile fields
- `emails` → only primary stored; `phoneNumbers` → only primary stored
- `active`: `Active`/`Initial` = `true`, all others = `false`
- Unmapped attrs stored as metadata under `urn:zitadel:scim:*` keys
- `displayName` takes precedence over `name.formatted`

**Required**: `name.familyName`, `name.givenName`, at least one email.

```yaml
SCIM:
  EmailVerified: true
  PhoneVerified: true
  MaxRequestBodySize: 1_000_000
  Bulk:
    MaxOperationsCount: 100
```

## Programmatic B2B Organization Setup

```bash
curl -X POST "https://${DOMAIN}/admin/v1/orgs/_setup" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
  "org": {"name": "Acme Corp", "domain": "acme.com"},
  "human": {
    "userName": "admin",
    "profile": {"firstName": "Admin", "lastName": "User", "displayName": "Admin User", "preferredLanguage": "en"},
    "email": {"email": "admin@acme.com", "isEmailVerified": true},
    "password": "S3cret-P4ss!"
  },
  "roles": ["ORG_OWNER"]
}'
```

Self-registration form: `{domain}/ui/login/register/org` — disable via `SetRestrictions` API.

## Restricting Console Access via hasProjectCheck

Enable `hasProjectCheck` on the default ZITADEL project, then grant only to admin orgs. Console UI hides this — use API:
```bash
curl -L -X PUT "https://${DOMAIN}/management/v1/projects/${PROJECT_ID}" \
  -H "Authorization: Bearer ${PAT}" \
  -H 'Content-Type: application/json' \
  --data-raw '{ "name": "ZITADEL", "hasProjectCheck": true }'
```

## Domain Discovery for Multi-Tenant Login

Enable "Domain discovery allowed" in Login Behavior settings to auto-route by email domain. Requires verified org domains. Effects:
- Org with single IdP → automatic redirect (no username prompt)
- Org with password + MFA → org-branded password login
- Default org → catches unmatched domains
