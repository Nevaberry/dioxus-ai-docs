# Security, Resource Access, and Multitenancy

## Managing certificates and authentication

### Certificate reload and validation

The Security plugin in 2.19.0 supports certificate hot reload and authority-certificate validation. A hot-reload option can skip distinguished-name validation; use it only when the certificate trust design makes that safe.

Since 3.2.0, SPIFFE X.509 SVID authentication is available through `SPIFFEPrincipalExtractor`, and auxiliary transports can be configured for SSL only.

OpenSearch 3.4.0 can authenticate from X.509 v3 Subject Alternative Name extensions. `securityadmin.sh` accepts `--timeout` or `-to`.

### JWT and client certificates

Security 3.1.0 supports roles in nested JWT claims. In 3.2.0, JWT authentication can resolve its subject from a nested claim. In 3.5.0, nested claim paths support dot notation.

In 3.3.0, the JWT backend can consume JWKS directly. Client-certificate authentication adds `clientcert_auth_domain.http_authenticator.config.skip_users`.

Security 3.5.0 protects gRPC with JWT and treats JWT header names case-insensitively. Basic authentication for gRPC follows in 3.6.0.

### Password and hashing behavior

The 3.0.0 password-strength validator accepts `good`. OpenSearch 3.2.0 adds Argon2 password hashing.

The 3.0.0 Blake2b salt-handling correction can change hashes for identical inputs. Update integrations and tests that compare generated Blake2b values.

## Updating Security configuration

### Renamed, removed, and dynamic settings

OpenSearch 3.0.0 removes the Security OpenSSL provider and renames whitelist settings to allowlist settings. The `_cat/shards` action requires `cluster:monitor/shards`; `ignore_hosts` accepts CIDR ranges.

Since 3.1.0, `plugins.security.cache.ttl_minutes` changes are picked up by a cluster-settings listener, and an endpoint can flush one user's cache.

OpenSearch 3.3.0 makes custom-attribute serialization dynamically configurable. Disabling `plugins.security.system_indices.enabled` permits plugin system requests.

In 3.4.0, resource settings are dynamically updateable. Static and custom configurations may overlap, with static configuration taking precedence. `plugins.security.system_indices.indices` is deprecated.

### Versioned configuration

OpenSearch 3.2.0 introduces an experimental versioned Security configuration system. It can validate permission for a request through a query parameter without executing the request and exposes an API for migrating resource-sharing data into Security.

Versioned configuration adds View and Rollback APIs in 3.3.0.

### Request validation

Since 3.8.0, Security-plugin PUT and PATCH requests enforce a 256-character maximum on every text input. Validate generated configuration before sending it.

## Authorizing resources

### Central resource authorization

OpenSearch 3.1.0 introduces a disabled-by-default resource authorization framework that centralizes sharing and access control in Security. Anomaly Detection is the first integrated plugin.

OpenSearch 3.3.0 adds resource-sharing management APIs and a Dashboards interface, DLS-backed visibility filtering, persisted tenant and principal visibility, an explicit protected-resource list, and centralized access control for ML model groups.

Flow Framework joins in 3.4.0. A single resource index can hold multiple shareable resource types. Migration requires `default_owner` and a default access level; sharing updates use POST rather than PATCH; and the share and revoke Java APIs are removed.

In 3.6.0, resource providers can declare parent type and parent-identifier fields for parent-child authorization. On-behalf-of token authentication no longer requires `encryption_key`.

Security resource configuration can also set a default access level. Rename `resource-action-groups.yml` to `resource-access-levels.yml` during upgrade.

### Scoped API keys

OpenSearch 3.7.0 Security can issue long-lived API keys whose cluster and index permissions are attached directly to the key rather than inherited from user roles. Keys support expiration, synchronous cluster-wide revocation, automatic protection of their system index, and create/list/revoke administration in Dashboards.

### DLS, FLS, and write controls

Since 3.5.0, dynamic `plugins.security.dls.write_blocked` blocks all writes when document-level restrictions apply.

In 3.7.0, DLS and FLS variables accept fallback values.

OpenSearch 3.8.0 allows DLS rules to use query-based terms lookup queries.

Star-tree optimization is suppressed whenever DLS, FLS, or field masking applies; do not assume acceleration on protected queries.

## Configuring tenants and object visibility

### Tenant isolation

OpenSearch 2.19.0 extends tenant-identifier isolation across Flow Framework and ML Commons resources and operations, including connectors, models, tasks, deployment, prediction, agents, search, and configuration.

In 3.7.0, `opensearch_security.multitenancy.tenants.preferred` becomes dynamically updateable through the Security configuration API without a Dashboards restart. `?auto_login=false` forces the login page, while `opensearch_security.auth.default_redirect_auth_type` selects the default redirect authenticator.

### Backend-role access strategies

OpenSearch 3.8.0 adds filter-by-backend-roles strategies for Alerting and Notifications. Each setting controls how backend-role filtering or matching determines access to that plugin's objects.

## Storing remote plugin metadata

### External metadata storage

The Remote Metadata SDK and repository wrapper in 2.19.0 let plugins store metadata externally rather than in system indexes on stateful nodes.

In 3.3.0, global resources are supported. Put and delete operations accept sequence number and primary term for optimistic concurrency; put, update, delete, and bulk operations accept refresh policy and timeout controls.

OpenSearch 3.4.0 adds customer-managed-key encryption and decryption for customer data, including role assumption for key operations.

## Auditing and protected operations

### Audit sinks and payloads

OpenSearch 3.4.0 audit webhook sinks support Basic authentication through `plugins.security.audit.config.username` and `plugins.security.audit.config.password`.

In 3.5.0, audit logs can use configured time zones and include document content for DELETE operations.

Since 3.8.0, audit logging can run in SSL-only mode without the full authentication and RBAC stack. The unified `disabled_categories` setting controls excluded audit-event categories.

### System and plugin operations

OpenSearch 3.0.0 removes REST access to system indexes. Use supported plugin APIs and roles instead of direct reads or writes.

When configuring notification resources in 3.6.0, account for the new `multi_tenancy_enabled` setting and changed settings prefix; existing configuration needs review.
