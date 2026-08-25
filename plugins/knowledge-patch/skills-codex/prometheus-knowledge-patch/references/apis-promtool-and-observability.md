# APIs, Promtool, and Observability

Use this reference for HTTP API contracts, `promtool` behavior, query
statistics, built-in diagnostics, and self-monitoring changes.

## HTTP API contracts

### Paginate rule groups defensively (3.1.0)

The rules API can paginate groups. Its `groupNextToken` field is present even
when empty, so clients must accept the field whether or not another page exists.

### Limit instant and range-query results (3.2.0)

`/query` and `/query_range` accept `limit`:

```text
/query?limit=100
/query_range?limit=100
```

### Read added status fields (3.2.0)

The `/status` response includes `Node` and `ServerTime`.

### Bound TSDB status processing (3.9.0)

The TSDB status endpoint returns at most 10,000 sets of statistics. Clients must
not assume its statistics are exhaustive or unbounded.

### Discover enabled server features (3.9.0)

Use `/api/v1/features` to inspect supported features rather than inferring them
only from the version.

### Consume the HTTP OpenAPI document (3.10.0)

`/api/v1/openapi.yaml` serves an OpenAPI 3.2 contract for the HTTP API.

### Inspect self-metrics as JSON (3.12.0)

`/api/v1/status/self_metrics` returns the current state of Prometheus's own
metrics as JSON.

### Parse duration expressions from the AST API (3.12.0)

`/parse_ast` responses include duration expressions.

### Use experimental metric and label search (3.13.0)

Experimental HTTP endpoints search metric names, label names, and label values.

### Cap search request limits (feature-flags)

With `search-api`, `--web.search.max-limit` caps each search endpoint's
requested `limit` and defaults to `10000`; excess requests get HTTP 400. The
ordinary response default of `100` is clamped to a smaller operator cap.
Setting the cap to `0` allows unbounded requests and is unsafe on untrusted
endpoints.

## Query statistics and diagnostics

### Profile wall time on demand (3.10.0)

Use `/debug/pprof/fgprof` for web-exposed wall-time profiling.

### Correlate query logs with traces (3.11.0)

When tracing is enabled, query-log entries include `traceID` and `spanID`.

### Distinguish storage reads from evaluator loads (3.13.0)

Query statistics expose `samplesRead`; with `stats=all` and
`promql-per-step-stats`, they also expose `samplesReadPerStep`. These count
storage I/O. `totalQueryableSamples` counts evaluator loads and can count a
reused sample in multiple range windows. The engine-wide storage-read counter
is `prometheus_engine_query_samples_read_total`.

Range subqueries stop at the parent's last actual step when the query end is
not step-aligned, preventing inflated `peakSamples`, `query.max-samples`
enforcement, and reads. An `@`-modified range under an at-modifier-unsafe
function also counts `totalQueryableSamples` correctly after the first step.

### Restrict accepted statistics values (3.13.2-3.14.0)

For `/api/v1/query` and `/api/v1/query_range`, `stats` values other than `true`
and `all` are deprecated. They still enable basic statistics but return a
warning and will be rejected in the next major release.

## Notification and rule self-monitoring

### Count failed alerts, not batches (3.1.0)

`prometheus_notifications_errors_total` increments by the number of affected
alerts rather than once per failed notification batch. Update alerts and
dashboards that interpreted each increment as one batch.

### Monitor rule evaluation and Go mutex wait (3.1.0)

Prometheus exports `rule_group_last_rule_duration_sum_seconds` and
`go_sync_mutex_wait_total_seconds_total`.

### Customize the mixin cluster label (3.3.0)

Set the Prometheus mixin's `clusterLabel` when `cluster` is not the desired
label name.

### Bound Alertmanager notification batches (3.4.0)

Use `--alertmanager.notification-batch-size` to cap a notification batch.

### Account for Alertmanager metric dimensions (3.10.0)

`prometheus_notifications_dropped_total`,
`prometheus_notifications_queue_capacity`, and
`prometheus_notifications_queue_length` have an `alertmanager` label. Queries
that expected one unlabeled aggregate must aggregate or filter the new
dimension.

### Clean stale rule metrics on reload (3.13.2-3.14.0)

Removing or renaming a rule group removes its stale
`rule_group_last_rule_duration_sum_seconds` and
`rule_group_last_restore_duration_seconds` series instead of leaking two series
per reload.

## Promtool input, output, and configuration

### Lint long scrape intervals (3.2.0)

Use the `too-long-scrape-interval` lint option to identify excessively long
scrape intervals.

### Ignore unsupported fields deliberately (3.2.0)

`promtool` accepts `--ignore-unknown-fields` when unrecognized configuration
fields should not fail validation.

### Pipe OpenMetrics into block creation (3.3.0)

`promtool tsdb create-blocks-from openmetrics` accepts OpenMetrics input from a
pipe.

### Validate gated PromQL syntax (3.4.0)

`promtool` supports PromQL feature flags so offline checks can parse the same
gated syntax as the server.

### Use fuzzy rule-test comparisons (3.5.0)

Rule unit tests can relax exact float64 matching:

```yaml
fuzzy_compare: true
```

### Set explicit rule-test start times (3.9.0)

Rule-unit-test definitions accept `start_timestamp` for time-sensitive cases.

### Push Remote Write 2 messages (3.8.0)

`promtool push metrics` selects Remote Write 2 with `--protobuf_message`.

### Parse gated duration and range syntax (3.10.0)

Promtool understands syntax associated with `promql-duration-expr` and
`promql-extended-range-selectors` when the matching features are supplied.

### Keep diagnostic output off stdout (3.11.0)

Promtool writes debug diagnostics to stderr, leaving stdout available for tool
output. Adjust pipelines that merged or parsed both streams.

### Add headers to instant queries (3.12.0)

`promtool query instant` accepts `--header`, matching `promtool query range`.

### Resolve HTTP-config paths from the config directory (3.13.0)

Relative paths inside the file passed to `--http.config.file` resolve from that
file's directory, not its parent. Adjust configurations that depended on the
old extra parent traversal.

### Override the remote-write push path (3.13.2-3.14.0)

`promtool push metrics` accepts `--remote-write.path` for backends that do not
use the default endpoint.

### Validate fill modifiers (3.13.2-3.14.0)

`promtool check rules` accepts
`--enable-feature=promql-binop-fill-modifiers` so it can validate rules using
`fill()`, `fill_left()`, and `fill_right()`.
