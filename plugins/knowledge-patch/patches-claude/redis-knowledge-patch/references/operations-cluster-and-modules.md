# Operations, Cluster, and Modules

## Runtime memory tracking

Redis 8.8 permits memory tracking to be enabled at runtime, but only in
non-clustered mode. Check topology before trying to enable it. This restriction
is recorded in batch `8.8.1`.

## Least-recently-modified eviction

Redis 8.6 adds `volatile-lrm` and `allkeys-lrm` as `maxmemory-policy` choices.
They evict by least-recently-modified behavior rather than least-recently-used
behavior.

## Hot-key detection

Redis 8.6 adds `HOTKEYS` for detecting and reporting hot keys. Redis 8.6.1
adds the initially missing `HOTKEYS HELP` subcommand.

## Slot and key-size telemetry

`CLUSTER SLOT-STATS` reports key count, CPU time, and network I/O per slot.
Use it to localize load within a cluster rather than relying only on node-wide
metrics.

`INFO KEYSIZES` exposes size distributions for basic data types.

## Per-type memory histograms

Redis 8.6 adds `key-memory-histograms` to collect memory-consumption
histograms per data type. It exposes these database distribution metrics:

- `db0_distrib_lists_sizes`
- `db0_distrib_sets_sizes`
- `db0_distrib_hashes_sizes`
- `db0_distrib_zsets_sizes`

Account for the collection cost when enabling the feature.

## Atomic cluster slot migration

Redis 8.4 adds `CLUSTER MIGRATION` for atomic slot migration. Atomic slot
movement does not make all queries atomic: during migration, the Search and
Time Series multi-key queries identified by the release notes can still return
partial or duplicate results.

Design callers to tolerate or reconcile those responses while migration is in
progress.

## Module configuration hooks

Redis 8.2 lets modules access Redis configuration through the
`RedisModule_Get*` and `RedisModule_Set*` APIs. Modules can also unregister
selected keyspace notifications with
`RM_UnsubscribeFromKeyspaceEvents`.

Keep module configuration validation and permissions aligned with the server's
own configuration behavior.

## MP-AOF backup and restore

Redis 8.10 adds `BACKUP` for node-side backup and restore based on multi-part
AOF. The feature belongs to the `8.10.0` batch.

Treat a node-local backup as one part of a topology-aware recovery plan. Verify
the persistence mode, target node, storage capacity, and restore procedure
before depending on it.

## Operational checklist

Before enabling or adopting one of these features:

1. Confirm standalone versus clustered topology.
2. Confirm persistence settings and their compatibility with the operation.
3. Establish the fixed maintenance release for the deployed minor line.
4. Capture baseline memory, key-size, slot, and latency measurements.
5. Exercise failover, migration, backup, and restore paths outside production.

The eviction, telemetry, migration, and module behaviors above originate in
the `8.0-8.6` batch unless a later batch is stated explicitly.
