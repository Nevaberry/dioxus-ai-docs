# Data Sources and Observability

Use this reference for data-source queries and configuration, expressions,
metrics, logs, traces, profiles, correlations, caching, and backend routing.

## Cross-cutting data-source behavior

### Dashboard data-source subqueries (since 11.5.0)

Queries that use the Dashboard data source can be nested as subqueries inside a
Mixed data source.

### Runtime registration (since 11.5.0)

Core Grafana supports data sources registered at runtime, so apps can provide data
sources without relying only on static installation-time registration.

### Enterprise query permission (since 11.6.0)

Enterprise data-source queries require the `query` permission; `read` no longer
satisfies the check. Drilldown access requires `datasources:explore`.

### Label-based access control (since 12.0.0)

Data-source LBAC is available as a self-service public-preview feature.

### Query headers and plugin context (since 12.1.0)

Data-source queries pass dashboard and panel titles in headers. Plugin-side
`usePluginContext` exposes its `PluginMeta` generic.

### Team filters for LBAC (since 12.1.0)

Enterprise data-source LBAC rules can filter by team.

### Configuration extensions (since 12.2.0)

Plugin extensions can register data-source configuration components.

### Strict UID PUT validation (since 12.3.0)

`PUT /api/datasources/uid/:uid` returns HTTP 400 when the payload UID differs
from the URL UID. Keep both identifiers identical.

### Correlation organization scope (since 12.3.0)

Correlations no longer accept `org_id=0`; use a concrete organization ID in
records and requests.

### OAuth pass-through disables caching (since 12.3.0)

Enterprise query caching is disabled when `oauthPassThru=true`, preventing
per-user OAuth credentials from being combined with cached results.

### UID-first routes (since 12.4.0)

Data-source routes addressed by names or internal IDs are deprecated. Migrate to
UID-based routes.

### Forwarded client identity (since 13.1.0)

Data sources add `forward_user_agent` to preserve the client `User-Agent`.

## CloudWatch and cloud integrations

### OpenSearch queries and AWS metrics (since 11.5.0)

CloudWatch supports OpenSearch PPL and SQL in Logs Insights, accepts an empty
`logstimeout`, and includes AWS Amplify Hosting metrics through its updated AWS
SDK.

### Azure Monitor and Prometheus (since 12.0.0)

Azure Monitor adds a logs query builder. Azure Prometheus exemplars are generally
available and enabled by default. Basic Logs queries are limited to one resource.

### Cloud identities and query scope (since 12.1.0)

Cloud Monitoring supports service-account impersonation. Azure Resource Graph
queries can select their scope.

### Default-region fallback (since 12.2.0)

CloudWatch queries use the configured default region when the query region is
unset.

### CloudWatch Logs anomalies (since 12.3.0)

CloudWatch Logs supports the Log Anomalies query type. Its editor recognizes the
Logs `diff` command with syntax highlighting and autocomplete.

### Log groups, batches, and exact matching (since 12.4.0)

CloudWatch OpenSearch SQL can select log groups through the selector and
`$__logGroups` macro. CloudWatch adds log-group-prefix and all-log queries. Batch
queries are generally available, and **Match exact** defaults to false.

### Google Cloud universe domains (since 12.4.0)

Cloud Monitoring supports Google Cloud `universe_domain` values.

### Forward OAuth identity (since 13.1.0)

Google Cloud Monitoring supports Forward OAuth Identity authentication.

### CloudWatch data-link behavior (since 13.1.0)

CloudWatch Logs results no longer include data links. Metric-expression data links
now carry an ID.

## Elasticsearch and OpenSearch

### Field discovery endpoint (since 11.5.0)

Elasticsearch discovers fields through `_field_caps`, not `_mapping`. Proxies and
Elasticsearch permissions must allow `_field_caps`.

### Serverless and raw query modes (since 12.4.0)

Elasticsearch supports serverless connections, a configurable default query mode,
and a raw DSL editor.

### Core removal and ES|QL editor (since 13.0.0)

The core Elasticsearch data source is removed, so deployments cannot assume it is
bundled. The Elasticsearch editor adds ES|QL and variable-query support.

## Prometheus and metrics

### Parallel and partner queries (since 12.0.0)

Grafana supports cloud-partner Prometheus data sources and enables
`prometheusRunQueriesInParallel` by default.

### Azure authentication deprecation notice (since 12.1.0)

Prometheus emits a deprecation message for Azure authentication.

### Incremental query exception (since 12.2.0)

Prometheus queries containing `$__range` do not use incremental querying.

### Type-migration advisor (since 12.3.0)

Grafana Advisor includes a Prometheus Type Migration check for data sources that
need migration.

### Core authentication and package removals (since 13.1.0)

The core Prometheus integration removes Azure and SigV4 authentication, and the
`grafana-prometheus` package is removed.

### Grafana HTTP metrics (since 12.2.0)

Grafana exports `http_response_size_bytes`, and plugin request metrics include the
plugin version.

### Native histogram default (since 12.4.0)

Grafana's own HTTP metrics use native histograms by default; classic histograms
remain configurable.

### Removed bundled dashboards and duplicate metrics (since 13.0.0)

Grafana no longer bundles Prometheus dashboards. Enterprise query caching removes
duplicate `grafana_caching_items` and `grafana_caching_size` metrics. Update
monitoring that consumes either asset.

## Loki and logs

### Derived fields and query operations (since 11.5.0)

Loki derived fields can use a regular expression with `label`. Query Builder
operations can be disabled and later re-enabled.

### Label lookup default (since 11.5.0)

Loki label lookup defaults to `/labels` with a `query` parameter instead of
`/series`. Update access rules and integrations that assume `/series`.

### Removed editor controls (since 11.6.0)

Loki editors no longer expose `Resolution`. The `hide_logs_download` setting can
hide the logs-download button.

### Removed experimental Loki options (since 12.1.0)

Loki removes `lokiQuerySplittingConfig` and experimental predefined operations.

### Log-level semantics (since 13.1.0)

Grafana recognizes `emergency` as a log level. Missing levels are `unspecified`,
which is distinct from the `unknown` classification for an unrecognized level.

### Usage Insights metadata (since 13.2.0)

Loki usage-insights events include the public-dashboard UID.

## Tempo, traces, and Zipkin

### Tempo exemplars, TLS, and saved filters (since 11.5.0)

Tempo supports TraceQL Metrics exemplars and honors data-source TLS for gRPC.
Trace-view span filters can be stored as panel options.

### Zipkin backend routing (since 11.5.0)

Zipkin queries run through the Grafana backend. Ensure server-side network access
and authentication to Zipkin.

### TraceQL metric modes (since 11.6.0)

Tempo supports instant TraceQL metrics queries and streamed TraceQL metric
results.

### Tempo ad hoc filters (since 12.0.0)

Tempo supports ad hoc filters and removes the **Aggregate by** option.

### Drilldown packaging (since 12.0.0)

The external-app Metrics Drilldown implementation is generally available and
legacy paths are removed. Traces Drilldown is preinstalled.

### Backend-routed Jaeger and Tempo lookups (since 12.3.0)

Jaeger calls move to its gRPC endpoint. In Enterprise, Tempo tag and tag-value
lookups move to backend `CallResource`; both require backend connectivity and
authentication.

### Streaming headers removed (since 12.4.0)

Tempo does not forward incoming or team headers for streaming requests.

### VictoriaMetrics traces and Pyroscope exemplars (since 12.4.0)

Trace data sources support VictoriaMetrics for traces-to-metrics. Pyroscope series
queries support exemplars.

### Streaming headers restored (since 13.0.0)

Tempo again forwards incoming and team headers for streaming requests, reversing
the 12.4 behavior.

### Zipkin core removal (since 13.1.0)

Zipkin is removed from the core data-source plugins. Deployments must no longer
assume it is bundled.

### Tempo normalized data shapes (since 13.1.0)

Tempo normalizes dynamic integer and double span attributes to `float64` and uses
a consistent nested span-subframe schema across span sets.

### Tracing file exporter (since 13.2.0)

Grafana tracing can write traces to a file in OTLP/JSON format.

## InfluxDB, SQL, and OpenTSDB

### InfluxDB PDC and raw-query filters (since 12.0.0)

Influx SQL supports PDC, and ad hoc filters work with raw InfluxDB queries.

### InfluxDB time-range autocomplete (since 12.1.0)

Tag-autocomplete queries can optionally apply a time-range filter.

### InfluxDB expressions and self-signed CAs (since 12.2.0)

InfluxDB ad hoc filters work with expressions, and data sources can use a
self-signed CA.

### PostgreSQL passfile authentication (since 12.3.0)

PostgreSQL data-source configuration does not require a password, allowing the
server process to use `PGPASSFILE`.

### SQL authentication and variable editors (since 12.4.0)

MSSQL supports current-user authentication. MySQL and PostgreSQL add variable
query editors.

### PostgreSQL connection and epoch handling (since 13.2.0)

PostgreSQL data sources no longer fail initialization when `maxOpenConns=0`.
Epoch-millisecond strings are parsed instead of becoming `NaN`.

### OpenTSDB 2.4 (since 11.6.0)

The OpenTSDB data source supports OpenTSDB 2.4.

## Expressions and query execution

### Prometheus query assistant removal (since 11.6.0)

The Prometheus query assistant and related components are removed.

### SQL Expressions public preview (since 12.2.0)

SQL Expressions are promoted to public preview.

### SQL `NOT` and CTE alerts (since 12.4.0)

SQL Expressions support `NOT`, and alerts can use SQL expressions containing a
CTE.

### Partial expression results (since 13.0.0)

Server-side expressions isolate broken pipeline nodes so unaffected nodes can
still return partial results.

### Memory, interpolation, and conversion (since 13.1.0)

Math-expression binary operations have a memory limit. SQL-expression schema
queries interpolate variables. String-to-number conversion preserves null and
empty strings.

### Table names with spaces (since 13.2.0)

SQL Expressions parse table names containing spaces.

## Profiles and self-hosted observability

### Explore Profiles preinstalled (since 11.5.0)

Explore Profiles is preinstalled on self-hosted Grafana; no separate plugin
installation is required.

### Pyroscope heatmap API (since 13.1.0)

Pyroscope supports its heatmap query API.

## Removed query and observability gates

### Query-related toggle removals (since 11.6.0)

`sqlQuerybuilderFunctionParameters` and `openSearchBackendFlowEnabled` are removed.

### Query and trace toggles removed (since 12.0.0)

`queryOverLive`, `live-service-web-worker`, and `traceQLStreaming` are removed.

### Query-builder metric search gate removed (since 12.2.0)

`prometheusCodeModeMetricNamesSearch` is removed.

### Drilldown and query feature removals (since 12.4.0)

`logRowsPopoverMenu`, `logsInfiniteScrolling`, `exploreMetricsRelatedLogs`, and
`postgresDSUsePGX` are removed. Drilldown Investigations and CSV drag-and-drop
snapshot queries are also removed.

### Removed routes and dashboard-version metric (since 13.1.0)

GroupAttributeSync routes and the dashboard-version metric are removed. API
clients and metric consumers must stop depending on them.
