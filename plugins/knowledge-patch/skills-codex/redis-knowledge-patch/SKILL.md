---
name: redis-knowledge-patch
description: Redis
version: 8.8.1
license: MIT
metadata:
  author: Nevaberry
---


# Redis Knowledge Patch

Use this skill when upgrading, securing, configuring, or developing against
Redis Open Source. Determine the deployed release and topology first, check the
security floors, and then open the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-upgrades.md](references/security-and-upgrades.md) | Security patch floors, integrated components, upgrade paths, ACL scope, TLS authentication, tested platforms |
| [data-structures-and-commands.md](references/data-structures-and-commands.md) | Arrays, hashes, strings, lists, sets, streams, bit operations, notifications, Cuckoo Filter durability |
| [search-json-and-timeseries.md](references/search-json-and-timeseries.md) | Vector indexes, hybrid search, scoring, profiling, JSON arrays, Time Series querying and aggregation |
| [operations-cluster-and-modules.md](references/operations-cluster-and-modules.md) | Memory controls, key and slot telemetry, eviction, atomic slot migration, backup, module hooks |

## Working method

1. Identify the exact Redis release, standalone or clustered topology,
   persistence mode, and whether the deployment came from Redis Stack or
   standalone modules.
2. Apply the security floor for the deployed minor line. Do not substitute a
   similarly numbered patch from a different minor line.
3. Re-audit ACL categories and key patterns when moving to integrated Search,
   JSON, Time Series, or probabilistic components.
4. Check persistence and migration caveats before using stream idempotency,
   slot migration, or node-side backup and restore.
5. Open the relevant reference before implementing an affected command; the
   quick reference deliberately compresses restrictions and maintenance floors.

## Breaking, security, and compatibility checks

### Patch security-sensitive deployments first

Use at least the fixed release shown for the deployed minor line.

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
| Crafted RedisBloom or TDigest `RESTORE` writes with RCE impact | 8.8.1 |
| Memory-safety and certificate-authentication issues on the 8.10 line | 8.10.1 |

The five-path RCE group spans client unblock, `RESTORE`, Lua, Time Series, and
probabilistic structures. The 8.10.1 fixes span CMSketch, TopK, TLS,
`SLOT_INFO`, Vector Set, and blocked-client paths; a crafted `SLOT_INFO` case
may allow RCE. Read the security reference for the full scope.

### Re-audit ACLs after component integration

Search, JSON, Time Series, Bloom, Cuckoo, Count-min sketch, Top-k, and t-digest
are integral components. Broad categories such as `@read` and `@write` include
their commands. Use `@search`, `@json`, `@timeseries`, `@bloom`, `@cuckoo`,
`@cms`, `@topk`, and `@tdigest` where narrower access is intended.

Search index access additionally requires key patterns that cover a superset
of the index prefixes. Multi-key Time Series reads fail if any matching key is
unreadable, while `TS.QUERYINDEX` reads metadata without requiring access to
the matched keys.

### Plan module-era upgrades explicitly

Binary distributions include the integrated components, and `redis-full.conf`
loads all of them; Vector Set remains preview in the integration guidance.
Replication or persistence upgrades are supported from module-free Redis,
deployments using the former standalone modules, and Redis Stack 7.2 or 7.4.
Account for packaging and ACL expansion in the migration plan.

### Remove obsolete vector assumptions

Redis Open Source no longer has proprietary LeanVec or LVQ Intel optimizations
from 8.2.1 onward. Use the compressed `SVS-VAMANA` index introduced in 8.2;
8.2.2 permits `BUILD_INTEL_SVS_OPT` for Intel optimizations.

### Respect stream persistence and cluster-query caveats

`XADD IDMPAUTO` and `IDMP` provide at-most-once production. On 8.6.0, do not
combine them with `appendonly yes` and `aof-use-rdb-preamble no`; 8.6.2 fixes
AOF rewrite and restoration of idempotency state.

`CLUSTER MIGRATION` moves slots atomically, but affected Search and Time Series
multi-key queries can still return partial or duplicate results during the
migration. Atomic slot movement does not make those query results atomic.

## High-value command changes

### Strings, hashes, and counters

- `DIGEST`, `DELEX`, and `SET` extensions support atomic compare-and-set and
  compare-and-delete flows on string keys.
- `MSETEX` atomically sets multiple string keys and updates their expiration.
- `INCREX` combines integer or floating-point increments, bounds, and
  expiration for window-counter rate limiting.
- Compact hashes store shared field names once for repeated schemas, and
  `HIMPORT` provides high-throughput bulk insertion for them.

### Lists, sets, and bit operations

- `LMOVEM` and blocking `BLMOVEM` move multiple list elements.
- `SUNIONCARD` and `SDIFFCARD` return union and difference cardinality.
- `BITOP` accepts `DIFF`, `DIFF1`, `ANDOR`, and `ONE`.
- `ZUNION`, `ZINTER`, `ZUNIONSTORE`, and `ZINTERSTORE` accept the `COUNT`
  aggregator.

### Streams

- `XDELEX`, `XACKDEL`, and extensions to `XADD` and `XTRIM` add `DELREF` and
  `ACKED` reference strategies.
- `XREADGROUP CLAIM min-idle-time` can return sufficiently idle pending entries
  and incoming entries in one read.
- `XNACK` lets a consumer explicitly release pending messages.
- `XREAD` and `XREADGROUP` accept `MAXCOUNT` and `MAXSIZE` to cap cumulative
  reply entry count and size.

### Core structures and notifications

- Array is a data structure.
- `OVERWRITTEN` reports complete value replacement, `TYPE_CHANGED` reports a
  key type change, and hash subkey notifications provide field-level events.
- Replicated `CF.LOADCHUNK` chunks prevent silent Cuckoo Filter loss after
  failover on the fixed maintenance releases.

## Search, JSON, and Time Series

### Vector and hybrid search

- `VSIM WITHATTRIBS` returns an element's JSON attribute, while `EPSILON` sets
  a maximum distance.
- `FT.HYBRID` combines results with RRF or LINEAR scoring. In its original
  behavior, post-`COMBINE` filtering is unavailable; default output contains
  only `key_id` and `score`; and `EXPLAINSCORE`, `YIELD_DISTANCE_AS`, and
  `WITHCURSOR` are unsupported.
- The `KNN` clause can request fewer candidates per shard, and
  `FT.PROFILE HYBRID` profiles hybrid queries.
- `search-default-scorer` sets the default text and tag scorer; `BM25STD` is
  the new default.
- `FT.ALIASLIST` enumerates aliases, Malay and Tagalog stemming is available,
  and `FT.CREATE` and `FT.ALTER` reject empty field names.

### JSON and Time Series

- `JSON.SET FPHA` selects the floating-point type for a homogeneous
  floating-point array.
- Range commands can apply multiple aggregators in one request. Time Series
  accepts NaN values and provides `COUNTNAN` and `COUNTALL`.
- `TS.NRANGE` and `TS.NREVRANGE` group multi-series results by timestamp;
  `TS.READ` supports optional blocking reads; and `TS.QUERYLABELS` discovers
  labels and their values.
- `TS.MRANGE` and `TS.MREVRANGE` accept `EXCLUDEEMPTY` to omit series with no
  samples.

## Operations quick reference

- Runtime memory tracking can be enabled only in non-clustered mode.
- `volatile-lrm` and `allkeys-lrm` select least-recently-modified eviction.
- `HOTKEYS` detects hot keys; `HOTKEYS HELP` is available from 8.6.1.
- `INFO KEYSIZES` reports size distributions for basic types, while
  `CLUSTER SLOT-STATS` reports per-slot key count, CPU time, and network I/O.
- `key-memory-histograms` collects per-type memory histograms and exposes
  database distribution metrics for lists, sets, hashes, and sorted sets.
- `BACKUP` provides node-side backup and restore based on multi-part AOF.
- Modules can read and write Redis configuration and selectively unsubscribe
  from keyspace notifications.
- `tls-auth-clients-user` enables client certificate authentication; failed
  attempts increment `acl_access_denied_tls_cert`. Server-to-server TLS can
  also authenticate peers by certificate.

Read the indexed reference before implementing an affected feature. It records
the exact command scope, maintenance floors, and topology-specific constraints.
