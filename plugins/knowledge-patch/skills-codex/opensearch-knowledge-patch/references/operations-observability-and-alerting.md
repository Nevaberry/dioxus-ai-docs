# Operations, Observability, and Alerting

## Investigating queries with Query Insights

### Historical top queries

Query Insights 2.19.0 adds a Dashboards interface for historical top-N queries, drill-down, configuration, and retention. The backend can fetch by identifier and expire records automatically; the custom local-index-name setting is removed.

In 3.1.0, insight queries can exclude selected indexes and attach metric labels to historical data. Dashboards adds dedicated Live Queries and Workload Management views.

Since 3.5.0, top-N records can include username and roles. Wrapper endpoints around Query Insights settings provide finer-grained access control, and the dashboard integrates Workload Management groups for filtering and sorting.

OpenSearch 3.6.0 adds an asynchronous rules service that returns recommendations with confidence and estimated impact. Top-N data can export timestamp-organized JSON to remote blob repositories, with S3 supported initially. Dashboards adds P90/P99 statistics and distribution, line, and heatmap views.

In 3.7.0, the Top Queries API accepts `recommendations` to include inline recommendations.

### Live and inflight queries

OpenSearch 3.0.0 adds an inflight/live-queries API for real-time monitoring and a `verbose` option on the top-queries API. Dashboards renders returned columns dynamically.

In 3.1.0, Live Queries responses include `isCancelled`. In 3.2.0, Dashboards supports multiple data sources and the reader search limit rises to 500.

Since 3.3.0, Live Queries can filter by Workload Management group, with bidirectional Dashboards navigation between live queries and groups. The 3.4.0 page adds version-aware settings and multiple-data-source support and can use security attributes in its Workload Management view.

In 3.6.0, identity filters by username and shared backend roles ensure non-admins see only authorized data. Live Queries adds shard task detail, an on-demand finished-query cache, and explicit failed-query tags.

The 3.7.0 Dev Tools profiler exposes shard timings and a collapsible query hierarchy with navigation from Query Details. Since 3.8.0, Live Queries records can contain username, roles, and backend roles for authorization-aware analysis.

## Applying workload management

Index-based auto-tagging in 3.1.0 assigns workload groups through rules, so clients need not always send a header tag. In 3.3.0, auto-tagging extends to principal attributes including username and role.

Since 3.7.0, each group can override search timeout, cancellation interval, maximum bucket count, and other search settings for every routed request.

## Exploring logs, traces, and metrics

### Discover and trace analytics

The disabled-by-default experimental Discover experience in 2.19.0 adds SQL and PPL alongside DQL and Lucene, plus autocomplete and improved data selection.

OpenSearch 3.1.0 Observability can use custom index names for OpenTelemetry spans, logs, and service maps, map non-OpenTelemetry log fields, and correlate traces to logs across clusters.

In 3.2.0, Trace Analytics accepts Data Prepper 2.11 OpenTelemetry output, while Dashboards makes service-map node and edge limits configurable.

OpenSearch 3.3.0 adds an optional unified Discover interface for log analytics, distributed tracing, automatic visualization selection, and context-aware analysis. Discover Traces supports click-to-filter exploration; separate conversational query and visualization actions remain disabled by default.

In 3.8.0, experimental, disabled-by-default SQL support in Discover logs integrates the date picker across Logs, Visualization, and Statistics tabs.

### Prometheus, APM, and packaged observability

Dashboards 3.5.0 can query and visualize Prometheus alongside logs and traces, with PromQL autocomplete and gauges. Its APM interface adds configuration, service and service-detail pages, application topology, and service-correlation drill-downs.

OpenSearch 3.6.0 adds a one-command Observability Stack bundling the collector, Data Prepper, OpenSearch, Prometheus, and Dashboards. Performance Analyzer adds a shard-operations collector.

In 3.7.0, Explore Metrics discovers Prometheus data sources and synchronizes generated PromQL with a raw editor. Dashboard variables use `$name` or `${name}` substitution, and visualization transformations can limit, sort, filter, aggregate, or compute fields without rerunning the base query.

The experimental 3.7.0 SLO catalog orders objectives by remaining error budget and supports burn-rate alerts and multi-window evaluation. A unified alerts view combines monitors and Prometheus rules and renders the Alertmanager routing tree read-only.

Since 3.8.0, metrics exploration can create alert rules directly. Prometheus metric rules support create, edit, clone, and delete through the Cortex ruler API, and Alert Manager manages anomaly detectors and forecasters.

### Investigations

Dashboards 3.6.0 investigations accept a hypothesis, track total and step durations, and rerun log analysis during reinvestigation.

## Detecting anomalies and forecasting

### Feature controls and result storage

Anomaly Detection 2.19.0 can trigger independently on a feature's rise or drop and apply per-feature moving suppression. An optional structured result-index format flattens entity values and arrays for easier queries and visualizations.

In 3.1.0, Anomaly Detection builds a self-updating forecast from a timestamped index by incrementally retraining a Random Cut Forest. Forecasts feed Alerting, and the Security plugin adds forecasting roles and permissions.

### Scheduling and authoring detectors

OpenSearch 3.2.0 supports anomaly intervals longer than one hour. In 3.3.0, real-time frequency scheduling and a suggest API are added, and frequency is optional.

Dashboards 3.4.0 adds Daily Insights with index management and data selection. Detectors gain an optional auto-create field, and missing-feature reporting honors detector frequency.

In 3.5.0, anomalies can be correlated by temporal-overlap similarity. In 3.6.0, detectors can be provisioned and managed through Terraform.

Since 3.8.0, single-stream detectors can use PPL as their source type and evaluate feature queries at runtime through PPL transport actions.

## Operating alerts and notifications

### Finding publication and request validation

OpenSearch 3.1.0 temporarily changes Alerting to publish a list of findings rather than one at a time. Document-level monitor create and update reject index patterns, and dry-run execution with an index pattern is blocked.

OpenSearch 3.2.0 reverts list publication: Alerting again publishes one finding at a time. Consumers should follow this later behavior.

In 3.3.0, monitors can use custom user attributes. Since 3.5.0, trigger execution can apply access control to result data exposed in the action context.

### Destinations and scheduling

OpenSearch 3.5.0 adds Mattermost as a notification-channel type and a Dashboards notification destination.

In 3.6.0, `plugins.alerting.monitor.max_triggers` caps triggers per monitor, while PPL and SQL monitors receive a configurable Dashboards lookback window.

OpenSearch 3.7.0 adds EventBridge Scheduler CRUD and SQS-backed external monitor scheduling. Configure the two-role EventBridge design with `execution_role_arn`.

### Multi-tenant restrictions

With Alerting multi-tenancy enabled in 3.7.0, email, findings, chained actions, Job Scheduler indexes, and other unsupported actions are disabled. Pluggable-data-format domains reject non-PPL monitor CRUD.

For multi-tenant anomaly data sources, default or flattened result indexes and historical analysis are disabled. Unsupported routes return HTTP 501.

In 3.8.0, Alerting adds a filter-by-backend-roles access strategy that controls how role filtering determines access to Alerting objects.
