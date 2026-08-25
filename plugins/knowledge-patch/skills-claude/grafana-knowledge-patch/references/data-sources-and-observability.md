# Data sources and observability

## Data-source identity, routing, and context

### UID validation

`failWrongDSUID` is enabled by default. REST and provisioning writes reject malformed data-source UIDs. Audit for characters outside `A-Z`, `a-z`, `0-9`, `-`, and `_`, and for values over 40 characters; create replacement sources and repoint dashboard JSON and alert queries rather than mutating invalid identity in place. (12.0-upgrade)

Add authentication as needed when using this local audit:

```bash
curl http://localhost:3000/api/datasources | jq '.[] | select((.uid | test("^[a-zA-Z0-9\\-_]+$") | not) or (.uid | length > 40)) | {id, uid, name, type}'
```

`PUT /api/datasources/uid/:uid` returns 400 if the payload UID differs from the path UID. (12.3.0)

Name- and numeric-ID-based data-source routes are deprecated in favor of UIDs. (12.4.0)

Numeric-ID routes are disabled by default. `datasourceLegacyIdApi` can temporarily re-enable them, but both routes and flag are scheduled for removal. (13.0-upgrade)

### Runtime registration, subqueries, and request context

Applications can register data sources at runtime. A query using the Dashboard data source can be nested as a subquery under Mixed. (11.5.0)

Data-source queries send dashboard and panel titles as headers. (12.1.0)

Plugin extensions can register components in a data-source configuration page. (12.2.0)

Grafana Actions supports Infinity authentication. (12.2.0)

`forward_user_agent` forwards the client `User-Agent`. (13.1.0)

## Prometheus and Mimir

Cloud-partner Prometheus sources are supported, and `prometheusRunQueriesInParallel` is enabled by default. (12.0.0)

Prometheus emits a deprecation notice for Azure authentication. Queries containing `$__range` do not use incremental querying. (12.1.0, 12.2.0)

Grafana Advisor includes a Prometheus Type Migration check to find sources that need migration. (12.3.0)

The core Prometheus integration removes Azure and SigV4 authentication, and the `grafana-prometheus` package is removed. Move authentication and package consumers to supported alternatives. (13.1.0)

## Loki and logs

### Label and query behavior

Loki derived fields can combine a regular expression with `label`. Query Builder operations can be disabled and re-enabled. Label lookup defaults to `/labels` with a `query` argument rather than `/series`; update proxy rules and consumers. (11.5.0)

Loki editors remove `Resolution`. The logs-download button can be hidden with `hide_logs_download`. (11.6.0)

The experimental `lokiQuerySplittingConfig` and predefined operations are removed. (12.1.0)

### Panels, fields, and downloads

A field selector integrates with Logs and the Logs table. Downloads contain selected fields instead of always exporting every field. (12.3.0)

The new Logs visualization is enabled by default. Logs panels support transformations with infinite scrolling and unwrapped logs with optional displayed-field columns. Explore stores sort order in the URL. (12.4.0)

Logs panels can expose a field selector, persist displayed fields, and hide Level. Plugins can provide a custom log grammar; OpenTelemetry log formatting recognizes dot-separated label names. (13.0.0)

Grafana recognizes `emergency`; a missing log level is `unspecified`, distinct from an unrecognized `unknown`. (13.1.0)

## Tempo, Jaeger, Zipkin, and traces

### Tempo querying and metrics

Tempo supports TraceQL Metrics exemplars and applies data-source TLS configuration to gRPC. Span filters can be stored as panel options. (11.5.0)

TraceQL supports instant metrics and streamed metrics results. (11.6.0)

Tempo supports ad hoc filters and removes **Aggregate by**. (12.0.0)

Tempo service graphs support native histograms. (12.1.0)

### Backend-routed requests and headers

Zipkin queries execute through the Grafana backend; server-side reachability and authentication are required. (11.5.0)

Jaeger API calls use its gRPC endpoint. Enterprise Tempo tag and tag-value lookups use backend `CallResource`, so they require backend connectivity and credentials. (12.3.0)

Tempo stops forwarding incoming and team headers for streaming requests in 12.4. (12.4.0)

Grafana resumes forwarding those headers for Tempo streaming in 13.0; treat the later behavior as authoritative for that release. (13.0.0)

### Core packaging and trace shapes

Zipkin is removed from core data-source plugins; install and manage a supported plugin rather than assuming it is bundled. (13.1.0)

Tempo normalizes dynamic integer and double span attributes to `float64` and uses the same nested span-subframe shape across span sets. (13.1.0)

Trace sources can use VictoriaMetrics for traces-to-metrics. (12.4.0)

## Pyroscope and profiles

Explore Profiles is preinstalled on self-hosted Grafana. (11.5.0)

Pyroscope can process and display sampling annotations. (12.2.0)

Pyroscope series queries support exemplars. (12.4.0)

Pyroscope adds a Call Tree visualization, accepts `profileIdSelector`, and attaches the complete label set to exemplars. (13.0.0)

The Pyroscope heatmap query API is supported. (13.1.0)

## CloudWatch

CloudWatch Logs Insights supports OpenSearch PPL and SQL. An empty `logstimeout` is valid, and updated SDK support adds Amplify Hosting metrics. (11.5.0)

If a query omits its region, CloudWatch uses the configured default region. (12.2.0)

CloudWatch Logs supports Log Anomalies; the editor highlights and completes the Logs `diff` command. (12.3.0)

OpenSearch SQL can select log groups using the selector and `$__logGroups`. CloudWatch supports prefix and all-log-group queries. Batch queries are generally available, and **Match exact** defaults to false. (12.4.0)

CloudWatch Logs results no longer contain data links, while metric-expression links include an ID. (13.1.0)

## Google Cloud and Azure

Azure Monitor adds a Logs query builder. Azure Prometheus exemplars are generally available and on by default; Basic Logs is limited to one resource per query. (12.0.0)

Cloud Monitoring supports service-account impersonation. Azure Resource Graph queries can choose a scope. (12.1.0)

Cloud Monitoring accepts Google Cloud `universe_domain`. (12.4.0)

Google Cloud Monitoring supports Forward OAuth Identity authentication. (13.1.0)

## Elasticsearch and OpenSearch

Elasticsearch field discovery uses `_field_caps`, not `_mapping`; permissions and proxies must allow the new endpoint. (11.5.0)

Elasticsearch supports serverless connections, a configurable default query mode, and a raw DSL editor. (12.4.0)

The core Elasticsearch data source is removed in 13.0, so it is no longer implicitly bundled. Its plugin query editor supports ES|QL and variable queries. (13.0.0)

## InfluxDB and OpenTSDB

Influx SQL supports PDC, and ad hoc filters work with raw queries. (12.0.0)

Tag autocomplete can apply a time-range filter. (12.1.0)

Ad hoc filters work with expressions, and a self-signed CA can be configured. (12.2.0)

OpenTSDB 2.4 is supported. (11.6.0)

## SQL data sources and SQL Expressions

SQL Expressions enter public preview. (12.2.0)

PostgreSQL data-source configuration can omit a password so the server process can use `PGPASSFILE`. (12.3.0)

MSSQL supports current-user authentication. MySQL and PostgreSQL have variable query editors. SQL Expressions support `NOT`, and alerts can use a SQL expression containing a CTE. (12.4.0)

SQL-expression schema queries interpolate variables. (13.1.0)

PostgreSQL sources initialize when `maxOpenConns=0`, epoch-millisecond strings parse instead of producing `NaN`, and SQL Expressions parse table names containing spaces. (13.2.0)

## Expressions and conversions

Math-expression binary operations have a memory limit. String-to-number conversion preserves null and empty-string values. (13.1.0)

## Transformations

Extract fields supports Delimiter and RegExp formats. Transformation filtering can match multiple query RefIDs. (11.5.0)

Variables work across all transformations. Unary **Add field from calculation** provides `round()`. (11.6.0)

Organize fields adds Auto, and Regression is generally available. (12.1.0)

Transpose has empty-value settings. Trend and Time series can show value labels. (12.2.0)

Transformations add smoothing. (12.4.0)

## Visualizations

### Histograms, timelines, and XY charts

Histogram supports multiple native histograms. (11.6.0)

State timeline renders `false` and empty-string values and supports mappings for `NaN` and null. XY charts accept time on the x-axis. (12.1.0)

### Canvas, tables, and charts

Canvas elements have one-click links and actions; visualization actions can ask for confirmation. (11.6.0)

Canvas can disable tooltips on one-click elements and choose connection direction dynamically. Pie sorting supports ascending, descending, or disabled. Tables support frozen columns, maximum variable-row height, and field-sourced tooltips. Trend supports a logarithmic x-axis. (12.2.0)

Canvas background images can come from non-icon fields. Time series accepts custom x-axis time units. Tables render array-valued `FieldType.other` as pills, format Pill and JSON cells, and attach data links or actions to sparkline cells. (12.3.0)

### Geomap and panel navigation

Geomap accepts a MapLibre style as a base layer, and its former beta layers are generally available. (12.3.0)

Click-and-drag panning is generally available for time series and works in candlestick, heatmap, and timeline. Heatmap supports a linear y-axis. Geomap XYZ layers accept variables and min/max zoom. (12.4.0)

## Metrics and telemetry compatibility

Grafana exports `http_response_size_bytes`, while plugin request metrics include the plugin version. (12.2.0)

Grafana HTTP metrics use native histograms by default; classic histograms remain configurable. (12.4.0)

Enterprise query caching removes duplicate `grafana_caching_items` and `grafana_caching_size`, and Grafana no longer bundles Prometheus dashboards. (13.0.0)

The dashboard-version metric is removed. (13.1.0)

Grafana tracing can write OTLP/JSON traces to a file. (13.2.0)

## Exploration applications

The external-app Metrics Drilldown implementation is generally available and old internal paths are removed. Traces Drilldown is preinstalled. (12.0.0)

The Prometheus query assistant and related components are removed. (11.6.0)

Drilldown Investigations and CSV drag-and-drop snapshot queries are removed. (12.4.0)

## Data and time precision

Standard datetime units are limited to millisecond precision. (12.0.0)
