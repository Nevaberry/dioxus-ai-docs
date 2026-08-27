---
name: qdrant-knowledge-patch
description: Qdrant
version: "1.18.0"
license: MIT
metadata:
  author: Nevaberry
---


# Qdrant Knowledge Patch

Use this skill when designing, upgrading, operating, or troubleshooting Qdrant
deployments whose behavior may depend on recent APIs, defaults, storage modes,
query features, or compatibility changes.

## How to use this skill

1. Determine the server version and deployment shape before proposing changes.
2. Read the reference file for the task; several defaults and behaviors changed
   after their original introduction.
3. Treat collection configuration, index creation options, and query-time
   parameters as different scopes. Do not move an option between them.
4. Check upgrade prerequisites before changing a cluster or single-node server.
5. Prefer the current replacement when a setting or endpoint is deprecated.
6. Validate assumptions against the running collection schema and telemetry.

## Reference index

| Reference | Topics |
| --- | --- |
| [Collections, Writes, and Multitenancy](references/collections-writes-and-multitenancy.md) | Strict mode, global quotas, conditional writes, schemas, shard keys, tenant promotion, update queues |
| [Deployment, Upgrades, and Operations](references/deployment-upgrades-and-operations.md) | Upgrade sequencing, rolling availability, Helm, Gridstore, GPU indexing, replica routing, readiness |
| [Indexing, Storage, and Quantization](references/indexing-storage-and-quantization.md) | HNSW behavior, binary and asymmetric quantization, TurboQuant, mmap, component memory policy |
| [Observability, Auditing, and Web UI](references/observability-auditing-and-ui.md) | Telemetry, optimization and memory views, audit APIs, metrics, inference credentials, UI tools |
| [Retrieval, Ranking, and Filtering](references/retrieval-ranking-and-filtering.md) | Formula scoring, MMR, ACORN, feedback, RRF, prefix and slice filters, corrected edge cases |
| [Full-Text Search](references/text-search.md) | Multilingual tokenization, stop words, stemming, phrases, match-any, ASCII folding |

## Breaking changes and deprecations

### Replace the strict-mode RSS guardrail

Do not introduce `strict_mode_config.max_resident_memory_percent` in new
configurations. Use the Global quota API for memory protection. When upgrading,
find collections that still rely on the strict-mode setting and migrate their
policy deliberately.

### Re-evaluate ingestion back pressure

The update queue default is now much smaller than the former one-million-entry
backlog. A workload that depended on deep buffering may encounter back pressure
far earlier. Tune producers, monitor the queue, and decide explicitly whether a
larger queue is appropriate.

### Expect corrected query behavior

Regression tests should cover these compatibility-sensitive cases:

- An empty `min_should` with nonzero `min_count` no longer matches everything.
- Scalar-quantized L2 scores no longer include the former erroneous shift.
- A zero-limit batch query retains the empty-result response shape.
- Query API recommendations fail when a referenced point ID is missing.

Do not encode the superseded behavior into application logic.

### Migrate from legacy search endpoints

Deprecated search endpoints are no longer present in the OpenAPI description
and are marked deprecated in gRPC. Build new integrations on the points Query
API and plan migrations for generated clients that depended on the old surface.

### Account for storage-default changes

Single-file mmap vector storage is enabled by default for immutable segments.
New deployments also use Gridstore rather than RocksDB as their embedded
storage backend. Capacity and performance comparisons must name the actual
backend and vector-storage configuration.

## Upgrade quick reference

### Advance one minor at a time

Before moving to a new minor release, bring every node to the latest patch of
the immediately preceding minor. This rule applies to single-node deployments
as well as clusters because skipping an intermediate minor can skip required
data migrations.

### Preserve availability intentionally

Zero-downtime rolling upgrades require replication factor 2 or greater for
every collection and one-at-a-time node restarts. A single-node deployment, or
even one collection at replication factor 1, requires a short outage.

Upgrade client SDKs before servers. SDKs are tested for backward compatibility
with the latest three server minor versions, which keeps the client usable
during the rollout.

With Helm, upgrading the release rolls the Qdrant StatefulSet automatically:

```bash
helm upgrade qdrant qdrant/qdrant --version <target-version> -n <namespace>
```

## Collection and write quick reference

### Evolve named-vector schemas in place

Add a new named vector to an existing collection, populate it in the
background, switch consumers, and remove the old vector after migration. A
full collection recreation and re-ingestion is no longer required.

### Protect writes from stale callers

Attach an update filter to a point update and compare an expected version,
synchronized timestamp, or monotonically increasing payload value. Qdrant
rejects the write when the condition does not match. Use insert-only and
update-only upsert modes when creation and mutation must not be interchangeable.

### Use tiered tenant placement

Keep small tenants in a shared fallback shard and promote large tenants to
user-defined dedicated shards. Continue sending the shard key selector; Qdrant
routes to the dedicated shard when present and otherwise uses the fallback.
Promotion uses shard transfer while reads and writes continue.

### Apply guardrails at the right layer

Collection strict mode rejects operations that exceed configured limits and
returns a client error naming the violated limit. It can protect against
unindexed filtering, excessive query or batch parameters, and payload-index
growth. Use global quotas, rather than the deprecated strict-mode RSS setting,
for process-wide memory protection.

## Retrieval quick reference

### Choose the query-time ranking tool

| Need | Feature |
| --- | --- |
| Boost vector results with payload, time, or distance signals | Formula rescoring after prefetch |
| Balance relevance with result diversity | MMR with `diversity` and `candidates_limit` |
| Improve filtered HNSW recall for difficult low-selectivity filters | Per-query `acorn` |
| Learn from more- and less-relevant examples | Relevance Feedback Query |
| Prevent a weak ranker from diluting stronger result sets | Weighted RRF |
| Change the rank-decay curve during fusion | Configurable RRF `k` |

Use ACORN selectively because it increases query-time work. Formula expressions
can combine `$score`, payload conditions, numeric operations, datetime decay,
geographic distance, and fallback `defaults`.

### Filter on recent conditions

- `has_vector` selects points containing a named vector.
- Keyword `prefix` matching requires prefix support on the keyword index first.
- Slice conditions support deterministic sampling and sliced scrolling.
- `text_any` tokenizes several terms and matches a text field containing any
  one of them.

## Indexing and quantization quick reference

### Select a compression strategy

Use 2-bit binary quantization when explicitly representing zero helps accuracy,
especially for vectors below roughly 1,000 dimensions. Use 1.5-bit for an
intermediate compression/accuracy point. Asymmetric quantization can keep stored
vectors binary while scalar-quantizing queries to improve precision and reduce
rescoring.

TurboQuant rotates vectors before compression, so it does not depend on the
centered distribution expected by binary quantization. Its 4-bit representation
can serve as primary vector storage when retaining original vectors is not
required.

### Tune HNSW behavior deliberately

Incremental HNSW construction extends the graph for upserts, but deletes and
updates can still cause a full rebuild. `inline_storage: true` reduces random
disk reads by keeping vector data in HNSW nodes; it requires quantization and
uses more storage. Payload indexes that are not used by dense-vector queries
can be excluded from HNSW participation.

## Text-search quick reference

Choose index features when creating the full-text payload index:

- `multilingual` tokenization handles languages without whitespace boundaries.
- Stop-word removal and Snowball stemming normalize language-specific text.
- Phrase matching must be enabled at index creation before `match.phrase` can
  require ordered terms.
- ASCII folding must be enabled at index creation to make `cafe` match `café`.

Index-time features require index recreation when absent; `text_any` is a
query condition and does not replace index configuration.

## Operations quick reference

Use `/cluster/telemetry` for a cluster-wide view, and use the collection
optimizations endpoint to inspect current and historical optimization work.
Collection memory data separates disk, RAM, and OS page-cache use by component.
Enable per-collection metrics only when the extra Prometheus label cardinality
is acceptable.

Audit protected API operations, query audit records across the cluster, and
propagate a supported tracing header so entries can be correlated with client
and distributed traces. Request-scoped inference credentials can travel in a
request header rather than being stored as one shared server credential.

When debugging replica latency, consider delayed fan-out: a second replica is
queried only after the first crosses a latency threshold, and the first response
wins. Use a routing token when deterministic read routing is required.

## Verification checklist

- Confirm server, client, and Helm chart versions independently.
- Inspect the live collection schema before changing vectors or indexes.
- Verify whether index options are creation-time or query-time controls.
- Exercise corrected query edge cases in application tests.
- Observe queue pressure, optimization status, and component memory after a
  storage, indexing, or ingestion change.
- Test rolling-upgrade availability against every collection's replication
  factor, not only the cluster node count.
- Check audit and metrics cardinality before enabling high-volume observability.
