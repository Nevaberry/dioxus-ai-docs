# Security and Configuration

Use this reference for authorizers, identities, audit logging, credentials,
`cassandra.yaml`, virtual settings, and extension loading.

## Authorization and identities

### Keep CIDR authorizer parameters (since 5.0.3)

`CassandraCIDRAuthorizer` accepts parameterized configuration and applies the
provided settings. Parameters are no longer silently lost during authorizer
construction.

### Expect stricter permission boundaries (since 5.0.3)

Authorization is tighter in DC and authorizer handling and on system keyspaces.
Access inadvertently allowed before can now be rejected; test upgrades with the
actual roles used by applications and operators.

### Grant access to virtual system keyspaces (since 5.0.5)

Permissions can be granted on `system_views` and `system_virtual_schema`.

```cql
GRANT SELECT ON KEYSPACE system_views TO monitoring_role;
GRANT SELECT ON KEYSPACE system_virtual_schema TO monitoring_role;
```

### Prevent superuser identity binding (since 5.0.7)

A regular user cannot bind an identity to a superuser. Provisioning flows must
perform that association under an appropriately privileged principal.

## Audit and credential safety

### Validate audit configuration at startup (since 5.0.3)

`audit_logging_options` are sanitized and validated during startup. Treat a
startup failure as a configuration defect rather than deferring validation
until the audit path is exercised.

### Rate-limit password changes (since 5.0.7)

Password changes are rate-limited. Rotation automation should serialize or back
off after rejection rather than retrying rapidly.

### Obfuscate more password forms (since 5.0.9)

`PasswordObfuscator` masks password forms that were previously missed. Logging
and diagnostic callers should still avoid emitting credentials and use the
obfuscator as defense in depth.

## YAML and server configuration

### Uncomment valid defaults safely (since 5.0.4)

Optional settings in the default `cassandra.yaml` remain parseable when
uncommented, including when configuration-management tools perform the edit.

### Select a batchlog endpoint strategy (since 5.0.3)

Batchlog endpoint selection accepts `random_remote`, `prefer_local`,
`dynamic_remote`, and `dynamic`.

```yaml
batchlog_endpoint_strategy: dynamic_remote
```

### Discover Paxos v2 configuration (since 5.0.9)

The shipped `cassandra.yaml` includes the Paxos v2 option and its configuration
information. Manage the option in the normal configuration template rather
than relying on an undocumented setting.

### Reject overlong table names (since 5.0.6)

Cassandra rejects table names that would produce filenames that are too long.
DDL generation must handle validation failure at schema creation rather than a
later filesystem-path error.

## Virtual settings inventory

### Parse complex values as JSON (since 5.0.6)

Complex values in `system_views.settings` are represented as JSON. Consumers
must parse them as JSON rather than depending on the earlier representation.

### Treat secrets as redacted (since 5.0.6)

Security-sensitive data is redacted in `system_views.settings`. Monitoring and
inventory code must not expect the view to return usable secret values.

### Include the complete settings surface (since 5.0.7)

Configurations previously absent from `system_views.settings` are included for
backward compatibility. Inventory consumers should tolerate the expanded row
set.

### Handle non-string mapping keys (since 5.0.9)

Queries against `system_views.settings` work when a setting contains non-string
keys. JSON or mapping consumers must preserve those values without assuming
every source key began as a string.

## Extension configuration

### Check reflected extension types first (since 5.0.9)

Cassandra verifies that a reflectively loaded extension has the required type
before initializing its class. Incompatible extension classes fail before
initialization, so configuration validation should report the type mismatch
directly.
