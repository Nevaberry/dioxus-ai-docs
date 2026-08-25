# Alerting

Use this reference for rule authoring, evaluation, state, recording rules,
Alertmanager integration, contact points, imports, templates, and alerting APIs.

## Provisioning, imports, and API transitions

### HCL rule export (since 11.5.0)

The alert-rule editor can export a newly created rule as HCL for HCL-based
provisioning workflows.

### Kubernetes alerting API default (since 11.5.0)

The `alertingApiServer` feature flag is enabled by default. Notification-policy
trees and previews use the Kubernetes API; its template-group API and UI also
return the default built-in templates.

### Prometheus conversion and imports (since 12.0.0)

An API converts submitted Prometheus rules to Grafana-managed rules. Imports of
data-source-managed rules skip rules managed by plugins.

### Prometheus YAML imports and metadata (since 12.1.0)

Grafana-managed Alerting can import Prometheus YAML. Imported rules evaluate
sequentially and preserve group labels and `query_offset`. The Prometheus Rules
API adds health and contact-point filters and exposes rule provenance.

### Stable conversion responses (since 12.2.0)

The Prometheus-to-Grafana conversion API is stable, can return JSON, and accepts
extra labels.

### File-provisioning fields and validation (since 12.2.0)

File provisioning accepts `keepFiringFor` and
`missing_series_evals_to_resolve`. Deleting a `TimeInterval` checks whether
`ActiveTimings` still uses it.

### Provisioning validation (since 12.3.0)

Provisioning accepts recording rules without conditions and rejects receivers
whose name is empty. Otherwise identical rules can be matched by position.

### Import authorization and defaults (since 12.4.0)

Prometheus-rule imports can use a configured default data source, and the import
UI is restricted to administrators. The template-testing API has a dedicated
permission; Enterprise enrichments have separate read and write permissions.

### App Platform receiver testing (since 12.4.0)

Receiver testing moves to Kubernetes-style App Platform APIs. Contact points in
the single-Alertmanager path gain versioning, and the default notification
configuration uses an empty receiver.

### Legacy Alertmanager endpoint migration (13.0-upgrade)

`DELETE /api/alertmanager/grafana/config/api/v1/alerts` and
`POST /api/alertmanager/grafana/config/api/v1/receivers/test` are removed.
`GET /api/alertmanager/grafana/config/api/v1/alerts`,
`GET /api/alertmanager/grafana/config/history`, and
`POST /api/alertmanager/grafana/config/history/{id}/_activate` are admin-only.

Move automation to
`/apis/notifications.alerting.grafana.app/v1beta1/namespaces/{namespace}/` and
use `receivers`, `routingtrees`, `templategroups`, `timeintervals`, and
`inhibitionrules` for contact points, policies, templates, mute timings, and
inhibition rules.

### Provisioning authorization and managed routes (since 13.0.0)

Rules assign managed routes through `notification_settings.policy`, not labels,
and managed routes have access control. Provisioning APIs accept resource-specific
permissions and enforce protected-field authorization; notification APIs enforce
provenance permissions. Legacy notification actions and legacy alert-rule
provisioning endpoints are deprecated.

### Rules API v2 transition (since 13.1.0)

The `alerting.rulesAPIV2` feature flag is available, and the panel alert-rule
drawer uses Rules API v2. Notification provisioning endpoints are deprecated, so
automation should move away from them.

### Staged configuration imports (since 13.2.0)

The import workflow can import notification templates, stage and summarize a
configuration, promote it or enable automatic synchronization, and revert a
staged import. Non-admin users can navigate the wizard while synchronization is
inactive.

## Rule identity, authoring, and lifecycle

### Diagnostics and threshold operators (since 11.6.0)

Rule creation and rule views expose dependency-graph errors. Threshold rules
support multiple operators.

### Rule UIDs and version restoration (since 11.6.0)

New rules added to groups may be assigned a UID. Version history can restore an
earlier rule version and retains the latest version after deletion.

### Missing-series resolution (since 12.0.0)

Rule APIs and the rule form support `MissingSeriesEvalsToResolve` and
`missing_series_evals_to_resolve`, making the resolution threshold configurable.

### Recovery windows (since 12.0.0)

The backend supports `keep_firing_for` and a `Recovering` state for rules that
remain firing during a recovery window.

### Deleted-rule lifecycle (since 12.0.0)

Deleted rules can be recovered. Rules marked permanently deleted are removed in a
separate operation.

### Titles and evaluation order (since 12.0.0)

Rule titles are no longer unique, and rules in a group can evaluate sequentially.
Use UIDs rather than titles as identifiers.

### Backend-only plugin expressions (since 12.0.0)

Expressions work with plugins whose `plugin.json` declares `backend: true` and
`alerting: false`.

### Negative simple thresholds (since 12.0.0)

Simple-condition alert thresholds accept negative values.

### Rules without groups and label selectors (since 13.1.0)

Legacy storage accepts label selectors in `AlertRule` and `RecordingRule`.
Grafana-managed rules can be created without a group.

## Evaluation, state, and recording rules

### State persistence and retries (since 11.5.0)

`state_periodic_save_batch_size` controls periodic state-save batch size, and
`max_attempts` now defaults to 3. Account for changed batching and retry behavior.

### Inactive alerts in panels (since 11.5.0)

Alert-list panels can include inactive alerts rather than only active states.

### Per-rule recording destinations (since 11.6.0)

Each recording rule can select its write target instead of relying only on a
shared destination.

### Alerting state and group API behavior (since 11.6.0)

`alertingSaveStateCompressed` entered public preview, and
`alertingNoNormalState` was removed. A nonexistent group at
`/api/ruler/grafana/api/v1/rules/{Namespace}/{Groupname}` returns HTTP 404.

### Single-source `$value` behavior (since 12.0.0)

For alerts with one data source, `$value` returns the query value. Review
notification templates that relied on its former representation.

### Instance persistence and transition notifications (since 12.1.0)

Alert instances persist `FiredAt`, and state history can write the `ALERTS`
metric. Grafana resends states absent from evaluation results and immediately
notifies on Error-to-Normal and NoData-to-Normal transitions.

### Recording-rule default and destinations (since 12.1.0)

Recording rules are enabled by default. Grafana-managed recording rules support
PDC, use `default_datasource_uid` as their default target, and can have writes
disabled per data source in the UI.

### Recording-rule private labels (since 12.2.0)

Grafana filters private labels before writing recording rules.

### Retry with backoff (since 12.2.0)

Alert-rule evaluation supports retry with backoff.

### Compressed-state default (since 12.2.0)

`alertingSaveStateCompressed` is enabled by default, making compressed alert-state
persistence the default behavior.

### State-write jitter and template limits (since 12.3.0)

Periodic state storage supports jitter to spread database writes. From 12.3.3,
Alerting limits expanded notification-template size; review unusually large
expansions.

### Pending periods and webhook metadata (since 12.4.0)

Pending periods apply to NoData and Error alerts. Alert labels become annotation
tags, and webhook `valueString` includes expression-type information.

### Single-node evaluation and administration (since 13.0.0)

Alerting adds single-node evaluation. Alert Activity gains saved searches, policy
filtering, notification and silence views; panel-based rule creation is gated by
`createAlertRuleFromPanel`; the Prometheus Rules API can sort by folder full path.

### Alerting toggle removals (since 13.2.0)

`AlertingCentralHistory` and `alertingSaveStateCompressed` are removed. Do not
keep configuration or behavior branches dependent on either toggle.

## Delivery, Alertmanager, and contact points

### Jira, Slack, and time-range links (since 11.6.0)

Alerting adds Jira integration, including cloud Alertmanagers, and Slack receivers
gain a color option. Dashboard and panel links generated in alert templates carry
the alert time range.

### Signed and templatable webhooks (since 12.0.0)

Webhook integrations can use HMAC signatures and templatable payloads so receivers
can verify notifications and consume customized bodies.

### Internal Alertmanager writes removed (since 12.0.0)

Settings cannot manually edit or restore the internal Alertmanager configuration,
and its internal POST endpoint is removed. Clients must stop using those writes.

### Alertmanager RBAC request action (since 12.0.0)

Alertmanager requests accept `reqAction` for RBAC checks.

### OAuth2 webhooks and remote SMTP (since 12.1.0)

Webhook receivers support OAuth2. Grafana can send SMTP configuration to a remote
Alertmanager.

### Redis Sentinel HA (since 12.1.0)

Grafana Alerting high availability supports Redis Sentinel.

### External integrations and provisioned folders (since 12.4.0)

OpsGenie is deprecated. External Alertmanager connections support client
certificates and TLS options. Alert rules cannot be saved into Git-synced folders.

### Remote-write headers and metrics (since 12.4.0)

Alerting uses data-source headers for remote writes.
`grafana_alerting_rule_group_rules` gains a `folder_uid` label. The HA
Alertmanager cluster-metrics prefix changes, so update selectors and dashboards.

### Mimir synchronization and contact restrictions (since 13.1.0)

The settings UI exposes Mimir Alertmanager auto-sync. Grafana can restrict
available contact-point integration types and limit email recipients to
organization members.

### Routing-tree and provenance behavior (since 13.2.0)

Routing trees named `default` or `user-defined` count as the default routing tree.
Deleting a time interval checks managed-route references. A contact-point
provenance mismatch returns HTTP 403 rather than 500.

## Permissions, origins, and enrichment

### Dedicated status permission (13.0-upgrade)

`GET /api/alertmanager/grafana/api/v2/status` requires
`alert.notifications.system-status:read` rather than
`alert.notifications:read`. Admins receive it through
`fixed:alerting.notifications:writer`; add it to affected custom roles.

### Enterprise alert enrichment (since 12.3.0)

Enterprise Alerting adds per-rule enrichment endpoints and rule-view components.
An enrichment mutator can insert rule-UID labels for efficient label selection.

### Rule origin and sender metrics (since 13.1.0)

Plugin rule origin is sent in `X-Rule-Origin`. External Alertmanager sender
metrics identify data sources by UID.
