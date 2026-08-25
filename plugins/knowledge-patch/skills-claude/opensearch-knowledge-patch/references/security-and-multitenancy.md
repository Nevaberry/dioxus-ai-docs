# Security and Multitenancy

Use this reference for authentication, request authorization, DLS/FLS, audit logging, certificates, API keys, resource sharing, and tenant-aware plugin behavior.

## Authentication and identity

### JWT

- In 3.0.0, password-strength validation accepts `good`.
- In 3.1.0, roles can come from nested JWT claims. A cluster-settings listener applies changes to `plugins.security.cache.ttl_minutes`, and an endpoint flushes one user's cache.
- In 3.2.0, JWT subject resolution supports a nested claim.
- In 3.3.0, the JWT backend can consume a JWKS directly.
- In 3.5.0, nested claims can be addressed with dot notation.
- Protected gRPC transport supports JWT in 3.5.0, and header names are case-insensitive.

### Certificates and workload identity

- In 2.19.0, Security supports certificate hot reload and CA validation, with an option to skip distinguished-name validation during reload.
- In 3.2.0, SPIFFE X.509 SVID authentication is available through `SPIFFEPrincipalExtractor`; auxiliary transports can be SSL-only.
- In 3.3.0, client-certificate authentication adds `clientcert_auth_domain.http_authenticator.config.skip_users`.
- In 3.4.0, X.509 v3 Subject Alternative Name extensions can provide authentication identity.

### Password hashing and login

- Argon2 password hashing is available in 3.2.0.
- In 3.7.0, `?auto_login=false` forces the login page and `opensearch_security.auth.default_redirect_auth_type` selects the default redirect authenticator.

### gRPC authentication

The Security plugin adds Basic authentication for gRPC in 3.6.0, supplementing the protected transport options. gRPC circuit-breaker protection is available since 3.5.0.

## Permissions and request validation

### Core permission changes

- In 3.0.0, `_cat/shards` requires `cluster:monitor/shards`.
- `ignore_hosts` accepts CIDR ranges in 3.0.0.
- In 3.2.0, a query parameter can validate whether a request is permitted without executing it.

### DLS and FLS

- Since 3.2.0, star-tree optimization is disabled under DLS, FLS, or field masking.
- In 3.5.0, dynamic `plugins.security.dls.write_blocked` blocks all writes when document-level restrictions apply.
- In 3.7.0, DLS/FLS variables can specify fallback values.
- In 3.8.0, DLS rules accept query-based terms lookup queries.

### Request input limits

Security-plugin PUT and PATCH requests in 3.8.0 enforce a 256-character maximum on every text input. Validate generated configuration values before sending them.

## API keys

OpenSearch 3.7.0 can issue long-lived API keys with cluster and index permissions attached directly to the key instead of inherited from user roles. Keys support expiration, synchronous cluster-wide revocation, automatic system-index protection, and create/list/revoke administration in Dashboards.

## Security configuration lifecycle

### Versioned configuration

- In 3.2.0, an experimental versioned security-configuration system is available.
- In 3.3.0, it adds View and Rollback APIs.

### Dynamic and static settings

- Security resource settings become dynamically updateable in 3.4.0.
- Static and custom security configurations may overlap, with static configuration taking precedence.
- `plugins.security.system_indices.indices` is deprecated in 3.4.0.
- In 3.3.0, disabling `plugins.security.system_indices.enabled` permits plugin system requests.
- Custom-attribute serialization becomes dynamically configurable in 3.3.0.

### Administration tools

`securityadmin.sh` accepts `--timeout` and `-to` in 3.4.0.

## Centralized resource authorization

### Framework rollout

- In 3.1.0, the disabled-by-default resource authorization framework begins centralizing sharing and access control in Security; Anomaly Detection is the first integrated plugin.
- In 3.2.0, an API migrates resource-sharing data into Security.
- In 3.3.0, resource sharing adds management APIs and a Dashboards UI, DLS-backed visibility filtering, stored tenant and principal visibility, an explicit protected-resource list, and centralized access for ML model groups.
- In 3.4.0, Flow Framework joins the framework, and one resource index can store several sharable resource types.

### Sharing migration and API changes

The 3.4.0 migration requires `default_owner` and a default access level. Update-sharing changes from PATCH to POST; the share and revoke Java APIs are removed.

### Parent-child authorization

In 3.6.0, resource providers can declare parent type and parent-ID fields. Security resource configuration can specify a default access level, and the filename changes from `resource-action-groups.yml` to `resource-access-levels.yml`.

On-behalf-of token authentication no longer requires `encryption_key` in 3.6.0.

## Tenants and plugin isolation

### Tenant-aware resources

In 2.19.0, tenant-ID isolation spans Flow Framework and ML Commons resources and operations, including connectors, models, tasks, deployment, prediction, agents, search, and configuration.

The 3.7.0 `opensearch_security.multitenancy.tenants.preferred` setting is dynamically updateable through the Security configuration API without restarting Dashboards.

### Alerting and Anomaly Detection constraints

With Alerting multi-tenancy enabled in 3.7.0, unsupported email, findings, chained actions, Job Scheduler indexes, and other actions are disabled. Pluggable-data-format domains reject non-PPL monitor CRUD.

For multi-tenant Anomaly Detection data sources, default and flattened result indexes and historical analysis are disabled. Unsupported routes return HTTP 501.

### Backend-role object access

In 3.8.0, Alerting and Notifications each add a filter-by-backend-roles strategy setting that controls whether filtering or matching backend roles grants access to objects.

## Audit logging

### Destinations and content

- In 3.4.0, webhook sinks support Basic authentication through `plugins.security.audit.config.username` and `plugins.security.audit.config.password`.
- In 3.5.0, audit logs support configurable time zones and can include document contents for DELETE operations.

### Standalone and selective auditing

In 3.8.0, audit logging can run in SSL-only mode without enabling the complete authentication and RBAC stack. The unified `disabled_categories` setting selects audit-event categories to exclude.

## Platform compatibility notes

### Provider and terminology changes

In 3.0.0, the Security plugin removes its OpenSSL provider and renames whitelist settings to allowlist settings.

### Blake2b hash compatibility

OpenSearch 3.0.0 corrects Blake2b salt handling. The same inputs can produce hashes different from older releases, so update fixtures and interoperability tests.
