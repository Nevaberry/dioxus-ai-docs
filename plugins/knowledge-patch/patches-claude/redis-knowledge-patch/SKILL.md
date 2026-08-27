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
Redis Open Source. Start with release and topology discovery, check the
security floor and ACL implications, and then open the reference for the
affected command family or operational task.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-upgrades.md](references/security-and-upgrades.md) | Security floors, integrated components, upgrades, ACL scope, TLS authentication, tested platforms |
| [data-structures-and-commands.md](references/data-structures-and-commands.md) | Arrays, hashes, strings, counters, lists, sets, streams, bit operations, sorted sets, notifications, Cuckoo Filters |
| [search-json-and-timeseries.md](references/search-json-and-timeseries.md) | Vector and hybrid Search, aliases and stemming, JSON arrays, Time Series queries and aggregation |
| [operations-cluster-and-modules.md](references/operations-cluster-and-modules.md) | Memory, eviction, telemetry, backup, atomic slot migration, module hooks |

## Working method

1. Identify the exact Redis release, deployment topology, persistence mode,
   and enabled components before applying version-sensitive advice.
2. Check the security floor for the deployed minor line. Do not treat the
   patch number from a different minor line as an equivalent fix.
3. Re-audit ACL rules when moving from standalone modules or Redis Stack to
   integrated Redis components.
4. Check persistence and cluster caveats before enabling stream idempotency,
   backup workflows, or slot migration.
5. Open the topic reference before implementing an affected command. It holds
   maintenance-release floors and restrictions omitted from this quick view.

## Breaking, security, and compatibility checks

### Patch security-sensitive deployments first

Choose a fixed release from the deployed minor line. Important minimums
include:

| Issue | Fixed release or releases |
| --- | --- |
| `redis-check-aof` stack overflow with RCE impact | 8.0.2 |
| HyperLogLog out-of-bounds writes | 8.0.3 |
| Four Lua memory and isolation issues | 8.0.4 |
| Probabilistic-filter memory-safety failures | 8.0.5 |
| CRLF error-reply injection | 8.0.6 |
| `XACKDEL` stack overflow with RCE impact | 8.2.3 |
| Response injection | 8.2.5, 8.4.2, or 8.6.1 |
| Five RCE-capable invalid-memory paths | 8.2.6, 8.4.3, or 8.6.3 |
| Module-string reply-copy use-after-free | 8.6.2 |
| Stream consumer-group `RESTORE` use-after-free | 8.2.8, 8.4.5, or 8.6.5 |
| `MSETEX` ACL key-pattern bypass | 8.4.4 |
| `SENTINEL SET` configuration injection | 8.6.4 |
| Crafted RedisBloom and TDigest `RESTORE` writes | 8.8.1 |
| Redis 8.10 memory-safety and TLS authentication issues | 8.10.1 |

The five-path RCE group spans client unblock, `RESTORE`, Lua, Time Series,
and probabilistic structures. The 8.10.1 group includes CMSketch RDB loading,
TopK cleanup, the TLS pending-data list, `SLOT_INFO` RDB loading, three Vector
Set paths, blocked-client reprocessing, and an embedded-NUL certificate bypass.

### Account for integrated components

Search, JSON, Time Series, Bloom, Cuckoo, Count-min sketch, Top-k, and t-digest
are integral components beginning in Redis 8. Binary distributions include
them, `redis-full.conf` loads them all, and Vector Set is preview functionality.

Replication and persistence upgrades can start from module-free Redis, Redis
using the former standalone modules, or Redis Stack 7.2 or 7.4. Plan component
packaging and ACL changes as part of the same migration.

### Re-audit ACLs

Broad categories such as `@read` and `@write` include commands from the
integrated components. Replace unintended broad grants with narrower
`@search`, `@json`, `@timeseries`, `@bloom`, `@cuckoo`, `@cms`, `@topk`, and
`@tdigest` rules.

Search index access also depends on key patterns: a user's patterns must cover
a superset of the index prefixes. Multi-key Time Series reads fail if any
matching key is unreadable, while `TS.QUERYINDEX` reads metadata without
requiring read access to those keys.

### Remove obsolete vector assumptions

The proprietary LeanVec and LVQ Intel optimizations are absent from Redis Open
Source starting in 8.2.1. Redis 8.2 provides compressed `SVS-VAMANA`; 8.2.2
allows the `BUILD_INTEL_SVS_OPT` build flag for Intel optimizations.

### Respect persistence and migration caveats

`XADD IDMPAUTO` and `IDMP` arrived in Redis 8.6. Redis 8.6.0 warns against
combining them with `appendonly yes` and `aof-use-rdb-preamble no`; Redis 8.6.2
fixes AOF rewrite and restoration of idempotency state.

`CLUSTER MIGRATION` moves slots atomically, but affected Search and Time Series
multi-key queries can still return partial or duplicate results while a
migration is in progress.

## High-value command changes

### Strings, counters, hashes, and sets

- `DIGEST`, `DELEX`, and `SET` extensions support atomic compare-and-set and
  compare-and-delete flows on strings.
- `MSETEX` atomically writes multiple string keys and updates expiration.
- `INCREX` combines integer or floating-point increments, bounds, and
  expiration for window-counter rate limiting.
- Compact hashes share field names among keys with the same schema; `HIMPORT`
  provides high-throughput bulk insertion for that encoding.
- `SUNIONCARD` and `SDIFFCARD` return union and difference cardinalities.

### Lists and streams

- `LMOVEM` and blocking `BLMOVEM` move multiple list elements.
- `XDELEX`, `XACKDEL`, and extensions to `XADD` and `XTRIM` add `DELREF` and
  `ACKED` deletion-reference strategies.
- `XREADGROUP CLAIM min-idle-time` combines sufficiently idle pending entries
  and incoming entries in one read.
- `XADD IDMPAUTO` and `IDMP` provide at-most-once production;
  `stream-idmp-duration` and `stream-idmp-maxsize` supply defaults.
- `XNACK` lets a consumer explicitly release pending messages.
- `XREAD` and `XREADGROUP` accept `MAXCOUNT` and `MAXSIZE` reply bounds.

### Core structures and notifications

- Array is a Redis data structure.
- `BITOP` supports `DIFF`, `DIFF1`, `ANDOR`, and `ONE`.
- `ZUNION`, `ZINTER`, `ZUNIONSTORE`, and `ZINTERSTORE` accept the `COUNT`
  aggregator.
- `OVERWRITTEN` reports full replacement, `TYPE_CHANGED` reports a type
  change, and hash subkey notifications emit field-level events.
- Replicated `CF.LOADCHUNK` chunks prevent silent Cuckoo Filter loss after
  failover on fixed maintenance releases.

## Search, JSON, and Time Series

### Vector and hybrid Search

- `VSIM WITHATTRIBS` returns an element's JSON attribute; `EPSILON` supplies a
  maximum distance.
- `FT.HYBRID` combines result sets with RRF or LINEAR scoring.
- In the original Redis 8.4 behavior, filtering after `COMBINE` is unavailable,
  the default response contains only `key_id` and `score`, and `EXPLAINSCORE`,
  `YIELD_DISTANCE_AS`, and `WITHCURSOR` are unsupported.
- A newer `KNN` argument requests fewer candidates per shard, and
  `FT.PROFILE HYBRID` profiles hybrid queries.
- `search-default-scorer` sets the default text and tag scorer; `BM25STD` is
  the new default.
- `FT.ALIASLIST` enumerates index aliases, and Search supports Malay and
  Tagalog stemming.
- `FT.CREATE` and `FT.ALTER` reject empty field names.

### JSON and Time Series

- `JSON.SET FPHA` selects the floating-point type for a homogeneous
  floating-point array.
- `TS.RANGE`, `TS.REVRANGE`, `TS.MRANGE`, and `TS.MREVRANGE` can apply multiple
  aggregators in one command.
- Time Series accepts NaN and provides `COUNTNAN` and `COUNTALL`.
- `TS.NRANGE` and `TS.NREVRANGE` query multiple series grouped by timestamp.
- `TS.READ` optionally blocks while reading from time series.
- `TS.QUERYLABELS` discovers labels and their values.
- `TS.MRANGE` and `TS.MREVRANGE EXCLUDEEMPTY` omit series with no samples.

## Operations quick reference

- Runtime memory tracking can be enabled only in non-clustered mode.
- `volatile-lrm` and `allkeys-lrm` select least-recently-modified eviction.
- `HOTKEYS` detects hot keys; `HOTKEYS HELP` is available from 8.6.1.
- `INFO KEYSIZES` reports size distributions for basic data types.
- `CLUSTER SLOT-STATS` reports per-slot key count, CPU time, and network I/O.
- `key-memory-histograms` collects per-type histograms and exposes database
  distribution metrics for lists, sets, hashes, and sorted sets.
- `BACKUP` performs node-side backup and restore using multi-part AOF.
- Modules can read and write Redis configuration and selectively unsubscribe
  from keyspace notifications.
- `tls-auth-clients-user` maps client certificates to a user; failed attempts
  increment `acl_access_denied_tls_cert`.
- Server-to-server TLS connections can authenticate peers by certificate.

Read the indexed reference before implementing any affected behavior. The
references preserve exact maintenance floors, ACL boundaries, persistence
warnings, topology restrictions, and command-specific constraints.
