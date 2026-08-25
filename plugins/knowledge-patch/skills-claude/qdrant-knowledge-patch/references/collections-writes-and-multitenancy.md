# Collections, Writes, and Multitenancy

## Collection strict mode

New collections default to Strict Mode (since 1.13.0). The collection-level
`strict_mode_config` rejects expensive requests that exceed its limits and
returns a client error identifying the exceeded limit. Guardrails include:

- unindexed filtering for retrieval;
- oversized point or search batches;
- excessive filter conditions;
- timeouts, `hnsw_ef`, and oversampling.

`enabled` is a dynamic toggle, and existing collections can be updated with
`PATCH`:

```http
PATCH /collections/{collection_name}
{
  "strict_mode_config": {
    "enabled": true,
    "unindexed_filtering_retrieve": true
  }
}
```

Strict mode can also cap the number of payload indexes (since 1.16.0).

Two later guardrails are `max_resident_memory_percent`, which rejects
memory-consuming writes after process RSS exceeds the configured percentage of
total system memory, and `search_max_batchsize`, which caps the query count in a
batch-search request (since 1.18.0):

```http
PATCH /collections/{collection_name}
{
  "strict_mode_config": {
    "max_resident_memory_percent": 90,
    "search_max_batchsize": 64
  }
}
```

The Global quota API supersedes `max_resident_memory_percent`; that strict-mode
setting is deprecated (since 1.19.0). Use global quotas for new memory policies
and migrate configurations that depend on the old RSS limit.

## Conditional and mode-restricted writes

Point updates can include an update filter that must match before Qdrant applies
the write (since 1.16.0). A failed condition rejects the update. Compare an
expected version field, synchronized timestamp, or other monotonically
increasing payload value to prevent a stale writer or background re-embedding
job from overwriting newer data.

Upserts can be restricted to insert-only or update-only operation (since
1.17.0). Insert-only prevents an intended create from overwriting an existing
point; update-only prevents an intended update from silently creating one.

## Named-vector schema evolution

Named vectors can be added to or removed from an existing collection without
recreating and re-ingesting it (since 1.18.0). For an embedding migration:

1. Add the new vector field.
2. Populate it in the background.
3. Move reads and writes to the new field.
4. Remove the old field after migration.

## Collection metadata

Collections can carry custom metadata (since 1.16.0). The Web UI later added
display and editing support; see the observability and UI reference.

## Tiered multitenancy

A multitenant collection can combine a shared fallback shard for small tenants
with user-defined dedicated shards for large tenants (since 1.16.0). Requests
provide a shard key selector. Qdrant routes to that tenant's dedicated shard
when it exists and otherwise uses the fallback shard.

Promote a growing tenant from the fallback to a dedicated shard through shard
transfer. Reads and writes continue during promotion, so application routing
does not need separate shared-versus-dedicated logic.

An API operation lists all user-defined shard keys (since 1.17.0), letting
applications and operators discover the current custom-sharding layout.

Queries specifying shard keys continue to work while resharding is in progress
(fixed in 1.18.3). Do not reject or suppress those application queries merely
because live resharding is active.

## Write-load queue and optimizer throttling

Shards queue pending changes and apply back pressure when the queue is full
(since 1.17.0). The original capacity was up to one million changes. For
latency-sensitive indexed-only searches, `prevent_unoptimized` throttles writes
toward the indexing rate so large unoptimized segments do not accumulate.

The default update queue length later dropped from one million to 200 (since
1.19.0). Workloads that relied on a deep backlog can therefore see back pressure
much earlier. Reassess producer concurrency and explicit queue configuration
when upgrading.
