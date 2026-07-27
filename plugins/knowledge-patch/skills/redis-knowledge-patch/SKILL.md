---
name: redis-knowledge-patch
description: Redis
version: "8.8.1"
license: MIT
metadata:
  author: Nevaberry
---

# Redis Knowledge Patch

Use this skill when upgrading, securing, configuring, or developing against
Redis Open Source. Start with the security and compatibility checks, then open
the reference that matches the task before relying on command, ACL, persistence,
Search, JSON, Time Series, cluster, or observability behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-upgrades.md](references/security-and-upgrades.md) | Security patch floors, integrated components, upgrade paths, ACL scope, TLS client authentication, tested platforms |
| [data-structures-and-commands.md](references/data-structures-and-commands.md) | Array, strings and counters, streams, bit operations, sorted sets, notifications, Cuckoo Filter durability |
| [search-json-and-timeseries.md](references/search-json-and-timeseries.md) | Vector indexes, hybrid search, scoring and profiling, JSON arrays, Time Series aggregation and NaN behavior |
| [operations-cluster-and-modules.md](references/operations-cluster-and-modules.md) | Memory controls, key and slot telemetry, hot-key detection, eviction, atomic slot migration, module hooks |

## Working method

1. Determine the deployed Redis release and topology before applying advice.
2. Check the security floors first; several fixes differ across maintained
   minor lines.
3. Re-audit ACLs when moving a module-era or Redis Stack deployment to Redis 8.
4. Check persistence and cluster caveats before adopting idempotent streams or
   atomic slot migration.
5. Load the topic reference for exact constraints and secondary features.

## Breaking, security, and compatibility checks

### Patch security-sensitive deployments first

Treat the following releases as minimum fix points for the named issue. Choose
the fix on the deployed minor line rather than comparing version strings across
minor lines.

| Issue area | Fixed release or releases |
| --- | --- |
| `redis-check-aof` stack overflow with RCE impact | 8.0.2 |
| HyperLogLog out-of-bounds writes | 8.0.3 |
| Four Lua memory and isolation CVEs | 8.0.4 |
| Probabilistic-filter memory-safety failures | 8.0.5 |
| CRLF error-reply injection | 8.0.6 |
| `XACKDEL` stack overflow with RCE impact | 8.2.3 |
| Response injection | 8.2.5, 8.4.2, or 8.6.1 |
| Five RCE-capable use-after-free or invalid-memory paths | 8.2.6, 8.4.3, or 8.6.3 |
| Module-string reply-copy use-after-free | 8.6.2 |
| Stream consumer-group `RESTORE` use-after-free with RCE impact | 8.2.8, 8.4.5, or 8.6.5 |
| `MSETEX` ACL key-pattern bypass | 8.4.4 |
| `SENTINEL SET` configuration injection | 8.6.4 |
| Crafted `RESTORE` payload writes in RedisBloom and TDigest with RCE impact | 8.8.1 |

The five-path RCE group spans client unblock, `RESTORE`, Lua, Time Series, and
probabilistic structures. Do not infer that one minor line's numeric suffix is
a substitute for the stated fixed release on another line.

### Re-audit ACLs after component integration

Search, JSON, Time Series, Bloom, Cuckoo, Count-min sketch, Top-k, and t-digest
are integral to Redis 8 and included in binary distributions. `redis-full.conf`
loads all components; Vector Set is preview.

Existing broad categories such as `@read` and `@write` now cover commands from
those components. Review old rules and use the narrower `@search`, `@json`,
`@timeseries`, `@bloom`, `@cuckoo`, `@cms`, `@topk`, and `@tdigest` categories
where broad access is unintended.

Search index access also depends on key patterns: the user's patterns must cover
a superset of the index prefixes. Multi-key Time Series reads fail if any
matching key is unreadable, while `TS.QUERYINDEX` reads metadata without needing
read access to the matched keys.

### Plan module-era upgrades explicitly

Replication or persistence upgrades are supported from module-free Redis,
Redis using the former standalone modules, and Redis Stack 7.2 or 7.4. Account
for the integrated component packaging and ACL expansion as part of the same
migration.

### Remove obsolete vector-optimization assumptions

The proprietary LeanVec and LVQ Intel optimizations are absent from Redis Open
Source starting in 8.2.1. Redis 8.2 provides the compressed `SVS-VAMANA` vector
index, and 8.2.2 permits the `BUILD_INTEL_SVS_OPT` build flag for Intel
optimizations.

### Respect persistence and migration caveats

`XADD` idempotency options arrived in 8.6. Redis 8.6.0 warns against combining
them with `appendonly yes` and `aof-use-rdb-preamble no`; 8.6.2 fixes AOF
rewrite and state restoration for idempotency state.

`CLUSTER MIGRATION` performs atomic slot migration. During a migration, the
Search and Time Series multi-key queries identified by the release notes can
still return partial or duplicate results, so atomic slot movement does not
make those query results atomic.

## High-value command changes

### Strings, counters, and multi-key writes

- `DIGEST`, `DELEX`, and `SET` extensions support atomic compare-and-set and
  compare-and-delete flows on string keys.
- `MSETEX` atomically sets multiple string keys and updates their expiration.
- `INCREX` combines integer or floating-point increments, bounds, and expiration
  for window-counter rate limiting.

### Streams

- `XDELEX` and `XACKDEL`, plus extensions to `XADD` and `XTRIM`, add `DELREF`
  and `ACKED` reference strategies for deletion.
- `XREADGROUP CLAIM min-idle-time` can return sufficiently idle pending entries
  and incoming entries in one read.
- `XADD IDMPAUTO` and `IDMP` provide at-most-once production, with
  `stream-idmp-duration` and `stream-idmp-maxsize` supplying defaults.
- `XNACK` lets a consumer explicitly release pending messages.

### Core and probabilistic structures

- Array is a data structure in Redis 8.8.
- `BITOP` supports `DIFF`, `DIFF1`, `ANDOR`, and `ONE`.
- `ZUNION`, `ZINTER`, `ZUNIONSTORE`, and `ZINTERSTORE` accept the `COUNT`
  aggregator.
- Replicated `CF.LOADCHUNK` chunks prevent silent Cuckoo Filter loss after
  failover on the fixed maintenance releases.

### Notifications

- `OVERWRITTEN` reports complete value replacement and `TYPE_CHANGED` reports
  a key type change.
- Hash subkey notifications provide field-level events.

## Search, JSON, and Time Series

### Vector and hybrid search

- `VSIM WITHATTRIBS` returns an element's JSON attribute; `EPSILON` sets a
  maximum distance.
- `FT.HYBRID` combines results with RRF or LINEAR scoring.
- In the original 8.4 behavior, post-`COMBINE` filtering is unavailable; the
  default response contains only `key_id` and `score`; and `EXPLAINSCORE`,
  `YIELD_DISTANCE_AS`, and `WITHCURSOR` are unsupported.
- The newer `KNN` clause can request fewer candidates per shard, and
  `FT.PROFILE HYBRID` profiles hybrid queries.
- `search-default-scorer` configures the default text and tag scorer; `BM25STD`
  is the new default.

### JSON and Time Series

- `JSON.SET FPHA` selects the floating-point type for a homogeneous
  floating-point array.
- `TS.RANGE`, `TS.REVRANGE`, `TS.MRANGE`, and `TS.MREVRANGE` can apply multiple
  aggregators in one command.
- Time Series accepts NaN values and provides `COUNTNAN` and `COUNTALL`.

## Operations quick reference

- Runtime memory tracking can be enabled only in non-clustered mode.
- `volatile-lrm` and `allkeys-lrm` select least-recently-modified eviction.
- `HOTKEYS` detects hot keys; `HOTKEYS HELP` is present from 8.6.1.
- `INFO KEYSIZES` reports size distributions for basic data types.
- `CLUSTER SLOT-STATS` reports per-slot key count, CPU time, and network I/O.
- `key-memory-histograms` collects per-type memory histograms and exposes
  database distribution metrics for lists, sets, hashes, and sorted sets.
- Modules can get and set Redis configuration and selectively unsubscribe from
  keyspace notifications.
- `tls-auth-clients-user` enables certificate-based client authentication;
  failures increment `acl_access_denied_tls_cert`.

Read the indexed reference before implementing an affected feature. It records
the maintenance-release floors, restrictions, and topology-specific behavior
that the quick reference intentionally compresses.
