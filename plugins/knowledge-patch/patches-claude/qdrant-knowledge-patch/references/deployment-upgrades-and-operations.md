# Deployment, Upgrades, and Operations

## Adjacent-minor upgrade compatibility

Before advancing to a new minor, bring every node to the latest patch of the
immediately preceding minor. For example, a 1.17 node is compatible with 1.16
but not 1.15, and a 1.15 deployment must reach 1.16.3 before moving to 1.17.
Single-node deployments have the same constraint because skipping the
intermediate minor can skip required data migrations.

## Replica-aware rolling upgrades

An upgrade is zero-downtime only when every collection has replication factor
2 or greater and nodes restart one at a time. A single-node cluster, or any
collection with replication factor 1, requires a short restart outage.

Upgrade client SDKs before the cluster. Qdrant SDKs are tested for backward
compatibility with the latest three server minor versions, which keeps clients
compatible through the server rollout.

Upgrading the Helm release automatically rolls the Qdrant StatefulSet:

```bash
helm upgrade qdrant qdrant/qdrant --version <target-version> -n <namespace>
```

## Gridstore deployment default

New deployments use Gridstore rather than RocksDB as the default embedded
storage backend (since 1.15.0). That release introduced no major API- or
index-breaking upgrade change, but upgrades from older releases should still
advance one version at a time.

## Vulkan GPU HNSW indexing

On-premises deployments can build HNSW indexes on modern Vulkan-capable GPUs
through preconfigured GPU container images (since 1.13.0). This works across
major GPU vendors, supports concurrent segment indexing on multiple GPUs, and
supports all Qdrant quantization options and data types. Check the logs to
confirm GPU detection and use rather than assuming the container found a GPU.

## Replica reads and tail latency

Delayed read fan-out sends a second request to another replica only after the
initial replica crosses a configured latency threshold, then uses whichever
response arrives first (since 1.17.0). This reduces slow-replica tail latency
without querying several replicas immediately for every read.

Read requests can also carry a routing token for deterministic read routes
(since 1.19.0). Use the token when stable routing matters rather than relying on
incidental replica selection.

## Resharding with custom shard keys

Queries specifying shard keys no longer fail solely because resharding is in
progress (fixed in 1.18.3). This makes live resharding compatible with
applications that continuously use custom sharding.

## ARM64 page-size support

Qdrant uses jemalloc 5.3.1, which supports page sizes larger than 4 KB on
`aarch64` systems (since 1.19.0). This removes the prior allocator limitation on
ARM64 environments configured with larger pages.

## Bootstrap readiness

`/readyz` no longer returns a false positive for a freshly bootstrapped peer
(fixed in 1.19.0). Orchestration should still gate traffic on readiness, but it
can rely on the corrected bootstrap signal.
