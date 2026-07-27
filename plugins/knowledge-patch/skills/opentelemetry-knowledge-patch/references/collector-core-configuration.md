# Collector Core and Configuration

The details in this reference apply to the Collector 0.157.0 batch.

## Core telemetry and schemas

### Batch-size histogram buckets

Core changes both batch-send-size histograms to power-of-two buckets from
128 B through 16 MiB:

- `otelcol_exporter_queue_batch_send_size_bytes`.
- `otelcol_processor_batch_batch_send_size_bytes`.

Update dashboards and alerts that hard-code histogram `le` values.

### Component configuration schemas

Collector core ships `config.schema.yaml` for:

- Debug, OTLP, and OTLP/HTTP exporters.
- The OTLP receiver.
- Batch and memory-limiter processors.
- Memory-limiter and zpages extensions.

The schemas contain validation rules and shared-library references. Regenerate
them with `schemagen`.

## Collector self-telemetry resources

Experimental resource detection for the Collector's own telemetry is
configured under `service.telemetry.resource.detection/development`.
Supported detectors are `container`, `host`, `process`, and `service`.

```yaml
service:
  telemetry:
    resource:
      detection/development:
        detectors:
          - host: {}
```

## Configuration reload

Collector core adds:

- Alpha `service.partialReload`.
- Beta `service.partialReloadReceivers`.

With `--feature-gates=service.partialReload`, a configuration reload restarts
only receivers when processors, exporters, extensions, and all other
non-receiver configuration remain unchanged.

## Go configuration APIs

- `configgrpc.BalancerName` is removed; use
  `configgrpc.DefaultBalancerName`.
- `xconfmap.WithForceUnmarshaler` is deprecated; use
  `confmap.WithForceUnmarshaler`.
- The `configstorage` module provides reusable storage-configuration fields.

## Removed and renamed Contrib configuration

- The failover connector removes `retry_gap` and `max_retries`.
- Contrib removes the JMX receiver code.
- The AWS ECS attributes processor type is `aws_ecs_attributes`, replacing
  `awsecsattributes` with no compatibility alias.
- `cumulativetodelta` remains only as a deprecated alias for
  `cumulative_to_delta`.
- `spanpruning` remains only as a deprecated alias for `span_pruning`.

## Processor and connector error defaults

The routing connector defaults `error_mode` to `ignore`. During its beta-gate
period, `--feature-gates=-connector.routing.defaultErrorModeIgnore` restores
`propagate`.

The filter and transform processors permanently default top-level
`error_mode` to `ignore`. Their stable compatibility gates are scheduled for
removal in 0.159.0.

## Host Metrics CPU defaults

The Host Metrics receiver now:

- Aggregates `system.cpu.time` and `system.cpu.utilization` across logical
  CPUs by default.
- Omits the `cpu` attribute by default.
- Enables `system.cpu.logical.count` by default.

Restore per-CPU series by selecting both `cpu` and `state`:

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

## OpAMP Supervisor recovery

Set `agent::collector_crash_log_snippet_kib` from 1 through 1024 to attach
recent Collector logs to crash and remote-configuration failure reports.

`agent.automatic_config_rollback` restores the last working remote
configuration when a newly delivered configuration fails.

## Core connection behavior

Collector core now applies `configgrpc.WaitForReady` to gRPC client
connections.
