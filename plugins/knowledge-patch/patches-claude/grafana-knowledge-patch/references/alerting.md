# Alerting

## Rule authoring, identity, and evaluation

### Portable rules and list visibility

The rule editor can export a newly created rule as HCL for HCL-based provisioning. Alert-list panels can include inactive alerts instead of limiting the display to active states. (11.5.0)

### Diagnostics, identity, and version history

Rule creation and rule views expose dependency-graph errors, and threshold rules accept multiple operators. New rules added to groups can receive UIDs. Version history can restore an earlier version and retains the newest version after deletion. Use the UID as identity: later rules no longer require unique titles. (11.6.0, 12.0.0)

Deleted rules can be recovered. A separate permanent-deletion state controls when a rule is actually removed. (12.0.0)

Rules in a group can evaluate sequentially. Alerting can also match otherwise identical rules by position; file provisioning accepts recording rules without conditions and rejects receivers whose name is empty. (12.0.0, 12.3.0)

Legacy storage accepts label selectors in `AlertRule` and `RecordingRule`, and Grafana-managed rules can be created without a group. (13.1.0)

### Conditions and evaluation states

Configure `MissingSeriesEvalsToResolve` in APIs or `missing_series_evals_to_resolve` in the rule form to control how many missing-series evaluations resolve an alert. `keep_firing_for` keeps a rule firing during its `Recovering` window. Simple-condition thresholds accept negative values. (12.0.0)

File provisioning accepts `keepFiringFor` and `missing_series_evals_to_resolve`. Evaluation can retry with backoff, and deleting a `TimeInterval` checks references from `ActiveTimings`. (12.2.0)

The pending period also applies to NoData and Error alerts. Alert labels become annotation tags, and webhook `valueString` includes the expression type. (12.4.0)

Single-node evaluation mode is available. Alert Activity includes saved searches, policy filtering, notification and silence views; panel-based rule creation is gated by `createAlertRuleFromPanel`, and the Prometheus Rules API can sort by full folder path. (13.0.0)

### Single-source template values and partial results

For an alert with one data source, `$value` returns the query value; review templates built around the older representation. Expressions work with backend plugins whose manifest sets `backend: true` and `alerting: false`. (12.0.0)

Server-side expressions isolate broken pipeline nodes so unaffected nodes can return partial results. (13.0.0)

## Rule conversion, import, and recording

### Prometheus rule conversion

An API converts submitted Prometheus rules into Grafana-managed rules. Data-source-managed imports skip rules controlled by plugins. (12.0.0)

Grafana-managed alerting can import Prometheus YAML. Imported rules run sequentially and preserve group labels and `query_offset`; the Prometheus Rules API adds health and contact-point filters and exposes provenance. (12.1.0)

The conversion API is stable, can respond with JSON, and accepts extra labels. (12.2.0)

Imports can use a configured default data source, while the import UI is administrator-only. (12.4.0)

The managed import workflow can import notification templates, stage and summarize configuration, promote it or enable automatic synchronization, and revert a staged import. When synchronization is inactive, non-admin users can navigate the wizard. (13.2.0)

### Recording rules

Each recording rule can choose its own write target. (11.6.0)

Recording rules are enabled by default. Grafana-managed recording rules support PDC, use `default_datasource_uid` as their default destination, and allow writes to be disabled per data source in the UI. (12.1.0)

Private labels are removed before recording-rule writes. (12.2.0)

Alerting uses data-source headers for remote writes. The `grafana_alerting_rule_group_rules` metric has a `folder_uid` label. (12.4.0)

## State persistence and transitions

### Batching, retries, and compression

`state_periodic_save_batch_size` controls periodic state-save batch size. The `max_attempts` default is 3, so upgrade capacity and retry assumptions together. (11.5.0)

`alertingSaveStateCompressed` entered public preview while `alertingNoNormalState` was removed. A missing group request at `/api/ruler/grafana/api/v1/rules/{Namespace}/{Groupname}` returns 404. (11.6.0)

Alert instances persist `FiredAt`, and state history can write the `ALERTS` metric. Alerts absent from evaluation results are resent; Error-to-Normal and NoData-to-Normal transitions notify immediately. (12.1.0)

Compressed state persistence became the default when `alertingSaveStateCompressed` was enabled by default. (12.2.0)

Periodic state storage supports jitter to distribute database writes. Starting in 12.3.3, expanded notification templates have a size limit; review unusually large expansions. (12.3.0)

`AlertingCentralHistory` and `alertingSaveStateCompressed` are later removed as feature toggles; remove both gates from configuration. (13.2.0)

### Removed state behavior

`alertingNoDataErrorExecution`, the Loki Alert State History toggles, and related removed gates no longer select alert execution or state-history behavior. (12.0.0)

## Contact points and notification delivery

### Webhooks and authentication

Webhooks support HMAC signatures and templatable payloads, allowing receivers to verify and customize notification bodies. (12.0.0)

Webhook receivers support OAuth2 authentication. Grafana can pass SMTP configuration to a remote Alertmanager. (12.1.0)

External Alertmanager connections accept client-certificate authentication and TLS options. OpsGenie is deprecated. (12.4.0)

### Integrations, links, and receiver behavior

Jira is available, including in cloud Alertmanagers, and Slack receivers accept a color option. Dashboard and panel links produced by alert templates include the alert time range. (11.6.0)

The default notification configuration uses an empty receiver. Contact points in the single-Alertmanager path are versioned, and receiver tests use Kubernetes-style App Platform APIs. (12.4.0)

Contact-point integration types can be restricted, and email recipients can be limited to organization members. The settings UI also exposes Mimir Alertmanager auto-sync. (13.1.0)

### Routes, mute timings, and provenance

Cloud migration treats mute timings as notification-policy dependencies and migrates the related resources together. (12.1.0)

Rules assign managed routes through `notification_settings.policy`, not labels. Managed routes have access control. Provisioning APIs accept resource-specific permissions and enforce authorization for protected fields; notification APIs enforce provenance permissions. Legacy notification actions and legacy rule-provisioning endpoints are deprecated. (13.0.0)

Routing trees named `default` or `user-defined` count as the default tree. Time-interval deletion checks managed-route references, and a contact-point provenance mismatch returns 403 rather than 500. (13.2.0)

## Alerting APIs and permissions

### Kubernetes alerting API

`alertingApiServer` is enabled by default. Notification-policy trees and previews use the Kubernetes API, and its template-group API and UI include built-in default templates. (11.5.0)

Alertmanager requests can carry `reqAction` for RBAC checks. (12.0.0)

Enterprise enrichments have separate read and write permissions, while template testing has its own permission. (12.4.0)

`alerting.rulesAPIV2` is available, and the panel rule drawer uses Rules API v2. Notification provisioning endpoints are deprecated; migrate automation away from them. (13.1.0)

### Legacy Alertmanager endpoints

The settings UI can no longer manually edit or restore internal Alertmanager configuration, and its internal POST endpoint is removed. (12.0.0)

`DELETE /api/alertmanager/grafana/config/api/v1/alerts` and `POST /api/alertmanager/grafana/config/api/v1/receivers/test` are removed. These routes are admin-only: `GET /api/alertmanager/grafana/config/api/v1/alerts`, `GET /api/alertmanager/grafana/config/history`, and `POST /api/alertmanager/grafana/config/history/{id}/_activate`. (13.0-upgrade)

Manage notification resources under `/apis/notifications.alerting.grafana.app/v1beta1/namespaces/{namespace}/`. Use `receivers`, `routingtrees`, `templategroups`, `timeintervals`, and `inhibitionrules` for contact points, policies, templates, mute timings, and inhibition rules. (13.0-upgrade)

### Dedicated permissions and metrics

`GET /api/alertmanager/grafana/api/v2/status` requires `alert.notifications.system-status:read`, not `alert.notifications:read`. Add it to custom roles; administrators receive it through `fixed:alerting.notifications:writer`. (13.0-upgrade)

Enterprise per-rule enrichment APIs and rule views can use a mutator that inserts rule-UID labels for efficient label-selector queries. (12.3.0)

The HA Alertmanager cluster-metric prefix changes; update selectors and dashboards. (12.4.0)

Plugin rule origin propagates in `X-Rule-Origin`, and external Alertmanager sender metrics identify data sources by UID. (13.1.0)

## High availability

Grafana Alerting high availability supports Redis Sentinel deployments. (12.1.0)
