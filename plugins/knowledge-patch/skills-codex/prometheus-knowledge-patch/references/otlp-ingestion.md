# OTLP Ingestion

Use this reference when configuring OTLP translation, metadata promotion,
delta-temporality handling, start timestamps, or histogram conversion.

## Translation strategies and identity

### Preserve UTF-8 while retaining suffixes (3.0.0)

Set `otlp.translation_strategy` to `NoUTF8EscapingWithSuffixes` to avoid UTF-8
normalization while retaining suffix translation.

### Preserve target identity and metric metadata (3.1.0)

Translation keeps identifying attributes in `target_info`. The receiver also
converts metric metadata and accepts colons in non-standard unit strings,
preserving more resource context without rejecting custom units.

### Leave names and attributes untranslated (3.4.0)

OTLP translation can preserve original OTLP metric names and attributes rather
than translating them. Choose this only when downstream Prometheus naming and
query behavior can accommodate those forms.

### Respect defaults without an `otlp` block (3.4.0)

Receiver defaults apply even when configuration omits the `otlp:` block.

### Escape with underscores but omit suffixes (3.6.0)

Use `UnderscoreEscapingWithoutSuffixes` to escape names with underscores
without translated suffixes:

```yaml
otlp:
  translation_strategy: UnderscoreEscapingWithoutSuffixes
```

### Handle leading underscores consistently (3.7.0)

From 3.7.1, translating an attribute beginning with one underscore prefixes
the label with `key_`; multiple consecutive underscores are preserved. This
restores behavior that 3.7.0 changed.

### Filter the metric-name attribute (3.10.0)

Conversion drops the reserved `__name__` attribute so it cannot create a
duplicate label next to the translated metric name.

### Monitor translation collisions (3.13.2-3.14.0)

Translation warns when distinct OTLP attributes sanitize to the same Prometheus
label. Monitor `prometheus_api_otlp_translation_warnings_total`, grouped by its
`category` label.

## Resource, scope, type, and unit metadata

### Promote resource attributes broadly (3.5.0)

Use `promote_all_resource_attributes` with selective exclusions:

```yaml
otlp:
  promote_all_resource_attributes: true
  ignore_resource_attributes:
    - service.instance.id
```

### Promote scope metadata (3.6.0)

Set `otlp.promote_scope_metadata` to add scope metadata as metric labels:

```yaml
otlp:
  promote_scope_metadata: true
```

### Add type and unit labels (3.6.0)

With `--enable-feature=type-and-unit-labels`, OTLP metrics receive `__type__`
and `__unit__` labels.

### Fill target-info sample intervals (3.6.0)

Prometheus generates `target_info` samples from the earliest through latest
sample for each OTLP resource, keeping its resource metadata available across
the resource's sample interval.

### De-duplicate target information (3.8.0)

OTLP ingestion de-duplicates `target_info` samples sharing the same series and
timestamp.

### Treat type and unit labels as reserved (feature-flags)

Ingestion metadata overrides incoming values for `__type__` and `__unit__`.
PromQL drops them under the same kinds of operations that drop `__name__`. If a
metadata WAL record conflicts with labels on a Remote Write 2 series, the
reserved metadata values take precedence.

## Delta temporality

### Convert deltas to cumulative metrics (3.2.0)

Enable `otlp-deltatocumulative` to convert delta-temporality metrics instead of
dropping them:

```text
--enable-feature=otlp-deltatocumulative
```

The converter keeps per-series state in memory. Restarting loses that state and
causes a counter reset; inactive state is cleared according to `max_stale`.

### Distinguish raw-delta ingestion (3.4.0)

The receiver can ingest delta metrics as-is. This is different from
`otlp-deltatocumulative`, which maintains cumulative state.

### Query native deltas as deltas (feature-flags)

`otlp-native-delta-ingestion` stores raw deltas and is mutually exclusive with
`otlp-deltatocumulative`. It ignores `StartTimeUnixNano` and records unknown
metric metadata. `rate()` and `increase()` are incorrect for these series; sum
aligned deltas directly:

```promql
sum_over_time(delta_metric[5m])
sum_over_time(delta_metric[5m]) / 5m
```

Align the range with the collection interval. Equal-timestamp deltas are not
summed. Federation can miscollect them when ingestion and scrape intervals
differ, and mixed delta/cumulative streams need an explicit distinguishing
label.

## Histograms, exemplars, and sums

### Convert explicit histograms to custom buckets (3.4.0)

An opt-in feature can translate OTLP explicit-bucket histograms into native
histograms with custom buckets.

### Store OTLP start times as created-time samples (3.7.0)

With `created-timestamp-zero-ingestion`, the receiver writes metric start times
into TSDB as created-time zero samples.

### Preserve OTLP sums (3.10.0)

A corrected ingestion path no longer silently loses OTLP sum metrics. Upgrade
deployments receiving OTLP sums rather than depending on affected behavior.

### Place histogram exemplars correctly (3.11.0)

OTLP exemplars are no longer mixed into the wrong parts of a histogram.

## Request handling and tracing

### Limit decompressed request size (3.12.0)

The OTLP write endpoint limits the decompressed size of gzip request bodies.
Size clients and gateway limits for the uncompressed payload, not only the
wire size.

### Allow insecure OTLP-over-HTTP tracing (3.12.0)

Prometheus no longer fails startup when tracing is configured to send insecure
OTLP over HTTP.
