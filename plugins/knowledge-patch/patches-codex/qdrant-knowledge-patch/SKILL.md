---
name: qdrant-knowledge-patch
description: Qdrant
version: "1.18.0"
license: MIT
metadata:
  author: Nevaberry
---


# Qdrant Knowledge Patch

Use this skill when implementing, reviewing, upgrading, or operating Qdrant.
Inspect the deployed server version, collection configuration, client version,
and cluster topology before applying version-dependent guidance.

## How to use this skill

1. For an upgrade, read the upgrade and operations reference first.
2. For an API or configuration change, load the reference for that topic.
3. Treat changed defaults, removed endpoints, and corrected result semantics as
   migration work, not as transparent implementation details.
4. Test retrieval quality after changing quantization, ranking, filtering, or
   HNSW storage because the tradeoffs are workload-dependent.
5. Test rolling upgrades against the actual replication factor and node path.

## Reference index

| Reference | Topics |
|---|---|
| [Auditing and inference](references/auditing-and-inference.md) | Protected-operation audit logs, cluster-wide audit queries, trace correlation, request-scoped inference credentials |
| [Collections and writes](references/collections-and-writes.md) | Strict mode, multitenancy, schemas, conditional writes, shard keys, update queues, memory policy, collection metadata |
| [Full-text search](references/full-text-search.md) | Multilingual tokenization, stop words, stemming, phrases, match-any, ASCII folding, keyword prefixes |
| [Upgrades and operations](references/upgrades-and-operations.md) | Adjacent-minor upgrades, rolling availability, telemetry, memory and metrics, readiness, UI operations, platform changes |
| [Vector search and ranking](references/vector-search-and-ranking.md) | HNSW, quantization, formula scoring, MMR, ACORN, relevance feedback, RRF, sparse IDF, corrected query behavior |

## Upgrade blockers and changed behavior

### Walk every adjacent minor

Do not skip minor releases. Bring all nodes to the latest patch of the current
minor, move to the immediately following minor, and repeat. Upgrade client SDKs
before servers. For a rolling upgrade, restart one node at a time and verify
that every collection has at least two replicas; otherwise schedule an outage.

### Replace the resident-memory strict-mode guard

Do not add new uses of `strict_mode_config.max_resident_memory_percent`. Move
memory enforcement to the Global quota API. Preserve the old field only while
migrating a deployment that still accepts it.

### Re-evaluate ingestion back pressure

The update-queue default is now 200 rather than one million. Explicitly size
the queue when a workload depended on a large write backlog, and monitor write
latency and rejection behavior during upgrades.

### Remove reliance on corrected edge cases

Audit code and tests for these behavior changes:

- An empty `min_should` with nonzero `min_count` no longer matches everything.
- Scalar-quantized L2 scores no longer include the erroneous shift.
- A zero-limit batch query preserves the empty-result response shape.
- Recommend queries error when a referenced point ID is absent.
- `/readyz` no longer returns a false positive for a fresh peer.

### Migrate from legacy search endpoints

Deprecated search endpoints are gone from the OpenAPI specification and are
deprecated in gRPC. Build new retrieval flows on the Query API and update
generated clients that depended on the removed OpenAPI paths.

## Collection safety quick reference

### Enable strict mode deliberately

New collections enable strict mode by default. Configure it to reject costly
unindexed filters, oversized write or search batches, excessive filter clauses,
timeouts, `hnsw_ef`, oversampling, too many payload indexes, and memory-heavy
writes. Rejections are client errors that identify the exceeded limit.

The `enabled` flag is dynamic, and existing collections can be updated with
`PATCH`. Keep the limits aligned with the indexes and request shapes used by
the application.

```http
PATCH /collections/{collection_name}
{
  "strict_mode_config": {
    "enabled": true,
    "search_max_batchsize": 64
  }
}
```

### Protect writes from stale or wrong operation types

Use conditional point updates when a payload version, timestamp, or monotonic
value must still match. Use insert-only mode for creates and update-only mode
for changes so an upsert cannot silently perform the opposite operation.

### Plan named-vector migrations in place

Add a new named vector to the existing schema, populate it in the background,
switch reads, and then remove the old field. Use `has_vector` when mixed points
temporarily contain different named vectors.

### Choose shared and dedicated tenant shards

Keep small tenants on the fallback shard and create dedicated shard keys for
large tenants. Promotion uses shard transfer while reads and writes continue;
applications can keep sending the same shard-key selector.

## Retrieval quick reference

### Prefer Query API composition

Use prefetch plus a formula to combine `$score`, payload conditions, numeric
expressions, datetime decay, or geographic decay. Supply `defaults` for absent
payload inputs. Use weighted RRF when constituent rankers have unequal value,
and configure the RRF `k` constant for the desired rank decay.

### Add diversity with MMR

MMR reranks a nearest-neighbor candidate set. `diversity` ranges from `0.0`
for relevance to `1.0` for diversity, and `candidates_limit` controls the
initial pool. Keep the candidate pool large enough for diversification.

```json
{
  "query": {
    "nearest": [0.01, 0.45, 0.67, 0.12],
    "mmr": {"diversity": 0.5, "candidates_limit": 100}
  },
  "limit": 10
}
```

### Use ACORN only on affected filters

Set the query-time `acorn` option for filtered HNSW searches where several
low-selectivity filters hide direct graph neighbors. It needs no index rebuild,
but its broader traversal adds runtime overhead.

### Select quantization by distribution and accuracy needs

- Binary 1-bit maximizes compression; 1.5-bit and 2-bit modes trade some space
  for accuracy, with 2-bit explicitly representing zero.
- Asymmetric quantization can combine binary stored vectors with
  scalar-quantized queries to improve precision without restoring full storage.
- TurboQuant rotates vectors before compression, avoiding binary
  quantization's centered-distribution assumption and supporting cosine, dot,
  and L2 distance.
- Four-bit TurboQuant may be primary storage when retaining original vectors is
  unnecessary.

Measure recall, score behavior, memory, disk, and latency with production-like
queries before selecting a primary representation.

### Tune HNSW storage and construction

GPU-enabled container images can build HNSW indexes on Vulkan-capable hardware,
including multiple GPUs and quantized vectors; confirm detection in the logs.
Incremental graph extension avoids a rebuild for new-point upserts, but deletes
and updates still trigger a full rebuild.

With quantization enabled, `inline_storage: true` stores vectors in HNSW nodes,
reducing random reads and permitting implicit rescoring at the cost of more
storage. Disable per-field HNSW participation for payload indexes never used by
dense-vector filtering.

## Text-search quick reference

Configure text analysis when creating the payload index:

- `multilingual` tokenization handles languages without whitespace boundaries.
- Stop-word removal and Snowball stemming normalize language-specific input.
- `phrase_matching: true` is required before `match.phrase` can be queried.
- `ascii_folding: true` lets unaccented queries match accented indexed text.
- `text_any` replaces a client-built `should` list for any-token matching.
- Keyword prefix matching requires prefix support on the keyword index first.

These options change indexing or query semantics. Reindex or create the index
with the required capability before relying on it.

## Operations quick reference

### Observe the cluster, not isolated peers

Use `/cluster/telemetry` for peer-wide activity, the collection optimization
endpoint for current and historical optimization work, and collection memory
reporting for disk, RAM, and page-cache use by vectors, payload, and indexes.
Use `per_collection=true` on metrics only when the added collection label is
acceptable for the monitoring system's cardinality.

### Control read latency and routing

Delayed fan-out sends a second request only after the first replica exceeds a
latency threshold and uses the first response. A routing token produces stable
read routes when deterministic routing matters.

### Keep audit and request correlation connected

Enable protected-operation audit logging, query entries across all nodes, and
pass `x-request-id`, `x-tracing-id`, or `traceparent` to correlate audited calls
with client and distributed traces. Pass external inference credentials in the
request header when keys must be scoped per inference request.

## Verification checklist

- Confirm the server and client versions before using an option or endpoint.
- Snapshot collection schemas, strict-mode settings, shard keys, and memory
  policies before an upgrade.
- Exercise insert-only, update-only, conditional-update, and rejection paths.
- Compare recall and score distributions after quantization or ranking changes.
- Test multilingual, phrase, folded, and prefix text behavior against the
  actual index configuration.
- Validate rolling availability with the real replication factors.
- Inspect telemetry, optimizations, memory, metrics, audit queries, and
  readiness during a staged rollout.
- Regenerate API clients after endpoint deprecations or specification changes.
