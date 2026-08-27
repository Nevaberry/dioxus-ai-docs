# Remote Storage and OTLP

## Remote-write defaults and remote-read contracts (`3.0-migration`)

Remote-write clients default `http_config.enable_http2` to `false`, allowing
parallel queues to use multiple sockets. Set it to `true` explicitly only to
retain the old HTTP/2 behavior.

TSDB-compatible remote storage must return only results matching requested
selectors. Third-party `remote_read` backends that return additional series can
trigger undefined behavior even though Prometheus does not explicitly enforce
the contract.

## UTF-8-preserving OTLP translation (`3.0.0`)

Set `otlp.translation_strategy: NoUTF8EscapingWithSuffixes` to preserve UTF-8
names while retaining metric suffix translation.

## OTLP identity and remote-write DNS (`3.1.0`)

OTLP translation retains identifying attributes in `target_info`. The receiver
also converts metric metadata and accepts colons in non-standard unit strings.

Remote-write clients can opt into a resolver that selects a random returned IP
so a multi-address endpoint does not always receive traffic at the same address.

## Delta-to-cumulative conversion (`3.2.0`)

Enable `otlp-deltatocumulative` to convert delta-temporality OTLP metrics rather
than dropping them:

```text
--enable-feature=otlp-deltatocumulative
```

Conversion keeps per-series state in memory. Restarting loses the state and
causes a counter reset; inactive state is cleared according to `max_stale`.

## Histogram and translation modes (`3.4.0`)

An opt-in feature translates OTLP explicit-bucket histograms into custom-bucket
native histograms. Translation configuration can also leave metric names and
attributes untranslated.

Primitive raw-delta ingestion is distinct from `otlp-deltatocumulative`: it
stores deltas rather than maintaining cumulative state. OTLP receiver defaults
apply even when the configuration omits the `otlp:` block.

## Resource attributes and Azure identity (`3.5.0`)

Promote all OTLP resource attributes while excluding selected keys:

```yaml
otlp:
  promote_all_resource_attributes: true
  ignore_resource_attributes:
    - service.instance.id
```

Remote-write Azure AD authentication accepts an empty `client_id` for a
system-assigned managed identity:

```yaml
azuread:
  managed_identity:
    client_id: ""
```

## Scope metadata and resource coverage (`3.6.0`)

`UnderscoreEscapingWithoutSuffixes` escapes names with underscores without
adding translated suffixes. Set `otlp.promote_scope_metadata: true` to expose
scope metadata as labels. With `type-and-unit-labels`, OTLP metrics receive
`__type__` and `__unit__` labels.

Prometheus generates `target_info` samples between the earliest and latest
samples for each resource, keeping resource metadata available across that
resource's sample interval.

## Remote-write metric migration and OTLP start times (`3.7.0`)

Replace deprecated remote-write metrics as follows:

| Deprecated | Replacement |
|---|---|
| `prometheus_remote_storage_samples_in_total` | `prometheus_wal_watcher_records_read_total{type="samples"}` plus `prometheus_remote_storage_samples_dropped_total` |
| `prometheus_remote_storage_histograms_in_total` | `prometheus_wal_watcher_records_read_total{type=~".*histogram_samples"}` plus `prometheus_remote_storage_histograms_dropped_total` |
| `prometheus_remote_storage_exemplars_in_total` | `prometheus_wal_watcher_records_read_total{type="exemplars"}` plus `prometheus_remote_storage_exemplars_dropped_total` |
| `prometheus_remote_storage_highest_timestamp_in_seconds` | `prometheus_remote_storage_queue_highest_timestamp_seconds`, which accounts for relabeling |

Remote write supports Azure Workload Identity. Remote Write 2 outgoing series
carry type and unit labels when `type-and-unit-labels` is enabled.

With `created-timestamp-zero-ingestion`, the OTLP receiver writes metric start
times as created-time zero samples. From 3.7.1, translating an attribute name
that starts with one underscore prefixes the label with `key_`; multiple
leading underscores are preserved.

## Remote Write 2 and authentication (`3.8.0`)

The receiver follows Remote Write 2.0-rc.4, renaming “created timestamp” to
“start timestamp”; integrations must use the updated schema and terminology.

OAuth2 supports the RFC 7523 section 3.1 JWT bearer grant. SigV4 supports
`use_fips_sts_endpoint` for a FIPS-compliant STS endpoint:

```yaml
sigv4:
  use_fips_sts_endpoint: true
```

OTLP ingestion de-duplicates `target_info` samples with the same series and
timestamp.

## Validation and custom Azure scope (`3.9.0`)

Remote-write AzureAD can request a custom scope. Remote read validates received
histograms rather than accepting invalid histogram data.

## OTLP loss and reserved names (`3.10.0`)

OTLP conversion filters the `__name__` attribute so it cannot create a duplicate
label beside the translated metric name. A fixed ingestion path prevents OTLP
sum metrics from being silently lost; OTLP-sum users should upgrade.

## Protocol error and timing semantics (`3.11.0`)

SigV4 HTTP authentication accepts an AWS `external_id`. Too-old Remote Write 2
histogram samples return HTTP 400 instead of 500, preventing pointless retries.
OTLP histogram exemplars are placed in the correct part of the histogram.
`prometheus_remote_storage_sent_batch_duration_seconds` is measured after the
request is sent rather than before it.

## Receiver validation and tracing (`3.12.0`)

Prometheus validates `remote_write.queue_config` fields at configuration load,
preventing a runtime panic or silent misconfiguration. The OTLP write endpoint
limits decompressed gzip request bodies. Insecure OTLP-over-HTTP tracing no
longer prevents startup.

## Azure Monitor certificates (`3.13.0`)

Remote write can authenticate to an Azure Monitor Workspace with a certificate.

## Raw delta and reserved-label constraints (`feature-flags`)

`otlp-native-delta-ingestion` stores raw deltas and is mutually exclusive with
`otlp-deltatocumulative`. It ignores `StartTimeUnixNano` and records unknown
metric metadata. `rate()` and `increase()` are wrong for these series; sum
aligned windows directly:

```promql
sum_over_time(delta_metric[5m])
sum_over_time(delta_metric[5m]) / 5m
```

Same-timestamp deltas are not combined. Federation can miscollect deltas when
ingestion and scrape intervals differ, and mixed delta/cumulative streams need
an explicit distinguishing label.

With `type-and-unit-labels`, ingestion metadata overrides user values for
`__type__` and `__unit__`. PromQL drops these labels in operations that drop
`__name__`; metadata WAL records also win conflicts with labels already on a
Remote Write 2 series.

## Translation and workload-identity diagnostics (`3.13.2-3.14.0`)

OTLP translation warns when distinct attributes sanitize to one Prometheus
label. Monitor `prometheus_api_otlp_translation_warnings_total{category=...}`.
Remote-write Azure workload identity honors `AZURE_FEDERATED_TOKEN_FILE`
instead of assuming a hard-coded token path.
