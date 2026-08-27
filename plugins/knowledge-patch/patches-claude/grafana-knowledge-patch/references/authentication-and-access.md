# Authentication and access control

## Service accounts and login controls

### API-key migration and removal

On the first 11.6 startup, Grafana migrates API keys to service accounts; allow for authentication-object migration during startup and update operational inventory. (11.6.0)

API-key endpoints and API-key authentication code are removed. Replace all remaining API-key clients with service accounts. (12.1.0)

### Brute-force and lockout behavior

Authentication can set the maximum login attempts before lockout. (11.5.0)

Login-attempt validation can key on IP address. (11.6.0)

A setting can disable username-based brute-force protection. Keep this distinct from other lockout dimensions when choosing the policy. (12.2.0)

## OAuth, SAML, LDAP, and SSO

### OAuth token handling

OAuth providers can authenticate token exchange with `client_secret_jwt`. Once token-refresh retries are exhausted, Grafana returns an error instead of silently proceeding. (11.5.0)

Improved session handling for OAuth and SAML is enabled by default. Azure/Entra workload identity and access-token user-info extraction are supported. (12.1.0)

OAuth can validate ID-token signatures. When `use_refresh_token` is enabled, it can require refresh tokens. SSO settings have a PATCH endpoint. (12.4.0)

SSO login remembers the user's last organization. Azure integrations support certificate authentication. Passwordless magic-link authentication is removed from both frontend and backend. (13.0.0)

### SAML and LDAP

Enterprise SAML accepts a configurable EntityID. Single logout includes the NameID and SessionIndex needed for the SLO exchange. (11.5.0)

`ssoSettingsSAML` is generally available and enabled by default. (11.6.0)

`ssoSettingsLDAP` is enabled by default. (12.1.0)

## JWT authentication

JWT authentication supports `TlsSkipVerify`. (11.6.0)

JWT identities can be mapped to organization roles. (12.0.0)

JWT accepts `tls_client_ca` and `jwk_set_bearer_token_file`. (12.2.0)

JWT also accepts inline public keys. (13.1.0)

## SCIM identity lifecycle

Group PATCH can add or remove members and change `externalId`. User PATCH ignores unsupported fields, and team `externalId` values can be changed. (12.1.0)

Enterprise SCIM can reject login for users that were not provisioned. Updates may clear `externalId`. DELETE now deletes a user rather than disabling the account, so downstream lifecycle expectations must change. (12.2.0)

SCIM is generally available. (12.4.0)

GroupAttributeSync routes are removed; clients must stop calling them. (13.1.0)

User-deletion audit events include the user name. (13.2.0)

## Role-based access control

### Plugin, drilldown, and query permissions

Plugin roles may include `plugins:write`. Drilldown access requires `datasources:explore`. In Enterprise, `query` is required for data-source queries; `read` is not an alternative. (11.6.0)

The plugin basic-role seeder no longer automatically grants plugin-app access. Audit explicit application grants after upgrade. (12.2.0)

### Dashboard, library, and snapshot permissions

Snapshot create and delete operations have separate RBAC roles. (11.5.0)

Dashboard endpoints under `/apis` perform fine-grained access checks, and `kubernetesClientDashboardsFolders` is enabled by default. (12.0.0)

Library-panel RBAC is generally available and enabled by default; `libraryPanelRBAC` is removed. Library elements can no longer be configured as library variables. (12.1.0)

Starting in 12.3.2, dashboard API requests enforce previously missing scope checks. Avatar requests require sign-in and respect their timeout, so anonymous avatar retrieval no longer works. (12.3.0)

### Data-source and organization scoping

Data-source label-based access control is available as a self-service public-preview feature. (12.0.0)

Enterprise LBAC rules can filter by team. (12.1.0)

Correlations cannot use `org_id=0`; records and requests need a concrete organization ID. (12.3.0)

### Grafana Live

Pushing data to Grafana Live is protected by RBAC. Grant a purpose-specific action instead of assuming authenticated users can push. (13.0.0)

## Custom roles and permission migrations

### Annotation permission replacements

Role creation, update, deletion, and assignment can fail when API-, Terraform-, or file-provisioned roles contain deprecated actions. Remove `fixed:annotations.dashboard:writer`, `fixed:annotations.dashboard:reader`, and `annotations:type:dashboard`; use dashboard or folder View/Edit/Admin permissions for dashboard annotations. Replace `annotations:*` with `annotations:type:organization` for organization annotations and dashboard/folder permissions for dashboard annotations. (13.0-upgrade)

### Global data-source scopes

A global role cannot carry a scope such as `datasources:uid:<uid>`. Recreate it with a new UID as a non-global role because role scope cannot be changed in place. Set `datasource_type` on data-source permission resources where possible. (13.0-upgrade)

### Action sets and role writes

RBAC writes persist action sets only. Automation should preserve action-set references rather than expecting expanded individual actions to be written. (12.3.0)

The CLI command `grafana cli admin flush-rbac-seed-assignment` clears seeded RBAC assignments when maintenance requires it. (12.4.0)

Enterprise removes `/access-control/assignments/search` and the `IncludeMapped` argument from `GET /access-control/users/{userId}/roles`. Stop sending the deprecated role version on writes; Grafana increments it automatically. (13.0.0)

## Viewer and anonymous behavior

`viewers_can_edit` is removed. Anonymous access enforces the configured Viewer organization role. (12.0.0)

## Cloud migration access

Cloud Migrations is enabled by default in 11.5, and a dedicated migration-assistant role controls access. (11.5.0)

The Cloud Migrations feature toggle is removed. Use the configuration setting when the feature must be disabled. (12.4.0)

## Auditing and sensitive data

Enterprise query auditing can independently control recording of data-source request and response bodies. (12.2.0)

Enterprise query caching is disabled for a data source with `oauthPassThru=true`, preventing per-user OAuth credentials from being mixed with cached results. (12.3.0)

Enterprise audit delivery to Loki can configure retries and a timeout. (12.4.0)

Data-source request and response bodies are disabled in Enterprise audit logs by default. Opt in only when their diagnostic value outweighs the sensitivity and volume. (13.0.0)

Loki usage-insights events include the public-dashboard UID. (13.2.0)

## Enterprise identity administration

The AWS Secrets Keeper UI supports guided creation, editing, activation, deactivation, and deletion. Apply the same change-control expectations to every lifecycle action. (13.1.0)
