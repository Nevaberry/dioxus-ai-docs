# Collector Exporters and Extensions

## Shared authentication and maturity

### Database authentication components (`collector-0.157.0`)

Use `configdbauth` configuration and the `dbauth` extension interface to share
database authentication, including AWS IAM authentication, across components.

### Promoted capabilities (`2026-08-stable`)

Load Balancing exporter metrics, AWS IAM database authentication, and Google
Cloud Pub/Sub Push log support are alpha.

## Datadog and SignalFx

### Synchronous Datadog delivery (`collector-0.157.0`)

The alpha, default-off `datadog.serializerexporter.UseSyncForwarder` gate
makes the Datadog metric serializer surface 4xx/5xx failures through
`exporterhelper`. With it enabled, `retry_on_failure`, sending-queue overflow
telemetry, and failed-point telemetry apply instead of failures being swallowed
by the legacy asynchronous forwarder.

### Datadog scope and metric handling (`2026-08-stable`)

With `datadog.EnableScopeConvention`, Datadog spans add `otel.scope.name` and
`otel.scope.version` while retaining deprecated `otel.library.*` attributes.
Batches containing multiple resource-log scopes are routed per scope. Legacy
clients no longer drop delta sums marked `datadog.metric.as_type=rate`.

### SignalFx Host Metrics translation (`collector-0.157.0`)

SignalFx derives `cpu.num_processors` from `system.cpu.logical.count` and
exports `system.cpu.time` and `system.disk.io` by default. Default CPU
translations assume state-aggregated Host Metrics output, but retain an
explicitly re-enabled `cpu` attribute.

### SignalFx span and RSS behavior (`2026-08-stable`)

SignalFx still accepts spans but no longer sends them to the retired
trace-correlation endpoint. It no longer excludes `container.memory.rss` by
default.

## Elasticsearch and OpenSearch

### Retry and managed templates (`collector-0.157.0`)

Elasticsearch uses `retry::retry_on_document_status` for document-level retry
codes independently of request-level retries. In `otel-v1` mode, OpenSearch
`mapping.manage_index_template` idempotently creates span and log composable
templates without replacing existing templates. Reject this option in other
mapping modes.

### Dynamic-index validation (`collector-0.157.0`)

OpenSearch rejects empty, dot-prefixed, and `..`-containing dynamic-index
substitutions, then tries the next attribute or configured fallback.

## Kafka and load balancing

### Kafka request mode (`collector-0.157.0`)

The default-off alpha `exporter.kafka.useRequestType` gate converts all
signals to Kafka records when the exporter request is created. In this mode,
`queue_batch.sizer: items` counts Kafka records and persistent
`sending_queue.storage` causes a startup error.

### Load-balancing ring behavior (`collector-0.157.0`)

The Load Balancing exporter uses 200 default virtual nodes rather than 100 and
a ring space of 131,071 rather than 36,000. Endpoint ordering no longer biases
ring assignment.

## Encoding and identity extensions

### Google Cloud log encoding and OIDC (`collector-0.157.0`)

The default-off
`extension.encoding.googlecloudlogentryencoding.DontEmitV0RPCConventions`
gate suppresses deprecated JSON-RPC error attributes while still emitting
`rpc.response.status_code`. The OIDC extension has an issuer-ignore option for
single-provider configurations.

## File and cloud exporters

### File exporter rotation migration (`collector-0.157.0`)

The File exporter creates output with mode `0644`, including rotated files.
On startup it renames lumberjack-format backups into timberjack's naming
scheme so `max_backups` and `max_days` can manage them after an upgrade.

### CloudWatch Logs size and pod templates (`2026-08-stable`)

AWS CloudWatch Logs retains a 256 KiB event default. Set
`max_event_payload_bytes: 1048576` for the service's 1 MiB ceiling; direct
callers can use `cwlogs.WithMaxEventPayloadBytes`. `{PodName}` in group or
stream templates resolves `k8s.pod.name` as well as the legacy `pod`
attribute.

### Azure Monitor HTTP success mapping (`2026-08-stable`)

Use
`telemetry_mappings.traces.http.success.additional_success_status_codes` for
additional successful client and server response codes. Set
`telemetry_mappings.traces.http.success.server_policy: otel` to treat
server-side 4xx responses as successful. Defaults preserve earlier mapping.

## Prometheus Remote Write

### HTTP settings, WAL, and label delivery (`2026-08-stable`)

HTTP client settings may be nested under `http`; nested values take precedence
over flat settings. WAL telemetry includes exporter ID. Deadline expiration is
retriable, idle exporters flush buffered WAL entries, and permissive label
sanitization preserves consecutive underscores.

## Tail storage and fleet registration

### Bounded Pebble storage (`2026-08-stable`)

Bound pending tail-sampling data with `max_storage_size_mib`:

```yaml
extensions:
  pebble_tail_storage:
    directory: /var/lib/otelcol/pebble-tail-storage
    max_storage_size_mib: 10240
```

### Sumo Logic fleets (`2026-08-stable`)

The Sumo Logic extension accepts `fleet_id`. If the fleet is invalid or
missing, registration retries without that ID.
