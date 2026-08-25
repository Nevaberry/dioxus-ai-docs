# Observability and Decision Logs

Use this reference for decision-log buffering and delivery, masking, labels,
file logging, Prometheus metrics, OpenTelemetry tracing, and correlation.

## Decision-log delivery

### Mask values inside arrays (`1.1.0`)

Decision-log masking can address array keys. Use it to redact sensitive values
that occur within arrays, not only values beneath object keys.

### Choose the event-based buffer (`1.3.0`)

Set `decision_logs.reporting.buffer_type` to `event` to reduce lock contention
under high request load. The tradeoff is that the event buffer, unlike the
default, does not provide precise memory-footprint guarantees.

```yaml
decision_logs:
  reporting:
    buffer_type: event
```

### Preserve upload caps (`1.5.0`)

Decision-log uploads retain the adaptive uncompressed-size limit, and the
decision plugin derives configuration boundaries from
`upload_size_limit_bytes`. Configured upload caps therefore remain in force
throughout upload handling.

### Upload as soon as a chunk fills (`1.13.0`)

Set `decision_logs.reporting.trigger` to `immediate` to upload events as soon
as the configured chunk-size criteria are met. The upload delay remains the
latest time at which an upload occurs.

```yaml
decision_logs:
  reporting:
    trigger: immediate
```

## Correlation and labels

### Correlate `opa exec` output (`1.2.0`)

`opa exec` results include the decision ID. Consumers can correlate execution
results directly with decision logs or traces.

### Emit rule labels (`1.17.0`)

Metadata annotations accept `labels`. Labels from every successfully evaluated
rule merge with inner-scope precedence:

```text
subpackages < package < document < rule
```

OPA deduplicates the merged labels and emits them in the top-level
`rule_labels` array. Both the runtime and Go SDK process the annotations by
default.

```rego
# METADATA
# scope: package
# labels:
#   service: authz
#   severity: info
package myapp

# METADATA
# labels:
#   severity: low
#   team: platform
allow if input.role == "admin"
```

The resulting labels include the inner override:

```json
{"rule_labels":[{"service":"authz","severity":"low","team":"platform"}]}
```

## File logging

### Route runtime and decisions through a rotating file (`1.15.0`)

Logger plugins use Go's `log/slog.Handler`. Select a runtime logger with
`server.logger_plugin` and route decision logs to the same plugin with
`decision_logs.plugin`. The built-in `file_logger` writes structured JSON and
supports rotation:

```yaml
server:
  logger_plugin: file_logger

decision_logs:
  plugin: file_logger

plugins:
  file_logger:
    path: /var/log/opa/server.log
    max_size_mb: 100
    max_age_days: 28
    max_backups: 3
    compress: true
    level: info
```

Custom builds can register another `slog.Handler`. Use `BufferedLogger` when
startup messages emitted before plugin initialization must reach that handler.

## Metrics

### Tune bundle-loading histogram buckets (`1.0.0`)

Prometheus configuration accepts custom buckets for
`bundle_loading_duration_ns`. Choose ranges that expose the bundle-loading
latencies relevant to the deployment.

### Count outbound built-in requests (`1.9.0`)

Topdown metrics include a counter for network requests made by `http.send`.
Use it to observe policy-driven outbound HTTP activity directly.

### Export Prometheus metrics through OTLP (`1.17.0`)

Distributed-tracing configuration can export Prometheus metrics via OTLP, so
an OTLP collector can receive OPA runtime metrics.

## Distributed tracing

### Trace discovery and identify resources (`1.2.0`)

The discovery plugin participates in distributed tracing. OPA server tracing
also accepts additional OpenTelemetry resource attributes so traces can carry
deployment-specific resource identity.

### Send spans to HTTP collectors (`1.3.0`)

Set `distributed_tracing.type` to `http` to use an HTTP collector. Distributed
tracing also exposes finer-grained batch span processor settings.

```yaml
distributed_tracing:
  type: http
```
