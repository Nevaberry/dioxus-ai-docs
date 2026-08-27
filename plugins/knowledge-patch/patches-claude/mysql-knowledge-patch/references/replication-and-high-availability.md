# Replication and High Availability

Use this reference when changing replication channels, version topology, Group
Replication, retry behavior, or binary-log assumptions.

## Version and transport compatibility

### Allow a higher-version source explicitly

A lower-version replica accepts a higher-version source only when
`replica_allow_higher_version_source` permits it. Set and review this variable
as part of the topology change instead of assuming cross-version acceptance.

### Expect encrypted connections and GTIDs

Replication connections default to encryption:

- `SOURCE_SSL=1`
- `group_replication_ssl_mode=REQUIRED`
- `group_replication_recovery_use_ssl=ON`

`gtid_mode` also defaults to `ON`. Provision certificates and validate GTID
behavior explicitly when upgrading an existing topology.

### Configure unlimited retries consistently

Since 9.7.2, `SOURCE_RETRY_COUNT=0` consistently means unlimited retries for
all receiver reconnect paths. A channel using zero continues after repeated
transient connection failures instead of stopping unexpectedly.

## Group Replication components

### Resource Manager

The Group Replication Resource Manager monitors secondary applier lag, recovery
lag, and memory. It ejects members that exceed:

- `group_replication_resource_manager.applier_channel_lag`
- `group_replication_resource_manager.recovery_channel_lag`
- `group_replication_resource_manager.memory_used_limit`

Automatic rejoin requires `group_replication_autorejoin_tries` greater than
zero.

### Primary Election

The Primary Election component can prefer the most up-to-date failover
candidate. Install it on every member and set
`group_replication_elect_prefers_most_updated.enabled=ON`.

### Community Edition availability

Community Edition includes the Replication Applier Metrics, Group Replication
Flow Control Statistics, Group Replication Resource Manager, Group Replication
Primary Election, and Telemetry components.

### Retire deprecated variables

In `9.7.2`, `group_replication_communication_stack` and
`group_replication_ip_allowlist` are deprecated and scheduled for removal.
Avoid new dependencies and plan to remove both from existing configurations.

## Binary-log behavior

### Size dependency history for the new default

`binlog_transaction_dependency_history_size` defaults to `1000000` rather
than `25000`; its maximum is now `10000000` rather than `1000000`. Set it
explicitly if dependency-memory or parallel-apply assumptions require the old
size.

### Understand SQL-layer foreign keys

Foreign-key constraints and cascades execute in the SQL layer, making their
changes completely visible in binary logs and replication. Start with
`innodb_native_foreign_keys` only when InnoDB-native handling must be retained.

For semisynchronous replication, replace removed `semisync_master` and
`semisync_slave` plugins with `semisync_source` and `semisync_replica`.
