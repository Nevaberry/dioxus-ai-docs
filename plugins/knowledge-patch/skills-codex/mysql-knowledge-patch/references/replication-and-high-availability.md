# Replication and High Availability

## Cross-version replication and retries

### Higher-version sources (9.7.0)

`replica_allow_higher_version_source` controls whether a lower-version replica
can replicate from a higher-version source. Set it only after validating the
topology's compatibility and rollback plan.

### Unlimited source retries (9.7.2)

`SOURCE_RETRY_COUNT=0` consistently means unlimited retries for every receiver
reconnect path. A channel configured this way continues retrying through repeated
transient failures instead of stopping after an internal path-specific limit.

## Secure defaults and GTIDs

### Encryption and identity defaults (9.4-9.6)

Replication connections default to encryption:

- `SOURCE_SSL=1`
- `group_replication_ssl_mode=REQUIRED`
- `group_replication_recovery_use_ssl=ON`

`gtid_mode` also defaults to `ON`. Configure certificates, recovery credentials,
and GTID-aware provisioning explicitly rather than assuming older defaults.

## Group Replication management

### Resource Manager and Primary Election (9.2-9.3)

The Resource Manager monitors secondary applier lag, recovery lag, and memory. It
ejects members that exceed
`group_replication_resource_manager.applier_channel_lag`,
`group_replication_resource_manager.recovery_channel_lag`, or
`group_replication_resource_manager.memory_used_limit`. Automatic rejoin requires
`group_replication_autorejoin_tries` greater than zero.

The Primary Election component can prefer the most up-to-date failover candidate
when it is installed on every member and
`group_replication_elect_prefers_most_updated.enabled=ON`.

### Communication settings deprecated (9.7.2)

`group_replication_communication_stack` and
`group_replication_ip_allowlist` are deprecated and scheduled for removal. Do not
create new dependencies on them, and plan migration for existing configuration.

## Binary-log behavior

### Dependency-history sizing (9.4-9.6)

`binlog_transaction_dependency_history_size` defaults to `1000000` instead of
`25000`; its maximum is `10000000`, up from `1000000`. Set it explicitly when
memory or parallel-apply behavior depends on the old size.

### Foreign-key changes in replication (9.4-9.6)

Foreign-key constraints and cascades execute in the SQL layer, making all their
changes visible in binary logs and replication. Start with
`innodb_native_foreign_keys` only when InnoDB-native handling is intentionally
required.
