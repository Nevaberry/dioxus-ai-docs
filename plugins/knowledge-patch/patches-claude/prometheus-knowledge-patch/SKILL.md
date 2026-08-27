---
name: prometheus-knowledge-patch
description: Prometheus
version: "3.13.0"
license: MIT
metadata:
  author: Nevaberry
---


# Prometheus Knowledge Patch

Use this skill when upgrading, configuring, querying, integrating, or operating
Prometheus and recent behavior may affect the result. Inspect the deployed
server, image, configuration, and client versions first. Apply version-tagged
guidance only when it matches the deployment, and prefer observed behavior and
the repository's tests over assumptions.

## Reference index

| Reference | Topics |
|---|---|
| [Histograms, TSDB, and start timestamps](references/histograms-tsdb-start-timestamps.md) | Native and classic histograms, TSDB compatibility, retention, WAL, encodings, start timestamps |
| [HTTP APIs and observability](references/http-apis-observability.md) | Query and status APIs, OpenAPI, self-metrics, tracing, notification and service metrics |
| [Migration, security, and deployment](references/migration-security-deployment.md) | Major-upgrade breaks, security floors, containers, logs, removed flags, redirect credentials |
| [PromQL](references/promql.md) | Language changes, experimental syntax, functions, modifiers, annotations, result corrections |
| [Promtool, UI, and feature flags](references/promtool-ui-feature-flags.md) | Validation and test tooling, UI behavior, feature discovery, current feature-gate constraints |
| [Remote storage and OTLP](references/remote-storage-otlp.md) | Remote read/write, protocol versions, authentication, OTLP translation and delta ingestion |
| [Scraping, configuration, and rules](references/scraping-configuration-rules.md) | Scrape negotiation, relabeling, reloads, rule evaluation, alerts, templates |
| [Service discovery](references/service-discovery.md) | Provider additions, metadata labels, filters, identity, reliability, build tags |

## Critical upgrade and security decisions

### Patch vulnerable lines before exposing endpoints

- On the 3.11 line, deploy at least 3.11.3. Earlier patch levels can disclose an
  AzureAD client secret, accept oversized Snappy remote-read requests, and
  expose stored-XSS paths in the UIs.
- Upgrade STACKIT service-discovery users to a fixed 3.12 release because
  rendered configuration previously exposed credentials.
- Prometheus 3.13.0 fixes CVE-2026-44990 in the UI and strips credentials and
  configured headers when an HTTP redirect crosses hosts.
- Use 3.13.2 or later when CVE-2026-56852 or GHSA-hrxh-6v49-42gf applies.

Read [Migration, security, and deployment](references/migration-security-deployment.md)
before choosing an image or patch level.

### Treat the v3 transition as a compatibility migration

- Remove feature gates that became default and replace the former `agent` and
  `remote-write-receiver` gates with `--agent` and
  `--web.enable-remote-write-receiver`.
- Remove the deleted `storage.tsdb.allow-overlapping-blocks`,
  `alertmanager.timeout`, and `storage.tsdb.retention` command-line flags.
- Upgrade through v2.55 before reusing a TSDB with v3. A v3 data directory
  cannot be downgraded below v2.55 without abandoning that persistent data.
- Configure Alertmanager API v2 and use Alertmanager 0.16.0 or later.
- Scrapes with a missing, unparsable, or unknown `Content-Type` now fail. Fix
  the producer or configure `fallback_scrape_protocol` deliberately.
- UTF-8 metric and label names are accepted by default. Set
  `metric_name_validation_scheme: legacy` globally or per job when old name
  validation is required.
- Update log parsing for `log/slog` fields such as `time`, `source`, and
  uppercase `level`, and update selectors for normalized `le` and `quantile`
  values such as `"1.0"`.

See [Migration, security, and deployment](references/migration-security-deployment.md)
for the complete transition checklist.

## Histograms, storage, and downgrade boundaries

### Native histogram activation is configuration-driven

Native histograms are stable starting in v3.9, so `native-histograms` becomes a
no-op, but scraping them still requires:

```yaml
global:
  scrape_native_histograms: true
```

Use `always_scrape_classic_histograms` to retain concurrently exposed classic
histograms; the old `scrape_classic_histograms` key is obsolete. Global,
per-job, and per-target controls are available, with target relabel labels
providing the narrowest override.

### Start-timestamp storage changes data compatibility

`st-storage` requires XOR2 for float chunks. Native- and float-histogram start
timestamps additionally require `histograms-st-encoding`. The resulting WAL
records need Prometheus 3.11 or later, and XOR2 or histogram-ST blocks may be
unreadable by older servers and downstream block consumers.

`st-synthesis` rewrites scraped cumulative values: it drops the first sample
and subtracts it from later samples. It does not apply to remote write or OTLP,
and it changes out-of-order handling and recovery after append failures.

Before enabling these features, read
[Histograms, TSDB, and start timestamps](references/histograms-tsdb-start-timestamps.md).

## PromQL compatibility quick reference

- Regular-expression `.` matches newlines as well as other characters.
- Duration and float literals are interchangeable, and duration expressions
  later become default. Use current `min_of()` and `max_of()` names instead of
  the earlier experimental duration `min()` and `max()` forms.
- Millisecond range selectors retain their precision rather than rounding to
  whole seconds.
- `histogram_fraction()` and `histogram_quantile()` return no value when classic
  and native histograms coexist at the same timestamp.
- `fill()`, `fill_left()`, and `fill_right()` supply values for unmatched sides
  of a binary expression; later fixes restore group-matched range results.
- Start-timestamp-aware rates cannot be combined with `anchored` or `smoothed`
  extended selectors.
- `sort()`, `sort_by_label()`, and `sort_by_label_desc()` do nothing in range
  queries and now emit warnings.
- Query raw OTLP deltas with aligned `sum_over_time()` windows; counter
  functions are wrong for natively stored delta values.

Read [PromQL](references/promql.md) before changing rule expressions or relying
on experimental syntax.

## Remote storage and OTLP quick reference

- Remote-write HTTP/2 now defaults off. Set `http_config.enable_http2: true`
  only when retaining the previous behavior is intentional.
- Replace deprecated remote-write input and highest-timestamp metrics with the
  WAL-watcher, dropped-sample, and queue-highest-timestamp metrics.
- Remote Write 2 uses “start timestamp” terminology and carries supported
  start timestamps, type labels, and unit labels.
- Too-old Remote Write 2 histogram samples return HTTP 400 so senders do not
  retry them indefinitely.
- Choose one OTLP delta mode: stateful delta-to-cumulative conversion or raw
  native delta ingestion. They are mutually exclusive.
- Validate translated label collisions through
  `prometheus_api_otlp_translation_warnings_total`.

Use [Remote storage and OTLP](references/remote-storage-otlp.md) for translation
strategies, identity propagation, authentication, and receiver limits.

## Scraping, configuration, and rules quick reference

- Explicitly configure `scrape_protocols` when created-timestamp zero injection
  must not make protobuf the first negotiation choice.
- Use `extra_scrape_metrics: true` globally or per job; the old
  `extra-scrape-metrics` feature gate is deprecated.
- Configuration reloads honor histogram scrape settings and automatic reload
  watches referenced rule and scrape files. Automatic reload is stable.
- Invalid remote-write queue settings are rejected while loading configuration.
- Unknown rule dependencies evaluate serially; optional concurrent evaluation
  applies only to dependency-free rules and should be bounded with
  `--rules.max-concurrent-evals`.
- API and UI clients must handle the explicit `unknown` state for an alerting
  rule that has not yet evaluated.

See [Scraping, configuration, and rules](references/scraping-configuration-rules.md)
for relabel overrides, alert delivery, reload cleanup, and template helpers.

## APIs and operational monitoring

- Discover server capabilities at `/api/v1/features` and the machine-readable
  HTTP contract at `/api/v1/openapi.yaml`.
- Query endpoints accept `limit`. For `stats`, use only `true` or `all`; other
  values are deprecated and scheduled for rejection.
- Distinguish `samplesRead` storage I/O from `totalQueryableSamples` evaluator
  loads. Enable `promql-per-step-stats` with `stats=all` for per-step reads.
- The TSDB status endpoint caps statistics at 10,000 sets.
- Monitor WAL/WBL unknown references, out-of-order distance, stale series,
  native histogram head use, OTLP translation warnings, and service-discovery
  update timestamps with their dedicated metrics.
- Notification metrics gain an `alertmanager` dimension, and each Alertmanager
  now has an independent send loop.

Read [HTTP APIs and observability](references/http-apis-observability.md) before
updating clients, dashboards, alerts, or tracing integrations.

## Service discovery and tooling

- Audit relabeling whenever a provider changes metadata labels. In particular,
  Hetzner `hcloud` no longer exposes `__meta_hetzner_datacenter`.
- Use provider-side filters where supported to reduce target volume before
  relabeling.
- `promtool` debug output is on stderr. Keep stdout separate in pipelines.
- Match `promtool` feature flags to gated PromQL syntax during checks, and use
  its fuzzy comparisons and explicit test start timestamps for time-sensitive
  rules.
- Prefer the feature discovery API over guessing support from a version string.

Consult [Service discovery](references/service-discovery.md) and
[Promtool, UI, and feature flags](references/promtool-ui-feature-flags.md) for
provider-specific and command-specific details.

## Working method

1. Identify the exact server version, image variant, enabled features, storage
   formats, remote protocol versions, and relevant client versions.
2. Read only the topic references needed for the task and honor their inline
   version attributions.
3. For upgrades, check security floors, removed options, storage downgrade
   boundaries, protocol changes, metric renames, and label-shape changes.
4. Validate configurations and rules with the matching `promtool` feature
   gates, then exercise affected API clients and dashboards.
5. Treat experimental formats and syntax as changeable. Preserve a rollback
   path before enabling storage encodings or ingestion modes that rewrite data.
