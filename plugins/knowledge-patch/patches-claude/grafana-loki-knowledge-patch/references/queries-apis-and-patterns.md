# Queries, APIs, and patterns

## Parquet query responses (3.4.0)

The query API can return Parquet. Request this response format when query
results should flow directly into columnar-data tooling.

## LogQL value and field semantics (3.4.0)

LogQL accepts comparisons against zero-byte values. Detected fields understand
byte units, allowing byte-valued data to participate in discovery and query
workflows.

## Query-result corrections (3.5.0)

Offsets are applied correctly to `last_over_time`, `first_over_time`, and
`quantile_over_time`. `approx_topk` is mapped in all cases. Remove workarounds
that compensated for the older evaluation or mapping behavior after verifying
the target deployment.

The query-path `json` parser no longer risks corrupting log lines. Preserve raw
line expectations in regression tests when retiring parser workarounds.

## Routing and query restrictions (3.5.0)

Label-values queries work when `server.http_path_prefix` is configured. Build
their URL with the prefix instead of bypassing it.

Aggregated-metric queries are accepted only from the Logs Drilldown
application. Other clients must not assume that query path is generally
available.

## Tenant applied-limits API (3.6.0)

The applied-limits endpoint returns the limits effective for a tenant and can
filter its response through an allowlist. A request for a nonexistent tenant
returns default limits, so callers must not infer tenant existence from a
successful default-valued response.

## Logs Drilldown capabilities (3.6.0)

Logs Drilldown provides a configuration endpoint, can return partial
metric-query results, and supports `unwrap` as a projection. Clients should
represent partial results explicitly rather than treating them as complete or
failed.

## Persisted patterns (3.6.0)

Patterns can be persisted as aggregated metrics behind a feature flag and
queried later. Persistence can be bounded by volume and frequency. The pattern
ingester also supports volume-based filtering and emits detected level as
structured metadata.

Coordinate the feature flag, persistence bounds, filtering, and metadata use;
enabling only the query side is insufficient.

## Index-gateway shuffle sharding (3.7.0)

Index-gateway clients support shuffle sharding. Use it when distributing client
work across index-gateway capacity according to the deployment's isolation
strategy.

## Query cache and multi-tenant patterns (3.7.0)

As of 3.7.3, `query_range` requests can disable caching. Make cache bypass an
explicit per-request decision rather than disabling shared cache
infrastructure.

The Patterns API accepts multi-tenant queries. Enforce the deployment's tenant
authorization when exposing this capability.

## Range evaluation and boolean operations (3.7.0)

As of 3.7.3, range-query evaluation timestamps align to the step grid. The
query engine no longer silently drops `OR` operations. Recheck expected sample
timestamps and results for clients that encoded the former behavior.

## Scheduler execution changes (3.7.0)

The scheduler accounts for total compute capacity, and worker threads are
shared across all scheduler connections. Both are breaking engine changes.
Revalidate concurrency and capacity assumptions rather than expecting a worker
allocation per connection.

## Validation and HTTP status behavior (3.7.0)

The ruler validates remote-write configuration. Include that validation in
configuration delivery checks.

Interval-limit violations return HTTP 400. Query clients should classify this
as an invalid or disallowed request, not a retryable server error.

## Label sketches in merged responses (3.7.6)

When query-range combines label responses, `MergeLabels` preserves sketch data.
Consumers of merged label results can use the returned sketch rather than
treating it as missing.
