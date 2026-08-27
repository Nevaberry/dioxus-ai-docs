# Identity, Access Control, and Enterprise Operations

Use this reference for authentication, SSO, SCIM, RBAC, roles, audit controls,
cloud migration, and Enterprise identity or security features.

## Authentication objects and login protection

### Login-attempt lockout (since 11.5.0)

Authentication can cap failed login attempts before locking out a user.

### API keys migrate to service accounts (since 11.6.0)

On the first 11.6 startup, Grafana migrates existing API keys to service accounts.
Plan for the authentication-object migration during upgrade.

### IP-based login validation (since 11.6.0)

Login-attempt validation can use the request IP address.

### Viewer and anonymous access (since 12.0.0)

`viewers_can_edit` is removed. Anonymous access now enforces the configured Viewer
organization role.

### API-key endpoint and code removal (since 12.1.0)

API-key endpoints and API-key authentication code are removed. Use service
accounts and their supported token flows.

### Brute-force username control (since 12.2.0)

Authentication adds a setting that disables username-based brute-force login
protection. Change it only with a compensating protection strategy.

### Passwordless magic links removed (since 13.0.0)

Passwordless magic-link authentication is removed from both frontend and backend.

## OAuth, JWT, SAML, and SSO

### OAuth client authentication and refresh failures (since 11.5.0)

OAuth providers can use `client_secret_jwt` during token exchange. Grafana returns
an error after token-refresh retries are exhausted rather than silently
continuing.

### SAML identity and single logout (since 11.5.0)

Enterprise SAML can configure an EntityID. Single logout carries the NameID and
SessionIndex needed for the SLO exchange.

### JWT TLS and SAML settings (since 11.6.0)

JWT authentication accepts `TlsSkipVerify`. `ssoSettingsSAML` is generally
available and enabled by default.

### JWT organization-role mapping (since 12.0.0)

JWT authentication can map authenticated identities to Grafana organization
roles.

### Session defaults, LDAP settings, and Entra identity (since 12.1.0)

Improved OAuth and SAML session handling is enabled by default, and
`ssoSettingsLDAP` is enabled by default. Authentication adds Azure/Entra workload
identity and access-token user-info extraction.

### JWT trust settings (since 12.2.0)

JWT authentication accepts `tls_client_ca` and `jwk_set_bearer_token_file`.

### OAuth token validation and refresh-token requirement (since 12.4.0)

OAuth can validate ID-token signatures and require refresh tokens when
`use_refresh_token` is enabled. SSO settings add a PATCH endpoint.

### Organization memory and Azure certificates (since 13.0.0)

SSO logins remember the user's last organization. Azure integrations support
certificate authentication.

### JWT inline public keys (since 13.1.0)

JWT authentication accepts inline public keys.

### Infinity and cloud query authentication (since 12.2.0)

Grafana Actions supports Infinity authentication.

## SCIM and identity lifecycle

### Groups, users, and team external IDs (since 12.1.0)

Enterprise SCIM group PATCH can add or remove members and update `externalId`.
User PATCH ignores unsupported fields. Team `externalId` values can be updated.

### Provisioned-user login and deletion (since 12.2.0)

Enterprise SCIM can reject login for users not provisioned by SCIM. Updates may
set an empty `externalId`. SCIM DELETE now deletes a user instead of disabling it.

### SCIM general availability (since 12.4.0)

SCIM is generally available.

### User-deletion audit metadata (since 13.2.0)

User-deletion audit records include the user name.

## RBAC, roles, and authorization

### Cloud migration and snapshot roles (since 11.5.0)

Cloud Migrations is enabled by default and has a dedicated migration-assistant
RBAC role. Creating and deleting snapshots have separate RBAC roles, allowing
independent grants.

### Plugin, Drilldown, and data-source permissions (since 11.6.0)

Plugin roles may include `plugins:write`. Drilldown requires
`datasources:explore`. In Enterprise, data-source queries require `query`; `read`
is not an alternative.

### Kubernetes dashboard authorization (since 12.0.0)

Dashboard endpoints under `/apis` perform fine-grained access checks, and
`kubernetesClientDashboardsFolders` is enabled by default.

### Alertmanager request actions (since 12.0.0)

Alertmanager requests support `reqAction` for RBAC checks.

### Library-panel RBAC (since 12.1.0)

Library-panel RBAC is generally available and enabled by default. The
`libraryPanelRBAC` feature flag is removed.

### Basic-role seeding change (since 12.2.0)

The plugin basic-role seeder no longer grants plugin-app access.

### Dashboard scopes and signed-in avatars (since 12.3.0)

From 12.3.2, dashboard APIs enforce scope checks that were previously absent.
Avatar requests require sign-in and honor timeout settings.

### Action-set writes (since 12.3.0)

RBAC writes persist only action sets. Role automation should preserve action-set
references instead of relying on expanded individual actions being written.

### Seed-assignment maintenance command (since 12.4.0)

Use `grafana cli admin flush-rbac-seed-assignment` to flush seeded RBAC
assignments.

### Stricter custom-role validation (13.0-upgrade)

Role creation, update, deletion, or assignment can fail when Terraform-, API-, or
provisioned roles include deprecated permissions. A global role cannot carry a
data-source UID scope such as `datasources:uid:<uid>`; recreate it as a non-global
role with a new UID because scope cannot change in place. Set `datasource_type` on
data-source permission resources where possible.

Remove `fixed:annotations.dashboard:writer`,
`fixed:annotations.dashboard:reader`, and `annotations:type:dashboard`; use
dashboard or folder View/Edit/Admin permissions for dashboard annotations.
Replace `annotations:*` with `annotations:type:organization` for organization
annotations and dashboard or folder permissions for dashboard annotations.

### Dedicated Alertmanager status action (13.0-upgrade)

`GET /api/alertmanager/grafana/api/v2/status` requires
`alert.notifications.system-status:read`. Admins inherit it through
`fixed:alerting.notifications:writer`; update affected custom roles.

### Grafana Live push authorization (since 13.0.0)

Pushing data to Grafana Live is protected by RBAC.

### Enterprise role API changes (since 13.0.0)

Enterprise removes `/access-control/assignments/search` and the `IncludeMapped`
parameter from `GET /access-control/users/{userId}/roles`. Stop sending the
deprecated role version on writes; Grafana now increments it automatically.

### Usage Insights identity (since 13.0.0)

Usage Insights events use UIDs instead of numeric IDs for data sources and
dashboards.

## Auditing, secrets, and Enterprise controls

### Query body auditing settings (since 12.2.0)

Enterprise auditing can configure whether data-source query request and response
bodies are recorded.

### Loki audit delivery (since 12.4.0)

Enterprise audit delivery to Loki can configure retries and a timeout.

### Audit-body default (since 13.0.0)

Enterprise audit logging disables data-source request and response bodies by
default. Explicitly opt in if those bodies are required.

### Secrets Keeper lifecycle (since 13.1.0)

The Enterprise AWS Secrets Keeper UI supports guided creation, editing,
activation, deactivation, and deletion.

## Cloud migration

### Notification dependencies (since 12.1.0)

Cloud migrations treat mute timings as notification-policy dependencies, so the
related resources migrate together.

### Configuration replaces feature toggle (since 12.4.0)

The Cloud Migrations feature toggle is removed. Use the configuration setting to
disable the feature when required.

## Enterprise reporting recipient controls

### Allowed domains (since 11.5.0)

Enterprise reporting can restrict report addresses by allowed email domain.

### Organization-member recipients (since 13.1.0)

Enterprise reporting can limit report-email recipients to organization members.
