# Query, Sampling, Metrics, and Telemetry

## Sampling

- **Tail and remote sampling (2.0.0):** V2 includes the Collector tail-based
  sampling processor and enables the `remotesampling` extension.
- **Per-operation defaults (2.2.0):** Sampling configuration inherits default
  per-operation strategies. This is a breaking behavior change; re-evaluate
  combinations of default and service-specific rules.
- **File reloads (2.2.0):** File-based strategies can reload periodically using
  a reload interval.
- **Stable strategy correction (2.5.0):** Corrected strategy behavior is stable
  and `sampling.strategies.bugfix-5270` is removed. Delete the obsolete flag.
- **Response compatibility (2.16.0):** The remote-sampling endpoint no longer
  emits its legacy response format; clients must parse the current format.

### Adaptive and remote components

`adaptive_sampling` observes traces and calculates per-service and per-endpoint
probabilities to meet throughput targets. Point `remote_sampling` at either a
static strategy file or adaptive sampling store, then enable HTTP and/or gRPC:

```yaml
extensions:
  remote_sampling:
    adaptive:
      sampling_store: sampling_store
      initial_sampling_probability: 0.1
    http:
    grpc:
```

## Query APIs and response behavior

- **Trace adjusters (2.2.0):** API v2/v3 handlers apply adjusters for clock
  skew, duplicate spans, span IDs, and attribute/event ordering. Consumers that
  rely on raw or order-sensitive responses must account for post-processing.
- **Time windows (2.2.0):** HTTP GetTrace and SearchTrace accept optional time
  windows, as does the API v3 GetTrace gateway.
- **Clock skew:** V2 query honors the configured maximum clock-skew adjustment
  (since 2.3.0). The adjuster also corrects span end timestamps
  (since 2.17.0), affecting returned end times and derived durations.
- **Metrics gRPC removal (2.3.0):** The metrics query service,
  `metricsquery.proto`, and related code are gone.
- **Metric-store API (2.18.0):** The metric-store contract no longer includes
  its minimum-step API. Custom stores and callers must remove or replace it.
- **Empty services (2.15.0):** API v3 services and
  `QueryService.GetServices` return an empty collection, not `nil`/`null`, when
  no services exist.
- **Summary search (2.19.0):** API v3 provides `FindTraceSummaries` and
  `GET /api/v3/trace-summaries`. Query uses native backend summaries when
  available, otherwise aggregates full traces; the gRPC storage adapter reads
  summaries.
- **Gateway parameters (2.19.0):** Camel-case parameters are accepted.
  Snake-case forms remain deprecated aliases. `query.num_traces` became
  `query.search_depth` with a deprecated alias, and the summary endpoint has a
  default search depth.
- **Attribute filters (2.19.0):** `GET /api/v3/traces` accepts
  `query.attributes`.
- **Trace identifiers (2.20.0):** HTTP query endpoints accept base64 trace IDs.
  Treat IDs as opaque strings rather than forcing hexadecimal conversion.

## Input normalization and request status

- **OTLP normalization (2.0.0):** Ingestion sanitizes invalid UTF-8 and empty
  service names. The OTLP receiver again listens on all interfaces; enforce
  intended exposure with binding and network policy.
- **Invalid payloads (2.3.0):** Invalid OTLP payloads return HTTP 400 rather
  than 500.
- **Span duration (2.7.0):** Negative span durations are sanitized.
- **Array tags (2.9.0):** Array-valued tags no longer fail as invalid strings.
- **Empty span names (2.16.0):** Empty span names are sanitized on ingestion.

## Prometheus, SPM, and metric naming

- **SPM defaults (2.0.0):** Service performance monitoring is enabled in v2.
  Its default metrics namespace follows the newer span-metrics connector
  default; update queries and dashboards that assume the old namespace.
- **Prometheus parameters:** Backend requests accept extra custom query
  parameters (since 2.2.0); `prometheus.extra_query_parameters` can be set from
  the CLI (since 2.5.0).
- **Malformed labels (2.7.0):** Invalid UTF-8 label values no longer cause
  Prometheus API requests to time out solely for that reason.
- **Prometheus TLS (2.9.0):** Mapstructure decoding recognizes the `tls`
  configuration.
- **SigV4 (2.12.0):** The Prometheus metrics backend supports AWS SigV4 HTTP
  authentication.
- **Timer buckets (2.17.0):** Metrics initialization parses duration-valued
  timer bucket settings.
- **SPM capability (2.17.0):** Query publishes metrics storage through storage
  capabilities. The UI uses that capability as the authoritative signal for
  SPM and Monitor-tab visibility.
- **Metric suffix transition:** OpenTelemetry counters used `_total` in 2.0.0.
  Jaeger stopped adding an extra `_total` in 2.10.0; update dashboards, alerts,
  and queries that used the doubly/incorrectly suffixed name.

## Internal and exported telemetry

- **Internal telemetry (2.0.0):** V2 configurations include the health-check
  extension and a temporary `expvar` extension. The Collector can observe its
  own internal telemetry.
- **Internal tracer environment (2.1.0):** Jaeger's internal tracer honors
  environment variables.
- **Query tracing (2.11.0):** `enabletracing` works in the v2 query extension.
- **UI and AI tracing (2.20.0):** The UI can export its own OTLP traces. The AI
  gateway and sidecar propagate trace context and attach GenAI span attributes.
