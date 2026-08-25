# Collections and Writes

Use this reference for collection guardrails, schemas, multitenancy, point
mutation semantics, shard-key administration, memory policy, and collection
management.

## Strict mode and quotas

### Collection strict mode (since 1.13.0)

`strict_mode_config` rejects requests that exceed collection-level safety
limits. It can guard against unindexed filtering, oversized batches or
payloads, too many filter conditions, long timeouts, excessive `hnsw_ef`, and
oversampling. A rejected request is a client error that identifies the limit.

New collections enable strict mode by default. `enabled` is a dynamic toggle;
use `PATCH` to change an existing collection.

```http
PATCH /collections/{collection_name}
{
  "strict_mode_config": {
    "enabled": true,
    "unindexed_filtering_retrieve": true
  }
}
```

Choose limits from real request sizes and indexed fields. A low unindexed
filtering limit is useful only if the application creates the payload indexes
needed by its filters.

### Payload-index count limit (since 1.16.0)

Strict mode can cap how many payload indexes a collection may have. Set this
guardrail where dynamic index creation could otherwise consume unbounded disk,
memory, or HNSW-related work.

### Memory and batch guardrails (since 1.18.0)

`search_max_batchsize` limits the number of queries accepted by a batch-search
request. `max_resident_memory_percent` rejects memory-consuming writes after
process resident memory exceeds the configured percentage of total system
memory.

```http
PATCH /collections/{collection_name}
{
  "strict_mode_config": {
    "max_resident_memory_percent": 90,
    "search_max_batchsize": 64
  }
}
```

### Move memory enforcement to global quotas (since 1.19.0)

The Global quota API supersedes strict mode's
`max_resident_memory_percent`, which is deprecated. Use global quotas for new
memory limits and migrate existing strict-mode RSS policies. Keep
`search_max_batchsize` as a separate collection request-shape guard.

## Conditional and intent-restricted writes

### Conditional point updates (since 1.16.0)

Attach an update filter that must match before Qdrant applies a point update.
When it does not match, Qdrant rejects the write. Use a payload version, a
synchronized timestamp, or another monotonically increasing value to prevent a
stale writer or background embedding job from overwriting newer data.

A safe optimistic-write flow is:

1. Read or retain the expected payload version.
2. Include that version in the update filter.
3. Write the new vector or payload and increment the version.
4. Treat rejection as a conflict; reread instead of blindly retrying.

### Insert-only and update-only upserts (since 1.17.0)

Select an upsert update mode that permits only insertion or only update. An
insert-only request prevents an intended create from replacing an existing
point. An update-only request prevents an intended change from silently
creating a missing point. These modes express point-existence intent; combine
them with conditional updates when payload revision also matters.

### Update-queue back pressure (since 1.17.0)

Shards queue pending changes and apply back pressure when the queue fills. The
initial capacity was as high as one million changes, preventing unbounded load
during heavy ingestion or replica recovery while retaining a large backlog.

### Reduced update-queue default (since 1.19.0)

The default queue length is now 200, down from one million. Workloads that
previously absorbed bursts in the queue can hit back pressure much sooner.
Explicitly configure capacity where a larger backlog is intentional, and load
test ingestion together with optimizer and replica-recovery activity.

## Named-vector schemas

### Filter by named-vector presence (since 1.13.0)

Use `has_vector` to select points that actually contain a named vector. This is
especially useful for heterogeneous collections and staged embedding
migrations.

```http
POST /collections/{collection_name}/points/scroll
{
  "filter": {
    "must": [
      {"has_vector": "image"}
    ]
  }
}
```

### Change named-vector schemas in place (since 1.18.0)

Named vectors can be added to or removed from an existing collection without
recreating and re-ingesting it. For an embedding migration:

1. Add the new named-vector field.
2. Populate it in the background.
3. Use `has_vector` to constrain reads that require the new embedding.
4. Switch production queries after coverage is sufficient.
5. Remove the old field only after consumers stop using it.

## Multitenancy and shard keys

### Tiered multitenancy (since 1.16.0)

A multitenant collection can place small tenants on a shared fallback shard and
large tenants on user-defined dedicated shards. Send a shard-key selector with
requests. Qdrant routes the tenant to its dedicated shard when present and to
the fallback otherwise.

Promote a growing tenant through shard transfer. Reads and writes continue
during promotion, so the application does not need distinct routing logic for
shared and dedicated states.

### List user-defined shard keys (since 1.17.0)

Use the shard-key listing API to discover a collection's current custom
sharding layout. Prefer this operation over an application-maintained guess
when reconciling tenants, administering transfers, or presenting shard state.

### Query shard keys during resharding (since 1.18.3)

Queries that specify shard keys can continue while resharding is in progress;
they no longer fail merely because the live resharding operation exists. Keep
normal error handling for unrelated shard or request failures.

## Collection metadata

### Custom metadata (since 1.16.0)

Collections can carry custom metadata. Use it for collection-scoped descriptive
or application management information rather than maintaining a disconnected
registry when the data naturally belongs with the collection.

### Metadata editing in the Web UI (since 1.19.0)

The Web UI displays and edits collection metadata. Account for UI-originated
changes if automation also manages the same keys, and define ownership to avoid
last-writer-wins surprises.

## Component memory and immutable segments

### Per-component memory policy (since 1.19.0)

Collection components share a `"memory"` setting whose modes are `"cold"`,
`"cached"`, and `"pinned"`. Choose the policy separately for individual
components rather than applying one undifferentiated memory behavior to the
whole collection.

- `cold` favors keeping the component out of resident memory.
- `cached` permits normal cache behavior.
- `pinned` favors keeping the component resident.

Match policy to access frequency and available RAM, then verify actual page
cache and resident use with collection memory reporting.

### Immutable-segment mmap default (since 1.19.0)

Single-file mmap vector storage is enabled by default for immutable segments.
Review disk, page-cache, and memory-policy behavior after upgrading instead of
assuming the previous storage layout.

## Payload-index administration

### Web UI payload indexes (since 1.19.0)

The Web UI can create payload indexes and manage their configuration. Apply the
same production change controls to UI-created indexes as to API-managed ones:
verify field type, full-text options, prefix support, resource impact, and
strict-mode index-count limits.

## Collection review checklist

- Record strict-mode limits and migrate the deprecated RSS guard to global
  quotas.
- Test conflict, missing-point, and existing-point paths for every write mode.
- Monitor queue pressure under ingestion, optimization, and replica recovery.
- Inventory named-vector coverage before removing a schema field.
- Reconcile shard keys through the API before and after tenant promotion.
- Define automation-versus-UI ownership for metadata and payload indexes.
- Validate each component's memory mode against collection-level usage data.
