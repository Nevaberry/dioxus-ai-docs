# Replication and High Availability

Use this reference when configuring source/replica links, Group Replication,
semisynchronous replication, GTIDs, dependency tracking, or foreign-key
replication visibility.

## Cross-version and transport policy

### Replicating from a higher-version source

In batch 9.7.0, `replica_allow_higher_version_source` controls whether a
lower-version replica may replicate from a higher-version source. Do not infer
compatibility from the connection succeeding; enable the variable only after
checking the statements and row events the replica must apply.

### Encryption and GTIDs default on

In batch 9.4-9.6, replication connections default to encryption:

```text
SOURCE_SSL=1
group_replication_ssl_mode=REQUIRED
group_replication_recovery_use_ssl=ON
```

`gtid_mode` also defaults to `ON`. Provision certificates and GTID-aware
topology automation before relying on these defaults.

## Group Replication management

### Resource Manager

The Group Replication Resource Manager monitors:

- secondary applier lag;
- recovery lag; and
- memory use.

It ejects members that exceed
`group_replication_resource_manager.applier_channel_lag`,
`group_replication_resource_manager.recovery_channel_lag`, or
`group_replication_resource_manager.memory_used_limit`. Automatic rejoin
requires `group_replication_autorejoin_tries` greater than zero.

### Primary election

The Primary Election component can prefer the most up-to-date failover candidate
when it is installed on every member and:

```text
group_replication_elect_prefers_most_updated.enabled=ON
```

Mixed installation does not provide the intended election behavior. Both the
Resource Manager and Primary Election component were introduced in the material
for batch 9.2-9.3 and are available in Community Edition in batch 9.7.0.
Community Edition also includes Replication Applier Metrics and Group
Replication Flow Control Statistics.

## Parallelism and semisynchronous replication

`replica_parallel_workers` has a minimum of `1` rather than `0` in batch
9.2-9.3. In batch 9.4-9.6, `replica_parallel_type` and
`group_replication_allow_local_lower_version_join` are removed.

The `semisync_master` and `semisync_slave` plugins are also removed. Use:

```text
semisync_source
semisync_replica
```

Update plugin-loading configuration, variable names, and monitoring labels
together.

## Binary-log scheduling and visibility

### Dependency-history sizing

`binlog_transaction_dependency_history_size` defaults to `1000000`, up from
`25000`, in batch 9.4-9.6. Its maximum rises from `1000000` to `10000000`.
Reassess memory and parallel-apply behavior before preserving an old explicit
value.

### Foreign keys execute in the SQL layer

Foreign-key constraints and cascades run in the SQL layer in batch 9.4-9.6, so
their changes are completely visible in binary logs and replication. Start the
server with `innodb_native_foreign_keys` only when InnoDB-native handling is
required for compatibility.

Test cascade-heavy workloads and downstream consumers when changing between the
two enforcement paths.

## Option tracking

Option Tracker in batch 9.2-9.3 covers binary logging, replicas, Group
Replication, and both optimizer types. Each feature exposes a global status item:

```text
option_tracker_usage:<feature_name>
```

The JSON usage field is a counter named `usedCounter`, not the former Boolean
`used`. Monitoring parsers must accept the numeric contract.
