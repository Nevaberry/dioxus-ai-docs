# Inputs, Parsing, and Enrichment

## HTTP-family ingestion

The HTTP input can decode gzip- or zstd-compressed request bodies (since
4.0.0). Confirm `Content-Encoding`, decompression failure behavior, and
post-decompression size limits with each sender.

The HTTP input can attach the address from `X-Forwarded-For` to an ingested
record (5.0-guide). Enable capture with `add_remote_addr` and choose its field
with `remote_addr_key`. Trust this value only when a controlled proxy strips or
rewrites untrusted forwarding headers.

Under worker load, HTTP-family inputs preserve busy and ingest-error behavior
more consistently (since 5.0.0). The HTTP, Splunk, and Elasticsearch inputs
also preserve response status codes across payload and error handling. Senders
can make more reliable retry decisions, but clients must be tested against the
actual status paths.

The Splunk input returns Splunk-compatible `401` and `403` responses for
missing, malformed, or invalid HEC authentication (since 5.0.9). Senders should
classify these as authentication or authorization failures rather than retrying
them as transient ingest errors.

## OpenTelemetry ingestion

The OpenTelemetry input accepts JSON traces and compressed gRPC messages, with
a 16 MB limit for gRPC messages (since 4.0.0). Enforce compatible producer
limits and verify the error path for oversized compressed and uncompressed
payloads.

OpenTelemetry variant values that are `NULL` are represented as empty strings,
and the input accepts a `NULL` body while packing an OTLP `AnyValue` (since
4.0.6). Preserve the semantic distinction in downstream logic if empty and
absent values matter.

Log and trace ID decoding performs stricter validation (since 4.2.0). Producers
that emit malformed identifiers can fail after an upgrade; validate IDs at the
producer boundary.

Stable OTLP/HTTP JSON metrics ingestion is available, along with improved JSON
trace validation and error reporting (5.0-guide). OpenTelemetry compatibility
also covers logs, metrics, and profiles, and metrics include exponential
histograms (since 5.0.0). Verify that the destination and processors preserve
profile payloads, histogram scale and buckets, and the intended temporality.

## Tail and multiline input

The Tail input supports Unicode encoders (since 4.0.0). Configure the encoding
to match the file and test multibyte characters across buffer boundaries.

Multiline processing has a buffer-truncation limit plus diagnostics and metrics
for oversized records (since 4.1.0). Set a limit suitable for worst-case stack
traces and alert on truncation rather than allowing silent loss.

Tail can truncate extremely long lines (since 4.2.0). It also exposes a counter
for skipped lines (since 5.0.0). Exercise both cases with records above the
configured limits, and distinguish intentional truncation from parser-related
skips in monitoring.

## Framing and line parsers

The Syslog input supports octet-counted messages for improved RFC framing
compatibility (since 4.2.0). Ensure senders and the input agree on framing;
mixed delimiter and octet-counting assumptions corrupt message boundaries.

TCP and UDP inputs support parsers for line-delimited records, including
structured formats such as JSON (since 5.0.4). Match line framing, parser
selection, and maximum record sizes to the producer. UDP still needs an
application-level strategy for datagram loss or truncation.

## Prometheus and system metrics inputs

The `prometheus_textfile` input collects Prometheus text files and supports
Windows globbing (since 4.0.6). Avoid reading partially replaced files by using
an atomic producer write pattern.

`nginx_exporter_metrics` accepts `scrape_interval`, whose default is `5s`
(since 4.0.6). Set it explicitly when scrape load or freshness matters.

The Node Exporter Metrics input has a Linux netstat collector (since 4.2.0).
An AMD GPU collector exposes GPU metrics (since 4.1.0).

`windows_exporter_metrics` aligns Prometheus metric names with
`windows_exporter` and provides `connection_state` TCP metrics (since 4.0.6).
It also accepts custom Windows Performance Counters through
`PerformanceCounter` entries (since 5.0.9). Schedule those custom counters
independently with `collector.performancecounter.scrape_interval`.

## Windows events

The `winevtlog` input auto-detects daylight saving time and initializes
time-zone data correctly (since 4.0.6). Recheck timestamp normalization around
DST boundaries.

Collected Windows events can be rendered as text (since 5.0.0). Choose text
rendering only when the loss of structured-field handling is acceptable to the
downstream pipeline.

## Kubernetes data

The Kubernetes filter can add owner-reference information to emitted records
(since 4.0.0). Use it when workload ownership is needed for routing, policy, or
cost attribution.

The Kubernetes events input exposes `db.journal_mode` and `db.locking`
(5.0-guide) for its SQLite-backed cursor state. Choose them for the filesystem
and concurrency model, then verify cursor survival and duplicate behavior
across restarts.

The Kubernetes filter can enrich Fluent Bit's own internal log records with
local Kubernetes metadata (since 5.0.9). Override the namespace metadata path
with `kube_namespace_file` when the default mount or runtime layout does not
apply.

## Internal logs and input lifecycle

The `fluentbit_logs` input turns Fluent Bit's internal logs into structured
pipeline records (5.0-guide). Filter and forward them like other telemetry, but
avoid a diagnostic loop in which forwarding failures recursively produce more
forwarded internal errors.

Input plugins, including TCP, `event_type`, and Splunk, participate in
pause/resume lifecycle handling (since 4.1.0). Exercise pause, queued work, and
resume under downstream backpressure.

## eBPF OpenSSL events

The eBPF input can trace OpenSSL handshake, read, write, and shutdown calls
with uprobes (since 5.0.9). Events carry per-CPU monotonic IDs, which establish
order within each CPU but not a single total order across CPUs.
