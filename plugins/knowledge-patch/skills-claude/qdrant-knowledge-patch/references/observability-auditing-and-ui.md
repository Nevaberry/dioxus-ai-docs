# Observability, Auditing, and Web UI

## Cluster-wide telemetry

`/cluster/telemetry` returns information for all peers rather than requiring
one `/telemetry` request per peer (since 1.17.0). It exposes cluster-wide
activity such as leader elections, resharding, and shard transfers.

## Segment optimization monitoring

`/collections/{collection_name}/optimizations` reports cluster-wide
optimization status and details for current and previous optimization
operations (since 1.17.0). The Web UI **Optimizations** tab shows the same data
as status, timelines, and per-cycle task durations.

## Collection memory monitoring

Collection disk, RAM, and OS page-cache consumption can be inspected by
component, including vectors, payload, and indexes, with values aggregated
across the cluster (since 1.18.0). Use the API or the collection detail page's
**Memory** tab.

## Per-collection API metrics

Pass `per_collection=true` to the metrics endpoint to add a `collection` label
to `rest_responses_*` and `grpc_responses_*` (since 1.18.0):

```http
GET /metrics?per_collection=true
```

The labeled series provide per-collection request counts, failures, and
response durations. Account for the added label cardinality before enabling it
on installations with many collections.

## Audit logging

Qdrant can audit API operations that require authentication or authorization,
creating an operational record of protected actions (since 1.17.0).

A query endpoint aggregates audit entries across all cluster nodes (since
1.18.0). Results contain details such as timestamp, API method, authentication
type, access result, and client information, and can be filtered by time range
or any field value. Prefer this cluster-wide query over inspecting each node's
log files separately.

Audit entries record a caller-supplied tracing ID when a request includes
`x-request-id`, `x-tracing-id`, or `traceparent` (since 1.18.0). Propagate one of
these headers to correlate protected operations with client and distributed
tracing logs.

## Request-scoped inference credentials

External inference-provider API keys can be supplied in a request header (since
1.17.0). This lets credentials accompany individual inference requests instead
of forcing all callers to share one server-side provider credential.

## Web UI tools

The redesigned point-search UI can find points similar to a selected point,
filter by payload values, or locate a point by ID (since 1.17.0).

The Web UI also supports these collection operations (since 1.19.0):

- create and manage payload indexes and their configuration;
- display resharding progress;
- display and edit collection metadata.
