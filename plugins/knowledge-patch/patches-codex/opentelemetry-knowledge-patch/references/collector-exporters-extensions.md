# Collector Exporters and Extensions

## Queue and batch telemetry

`otelcol_exporter_queue_batch_send_size*` measures requests after batching and
exists only when `sending_queue.batch` is configured. Enqueue-time sizing uses
`otelcol_exporter_enqueue_size` and
`otelcol_exporter_enqueue_size_bytes`.

## Datadog

### Synchronous serializer delivery

The alpha, default-off `datadog.serializerexporter.UseSyncForwarder` gate
surfaces metric serializer 4xx/5xx failures through `exporterhelper`. With it
enabled, `retry_on_failure`, sending-queue overflow telemetry, and failed-point
telemetry apply; the legacy asynchronous forwarder swallowed those failures.

### Scope and metric handling

With `datadog.EnableScopeConvention`, spans add `otel.scope.name` and
`otel.scope.version` while retaining deprecated `otel.library.*` attributes.
Batches with multiple resource-log scopes are routed per scope. Legacy clients
no longer drop delta sums marked `datadog.metric.as_type=rate`.

## Elasticsearch and OpenSearch

- Elasticsearch document-level retries use
  `retry::retry_on_document_status`, independently of request-level retry
  codes.
- In `otel-v1` mapping mode, `mapping.manage_index_template` can idempotently
  create OpenSearch span and log composable templates without overwriting
  existing templates. Reject this option in every other mapping mode.
- OpenSearch rejects dynamic-index substitutions that are empty, begin with
  `.`, or contain `..`; it then tries the next attribute or configured
  fallback.

## Kafka request mode

The default-off alpha `exporter.kafka.useRequestType` gate converts every
signal to Kafka records when creating the exporter request. In this mode,
`queue_batch.sizer: items` counts Kafka records. Persistent
`sending_queue.storage` is a startup error.

## SignalFx

- `cpu.num_processors` is derived from `system.cpu.logical.count`.
- `system.cpu.time` and `system.disk.io` are exported by default.
- Default CPU translations expect state-aggregated Host Metrics output, but
  continue to support an explicitly re-enabled `cpu` attribute.
- Spans are still accepted but are no longer sent to the retired
  trace-correlation endpoint.
- `container.memory.rss` is no longer excluded by default.

## Encoding and OIDC

- The default-off
  `extension.encoding.googlecloudlogentryencoding.DontEmitV0RPCConventions`
  gate suppresses deprecated JSON-RPC error attributes while retaining
  `rpc.response.status_code`.
- The OIDC extension can ignore issuer validation for single-provider
  configurations.

## File exporter

Output files use mode `0644`, including rotated files. At startup, older
lumberjack-format backups are renamed into timberjack's scheme so
`max_backups` and `max_days` can manage them after upgrade.

## Load Balancing exporter

The default virtual-node count is 200 rather than 100, and ring space is
131,071 rather than 36,000. Endpoint order no longer biases ring assignment.
Load Balancing exporter metrics are alpha.

## AWS CloudWatch Logs

The default event limit remains 256 KiB. Set
`max_event_payload_bytes: 1048576` to use the service's 1 MiB ceiling; direct
callers can use `cwlogs.WithMaxEventPayloadBytes`.

`{PodName}` in log-group or stream templates resolves `k8s.pod.name` as well
as the legacy `pod` attribute (batch `2026-08-stable`).

## Azure Monitor

`telemetry_mappings.traces.http.success.additional_success_status_codes`
adds successful HTTP status codes for client and server spans. Setting
`telemetry_mappings.traces.http.success.server_policy: otel` treats
server-side 4xx responses as successful. Defaults preserve the older mapping.

## Prometheus Remote Write

- HTTP client configuration can live under nested `http`, which takes
  precedence over flat settings.
- WAL telemetry carries the exporter ID.
- Deadline expiration is retriable rather than permanent.
- An idle exporter flushes buffered WAL entries.
- Permissive label sanitization preserves consecutive underscores.

## Tail storage and Sumo Logic

Bound Pebble tail-sampling storage with `max_storage_size_mib`:

```yaml
extensions:
  pebble_tail_storage:
    directory: /var/lib/otelcol/pebble-tail-storage
    max_storage_size_mib: 10240
```

The Sumo Logic extension accepts `fleet_id`. If the fleet is absent or
invalid, registration retries without that ID.
