# Plugins, Authentication, and Observability

## REST authentication and TLS

### Use AWS SSO credentials (`1.5.0`)

REST plugins can source AWS credentials from SSO. Deployments no longer need to
substitute another credentials provider solely because the caller uses AWS SSO.

### Sign assertions with Azure Key Vault (`1.5.0`)

REST clients can delegate client-assertion signing to Azure Key Vault, keeping
the signing key in the vault rather than loading it into OPA.

### Move per-request authentication into `Prepare` (`1.15.0`)

`HTTPAuthPlugin.NewClient()` is called once for each `Client`, and its result is
cached. Put request counters, transport wrapping, logging or metric side effects,
and all other per-request work in `Prepare()`; work left in `NewClient()` runs
only once.

### Control client-certificate rereads (`1.15.0`)

Set `cert_reread_interval_seconds` on REST plugins to control TLS client
certificate reloads. The backward-compatible default reloads on every request.
REST TLS configuration also inherits the server's minimum TLS version and
cipher suites.

### Sign with web-identity credentials (`1.15.0`)

REST-plugin AWS signing can use service-account Web Identity credentials when
obtaining Assume Role credentials.

### Cache JWT verification tokens (`1.1.0`)

The `io.jwt` verification built-ins support a configurable token cache. Tune the
cache to exchange memory for less repeated verification work.

## Decision logs and runtime logging

### Mask values inside arrays (`1.1.0`)

Decision-log masking can address array keys, allowing sensitive values nested
inside arrays to be removed from emitted events.

### Choose the event buffer (`1.3.0`)

Set `decision_logs.reporting.buffer_type` to `event` to reduce lock contention
under high request load. Unlike the default buffer, it does not give precise
memory-footprint guarantees.

```yaml
decision_logs:
  reporting:
    buffer_type: event
```

### Preserve upload limits (`1.5.0`)

Decision-log uploads retain the adaptive uncompressed-size limit, and the
plugin derives its configuration boundaries from `upload_size_limit_bytes`.
Configured caps remain effective throughout upload handling.

### Upload when a chunk fills (`1.13.0`)

Set `decision_logs.reporting.trigger` to `immediate` to send events when the
configured chunk-size criteria are reached. The upload delay still defines the
latest an upload may happen.

```yaml
decision_logs:
  reporting:
    trigger: immediate
```

### Route logs through a rotating file plugin (`1.15.0`)

Logger plugins implement Go's `log/slog.Handler`. Select one with
`server.logger_plugin` and set `decision_logs.plugin` to the same name when
runtime and decision logs should share output. Built-in `file_logger` emits
rotating structured JSON. Custom builds can register another handler and use
`BufferedLogger` to retain startup messages emitted before plugin initialization.

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

### Attach rule labels (`1.17.0`)

Metadata annotations accept `labels`. Labels from every successfully evaluated
rule are merged with inner-scope precedence—`subpackages`, `package`,
`document`, then `rule`—deduplicated, and emitted in top-level `rule_labels`.
The runtime and Go SDK process these annotations by default.

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

The resulting labels include `service: authz`, `severity: low`, and
`team: platform`.

## Metrics and tracing

### Tune bundle-loading histograms (`1.0.0`)

Prometheus configuration accepts custom buckets for
`bundle_loading_duration_ns`. Choose buckets that separate expected download
and activation times from slow bundle loads.

### Trace discovery and identify resources (`1.2.0`)

The discovery plugin participates in distributed tracing. Server tracing also
accepts extra OpenTelemetry resource attributes so spans can identify their
deployment or service.

### Send traces to HTTP collectors (`1.3.0`)

Set `distributed_tracing.type` to `http` for an HTTP collector. Finer-grained
batch span processor settings are also available.

```yaml
distributed_tracing:
  type: http
```

### Count `http.send` network requests (`1.9.0`)

Topdown metrics expose a counter for actual outbound network requests made by
the `http.send` built-in. Use it to distinguish evaluations from network use,
including effects of caching.

### Export Prometheus metrics over OTLP (`1.17.0`)

Distributed-tracing support can export Prometheus metrics via OTLP, allowing an
OTLP collector to receive runtime metrics alongside telemetry.

## Bundle and status plugin lifecycle

### Handle trigger failures at the call site (`1.0.0`)

The bundle plugin trigger method returns errors directly. Integrations can
handle a failed trigger without relying only on later plugin state or logs.

### Bound status-plugin shutdown (`1.5.0`)

Configure the status plugin's graceful-shutdown timeout when process shutdown
must complete within a known bound.

### Avoid the plugin-manager shutdown hang (`1.17.0`)

OPA 1.16.0 restores bundle-download, `print()`, and other plugin-originated logs
that 1.15.x dropped, but its plugin manager can hang while stopping. Use 1.16.1,
which fixes the shutdown regression.

## Outbound identity

### Update `User-Agent` matchers (`1.18.0`)

Bundle, discovery, decision-log, status, `http.send`, and AWS KMS/ECR requests
use the valid product token `Open-Policy-Agent/<version>` rather than
`Open Policy Agent/<version>`. Update exact-match WAF and log rules.

```text
User-Agent: Open-Policy-Agent/<version> (<os>, <arch>)
```
