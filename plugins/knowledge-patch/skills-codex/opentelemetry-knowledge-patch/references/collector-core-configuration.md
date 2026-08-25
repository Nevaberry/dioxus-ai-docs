# Collector Core and Configuration

## Core metric semantics

### Batch-size histogram buckets

`otelcol_exporter_queue_batch_send_size_bytes` and
`otelcol_processor_batch_batch_send_size_bytes` use power-of-two buckets from
128 B through 16 MiB. Update dashboards and alerts that hard-code histogram
`le` values.

Exporter queue metrics have more specific semantics:

- `otelcol_exporter_queue_batch_send_size*` measures requests after batching
  and exists only with `sending_queue.batch`.
- Enqueue-time sizing is reported by `otelcol_exporter_enqueue_size` and
  `otelcol_exporter_enqueue_size_bytes`.

Log- and profile-record scraper metrics use unit `{record}`, not
`{datapoint}` (batch `2026-08-stable`).

## Configuration schemas

Core supplies `config.schema.yaml` for:

- debug, OTLP, and OTLP/HTTP exporters
- the OTLP receiver
- batch and memory-limiter processors
- memory-limiter and zpages extensions

The schemas contain validation and shared-library references. Regenerate them
with `schemagen`.

## Collector self-telemetry resource detection

Experimental resource detection for the Collector's own telemetry is
configured under `service.telemetry.resource.detection/development`. Supported
detectors are `container`, `host`, `process`, and `service`.

```yaml
service:
  telemetry:
    resource:
      detection/development:
        detectors:
          - host: {}
```

## Partial receiver reload

Core has alpha `service.partialReload` and beta
`service.partialReloadReceivers` feature gates. With
`--feature-gates=service.partialReload`, a configuration reload can restart
only receivers when processors, exporters, extensions, and every other
non-receiver setting are unchanged.

## Go configuration APIs

- `configgrpc.BalancerName` is removed; use
  `configgrpc.DefaultBalancerName`.
- `xconfmap.WithForceUnmarshaler` is deprecated; use
  `confmap.WithForceUnmarshaler`.
- The `configstorage` module provides reusable storage-configuration fields.
- `configgrpc.WaitForReady` is now applied to gRPC client connections.
- Core no longer embeds `confighttp.ServerConfig` in zpages `Config` or
  `configauth.Config` in `confighttp.AuthConfig`. Go integrations must use the
  new named fields rather than promoted fields.

## Removed and renamed components

- The failover connector no longer accepts `retry_gap` or `max_retries`.
- The JMX receiver code is removed.
- Rename processor type `awsecsattributes` to `aws_ecs_attributes`; the old
  name has no alias.
- `cumulativetodelta` and `spanpruning` are deprecated aliases for
  `cumulative_to_delta` and `span_pruning`.
- `kafkatopicsobserver`, its `kafka.topics` endpoint type, and receiver-creator
  rules for that endpoint are removed. Use `kafkareceiver` topic regex
  support.
- Exporter type `azuremonitor` is renamed to `azure_monitor`.
- Receiver type `sqlquery` is renamed to `sql_query`; its old name remains as
  a deprecated alias.
- Huawei Cloud CES and Simple Prometheus receivers are Unmaintained.

## Error-mode defaults

The routing connector defaults top-level `error_mode` to `ignore`. During the
beta-gate period,
`--feature-gates=-connector.routing.defaultErrorModeIgnore` restores
`propagate`.

The filter and transform processors permanently default top-level
`error_mode` to `ignore`; their stable compatibility gates are scheduled for
removal in 0.159.0.

## Host Metrics CPU defaults

Host Metrics aggregates `system.cpu.time` and
`system.cpu.utilization` across logical CPUs by default, omits `cpu`, and
enables `system.cpu.logical.count`. Restore per-CPU series by selecting both
`cpu` and `state`:

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

## Shared database authentication

Contrib provides `configdbauth` configuration and a `dbauth` extension
interface so components can share database authentication, including AWS IAM
authentication. AWS IAM database authentication is alpha.

## OpAMP Supervisor

- Set `agent::collector_crash_log_snippet_kib` from 1 through 1024 to attach
  recent Collector logs to crash and remote-configuration failure reports.
- `agent.automatic_config_rollback` restores the last working remote
  configuration after a newly delivered configuration fails.
- Package upgrades accept tar.gz archives and an `agent_binary` setting.

## Service-manager integration

The `sd_notify` extension integrates the Collector with the `sd_notify(3)`
protocol.
