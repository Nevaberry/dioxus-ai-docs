# HTTP APIs and Observability

## Rule API and self-monitoring (`3.1.0`)

The rules API paginates rule groups. Its `groupNextToken` field is present even
when empty, so clients must accept it whether or not another page exists.

Prometheus exports `rule_group_last_rule_duration_sum_seconds` and
`go_sync_mutex_wait_total_seconds_total`. Notification-error counting is per
affected alert rather than per failed batch.

## Query limits and status fields (`3.2.0`)

`/query` and `/query_range` accept `limit`:

```text
/query?limit=100
/query_range?limit=100
```

The `/status` response includes `Node` and `ServerTime`.

## Target and mixin metadata (`3.3.0`)

Dropped targets from `/api/v1/targets` include their scrape pool. The Prometheus
mixin's `cluster` label can be customized with `clusterLabel`.

## Storage replay metrics (`3.4.0`)

Monitor unknown replay references with
`prometheus_tsdb_wal_replay_unknown_refs_total` and
`prometheus_tsdb_wbl_replay_unknown_refs_total`.

## Loaded blocks, tracing, and stale series (`3.6.0`)

`/v1/status/tsdb/blocks` exposes metadata for loaded TSDB blocks. Scrape
requests include `traceparent`. `prometheus_tsdb_head_stale_series` reports
stale series in the Head block.

## Histogram annotations (`3.7.0`)

PromQL produces warn-level annotations for certain histogram counter-reset
conflicts. Surface annotations in API clients instead of discarding them.

## Alert states and sample limits (`3.8.0`)

Clients must accept `unknown` for an alerting rule not yet evaluated. Histogram
samples count toward the configured query sample limit.

## Feature discovery and bounded status data (`3.9.0`)

Use `/api/v1/features` to discover supported capabilities rather than infer
them from a version. The TSDB status endpoint returns at most 10,000 sets of
statistics.

Most `prometheus_sd_refresh` metrics carry a `config` label with the job name.
`prometheus_tsdb_sample_ooo_delta` measures every sample's out-of-order distance.
Query, rule, discovery, and scrape instrumentation supplies native histograms
beside summaries, and notification latency adds
`prometheus_notifications_latency_histogram_seconds`.

## API schema, profiles, and notification dimensions (`3.10.0`)

The OpenAPI 3.2 document is at `/api/v1/openapi.yaml`. Wall-time profiling is
available at `/debug/pprof/fgprof`.

Notification dropped, queue-capacity, and queue-length metrics have an
`alertmanager` label. Each Alertmanager has its own send loop. `/-/ready`
restores `X-Prometheus-Stopping` during the shutdown `NotReady` state.

## Discovery timing and trace correlation (`3.11.0`)

`prometheus_sd_last_update_timestamp_seconds` reports when a discovery update
was last sent to consumers. With tracing enabled, query-log records include
both `traceID` and `spanID`.

## Self-metrics and AST responses (`3.12.0`)

`/api/v1/status/self_metrics` returns the server's own current metrics as JSON.
`/parse_ast` responses include duration expressions. Series for removed scrape
jobs' per-job discovery refresh and discovered-target metrics are cleaned up.

## Search and query read statistics (`3.13.0`)

Experimental API endpoints search metric names, label names, and label values.

Query statistics expose `samplesRead`, and `samplesReadPerStep` with `stats=all`
plus `promql-per-step-stats`. These measure storage I/O.
`totalQueryableSamples` instead counts samples loaded into the evaluator and can
count one reused sample in multiple range windows. The engine-wide storage-read
counter is `prometheus_engine_query_samples_read_total`.

Range subqueries no longer execute beyond a parent's last real step when the
end is not step-aligned, correcting peak/sample-limit/read accounting.

## Search API resource caps (`feature-flags`)

With `search-api`, `--web.search.max-limit` caps each endpoint's requested
`limit` and defaults to 10000. Requests above it return HTTP 400. The normal
response default of 100 is clamped to a smaller operator cap. A cap of `0`
allows unbounded requests and is unsafe for untrusted endpoints.

## Current diagnostics and API deprecations (`3.13.2-3.14.0`)

For `/api/v1/query` and `/api/v1/query_range`, only `stats=true` and `stats=all`
are current. Other values still enable basic statistics but return a warning
and are scheduled for rejection in the next major release.

Monitor OTLP name collisions with
`prometheus_api_otlp_translation_warnings_total{category=...}` and current head
native histogram use with `prometheus_tsdb_head_native_histogram_series` and
`prometheus_tsdb_head_native_histogram_buckets`. TSDB query errors that were
previously discarded are now returned to callers.
