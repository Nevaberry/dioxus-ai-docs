# Collector Core and Configuration

## Core telemetry and schemas

### Batch-size histogram buckets (`collector-0.157.0`)

`otelcol_exporter_queue_batch_send_size_bytes` and
`otelcol_processor_batch_batch_send_size_bytes` use power-of-two buckets from
128 B through 16 MiB. Update dashboards and alerts that hard-code histogram
`le` values.

### Exporter queue and scraper telemetry (`2026-08-stable`)

`otelcol_exporter_queue_batch_send_size*` measures requests after batching and
exists only with `sending_queue.batch`. Enqueue-time sizing uses
`otelcol_exporter_enqueue_size` and `otelcol_exporter_enqueue_size_bytes`.
Log- and profile-record scraper metrics use `{record}` rather than
`{datapoint}`.

### Component configuration schemas (`collector-0.157.0`)

Collector core ships `config.schema.yaml` for the debug, OTLP, and OTLP/HTTP
exporters; OTLP receiver; batch and memory-limiter processors; and
memory-limiter and zpages extensions. Schemas include validation rules and
shared-library references and can be regenerated with `schemagen`.

### Collector self-telemetry resource detection (`collector-0.157.0`)

Apply experimental resource detection to the Collector's own telemetry under
`service.telemetry.resource.detection/development`. Supported detectors are
`container`, `host`, `process`, and `service`.

```yaml
service:
  telemetry:
    resource:
      detection/development:
        detectors:
          - host: {}
```

## Reload and service integration

### Partial receiver reload (`collector-0.157.0`)

Collector core has the alpha `service.partialReload` and beta
`service.partialReloadReceivers` gates. With
`--feature-gates=service.partialReload`, a configuration reload restarts only
receivers when processors, exporters, extensions, and every other
non-receiver configuration are unchanged.

### Service manager and package upgrades (`2026-08-stable`)

The `sd_notify` extension integrates the Collector with `sd_notify(3)`.
OpAMP Supervisor package upgrades accept tar.gz archives and an `agent_binary`
setting.

### OpAMP recovery controls (`collector-0.157.0`)

Set `agent::collector_crash_log_snippet_kib` from 1 through 1024 to attach
recent Collector logs to crash and remote-configuration failure reports.
`agent.automatic_config_rollback` can restore the last working remote
configuration after a newly delivered configuration fails.

## Go configuration APIs

### Renamed and shared configuration APIs (`collector-0.157.0`)

Replace removed `configgrpc.BalancerName` with
`configgrpc.DefaultBalancerName`. Replace deprecated
`xconfmap.WithForceUnmarshaler` with `confmap.WithForceUnmarshaler`. Use the
new `configstorage` module for reusable storage-configuration fields.
Collector core now applies `configgrpc.WaitForReady` to gRPC client
connections.

### Named fields instead of embedding (`2026-08-stable`)

Collector core 0.159 no longer embeds `confighttp.ServerConfig` in zpages
`Config` or `configauth.Config` in `confighttp.AuthConfig`. Go integrations
that depended on promoted fields must use the new named fields.

## Component names and lifecycle

### Removed and renamed configuration (`collector-0.157.0`)

The failover connector removes `retry_gap` and `max_retries`. The JMX receiver
code is removed. Rename processor type `awsecsattributes` to
`aws_ecs_attributes`; there is no alias. `cumulativetodelta` and `spanpruning`
remain only as deprecated aliases for `cumulative_to_delta` and
`span_pruning`.

### Component lifecycle and IDs (`2026-08-stable`)

`kafkatopicsobserver`, its `kafka.topics` endpoint type, and receiver-creator
rules for that type are removed; use `kafkareceiver` topic-regex support.
Rename exporter type `azuremonitor` to `azure_monitor`. Rename receiver type
`sqlquery` to `sql_query`; the old receiver name is a deprecated alias. Huawei
Cloud CES and Simple Prometheus receivers are Unmaintained.

## Processing and Host Metrics defaults

### Processor and connector error modes (`collector-0.157.0`)

The routing connector defaults `error_mode` to `ignore`. During its beta gate
period, `--feature-gates=-connector.routing.defaultErrorModeIgnore` restores
`propagate`. Filter and transform processors permanently default top-level
`error_mode` to `ignore`; their stable compatibility gates are scheduled for
removal in 0.159.0.

### Host Metrics CPU aggregation (`collector-0.157.0`)

Host Metrics aggregates `system.cpu.time` and `system.cpu.utilization` across
logical CPUs by default, omits `cpu`, and enables
`system.cpu.logical.count`. Restore per-CPU series by selecting both `cpu` and
`state` explicitly:

```yaml
receivers:
  hostmetrics:
    scrapers:
      cpu:
        metrics:
          system.cpu.time:
            attributes: [cpu, state]
          system.cpu.utilization:
            attributes: [cpu, state]
```
