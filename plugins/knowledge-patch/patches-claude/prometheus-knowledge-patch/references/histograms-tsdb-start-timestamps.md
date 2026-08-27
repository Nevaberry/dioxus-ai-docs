# Histograms, TSDB, and Start Timestamps

## Native histogram activation and classic retention (`3.0-migration`)

Starting in v3.9, `native-histograms` is a no-op because native histograms are
stable. Scraping them still requires the configuration introduced for v3.8:

```yaml
global:
  scrape_native_histograms: true
```

When a target exposes native and classic forms together, use
`always_scrape_classic_histograms`; `scrape_classic_histograms` is the obsolete
name. The option can be global or job-specific.

## Created timestamps and out-of-order histograms (`3.0.0`)

With `created-timestamp-zero-ingestion`, processing a created timestamp no
longer emits an additional `_created` series. Created-timestamp processing also
supports native histograms, and the TSDB accepts out-of-order native-histogram
samples.

## Reloaded histogram settings (`3.1.0`)

Configuration reloads honor both `always_scrape_classic_histograms` and
`convert_classic_histograms_to_nhcb`; reloaded values are not silently ignored.

## Ingestion disablement (`3.3.0`)

When native-histogram ingestion is disabled, scraping skips native-histogram
series rather than ingesting them anyway.

## Out-of-order and custom-bucket controls (`3.4.0`)

`--enable-feature=ooo-native-histograms` is a no-op. Out-of-order native
histograms are enabled when `out_of_order_time_window` is positive and the
then-required `native-histograms` feature is enabled.

Classic-to-native custom-bucket conversion can be global:

```yaml
global:
  convert_classic_histograms_to_nhcb: true
```

Monitor unknown series references encountered during replay with
`prometheus_tsdb_wal_replay_unknown_refs_total` and
`prometheus_tsdb_wbl_replay_unknown_refs_total`.

## Transport, schemas, and result typing (`3.7.0`)

Federation transports native histograms with custom buckets. Remote Write 1.0
cannot, so Prometheus blocks those sends and logs a warning.

Unsupported native-histogram schemas are rejected during append. Scrape and
remote write reduce schemas -9 through 52 in resolution to fit the supported
maximum. WAL/WBL replay ignores invalid schemas, while exponential schemas read
from chunks or remote read are reduced in resolution.

Histogram operations emit warn annotations for certain counter-reset
conflicts. Subtraction, or multiplication or division by a negative factor,
produces a gauge native histogram.

## Custom bounds and query accounting (`3.8.0`)

Custom bounds reject a NaN threshold but accept `-Inf` as the first bound.
Native-histogram addition and subtraction reconcile mismatched custom-bucket
boundaries rather than requiring identical bounds. Query sample-limit
enforcement counts histogram samples.

Classic-to-NHCB conversion can run with created-timestamp zero ingestion.

## TSDB operations and histogram validation (`3.9.0`)

The TSDB status endpoint returns at most 10,000 statistic sets. Configure the
Thanos-compatible compaction-delay file with
`--storage.tsdb.delay-compact-file.path` and the loaded-block refresh cadence
with `--storage.tsdb.block-reload-interval`.

Most query, rule, service-discovery, and scrape instrumentation exposes native
histograms alongside summaries. Notification latency additionally exposes
`prometheus_notifications_latency_histogram_seconds`.

`prometheus_tsdb_sample_ooo_delta` records each sample's out-of-order distance
in seconds, whether accepted or rejected. Remote-read histograms are validated
instead of silently accepting invalid data. `rate()`, `increase()`, and
`delta()` produce gauge histograms for histogram inputs.

Prometheus 3.9.1 fixes an Agent-mode startup crash; use it instead of 3.9.0 for
Agent deployments.

## Stale-series compaction (`3.10.0`)

`stale_series_compaction_threshold` enables experimental early compaction of
stale series from memory and controls the threshold. Treat it as experimental
storage behavior.

## Retention, startup state, and encodings (`3.11.0`)

`storage.tsdb.retention.percentage` caps TSDB disk use by percentage. Removing
file-based retention falls back to CLI values, and file-based
`storage.tsdb.retention.time` no longer has a unit mismatch that made retention
one million times too long.

The `fast-startup` feature persists active-series state in `series_state.json`
in the WAL directory for reuse after restart.

`st-storage` stores ingested start timestamps from scrapes or OTLP in the TSDB
and Agent WAL and exposes them through Remote Write 2:

```text
--enable-feature=st-storage
```

`xor2-encoding` selects a float-sample chunk encoding optimized for scraped
data and capable of encoding start timestamps:

```text
--enable-feature=xor2-encoding
```

## Start-timestamp queries and synthesis (`3.12.0`)

With `--enable-feature=use-start-timestamps`, `rate()`, `irate()`, and
`increase()` use stored start timestamps and `resets()` detects their resets.
This mode cannot be combined with `anchored` or `smoothed` selectors.

`--enable-feature=st-synthesis` synthesizes missing start timestamps for
scraped cumulative metrics, which can help Remote Write 2 consumers expecting
delta or OpenTelemetry semantics. PromQL test `load` blocks accept `@st` to
specify sample start timestamps.

Percentage retention works with the new data path and preserves decimals.
Concurrent Agent appends for one label set no longer create duplicate in-memory
series or WAL records.

## Runtime encoding and persistence fixes (`3.13.0`)

`storage.tsdb.chunk_encoding.floats` selects `xor` or `xor2` at runtime,
independently of the `xor2-encoding` feature flag.

Chunk-snapshot encoding for `EncXOR2` is fixed; earlier behavior could corrupt
the TSDB on restart when XOR2 series existed. `CompactStaleHead` and
`CompactSelectedSeries` now retain label records through checkpoint/replay and
preserve samples at chunk-range boundaries. Upgrade early-stale-compaction
deployments because old eviction paths could cause replay failure or data loss.

## Encoding prerequisites and synthesis semantics (`feature-flags`)

`st-storage` does not select an ST-capable block format. Float chunks must
resolve to XOR2 or startup/config reload fails; persisting native- and
float-histogram start timestamps also requires
`--enable-feature=histograms-st-encoding`. `SamplesV2` WAL records require
Prometheus 3.11 or later. XOR2, `histogramST`, and `floathistogramST` blocks can
be unreadable by older releases or downstream consumers, and their
experimental formats can change.

`use-start-timestamps` also enables the PromQL `start_timestamp()` function and
remains incompatible with extended range selectors.

For scraped cumulative metrics without a start timestamp, `st-synthesis` drops
the first sample and subtracts it from later samples, so stored values differ
from scraped values. It does not support remote write or OTLP, rejects those
metrics' out-of-order samples regardless of `out_of_order_time_window`, and
clears synthesis state after an append failure so the next sample becomes a
newly dropped reference point.

## Restart, compaction, and stale-series correctness (`3.13.2-3.14.0`)

Prometheus 3.14 fixes potential restart data loss after out-of-order ingestion
and compaction, samples and errors missing after deleted-series restart, and
native-histogram corruption after restart. Out-of-order queries no longer hold
up compaction for hours while memory grows.

Mixed float, integer-histogram, and float-histogram series are no longer
evicted early, and `prometheus_tsdb_head_stale_series` no longer over-counts
them. Previously discarded TSDB query errors reach callers. Compaction also
preserves the configured float encoding rather than rewriting XOR2 to XOR.

Monitor head native histograms with
`prometheus_tsdb_head_native_histogram_series` and
`prometheus_tsdb_head_native_histogram_buckets`.
