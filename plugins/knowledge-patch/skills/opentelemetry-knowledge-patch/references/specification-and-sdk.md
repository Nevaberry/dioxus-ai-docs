# Specification and SDK

## Context propagation

### Environment-variable carriers

Environment-variable context propagation carriers are Release Candidate.
Their names follow POSIX.1-2024-aligned restrictions and normalization:

- Normalize requested keys, carrier keys, and returned keys.
- Read and return only normalized environment-variable names.
- An empty name normalizes to `_`.
- The specification does not prescribe caching behavior.

Context propagation also requires the W3C randomness flag.

### Legacy compatibility

- The Jaeger and OT Trace propagators are deprecated; implementations are
  optional.
- The Zipkin exporter specification is deprecated; implementing it is
  optional.
- The specification's OpenTracing and OpenCensus compatibility requirements
  are deprecated.

## Tracing and sampling APIs

- `AlwaysRecord` is a stable sampler.
- `TraceIdRatioBased` has been restored, but it has a deprecation timeline.
- The Tracer `enabled` operation is stable.

## Metrics APIs and export

- Synchronous instruments' `Enabled` API is stable.
- Synchronous instruments have a new in-development `Bind` API.
- The periodic exporting `MetricReader` has an in-development
  `maxExportBatchSize` parameter.
- A metric stream name supplied by a View is not subject to instrument-name
  syntax validation.

## Logs, events, and profiles

### Logging APIs and filtering

- Logs have an optional ergonomic API.
- Logger `Emit` has a stable optional `Exception` parameter.
- Logger configuration adds `minimum_severity` and `trace_based`.
- `LogRecordProcessor.Enabled` is stable.

### Signal bridges and entity events

- The Logs specification defines an event-to-span-event bridge.
- Entity information can be communicated as structured log events.

### Profiles

OpenTelemetry documents the Profiles signal and includes a Profiles data
model. Supplementary documentation describes pprof integration.

## Resources and attribute values

### Resource meaning

A Resource describes the observed entity. It does not describe the component
merely because that component technically emitted the telemetry.

### Complex values

Complex `AnyValue` attribute types and their limits are stable. Non-OTLP
guidance covers:

- Byte arrays.
- Empty values.
- Arrays and maps.
- Nested values.

In-development guidance recommends JSON-object string representations for
attributes and attribute collections.

## SDK self-observability

An in-development SDK self-observability section applies across the Tracing,
Metrics, and Logs SDK specifications. Supplementary guidance is
non-normative.

## Declarative SDK configuration

Significant parts of declarative configuration are stable:

- `create` and `parse` defaults and validation are clarified.
- `create` permits optional programmatic customization.
- Strict YAML parsing is recommended.
- Environment substitution may use language-specific prefixes.
- Boolean environment-variable guidance applies to environment variables, not
  to other configuration interfaces.

### Names and unset behavior

- `TracerConfig`, `MeterConfig`, and `LoggerConfig` use `enabled`, replacing
  `disabled`.
- `ComponentProvider` is renamed to `PluginComponentProvider`.
- `CreatePlugin` is renamed to `CreateComponent`.
- An unset instrumentation configuration returns an empty object.

## Prometheus and OpenMetrics

### Exporter configuration keys

Recommended Prometheus Metric Exporter properties are:

| Current property | Replaced property |
| --- | --- |
| `scope_info_enabled` | `without_scope_info` |
| `target_info_enabled` | `without_target_info` |
| `resource_constant_labels` | `with_resource_constant_labels` |

### Stable conversion and exporter behavior

Stable conversion paths cover these Prometheus-to-OTLP data types:

- Counters.
- Gauges.
- Summaries.
- Classic histograms.

Stable OpenTelemetry-to-Prometheus conversion covers:

- Sums, gauges, and histograms.
- Scope and attributes.
- Exemplars and metadata.

Exporter sections for host, port, temporality, version and format, scope
information, default aggregation, resource attributes, and client-library
behavior are stable.

An optional conversion maps an OpenTelemetry Histogram to a Prometheus Native
Histogram with Custom Buckets.
