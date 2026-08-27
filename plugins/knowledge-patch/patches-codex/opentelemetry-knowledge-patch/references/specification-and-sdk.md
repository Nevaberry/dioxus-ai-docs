# Specification and SDK

## Context propagation

### Environment-variable carriers

The environment-variable carrier specification is Release Candidate. Apply
POSIX.1-2024-aligned restrictions and normalization to requested names, carrier
keys, and returned keys. Read and return only normalized environment-variable
names; an empty name normalizes to `_`. The specification does not prescribe
carrier caching.

Context propagation also requires the W3C randomness flag.

### Legacy propagation and compatibility

- Jaeger and OT Trace propagators are deprecated; implementations may omit
  them.
- OpenTracing and OpenCensus compatibility requirements are deprecated.

## Tracing and metrics APIs

- `AlwaysRecord` is stable.
- `TraceIdRatioBased` has been restored but has a deprecation timeline.
- Tracer `enabled`, synchronous instrument `Enabled`, and
  `LogRecordProcessor.Enabled` are stable enablement checks.
- Synchronous instruments add an in-development `Bind` API.
- Periodic exporting `MetricReader` adds an in-development
  `maxExportBatchSize` parameter.
- Metric stream names supplied by a View are exempt from instrument-name
  syntax validation.

## Logs, profiles, and entities

- Logs add an optional ergonomic API. Logger `Emit` has a stable optional
  `Exception` parameter; logger configuration adds `minimum_severity` and
  `trace_based`.
- The Logs specification defines an event-to-span-event bridge.
- Entity information can be represented as structured log events.
- Profiles have a signal specification and data model, supplemented by pprof
  documentation.
- The specification defines Entity and adds Entity support to the Resource SDK
  (batch `2026-08-stable`).
- Standard OTLP exporter configuration includes maximum request- and
  response-size options.

## Resources and attribute values

A Resource describes the observed entity, not necessarily the component that
emitted the telemetry.

Complex `AnyValue` attributes and their limits are stable. For non-OTLP
transport, follow the dedicated guidance for byte arrays, empty values,
arrays, maps, and nested values. JSON-object string representations for
individual attributes and attribute collections remain in development.

## SDK self-observability

An in-development SDK self-observability section applies across the Tracing,
Metrics, and Logs SDK specifications. Its supplementary guidance is
non-normative.

## Declarative SDK configuration

Significant portions of declarative configuration are stable:

- `create` and `parse` defaults and validation are clarified.
- `create` may accept optional programmatic customization.
- Prefer strict YAML parsing.
- Environment substitution may use language-specific prefixes.
- The boolean environment-variable rules do not automatically apply to other
  configuration interfaces.
- `TracerConfig`, `MeterConfig`, and `LoggerConfig` use `enabled`, replacing
  `disabled`.
- `ComponentProvider` is renamed to `PluginComponentProvider`.
- `CreatePlugin` is renamed to `CreateComponent`.
- An unset instrumentation configuration returns an empty object.

## Prometheus and OpenMetrics interoperability

### Exporter configuration

Use `scope_info_enabled`, `target_info_enabled`, and
`resource_constant_labels`. These replace `without_scope_info`,
`without_target_info`, and `with_resource_constant_labels`.

The exporter host, port, temporality, version/format, scope-info,
default-aggregation, resource-attribute, and client-library sections are
stable.

### Stable conversion paths

Stable conversions cover:

- Prometheus counters, gauges, summaries, and classic histograms to OTLP.
- OpenTelemetry sums, gauges, histograms, scope, attributes, exemplars, and
  metadata to Prometheus.

An optional conversion maps OpenTelemetry Histograms to Prometheus Native
Histograms with Custom Buckets.

The Zipkin exporter specification is deprecated, and implementing that
exporter is optional.
