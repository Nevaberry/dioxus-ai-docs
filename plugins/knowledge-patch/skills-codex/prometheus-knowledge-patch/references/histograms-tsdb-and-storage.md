# Histograms, TSDB, and Storage

Use this reference before enabling native histograms, changing block or WAL
formats, tuning retention, or adopting experimental storage behavior.

## Native histogram ingestion and compatibility

### Configure scraping even after stabilization (3.0-migration)

From v3.9, `native-histograms` is a no-op because the feature is stable, but
scraping native histograms still requires the configuration introduced in
v3.8:

```yaml
global:
  scrape_native_histograms: true
```

### Ingest Created-Timestamp and out-of-order histograms (3.0.0)

Created-Timestamp processing supports native histograms, and TSDB accepts
out-of-order native-histogram samples when out-of-order ingestion is configured.

### Persist automatic-metric metadata in the WAL (3.2.0)

The `metadata-wal-records` feature writes metadata for automatic metrics to the
WAL. Account for those records in WAL readers and recovery tooling.

### Retire the dedicated out-of-order flag (3.4.0)

`--enable-feature=ooo-native-histograms` is a no-op. Out-of-order native
histograms are enabled when `out_of_order_time_window` is greater than zero and
native histograms are enabled for releases that still require that feature
gate.

### Monitor unknown replay references (3.4.0)

Use `prometheus_tsdb_wal_replay_unknown_refs_total` and
`prometheus_tsdb_wbl_replay_unknown_refs_total` for unknown series references
encountered during WAL and WBL replay.

### Track stale Head series (3.6.0)

`prometheus_tsdb_head_stale_series` reports stale series in the Head block.

### Validate and reduce schemas (3.7.0)

Unsupported native-histogram schemas are rejected on append. For scrape and
remote write, schemas from -9 through 52 are reduced in resolution to the
supported maximum. Invalid schemas are ignored during WAL/WBL replay, while
exponential schemas read from chunks or remote read are also reduced.

### Validate custom bounds (3.8.0)

Custom-bucket native histograms reject a NaN threshold. `-Inf` is valid as the
first custom-bound value.

### Combine conversion with zero-timestamp ingestion (3.8.0)

Classic-histogram-to-NHCB conversion can run together with
created-timestamp zero ingestion.

### Observe native histograms across subsystems (3.9.0)

PromQL, rule, service-discovery, and scrape instrumentation provide native
histograms alongside summaries. Notification latency also exposes
`prometheus_notifications_latency_histogram_seconds`.

### Measure out-of-order distance (3.9.0)

`prometheus_tsdb_sample_ooo_delta` records the out-of-order distance in seconds
for every sample, whether accepted or rejected.

### Count Head histogram series and buckets (3.13.2-3.14.0)

Use `prometheus_tsdb_head_native_histogram_series` and
`prometheus_tsdb_head_native_histogram_buckets` to measure current Head usage.

## Block loading, inspection, and interoperability

### Inspect loaded block metadata (3.6.0)

`/v1/status/tsdb/blocks` exposes metadata for blocks currently loaded by
Prometheus.

### Configure a Thanos-compatible delay file (3.9.0)

Use `--storage.tsdb.delay-compact-file.path` for the compaction-delay file used
for improved Thanos interoperability.

### Tune block reload cadence (3.9.0)

Set `--storage.tsdb.block-reload-interval` to control how often TSDB reloads
blocks.

### Dump labels without samples (3.9.0)

For a labels-only JSON TSDB dump, run:

```text
promtool tsdb dump --format seriesjson
```

## Retention and Head compaction

### Enable early stale-series compaction cautiously (3.10.0)

`stale_series_compaction_threshold` experimentally compacts stale series out of
memory once the configured threshold is reached. Validate WAL replay and chunk
boundaries before production use.

### Configure percentage-based retention (3.11.0)

`storage.tsdb.retention.percentage` limits TSDB storage to a percentage of
disk. Removing retention from the configuration falls back to CLI settings.
File-based `storage.tsdb.retention.time` no longer has the unit mismatch that
made retention one million times too long.

### Apply percentage-retention corrections (3.12.0)

Percentage-based retention works with the newer data path and preserves decimal
precision.

### Upgrade early-compaction deployments (3.13.0)

`CompactStaleHead` and `CompactSelectedSeries` retain label records through WAL
checkpoint/replay and preserve samples at chunk-range boundaries. Earlier
eviction paths could fail replay or lose samples.

### Preserve mixed-type stale series (3.13.2-3.14.0)

Series changing among float, integer-histogram, and float-histogram samples are
not evicted early. `prometheus_tsdb_head_stale_series` also no longer
over-counts them.

## Start timestamps and experimental encodings

### Record active-series state for fast startup (3.11.0)

`--enable-feature=fast-startup` writes active-series state to
`series_state.json` in the WAL directory for reuse after restart.

### Store start timestamps (3.11.0)

`--enable-feature=st-storage` stores ingested start timestamps, formerly called
Created Timestamps, from scrapes or OTLP in TSDB and the Agent WAL and exposes
them through Remote Write 2.

### Select XOR2 block encoding (3.11.0)

`--enable-feature=xor2-encoding` chooses a float-sample chunk encoding optimized
for scraped data that can encode start timestamps.

### Synthesize missing timestamps (3.12.0)

`--enable-feature=st-synthesis` synthesizes unknown start timestamps for
scraped cumulative metrics, useful when forwarding Remote Write 2 data to
delta- or OpenTelemetry-based backends.

### Select float encoding at runtime (3.13.0)

`storage.tsdb.chunk_encoding.floats` selects `xor` or `xor2` independently of
`--enable-feature=xor2-encoding`.

### Satisfy start-timestamp encoding prerequisites (feature-flags)

`st-storage` does not select an ST-capable block encoding. Float chunks must
resolve to XOR2 or startup/config reload fails. Persisting native- and
float-histogram start timestamps additionally requires
`--enable-feature=histograms-st-encoding`. `SamplesV2` WAL records can be
replayed only by Prometheus 3.11 or later.

XOR2, `histogramST`, and `floathistogramST` blocks are unreadable by older
releases. Their experimental formats can change, and downstream block readers
may not support them. Enabling them creates a downgrade and interoperability
boundary.

### Understand synthesis rewrites (feature-flags)

For scraped cumulative metrics without start timestamps, `st-synthesis` drops
the first sample and subtracts its value from later samples, so stored raw
values differ from the scrape stream. It is not implemented for remote write or
OTLP. It rejects those metrics' out-of-order samples regardless of
`out_of_order_time_window`; after an append failure it clears series state, so
the next sample becomes another dropped reference point.

### Use direct I/O only on Linux (feature-flags)

`--enable-feature=use-uncached-io` uses Linux direct I/O for chunk writes and
bypasses the page cache.

## Correctness fixes requiring upgrades

### Prevent duplicate Agent appends (3.12.0)

Concurrent Agent appends for one label set no longer create duplicate in-memory
series or duplicate WAL records.

### Avoid XOR2 restart corruption (3.13.0)

Chunk-snapshot encoding for `EncXOR2` is fixed. Earlier behavior could corrupt
TSDB on restart when XOR2 series were present.

### Preallocate the active query tracker (3.13.2-3.14.0)

The active query tracker file is preallocated, avoiding SIGBUS crashes when the
data disk is full.

### Apply restart and compaction fixes (3.13.2-3.14.0)

Prometheus 3.14 fixes potential restart data loss after out-of-order ingestion
and compaction, missing samples and errors from deleted series after restart,
and corrupted native histograms after restart. Out-of-order queries no longer
block compaction for hours while memory grows.

### Surface TSDB query failures (3.13.2-3.14.0)

TSDB query errors previously discarded are returned to callers.

### Preserve float encoding through compaction (3.13.2-3.14.0)

Compaction honors the configured float chunk encoding rather than silently
rewriting XOR2 chunks as XOR.
