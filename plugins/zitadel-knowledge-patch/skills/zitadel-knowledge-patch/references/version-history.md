# Version History & Breaking Changes

## v3.0 (2025-05-02)

### License Change: Apache 2.0 → AGPL3
Affects all self-hosting deployments — AGPL3 requires source disclosure if you modify and serve Zitadel over a network.

### CockroachDB Support Removed (PostgreSQL Only)
**Breaking**: CockroachDB is no longer supported. Use `zitadel mirror` to migrate:
```bash
zitadel mirror --from-config cockroach.yaml --to-config postgres.yaml
```
See: https://zitadel.com/docs/self-hosting/manage/cli/mirror

### Actions V2 API: v3 Alpha → v2 Beta (Breaking)
Actions management API moved from API v3 alpha to v2 beta. All v3 alpha endpoints removed. The action v2 feature flag was also removed — Actions V2 is always enabled.

Actions V2 uses a **targets + executions** model instead of V1 JavaScript-based action flows. Targets are HTTP webhook endpoints; executions bind targets to API conditions.

### Web Keys Management API: v3 Alpha → v2 Beta (Breaking)
OIDC signing key management moved from v3 alpha to v2 beta. All v3 alpha web key endpoints removed.

### New Permission Check Framework
Supports system users for service-to-service integrations using system-level access.

### Actions V2: Refresh Token in Post-Authentication Context
Webhooks can access refresh tokens during authentication flows.

---

## v4.0 (2025-07-31)

### API v2: Resource-Based APIs Now Standard
Completes migration of core resources to resource-based API v2.

**General Availability (GA):**
- Actions V2 (promoted from beta)
- Caches V2

**Beta:**
- Instance Service V2, Project V2, App V2 (including App Keys V2)
- Authorization V2, Permission V2, Settings V3

All new v2 APIs use **ConnectRPC exclusively** — no OpenAPI 2.0/Swagger for new endpoints. Existing v1 APIs remain but many endpoints are deprecated.

Migration guide: `https://zitadel.com/docs/apis/migration_v1_to_v2`

### Deprecated V1 Endpoints (Breaking)
**Organization Objects V1** — User management (`AddMachineUser`, `UpdateMachine`, `GenerateMachineSecret`, `RemoveMachineSecret`, machine keys, user metadata, PATs, app keys), all project CRUD, all membership management.

**Instance Lifecycle V1** — `GetMyInstance`, instance domains, trusted domains, org lookup, IAM members.

Use V2 resource APIs instead.

### Login V2 Is Now Default
Login V2 (Next.js app communicating via Session API) is default for all new instances. Replaces Login V1's server-side rendered Go templates.

### ConnectRPC: Exclusive Protocol for New APIs
Clients can use native gRPC (HTTP/2), gRPC-Web (HTTP/1.1), or Connect protocol (HTTP POST with JSON or protobuf).

### Actions V2: Now GA with ClientID in Context
Action execution context now includes `clientID`.

### JWT IdP Intent
JWT-based identity provider intents for authenticating users through IdP linking without browser redirects.

### Service Ping (Self-Hosting)
Opt-out telemetry. Docs: `https://zitadel.com/docs/self-hosting/manage/service_ping`

### SHA2 and PHPass Password Hash Import
Enables migration from systems using SHA2/PHPass hashes (e.g., WordPress) without forcing password resets.

### Custom Organization IDs
`AddOrganizationRequest` accepts a custom org ID; response returns all admins.

### Initial Admin PAT Gets IAM_LOGIN_CLIENT
Setup-created PAT now has `IAM_LOGIN_CLIENT` role for login-related API calls.

---

## V2 API GA Promotion Timeline (v4.4–v4.13)

| Version | Service Promoted to GA |
|---------|----------------------|
| v4.5.0 | Application Service, Permission Service |
| v4.5.0 | Settings v2beta deprecated (→ Settings v3) |
| v4.6.0 | Project Service, Authorization Service, Instance Service |
| v4.7.0 | Organization API |
| v4.13.0 | WebKeys V2 |

---

## v4.1–v4.13 Feature Releases

### Actions V2: Request Header Propagation (v4.2.0)
Webhook targets receive original HTTP request headers (auth tokens, correlation IDs, custom headers).

### List Users by Metadata Query (v4.2.0)
V2 `ListUsers` endpoint can filter by metadata key-value pairs.

### HTTP Identity Provider Signing Key (v4.2.0)
HTTP IdP configs now support a signing key for signed request verification.

### OIDC Audience Roles Claim: Added Then Reverted
**Warning**: Added in v4.3.0, **reverted in v4.3.2**. Do not rely on this feature.

### Login V2: Comprehensive Theme System (v4.4.0)
Full CSS-level theme customization for the Next.js login app (separate from branding/policy settings).

### Await Initial Database Connection (v4.4.0)
Startup waits for PostgreSQL instead of failing immediately. Useful for container orchestration.

### Drupal7 Password Hash Import (v4.6.0)
Added Drupal7 hash verifier. Combined with SHA2 and PHPass, covers Drupal 7 migrations.

### Actions V2: JWT and JWE Payload Types (v4.8.0)
Targets can receive payloads as signed JWT or encrypted JWE for secure webhook delivery.

### Token Exchange: Beta → GA (v4.11.0)
OAuth2 Token Exchange (RFC 8693) — no feature flag needed.

### OIDC Back-Channel Logout: Beta → GA (v4.11.0)
Worker queue for async logout notifications. Configure `backchannel_logout_uri` on OIDC apps.

### XOAUTH2 for SMTP (v4.11.0)
OAuth2-based SMTP auth for Google Workspace and Microsoft 365.

### Cross-App Distributed Tracing (v4.11.0)
V2 APIs support OpenTelemetry context propagation.

### Log Streams and GCP Error Reporting (v4.11.0)
Configurable log streams and native GCP Error Reporting.

### PostgreSQL 18 Compatibility (v4.11.0)

### Machine User Access Token Type (v4.12.0)
V2 API allows specifying JWT or opaque token type for machine users:
```
machine: {
  access_token_type: ACCESS_TOKEN_TYPE_JWT  // or ACCESS_TOKEN_TYPE_BEARER
}
```

### Password Reset with Current Password (v4.12.0)
"Change password" flow requiring current password.

### Trusted Domains at Instance Setup (v4.12.0)
`AddInstance` accepts trusted domains upfront.

### Login V2 Operational Features (v4.12.0–v4.13.0)
- TLS termination (built-in config)
- `LOGIN_SERVICE_KEY_FILE` env var for auth
- Multi-domain redirect configuration
- Dynamic languages from Zitadel settings
- `/ready` Kubernetes readiness probe
- OTEL push-based observability

### DSN/URL Connection Strings (v4.13.0)
```yaml
Database:
  postgres:
    dsn: "postgresql://user:pass@host:5432/zitadel?sslmode=require"
Caches:
  Connectors:
    Redis:
      dsn: "redis://user:pass@host:6379/0"
```

### Metadata in CreateUser/UpdateUser (v4.13.0)
Set metadata directly in user create/update requests. `SetUserMetadata` and `SetOrganizationMetadata` can now delete entries.

### Actions V2: Metadata via RetrieveIdentityProviderIntent (v4.13.0)
Supports metadata updates during IdP authentication flows.

---

## v5.0 (Planned)

A `v5.0.0-base` placeholder tag was created 2026-03-23. No features released yet.

### Breaking Removals
- **Actions V1 removed** — migrate to V2 targets + executions
- **Login V1 removed** — Login V2 (Next.js) becomes the only option
- **All V1 APIs removed** — migrate to V2 resource-based APIs

### Planned Features
- **User Groups**: Groups within orgs with user assignment (GitHub #9702)
- **User Uniqueness at Org Level**: Configurable instance-wide vs org-level username uniqueness (GitHub #9535)
- **Optional User Fields**: User creation with only username; email, first/last name become optional (GitHub #4386)
