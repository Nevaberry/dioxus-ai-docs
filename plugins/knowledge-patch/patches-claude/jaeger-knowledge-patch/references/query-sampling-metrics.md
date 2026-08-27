# Query, Sampling, and Metrics

## Query and storage request behavior

- In **2.1.0**, v2 `ArchiveTraceRequest` time fields became non-nullable. The
  v1 `GetTraceRequest` gained a time window with non-pointer start and end
  values. Update clients and adapters that constructed or inspected the old
  shapes.
- Since **2.2.0**, HTTP `GetTrace` and `SearchTrace` accept optional time
  windows, as does API v3's `GetTrace` gateway.
- Since **2.2.0**, API v2 and v3 handlers apply trace adjusters. Responses may
  be normalized for clock skew, duplicate spans, span IDs, and attribute or
  event ordering. Consumers must not assume raw storage ordering or values.
- Since **2.3.0**, v2 query honors the configured maximum clock-skew adjustment.
- Since **2.17.0**, clock-skew adjustment changes a span's end timestamp as well
  as its start, so returned end times and derived durations may differ.
- Since **2.15.0**, API v3 and `QueryService.GetServices` return an empty
  array/list rather than `nil` or `null` when no services exist.
- Since **2.20.0**, HTTP query endpoints accept base64-encoded trace IDs.
  Clients should treat identifiers as opaque strings rather than forcing
  hexadecimal conversion.

## Removed and changed APIs

- Since **2.3.0**, Jaeger no longer provides the gRPC metrics query service,
  `metricsquery.proto`, or its generated implementation. Migrate callers to
  supported metrics/query surfaces.
- Since **2.18.0**, the metric-store interface no longer exposes a minimum-step
  API. Custom metric stores and callers must remove or replace it.
- Since **2.19.0**, storage-v2 `FindTraceIDs` uses
  `FindTraceIDsRequest`. Regenerate callers and implementations.

## Trace-summary and API v3 search

- Since **2.19.0**, API v3 provides `FindTraceSummaries` over gRPC and
  `GET /api/v3/trace-summaries` over HTTP. The query service uses a native
  backend summary implementation where available and otherwise aggregates full
  traces. The gRPC storage adapter supports summary reads.
- Since **2.19.0**, the UI uses `/api/v3/trace-summaries` for search results.
  Storage-specific summary columns are hidden when the backend does not support
  them.
- Since **2.19.0**, the HTTP gateway accepts camelCase parameters. Existing
  snake_case spellings remain deprecated aliases.
  `query.num_traces` became `query.search_depth`, with the old name retained as
  a deprecated alias, and trace-summary search supplies a default depth.
- Since **2.19.0**, `GET /api/v3/traces` accepts `query.attributes` to filter by
  attributes.
- Since **2.20.0**, Elasticsearch implements native summary reads, removing the
  need for full-trace fallback on that backend.

## Trace adjustment and data acceptance

- Since **2.7.0**, ingestion sanitizes negative span durations.
- Since **2.16.0**, ingestion sanitizes empty span names.
- Since **2.9.0**, array-valued tags no longer fail with an
  invalid-string-type error.
- Since **2.7.0**, Prometheus API calls no longer time out solely because a
  label contains invalid UTF-8.

See [ingestion-operations.md](ingestion-operations.md) for OTLP response and
receiver behavior.

## Sampling components and strategies

- Since **2.0.0**, the distribution includes the OpenTelemetry Collector
  tail-based sampling processor and the `remotesampling` extension. The v2
  configuration enables remote sampling.
- In the **v2-runtime-model**, `adaptive_sampling` observes collected traces and
  calculates per-service and per-endpoint probabilities to meet throughput
  targets. Configure `remote_sampling` with a static strategy file or adaptive
  store, then enable HTTP and/or gRPC service endpoints.

```yaml
extensions:
  remote_sampling:
    adaptive:
      sampling_store: sampling_store
      initial_sampling_probability: 0.1
    http:
    grpc:
```

- Since **2.2.0**, sampling inherits default per-operation strategies. This is
  a breaking behavior change for configurations that combine default and
  service-specific operation rules.
- Since **2.2.0**, file-based strategies accept a reload interval, allowing
  periodic pickup of file changes.
- Since **2.5.0**, the corrected behavior formerly gated by
  `sampling.strategies.bugfix-5270` is stable and the flag is removed.
- Since **2.16.0**, the remote-sampling endpoint no longer supports its legacy
  response format. Update clients that still parse it.

## Prometheus backend

- Since **2.2.0**, Jaeger-generated Prometheus requests can include additional
  custom query parameters.
- Since **2.5.0**, `prometheus.extra_query_parameters` can also be set through
  the CLI.
- Since **2.9.0**, mapstructure decoding recognizes Prometheus `tls`, so mapped
  TLS configuration is applied.
- Since **2.12.0**, Prometheus supports AWS SigV4 HTTP authentication for
  AWS-hosted services that require signed requests.

## SPM and storage capabilities

- Since **2.0.0**, service performance monitoring is enabled in v2. Its initial
  default namespace followed the newer span-metrics connector namespace, so
  dashboards and queries built for the old namespace require adjustment.
- In **2.8.0**, the experimental Elasticsearch metrics path first implemented
  call rate.
- In **2.9.0**, experimental Elasticsearch/OpenSearch SPM added error rate,
  latency, optimized time ranges, and an OpenSearch option; their storage
  configuration includes `metrics_storage`.
- Since **2.17.0**, the query service publishes metrics storage through backend
  capabilities. The UI uses that capability—not heuristic configuration—as the
  authoritative signal for SPM and Monitor-tab availability.
- Since **2.18.0**, experimental ClickHouse metric storage implements call
  rate, error rate, and latency.

## Metrics behavior and endpoints

- Since **2.0.0**, OpenTelemetry counter names used the `_total` suffix. In
  **2.10.0**, Jaeger stopped appending an additional `_total`; dashboards,
  alerts, and queries must use the corrected name rather than the accidentally
  double-suffixed form.
- Since **2.4.0**, `/quality-metrics` returns trace-quality data in its expected
  response format.
- Since **2.9.0**, `/deep-dependencies` provides a dedicated
  deep-dependency endpoint.
- Since **2.11.0**, `enabletracing` works in the v2 query extension. A
  configuration that already enabled it will begin producing the intended
  tracing.
- Since **2.17.0**, metrics initialization parses timer-duration bucket values.
- Since **2.15.0**, Jaeger ships a Grafana dashboard for the metrics exporter.
- Since **2.17.0**, the SPM Compose example again includes Grafana, and the
  monitoring assets include a dashboard generated with the Go SDK.
