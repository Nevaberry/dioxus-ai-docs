# Collector Exporters and Extensions

The details in this reference apply to the Collector 0.157.0 batch.

## Shared database authentication

Contrib adds `configdbauth` configuration and a `dbauth` extension interface.
Components can use them to share database authentication, including AWS IAM
authentication.

## Datadog exporter delivery

The alpha, default-off
`datadog.serializerexporter.UseSyncForwarder` gate makes the Datadog metric
serializer report 4xx and 5xx failures through `exporterhelper`.

When enabled:

- `retry_on_failure` applies to the serializer path.
- Sending-queue overflow telemetry applies.
- Failed-point telemetry applies.

The legacy asynchronous forwarder swallowed these failures.

## Elasticsearch and OpenSearch

### Elasticsearch retry policy

`retry::retry_on_document_status` configures document-level retry status codes
independently of request-level retries.

### OpenSearch templates and dynamic indexes

In `otel-v1` mode, `mapping.manage_index_template` can idempotently create
span and log composable templates without overwriting existing templates.
The option is rejected in other mapping modes.

Dynamic-index substitutions are rejected when they are:

- Empty.
- Prefixed with `.`.
- Contain `..`.

After a rejected substitution, the exporter tries the next attribute or the
configured fallback.

## Kafka request mode

The alpha `exporter.kafka.useRequestType` gate is default-off. When enabled:

- Every signal is converted into Kafka records when the exporter request is
  created.
- `queue_batch.sizer: items` counts Kafka records.
- Configuring persistent `sending_queue.storage` is a startup error.

## SignalFx host-metric translation

The SignalFx exporter:

- Derives `cpu.num_processors` from `system.cpu.logical.count`.
- Exports `system.cpu.time` and `system.disk.io` by default.
- Assumes state-aggregated Host Metrics CPU output in its default
  translations.
- Still supports an explicitly re-enabled `cpu` attribute.

## Encoding and OIDC extensions

### Google Cloud log-entry encoding

The default-off
`extension.encoding.googlecloudlogentryencoding.DontEmitV0RPCConventions`
gate suppresses deprecated JSON-RPC error attributes while continuing to emit
`rpc.response.status_code`.

### OIDC

The OIDC extension adds an issuer-ignore option for single-provider
configurations.

## File exporter rotation

- Output files use mode `0644`, including when rotation is enabled.
- On startup, older lumberjack-format backups are renamed into timberjack's
  naming scheme.
- The migration lets `max_backups` and `max_days` manage those older backups
  after upgrade.

## Load-balancing exporter

- The default virtual-node count increases from 100 to 200.
- Default ring space increases from 36,000 to 131,071.
- Endpoint ordering no longer biases ring assignment.
