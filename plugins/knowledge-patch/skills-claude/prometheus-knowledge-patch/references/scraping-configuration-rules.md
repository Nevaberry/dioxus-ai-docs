# Scraping, Configuration, and Rules

## Strict scrape protocol handling (`3.0-migration`)

A target with no accepted `Content-Type`, or with an unparsable or unknown
value, fails instead of implicitly falling back to Prometheus text. Fix the
endpoint to advertise protobuf-delimited, Prometheus text 0.0.4/1.0.0, or
OpenMetrics 0.0.1/1.0.0. Otherwise set `fallback_scrape_protocol` explicitly.

When retaining classic histograms beside native ones, replace
`scrape_classic_histograms` with `always_scrape_classic_histograms`.

## Notifications, reloads, and dependency safety (`3.1.0`)

`prometheus_notifications_errors_total` increments by the number of affected
alerts, not once per failed batch. Update alerts that interpreted an increment
as one notification attempt.

Reloads apply `always_scrape_classic_histograms` and
`convert_classic_histograms_to_nhcb`. Rule dependency analysis falls back to
serial evaluation whenever it cannot prove concurrency safe. The OpenMetrics
parser accepts quoted exemplar keys.

## UTF-8 relabeling and rules (`3.2.0`)

Replace relabel actions accept UTF-8 in `targetLabel`. `$<chars>` and
`${<chars>}` expand in replacements, including the `replacement` field of
`LabelMap`. Rule names accept UTF-8 except `{` and `}`, which common-mistake
checks still reject.

With `metadata-wal-records`, metadata for automatic metrics is written to the
WAL.

## Rule YAML and alert relabeling (`3.3.0`)

Rule files support YAML anchors and aliases. Alert relabeling participates in
the decision to drop an alert; a drop decision is no longer made without the
relabel result.

## Scrape escaping, conversion, and reload (`3.4.0`)

Scrape configuration can select the escaping scheme requested during content
negotiation. Set `convert_classic_histograms_to_nhcb` globally when all jobs
share the policy:

```yaml
global:
  convert_classic_histograms_to_nhcb: true
```

Set the maximum notification batch size with
`--alertmanager.notification-batch-size`. Automatic configuration reload
reacts to changes in referenced rule and scrape configuration files, not only
the main file.

## Global classic scraping and early validation (`3.5.0`)

`always_scrape_classic_histograms` can be global:

```yaml
global:
  always_scrape_classic_histograms: true
```

Rule parse errors are detected during startup before normal evaluation begins.

## Template helpers and tracing (`3.6.0`)

Templates provide `toDuration()` and `now()`. Scrape requests carry a
`traceparent` header so scrape activity can join propagated tracing context.

## Alertmanager relabel isolation (`3.7.0`)

Mutating actions in one `alertmanager_config.alert_relabel_configs` block do
not pass the changed alert into later Alertmanager configuration blocks. Treat
each block's relabeling as independently scoped.

## URL escaping and unevaluated alerts (`3.8.0`)

Alert templates provide `urlQueryEscape` for dynamic URL query values:

```text
{{ urlQueryEscape $labels.instance }}
```

An alerting rule not yet evaluated has the explicit `unknown` state. API and UI
consumers must handle it alongside established states.

## Scrape compatibility and regression floor (`3.9.0`)

Classic protobuf scrapes no longer require the declared unit to appear in the
metric name. Prometheus 3.9.1 restores scrape relabel `keep` and `drop`, which
were broken in 3.9.0; use 3.9.1 when depending on those actions.

## Alertmanager delivery semantics (`3.10.0`)

`prometheus_notifications_dropped_total`,
`prometheus_notifications_queue_capacity`, and
`prometheus_notifications_queue_length` carry an `alertmanager` label. Aggregate
explicitly when old queries expected a single unlabeled series.

Each configured Alertmanager has an independent send loop instead of sharing
one, changing how multi-Alertmanager delivery is scheduled. During shutdown,
`/-/ready` includes `X-Prometheus-Stopping` while `NotReady`.

## Alert continuity across reloads (`3.11.0`)

Increasing an alert's `FOR` period no longer resets its state incorrectly to
pending. Alert state restoration also works when rule labels contain Go
template expressions.

## Stable reload and configuration validation (`3.12.0`)

Automatic configuration reload is stable. `remote_write.queue_config` is
validated while loading configuration so invalid values fail early rather than
causing runtime panics or silent misconfiguration.

Per-job `prometheus_sd_refresh*` and `prometheus_sd_discovered_targets` series
are removed when the scrape job is removed.

## Per-target histogram controls (`3.13.0`)

Target relabeling can override histogram policy with
`__convert_classic_histograms_to_nhcb__`,
`__always_scrape_classic_histograms__`, and
`__scrape_native_histograms__`:

```yaml
relabel_configs:
  - target_label: __scrape_native_histograms__
    replacement: "true"
```

## Current feature-driven configuration (`feature-flags`)

`--enable-feature=extra-scrape-metrics` is deprecated. Enable the replacement
globally or per job:

```yaml
global:
  extra_scrape_metrics: true
```

It stores `scrape_timeout_seconds`, `scrape_sample_limit`, and
`scrape_body_size_bytes`. A zero sample limit means unlimited. Body size is
`-1` when the body-size limit caused failure and `0` for other scrape failures.

Unless `scrape_protocols` is explicit, `created-timestamp-zero-ingestion`
changes the global preference to `PrometheusProto`, `OpenMetricsText1.0.0`,
`OpenMetricsText0.0.1`, then `PrometheusText0.0.4`.

`concurrent-rule-eval` runs dependency-free rules within a group concurrently.
Bound its additional query load with `--rules.max-concurrent-evals`, whose
default is `4`.

## Rendered config and rule-metric cleanup (`3.13.2-3.14.0`)

`/api/v1/status/config` preserves explicitly empty `separator: ""` and
`replacement: ""` fields instead of omitting them.

Removing or renaming a rule group deletes its stale
`rule_group_last_rule_duration_sum_seconds` and
`rule_group_last_restore_duration_seconds` series instead of leaking two
series per reload.
