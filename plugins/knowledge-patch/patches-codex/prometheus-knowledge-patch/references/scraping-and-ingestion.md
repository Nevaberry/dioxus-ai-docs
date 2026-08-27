# Scraping and Ingestion

Use this reference for scrape protocol negotiation, metric naming, relabeling,
histogram scrape controls, and created-timestamp behavior.

## Protocol negotiation and parsing

### Require a recognized Content-Type (3.0-migration)

A scrape fails when a target omits an accepted `Content-Type` or supplies an
unparsable or unknown value. Fix the exporter to advertise protobuf-delimited,
Prometheus text 0.0.4/1.0.0, or OpenMetrics 0.0.1/1.0.0. Otherwise configure
`fallback_scrape_protocol` explicitly for that target.

### Accept quoted OpenMetrics exemplar keys (3.1.0)

The OpenMetrics text parser accepts the format's quoted exemplar-key form, so
producers using quoted keys are not rejected.

### Request an escaping scheme (3.4.0)

Scrape configuration can select the escaping scheme requested from targets
during content negotiation. Set it when exporter name escaping must be
predictable.

### Relax classic-protobuf unit naming (3.9.0)

Classic protobuf scraping no longer requires the unit to be part of the metric
name. Producers may supply unit metadata independently of the name.

### Created-timestamp zero injection changes negotiation (feature-flags)

Unless `scrape_protocols` is explicit, enabling
`created-timestamp-zero-ingestion` changes the global preference to
`PrometheusProto`, `OpenMetricsText1.0.0`, `OpenMetricsText0.0.1`, then
`PrometheusText0.0.4`. Configure the list explicitly when protobuf-first
negotiation is not desired.

## Names, labels, and relabeling

### Choose UTF-8 or legacy validation (3.0-migration)

Metric and label names accept UTF-8. Previously rejected names can be ingested,
and exposed names may change after upgrade. Preserve the earlier validation
globally or per scrape job:

```yaml
global:
  metric_name_validation_scheme: legacy
```

The allowed values are `utf8` and `legacy`.

### Normalize classic histogram and summary labels (3.0-migration)

Classic histogram `le` and summary `quantile` values are stored as float-like
strings regardless of protocol. An exposed `"1"` becomes `"1.0"`. Update
rules, alerts, and dashboards that match integer strings; queries spanning the
transition can still be surprising.

```promql
my_classic_hist_bucket{le="1.0"}
```

### Use UTF-8 relabel targets and replacements (3.2.0)

Replace relabel actions accept UTF-8 in `targetLabel`. `$<chars>` and
`${<chars>}` expand, and the same behavior applies to the `replacement` field
for `LabelMap` actions.

### Inspect explicitly empty relabel fields (3.13.2-3.14.0)

`/api/v1/status/config` includes `separator: ""` and `replacement: ""` when
either field was explicitly set empty. Configuration consumers must distinguish
an explicit empty value from an omitted field.

## Created and start timestamps

### Do not expect extra `_created` series (3.0.0)

With `created-timestamp-zero-ingestion`, processing created timestamps no
longer creates additional `_created` time series.

## Histogram scrape controls

### Rename the classic-retention option (3.0-migration)

Replace job-level `scrape_classic_histograms` with
`always_scrape_classic_histograms` when retaining a concurrently exposed
classic histogram:

```yaml
scrape_configs:
  - job_name: mixed-histograms
    scrape_native_histograms: true
    always_scrape_classic_histograms: true
```

### Reload all histogram scrape settings (3.1.0)

Configuration reloads honor `always_scrape_classic_histograms` and
`convert_classic_histograms_to_nhcb`; they are no longer silently ignored.

### Skip disabled native histograms (3.3.0)

When native-histogram ingestion is disabled, scraping skips native-histogram
series rather than ingesting them unexpectedly.

### Configure classic-to-NHCB conversion globally (3.4.0)

Set `convert_classic_histograms_to_nhcb` in `global` rather than repeating it
for each job when all scrapes need the same conversion:

```yaml
global:
  convert_classic_histograms_to_nhcb: true
```

### Retain classic histograms globally (3.5.0)

`always_scrape_classic_histograms` is also a global option:

```yaml
global:
  always_scrape_classic_histograms: true
```

### Send trace context on scrapes (3.6.0)

Scrape requests include the `traceparent` HTTP header, allowing scrape work to
participate in propagated tracing context.

### Override histogram behavior per target (3.13.0)

Target relabeling can set these reserved labels for individual targets:

- `__convert_classic_histograms_to_nhcb__`
- `__always_scrape_classic_histograms__`
- `__scrape_native_histograms__`

```yaml
relabel_configs:
  - target_label: __scrape_native_histograms__
    replacement: "true"
```

## Scrape metadata and diagnostics

### Include scrape-pool data for dropped targets (3.3.0)

Dropped targets returned by `/api/v1/targets` include their scrape pool name.
Use it to attribute a dropped target to its job.

### Move extra scrape metrics into configuration (feature-flags)

`--enable-feature=extra-scrape-metrics` is deprecated. Enable the replacement
globally or per scrape configuration:

```yaml
global:
  extra_scrape_metrics: true
```

This stores `scrape_timeout_seconds`, `scrape_sample_limit`, and
`scrape_body_size_bytes`. A zero sample limit means unlimited. Body size is
`-1` when the size limit caused failure and `0` for other scrape failures.
