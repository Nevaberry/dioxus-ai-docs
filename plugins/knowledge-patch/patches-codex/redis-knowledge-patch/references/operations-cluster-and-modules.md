# Operations, Cluster, and Modules

Use this reference for memory instrumentation, eviction, hot-key diagnosis,
cluster telemetry and migration, backup, and module APIs.

## Runtime memory tracking

Memory tracking can be enabled at runtime only in non-clustered mode. Do not
design a cluster operating procedure that depends on toggling it at runtime.
This restriction is from source batch `8.8.1`.

## Least-recently-modified eviction

Redis 8.6 adds `volatile-lrm` and `allkeys-lrm` to `maxmemory-policy`. They
select least-recently-modified eviction for expiring keys or all keys,
respectively.

## Per-type memory histograms

Redis 8.6 adds `key-memory-histograms` to collect memory-consumption
histograms per data type. It exposes the following database distribution
metrics:

- `db0_distrib_lists_sizes`;
- `db0_distrib_sets_sizes`;
- `db0_distrib_hashes_sizes`; and
- `db0_distrib_zsets_sizes`.

## Hot-key detection

Redis 8.6 adds `HOTKEYS` to detect and report hot keys. Redis 8.6.1 adds the
previously missing `HOTKEYS HELP` subcommand.

## Key-size and slot telemetry

`INFO KEYSIZES` reports size distributions for basic data types.

`CLUSTER SLOT-STATS` reports per-slot key count, CPU time, and network I/O.
Use it to locate slot-level concentration rather than inferring slot pressure
from node totals alone. This telemetry is attributed to batch `8.0-8.6`.

## Atomic cluster slot migration

Redis 8.4 adds `CLUSTER MIGRATION` for atomic slot migration. During migration,
affected Search and Time Series multi-key queries can still return partial or
duplicate results. Plan retries or validation where those result anomalies
matter.

## MP-AOF backup and restore

The `BACKUP` command provides node-side backup and restore based on multi-part
AOF. This addition comes from batch `8.10.0`.

## Module configuration hooks

Redis 8.2 lets modules access Redis configuration through the
`RedisModule_Get*` and `RedisModule_Set*` APIs.

Modules can also unregister selected keyspace notifications with
`RM_UnsubscribeFromKeyspaceEvents`, avoiding an all-or-nothing subscription
lifecycle.
