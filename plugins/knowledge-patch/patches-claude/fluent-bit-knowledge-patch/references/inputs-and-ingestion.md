# Inputs and Ingestion

## OpenTelemetry ingestion

Version 4.0.0 adds JSON traces and compressed gRPC messages to the
OpenTelemetry input. A gRPC message is limited to 16 MB, so configure senders
to split larger payloads and test the receiver's rejection path. In 4.0.6,
OpenTelemetry variant values that are `NULL` are handled as empty strings, and
an OTLP `AnyValue` may carry a `NULL` body during packing.

Starting in 4.2.0, log and trace ID decoding is stricter. Reject or repair
malformed identifiers at the producer; do not expect the input to accept a
nonconforming encoding.

The `5.0-guide` source batch makes OTLP/HTTP JSON metrics ingestion stable and
improves JSON trace validation and error reporting. Version 5.0.0 broadens
OpenTelemetry handling across logs, metrics, and profiles, and metric support
includes exponential histograms.

## Shared HTTP-family listeners

The HTTP, Splunk, Elasticsearch, OpenTelemetry, and Prometheus Remote Write
inputs use the following canonical listener settings from `5.0-guide`:

- `http_server.http2`
- `http_server.buffer_chunk_size`
- `http_server.buffer_max_size`
- `http_server.max_connections`
- `http_server.workers`
- `http_server.ingress_queue_event_limit`
- `http_server.ingress_queue_byte_limit`

The legacy `http2`, `buffer_chunk_size`, and `buffer_max_size` keys remain
compatibility aliases. Prefer canonical keys when changing a configuration so
all HTTP-family inputs express listener limits consistently.

HTTP request bodies may be compressed with gzip or zstd since 4.0.0. The HTTP
input can also capture the address carried in `X-Forwarded-For`: enable
`add_remote_addr` and set `remote_addr_key` to choose the record field.

Under worker load, 5.0.0 preserves busy and ingestion-error behavior more
consistently. HTTP, Splunk, and Elasticsearch inputs also retain their response
status codes through payload and error handling. Producer retry policy should
distinguish busy responses from permanent payload errors.

Since 5.0.4, an HTTP input can optionally expose `GET /health` as a readiness
probe for HTTP ingestion. This endpoint is separate from the built-in server's
JSON `/api/v2/health` endpoint.

## Internal logs and Kubernetes context

The `fluentbit_logs` input in `5.0-guide` ingests Fluent Bit's own logs as
structured records, allowing normal filtering and forwarding. Prevent a
feedback loop when those records are sent through an output whose errors feed
the same internal-log stream.

The Kubernetes filter can add owner-reference information to records since
4.0.0. In 5.0.9 it can enrich internal log records from local Kubernetes
metadata; use `kube_namespace_file` to override the namespace metadata file
path.

The Kubernetes events input exposes `db.journal_mode` and `db.locking` in
`5.0-guide`. These settings control its SQLite-backed cursor persistence and
database access behavior; preserve cursor durability when tuning locking or
journal behavior.

## Tail and multiline inputs

The Tail input supports Unicode encoders since 4.0.0. Version 4.1.0 adds a
multiline buffer-truncation limit together with metrics and diagnostics for
oversized multiline records. Set a deliberate limit and alert on truncation
rather than allowing large multiline events to remain invisible.

Version 4.2.0 lets Tail truncate extremely long lines. In 5.0.0, Tail also
exposes a skipped-line counter, making otherwise silent input loss observable.
Monitor both truncation diagnostics and skipped lines because they represent
different loss modes.

## Network and line-oriented inputs

Syslog supports octet-counted messages since 4.2.0, improving compatibility
with senders that use RFC-style length framing. In 5.0.4, TCP and UDP inputs
can apply parsers to line-delimited records, including structured payloads such
as JSON. Test framing and parsing together so a multiline payload is not
mistaken for multiple records.

Input plugins gained broader pause/resume lifecycle support in 4.1.0,
including TCP, `event_type`, and Splunk. Exercise pause and resume under
backpressure rather than assuming every input continues reading.

## Prometheus and exporter inputs

The `prometheus_textfile` input introduced in 4.0.6 reads Prometheus text files
and supports file globbing on Windows. The `nginx_exporter_metrics` input also
adds `scrape_interval` in 4.0.6, with a default of `5s`.

Windows Exporter Metrics aligned its Prometheus metric names with
`windows_exporter` in 4.0.6 and added TCP `connection_state` metrics. Revisit
queries that used the older names.

In 5.0.9, `windows_exporter_metrics` accepts user-defined Windows Performance
Counters through `PerformanceCounter` entries. Set
`collector.performancecounter.scrape_interval` when custom counters need a
schedule independent of the other collectors.

Node Exporter Metrics adds a Linux netstat collector in 4.2.0. An AMD GPU
metrics collector is available since 4.1.0. Enable only collectors supported
by the host and expected by downstream dashboards.

## Windows events

The `winevtlog` input in 4.0.6 automatically detects daylight saving time and
initializes time-zone information correctly. Version 5.0.0 adds rendering of
collected Windows events as text. Validate timestamp and text formatting with
events spanning a daylight-saving transition.

## Service-specific inputs

The Vivo Exporter uses `/api/v1/` endpoints and supports groups since 4.2.0.
Update endpoint assumptions and group selection together.

In 5.0.9, the Splunk input emits Splunk HEC-compatible `401` and `403`
responses for missing, malformed, or invalid authentication. Senders can use
those status codes to classify authentication failures instead of retrying
them as transient ingestion errors.

## eBPF OpenSSL tracing

The eBPF input in 5.0.9 can attach uprobes to OpenSSL TLS handshake, read,
write, and shutdown calls. Events carry per-CPU monotonic identifiers, which
provide ordering within each CPU but do not define one global order across
CPUs.
