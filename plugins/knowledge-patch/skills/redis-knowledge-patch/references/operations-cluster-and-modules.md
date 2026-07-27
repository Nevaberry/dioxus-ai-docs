# Operations, Cluster, and Modules

Use this reference when tuning memory, finding hot or oversized keys,
monitoring cluster slots, migrating slots, or integrating a module with Redis
configuration and keyspace notifications.

## Runtime memory tracking

Redis 8.8 allows memory tracking to be enabled at runtime in non-clustered
mode. Do not assume the runtime control is available in clustered deployments.

## Memory policy and histograms

Redis 8.6 adds least-recently-modified eviction through two
`maxmemory-policy` values:

- `volatile-lrm`
- `allkeys-lrm`

Redis 8.6 also adds `key-memory-histograms` to collect memory-consumption
histograms per data type. It exposes these per-database distribution metrics:

- `db0_distrib_lists_sizes`
- `db0_distrib_sets_sizes`
- `db0_distrib_hashes_sizes`
- `db0_distrib_zsets_sizes`

## Hot keys and key sizes

Redis 8.6 adds `HOTKEYS` to detect and report hot keys. Redis 8.6.1 adds the
previously missing `HOTKEYS HELP` subcommand.

`INFO KEYSIZES` exposes size distributions for basic data types. Use it for
distribution-level visibility; use the per-type memory histograms when memory
consumption, rather than logical size alone, is the target.

## Per-slot cluster telemetry

`CLUSTER SLOT-STATS` reports these values per slot:

- key count;
- CPU time; and
- network I/O.

## Atomic slot migration

Redis 8.4 adds `CLUSTER MIGRATION` for atomic slot migration. During migration,
the Search and Time Series multi-key queries listed in the release notes can
still return partial or duplicate results. Treat slot movement and multi-key
query result consistency as separate concerns.

## Module configuration and notification hooks

Redis 8.2 allows modules to access Redis configuration through the
`RedisModule_Get*` and `RedisModule_Set*` API families. Modules can also
unregister selected keyspace notifications with
`RM_UnsubscribeFromKeyspaceEvents`.

The operational and module changes are from batch `8.0-8.6`, while runtime
memory tracking is from batch `8.8.1`.
