# Queries, APIs, and Command-Line Tools

Use this reference for LogQL evaluation, query and label APIs, caching, Patterns,
tenant limits, ruler operations, `logcli`, `lokitool`, and canary queries.

## Return Parquet query results

Since 3.4.0, the query API can return Parquet. Select that response format when
columnar-data tools should consume results directly, and ensure clients handle
the binary format and response metadata rather than assuming JSON.

## Apply corrected LogQL semantics

In 3.5.0, offsets are applied correctly to:

- `last_over_time`;
- `first_over_time`;
- `quantile_over_time`.

The same batch maps `approx_topk` in all cases and fixes the query-path `json`
parser so it does not corrupt log lines. Re-run golden tests that encoded the
older incorrect results.

LogQL permits comparisons against zero-byte values as of 3.4.0, and detected
fields recognize byte units.

In 3.7.3, range-query evaluation timestamps align to the step grid, and the
query engine no longer silently drops `OR` operations. Update timestamp and
set-operation expectations in dashboards, alerts, recording rules, and tests.

## Resolve label and metadata collisions

Parsed labels no longer override same-named structured metadata as of 3.7.0.
This is breaking query behavior. Avoid ambiguous names where practical and
expect the structured-metadata value to remain authoritative on collision.

The internal `__aggregated_metric__` label is hidden from `/series` and
`/labels` as of 3.6.0. Discovery clients should not require that internal label
in either response.

## Preserve label sketches in merged responses

In 3.7.6, query-range `MergeLabels` preserves sketch data when combining label
responses. Consumers of merged label results can use the returned sketch; do
not treat it as absent merely because the response passed through a merge.

## Route prefixed APIs correctly

Label-values requests work when `server.http_path_prefix` is set as of 3.5.0.
Build client routes from the configured prefix and verify both gateway and Loki
handling.

Aggregated metric queries are accepted only from the Logs Drilldown application
as of 3.5.0. Do not generalize that query path to arbitrary callers.

## Handle response-status changes

Push requests containing no streams return HTTP 422 as of 3.4.0. Interval-limit
violations return HTTP 400 as of 3.7.0. Classify each as a client-side request
problem rather than retrying it indefinitely as a transient server failure.

## Inspect effective tenant limits

Loki adds an applied-limits endpoint in 3.6.0. It returns the limits configured
for a tenant and can restrict fields through an allowlist. A request for a
nonexistent tenant returns default limits.

Use the response to inspect effective configuration, but distinguish an unknown
tenant receiving defaults from a known tenant with explicit overrides.

## Control query caching

As of 3.7.3, `query_range` requests can disable caching. Use this for workflows
that require a fresh evaluation, and propagate the control through any gateway
or client layer that constructs the request.

## Use Logs Drilldown additions

Logs Drilldown gains a configuration endpoint and partial metric-query results
in 3.6.0. Callers must be able to recognize and handle partial results. It also
supports `unwrap` as a projection.

## Persist and query patterns

As of 3.6.0, patterns can be persisted as aggregated metrics behind a feature
flag and queried later. Persistence can be bounded by volume and frequency.
The pattern ingester supports volume-based filtering and emits detected log
level as structured metadata.

The Patterns API accepts multi-tenant queries as of 3.7.0. Apply the caller's
tenant authorization across the full requested tenant set.

## Attribute generated queries

Since 3.4.0, ruler-issued queries carry the rule name and rule type in query
tags. Preserve those tags through gateways and use them for attribution and
diagnostics.

## Configure `logcli`

In 3.4.0, `logcli` can opt into `ProxyFromEnvironment` and includes common
labels in its output. Enable environment proxy behavior explicitly when it is
required and account for common labels in parsers and golden output.

In 3.6.0, `logcli` adds delete commands. Coordinate their use with the delete
request store and compactor behavior rather than treating a submitted request
as immediate physical removal.

As of 3.7.0, `logcli` can send custom headers. Use them for the deployment's
required routing or authentication metadata while avoiding accidental secret
exposure in shell history and logs.

## Use health and rule-checking commands

Loki adds a `loki health` command in 3.6.0. Use it for process health checks
appropriate to the deployed component.

The ruler rule checker can validate a namespace and group as of 3.6.0. The
ruler also validates remote-write configuration as of 3.7.0, so treat invalid
configuration as an actionable validation failure before rollout.

## Configure `lokitool`

As of 3.7.0, `lokitool`:

- supports regular-expression namespace filtering;
- uses the updated ruler path;
- accepts alternative TLS environment variables.

Update scripts that hard-code the older path or environment-variable set, and
test regex filters against the intended namespace population.

## Configure canary queries

The canary accepts an arbitrary label set for its query as of 3.7.0. Use labels
that uniquely select the canary stream under the deployment's relabeling and
tenant conventions.

## Query and CLI validation checklist

- Compare corrected range aggregations, `approx_topk`, JSON parsing, step-grid
  timestamps, and `OR` behavior with representative data.
- Test parsed-label collisions and discovery without the internal aggregated
  metric label.
- Request Parquet and decode it with the actual downstream client.
- Exercise path-prefixed label values and the Drilldown-only query restriction.
- Classify HTTP 400 and 422 responses without unbounded retry.
- Query applied limits for known and unknown tenants and with an allowlist.
- Compare cached and cache-disabled `query_range` requests.
- Handle partial Drilldown metrics and bounded persisted patterns.
- Verify `logcli` proxying, labels, headers, and delete commands.
- Check ruler namespaces, groups, remote write, `lokitool` routing, and canary
  label selection.
- Confirm query-range label merges retain sketches.
