# Configuration, Security, and Observability

## Configuration and runtime

### Parameterized CIDR authorizer configuration

`CassandraCIDRAuthorizer` applies configured parameters instead of losing them
(since 5.0.3). Keep parameterized authorizer settings in the intended
configuration path and verify them after startup.

### Startup validation for audit logging

`audit_logging_options` are sanitized and validated during startup (since
5.0.3). Malformed audit settings should be treated as startup configuration
errors.

### Valid default YAML when options are uncommented

Optional entries in the default `cassandra.yaml` remain parseable when
uncommented (since 5.0.4), including when downstream configuration tooling
processes the file.

### Null tombstones in FQL batches

Full Query Logging batch statements support null column-value tombstones
(since 5.0.4). Logging and replay tooling must preserve these null entries.

### Full Java 17 support

Cassandra supports running fully on Java 17 (since 5.0.5). Align service,
diagnostic, and build runtimes when standardizing on Java 17.

### First boot with a disk-usage limit

Configuring `data_disk_usage_max_disk_size` before the data directory exists
does not crash a node on first boot (since 5.0.5).

### Forced optimized index-status format

`IndexStatusManager` can be forced to use the optimized index-status format
when automatic selection is unsuitable (since 5.0.7).

### Correct failure-detector maximum-interval default

The failure detector calculates its default maximum interval correctly (since
5.0.7). Clusters that retain the default may observe changed failure-detection
timing after an upgrade.

### Type checking for reflectively loaded extensions

Cassandra verifies the required type of a reflectively loaded extension before
initializing the class (since 5.0.9). An incompatible class is rejected before
its initialization side effects occur.

## Authorization and secrets

### Stricter authorization boundaries

Authorization is tighter for data-center and authorizer handling and for
system keyspaces (since 5.0.3). Access inadvertently allowed by older releases
may now be rejected; grant only the required permissions explicitly.

### Grants on virtual system keyspaces

Permissions can be granted on `system_views` and `system_virtual_schema`
(since 5.0.5):

```cql
GRANT SELECT ON KEYSPACE system_views TO monitoring_role;
GRANT SELECT ON KEYSPACE system_virtual_schema TO monitoring_role;
```

### Superuser identity-binding restriction

A regular user cannot bind an identity to a superuser (since 5.0.7).
Provisioning flows must use a suitably privileged actor for that association.

### Rate-limited password changes

Password changes are rate-limited (since 5.0.7). Rotation automation should
pace requests and handle a rate-limit rejection instead of assuming every
rapid repeated change succeeds.

### Broader password obfuscation

`PasswordObfuscator` masks password forms that were previously missed (since
5.0.9). Logs and diagnostics should no longer expose those forms, but callers
must still avoid emitting secrets through unrelated fields.

## Guardrails

### Guardrail configuration commands

`nodetool getguardrailsconfig` and `setguardrailsconfig` expose guardrail
configuration with the simplified final command interface (since 5.0.5):

```shell
nodetool getguardrailsconfig
```

### Disabling a tripped disk-usage guardrail

The disk-usage guardrail can be disabled after its failure threshold has
already been reached (since 5.0.7). Operators can recover configuration control
without first clearing the tripped condition.

## Virtual tables and management interfaces

### JSON values in `system_views.settings`

Complex settings are represented as JSON in `system_views.settings` (since
5.0.6). Parse those values as JSON instead of relying on the earlier
representation.

### Prepared-statement invalidation over JMX

`StorageService.dropPreparedStatements` is exposed through JMX (since 5.0.6),
allowing management clients to invalidate prepared statements.

### Sensitive-settings redaction

`system_views.settings` redacts security-sensitive information (since 5.0.6).
Monitoring and configuration-inventory consumers must not expect secret values
from the view.

### Native connection cap over JMX

`StorageProxyMBean` exposes
`NativeTransportMaxConcurrentConnectionsPerIp` (since 5.0.6), making the
per-IP native transport connection limit available to JMX clients.

### Complete `system_views.settings` configuration coverage

Configuration rows previously missing from `system_views.settings` are
included again for backward compatibility (since 5.0.7). Inventory consumers
can discover those settings through the virtual table.

### Non-string keys in `system_views.settings`

Queries against `system_views.settings` tolerate settings containing
non-string keys (since 5.0.9). Consumers should still parse the resulting
structured representation rather than assuming every key is a string.

## Operational signals

### No heap dumps for handled exceptions

Handled exceptions do not generate heap dumps (since 5.0.7). Incident tooling
must not wait for or require a dump artifact when Cassandra catches and handles
an exception.

### Correct direct-memory reporting in `nodetool gcstats`

`nodetool gcstats` reports direct-memory usage correctly (since 5.0.7).
Monitoring should consume the corrected value after upgrading rather than
applying compensation for the old output.
