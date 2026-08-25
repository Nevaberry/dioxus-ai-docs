# Observability, Alerting, and Dashboards

Use this reference for logs, traces, metrics, dashboards, monitors, notifications, anomaly detection, forecasting, and investigation workflows.

## Discover, logs, and traces

### Unified Discover

- In 2.19.0, a disabled-by-default Discover view adds SQL and PPL alongside DQL and Lucene, with autocomplete and improved data selection.
- In 3.3.0, an optional redesign unifies log analytics, distributed tracing, automatic visualization selection, and context-aware analysis. Discover Traces adds click-to-filter exploration; disabled-by-default AI tools add conversational query and visualization actions.
- In 3.8.0, experimental Discover Logs runs SQL with date-picker integration across Logs, Visualization, and Statistics and is disabled by default.

### Trace Analytics

- In 3.1.0, Observability can use custom indexes for OpenTelemetry spans, logs, and service maps, map non-OpenTelemetry log fields, and correlate traces to logs across clusters.
- In 3.2.0, Trace Analytics accepts Data Prepper 2.11 OpenTelemetry output. Dashboards makes maximum service-map node and edge counts configurable.
- In 3.5.0, APM adds configuration, service and service-detail views, an application topology map, and service-correlation drill-downs.

### Agent and packaged observability

In 3.6.0, Agent Traces captures agent, language-model, and tool spans through OpenTelemetry. A Python instrumentation SDK supports Dashboards DAG and token-usage views.

The 3.6.0 one-command Observability Stack bundles the collector, Data Prepper, OpenSearch, Prometheus, and Dashboards. Performance Analyzer adds a shard-operations collector.

## Metrics and dashboards

### Prometheus and APM

OpenSearch Dashboards 3.5.0 can query and visualize Prometheus beside logs and traces, with PromQL autocomplete and gauge metrics.

### Explore Metrics

In 3.7.0, Explore Metrics discovers Prometheus data sources and keeps generated PromQL synchronized with the raw editor. Dashboard variables substitute `$name` or `${name}`. Visualization transformations can limit, sort, filter, aggregate, and compute fields without rerunning the base query.

### Metrics alert workflows

In 3.8.0, Metrics exploration can create alert rules directly. Prometheus metric rules support create, edit, clone, and delete through the Cortex ruler API, and Alert Manager manages anomaly detectors and forecasters.

### SLOs and unified alerts

The experimental 3.7.0 SLO catalog sorts objectives by remaining error budget and supports burn-rate alerts and multi-window evaluation. A unified alert view combines monitors with Prometheus rules and renders the Alertmanager routing tree read-only.

## Alerting

### Finding publication compatibility

- In 3.1.0, Alerting briefly publishes findings as a list rather than one at a time. Document-level monitor create and update reject index patterns, and dry-run execution with an index pattern is blocked.
- In 3.2.0, list publication is reverted; Alerting again publishes an individual finding. Version-gate consumers across this transition.

### Monitor execution and limits

- In 3.3.0, monitors can use custom user attributes.
- In 3.5.0, trigger execution can apply access control to result data exposed in its context.
- In 3.6.0, `plugins.alerting.monitor.max_triggers` caps triggers per monitor. Dashboards adds a configurable lookback window for PPL and SQL monitors.
- In 3.7.0, PPL monitor CRUD and manual execution are available through Alerting. Manual runs perform RBAC checks, and monitor names can be up to 100 characters rather than 30.

### PPL Alerting API lifecycle

- In 3.4.0, PPL Alerting adds monitor execution and statistics, get/search/delete monitor calls, and alert retrieval and lifecycle operations. Alerting V2 roles are added to `roles.yml`; bucket-level Dashboards trigger definitions can include keyword filters.
- In 3.6.0, experimental PPL Alerting assets are removed pending refactoring. Dashboards moves its APIs to v1 and no longer maintains separate legacy and PPL paths.

### External schedules

OpenSearch 3.7.0 adds EventBridge Scheduler CRUD and SQS-backed external monitor scheduling. Configure the two-role EventBridge design with `execution_role_arn`.

## Notifications

### Channels

Mattermost is a notification-channel type and a Dashboards destination in 3.5.0.

### Configuration migration

Notifications 3.6.0 adds `multi_tenancy_enabled` and changes its settings prefix. Review existing notification settings during upgrade.

### Tenant restrictions

Alerting multi-tenancy in 3.7.0 disables unsupported email, findings, chained actions, Job Scheduler indexes, and other actions. Pluggable-data-format domains reject non-PPL monitor CRUD, and unsupported routes return 501.

In 3.8.0, Alerting and Notifications each add a filter-by-backend-roles access strategy for object filtering or role matching.

## Anomaly Detection and forecasting

### Feature controls and result shape

In 2.19.0, detectors can trigger independently on a feature rise or drop and apply moving suppression per feature. An optional structured result-index format flattens entity values and arrays for easier querying and visualization.

### Forecasting

OpenSearch 3.1.0 adds native time-series forecasts over timestamped indexes. A self-updating Random Cut Forest incrementally retrains on new points, forecasts can feed Alerting, and Security includes forecasting roles and permissions.

### Scheduling and insights

- In 3.2.0, detector intervals may exceed one hour.
- In 3.3.0, real-time frequency scheduling and a suggest API are available; frequency is optional.
- In 3.4.0, Dashboards adds Daily Insights with index management and data selection. Detectors add optional auto-create fields, and missing-feature reporting honors detector frequency.

### Correlation and administration

- In 3.5.0, Anomaly Detection correlates anomalies by temporal-overlap similarity.
- In 3.6.0, detectors can be provisioned and managed through Terraform.
- In 3.8.0, single-stream detectors can use PPL as their source, evaluating feature queries through PPL transport actions.

### Multi-tenant limitations

For multi-tenant services in 3.7.0, Anomaly Detection data sources disable default or flattened result indexes and historical analysis.

## Investigations

Dashboards investigations in 3.6.0 can accept a hypothesis, record investigation and step durations, and rerun log analysis during reinvestigation.

## Query Insights integration

Query Insights views support historical top-N analysis, live inflight queries, query profiling, recommendations, multiple data sources, workload groups, and user-aware filtering. See [Search, Relevance, and Query Insights](search-relevance-and-insights.md) for API and authorization details.

## Legacy removals

OpenSearch 3.0.0 replaces Performance Analyzer RCA with Telemetry, removes Gantt Charts from the Dashboards bundle, and drops support for legacy Observability notebooks.
