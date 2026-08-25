# Upgrades and Operations

Use this reference for upgrade sequencing, rollout availability, storage and
platform changes, write throttling, replica reads, telemetry, optimization,
memory, metrics, readiness, and Web UI operations.

## Upgrade sequencing

### Walk adjacent minors (`upgrade-guide`)

Before advancing to a new minor version, every node must reach the latest patch
of the immediately preceding minor. A node on 1.17 is compatible with 1.16 but
not 1.15; a 1.15 deployment must first reach 1.16.3 before moving to 1.17.

Apply the same rule to single-node deployments. Skipping an intermediate minor
can skip required data migrations even when mixed-node compatibility is not a
concern.

A safe plan is:

1. Inventory every server version and the target minor.
2. Upgrade all nodes to the latest patch of the current minor.
3. Advance exactly one minor and let required migrations complete.
4. Verify health, collection state, and query/write behavior.
5. Repeat until the target is reached.

### Upgrade client SDKs first (`upgrade-guide`)

Upgrade client SDKs before the cluster. Qdrant SDKs are tested for backward
compatibility with the latest three server minor versions, so newer clients can
remain compatible while servers roll forward. Exercise application tests
against the old server before beginning the server rollout.

### Determine whether rolling means zero downtime (`upgrade-guide`)

Zero-downtime rollout requires every collection to have replication factor 2
or greater and nodes to restart one at a time. A single-node cluster, or any
collection with replication factor 1, requires a short restart outage.

Do not infer availability from cluster node count alone; inspect each
collection's replication factor.

### Helm rollout (`upgrade-guide`)

Upgrading the Helm release makes Kubernetes roll the Qdrant StatefulSet
automatically:

```bash
helm upgrade qdrant qdrant/qdrant --version <target-version> -n <namespace>
```

The automatic StatefulSet rollout does not waive the adjacent-minor or replica
requirements. Pin an appropriate chart target and observe one pod transition at
a time.

## Storage and platform changes

### Gridstore default (since 1.15.0)

New deployments use Gridstore rather than RocksDB as the default embedded
storage backend. This release has no major API- or index-breaking upgrade
changes, but upgrades from older releases are still recommended one version at
a time. Distinguish new-deployment defaults from the backend already used by an
existing installation.

### Larger ARM64 page sizes (since 1.19.0)

Qdrant uses jemalloc 5.3.1, adding support for page sizes larger than 4 KB on
`aarch64`. Re-test ARM64 images and hosts that use larger pages; an older
allocator assumption should no longer be treated as a platform blocker.

## Write-load control

### Queueing and indexed-only throttling (since 1.17.0)

Shards queue pending changes and apply back pressure when the queue fills,
preventing heavy ingestion or replica recovery from creating runaway load.

For latency-sensitive indexed-only searches, enable the `prevent_unoptimized`
optimizer setting. It throttles writes toward the indexing rate so large
unoptimized segments do not accumulate. Balance ingestion throughput against
the latency guarantee expected by indexed-only reads.

The queue default later dropped sharply; review the collection and writes
reference before relying on backlog capacity.

## Replica reads

### Delayed read fan-out (since 1.17.0)

Configure a latency threshold after which a read sends a second request to
another replica. Qdrant uses whichever response arrives first. This reduces
tail latency from a slow replica without sending every read to multiple
replicas immediately.

Choose the delay from observed latency distributions. A threshold that is too
short amplifies ordinary traffic; one that is too long does not protect the
tail.

### Deterministic read routing (since 1.19.0)

Supply a routing token when read requests need stable deterministic routes.
Use it for locality or reproducibility requirements while preserving retry
handling for unavailable routes and changing cluster topology.

## Telemetry and optimization

### Cluster-wide telemetry (since 1.17.0)

`/cluster/telemetry` returns information for all peers, avoiding a separate
`/telemetry` request to each node. It covers cluster-wide activity including
leader elections, resharding, and shard transfers.

Prefer the cluster endpoint for an operator view. Retain peer-specific queries
only when diagnosing a node-level detail not evident in the aggregate.

### Segment optimization monitoring (since 1.17.0)

`/collections/{collection_name}/optimizations` reports cluster-wide
optimization status and details for current and past operations. The Web UI's
Optimizations tab presents status, timelines, and per-cycle task durations.

Use this data to distinguish slow queries caused by active optimization from a
persistent index or hardware problem, and to correlate write load with
optimizer backlog.

### Collection memory monitoring (since 1.18.0)

Inspect disk, RAM, and operating-system page-cache usage by component,
including vectors, payload, and indexes. Values aggregate across the cluster.
The same data is available by API and in the collection detail page's
**Memory** tab.

Check component-level use after changing quantization, HNSW inline storage,
payload indexes, mmap defaults, or memory policy.

### Per-collection API metrics (since 1.18.0)

Pass `per_collection=true` to add a `collection` label to
`rest_responses_*` and `grpc_responses_*`. This exposes per-collection request
counts, failures, and response durations.

```http
GET /metrics?per_collection=true
```

The added label increases metrics cardinality. Enable it deliberately and
confirm the monitoring backend can absorb the number of collections.

## Readiness and live operations

### Bootstrap readiness (since 1.19.0)

`/readyz` no longer reports a false positive for a freshly bootstrapped peer.
Use the endpoint for rollout readiness, but continue to validate application
queries and cluster membership before declaring a migration complete.

### Resharding progress in the Web UI (since 1.19.0)

The Web UI displays resharding progress. Use it as an operator view alongside
cluster telemetry and application checks. Shard-key queries can continue during
live resharding where the corresponding fix is present.

### Point search in the Web UI (since 1.17.0)

The redesigned point-search interface can:

- find points similar to a selected point;
- filter by payload values; and
- locate a point by ID.

Use it for inspection and diagnosis. Reproduce production issues through the
same API parameters when the UI's interactive request differs from application
traffic.

## Upgrade validation checklist

- Upgrade the SDK, then every server through adjacent minors and latest patch
  prerequisites.
- Confirm every collection's replication factor before promising zero downtime.
- Observe StatefulSet pod order rather than assuming a Helm command completed
  the application migration.
- Record existing storage backends and test new-deployment defaults separately.
- Load test queue pressure and `prevent_unoptimized` with ingestion and recovery.
- Tune delayed fan-out from measured latency and verify deterministic routes.
- Compare cluster telemetry, optimizer history, collection memory, and
  per-collection request metrics before and after rollout.
- Verify readiness, resharding, shard-key queries, and Web UI inspection on a
  staged cluster.
- Re-test ARM64 targets with their actual page size and container image.
