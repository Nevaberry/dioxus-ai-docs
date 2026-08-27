# Specification and SDK

## Context propagation and sampling

### Environment-variable carriers (`specification`)

The carrier specification is Release Candidate. Apply POSIX.1-2024-aligned
name restrictions and normalization to requested, carrier, and returned keys.
Read and return only normalized environment-variable names, normalize an empty
name to `_`, and do not assume that implementations cache carrier data.

### W3C randomness and sampling (`specification`)

Context propagation requires the W3C randomness flag. `AlwaysRecord` is
stable. `TraceIdRatioBased` has been restored, but it also has a deprecation
timeline.

### Deprecated compatibility paths (`specification`)

Jaeger and OT Trace propagators are deprecated and optional to implement. The
Zipkin exporter specification is also deprecated and optional to implement.
OpenTracing and OpenCensus compatibility requirements are deprecated.

## Signal APIs

### Enablement and metric instruments (`specification`)

The Tracer `enabled` operation, synchronous instruments' `Enabled` API, and
`LogRecordProcessor.Enabled` are stable. Synchronous instruments also have an
in-development `Bind` API. A metric stream name supplied by a View is exempt
from instrument-name syntax validation.

### Periodic export batching (`specification`)

The periodic exporting `MetricReader` has an in-development
`maxExportBatchSize` parameter.

### Logging APIs and bridges (`specification`)

Logs provide an optional ergonomic API. Logger `Emit` has a stable optional
`Exception` parameter, and logger configuration includes `minimum_severity`
and `trace_based`. The Logs specification also defines an event-to-span-event
bridge, and entity information can be carried as structured log events.

### Profiles (`specification`)

The Profiles signal has a specification and data model, supplemented by pprof
documentation.

## Resources, entities, and attributes

### Resource meaning (`specification`)

A Resource describes the observed entity, not the component that technically
emits telemetry.

### Entity support and OTLP limits (`2026-08-stable`)

Specification 1.60 defines Entity and adds Entity support to the Resource SDK
specification. The standard OTLP exporter configuration list includes maximum
request- and response-size options.

### Complex attribute values (`specification`)

Complex `AnyValue` attribute types and their limits are stable. Non-OTLP
guidance covers byte arrays, empty values, arrays, maps, and nested values.
In-development guidance recommends JSON-object string representations for
attributes and attribute collections.

## SDK configuration and self-observability

### SDK self-observability guidance (`specification`)

An in-development SDK self-observability section applies across the Tracing,
Metrics, and Logs SDK specifications, with supplementary non-normative
guidance.

### Declarative configuration behavior (`specification`)

Significant portions of declarative configuration are stable. `create` and
`parse` defaults and validation are clarified; `create` permits optional
programmatic customization; strict YAML parsing is recommended. Environment
substitution may use language-specific prefixes, and boolean
environment-variable guidance does not apply to other configuration
interfaces.

### Declarative names and unset behavior (`specification`)

`TracerConfig`, `MeterConfig`, and `LoggerConfig` use `enabled` instead of
`disabled`. Rename `ComponentProvider` to `PluginComponentProvider` and
`CreatePlugin` to `CreateComponent`. An unset instrumentation configuration
returns an empty object.

### Processor metric semantics (`2026-08-stable`)

Record `otel.sdk.processor.span.processed` and
`otel.sdk.processor.log.processed` when a processor passes items to an
exporter—not when its queue accepts them or export completes. Export outcome
does not change the count.

## Prometheus and OpenMetrics interoperability

### Prometheus exporter property names (`specification`)

Use `scope_info_enabled`, `target_info_enabled`, and
`resource_constant_labels`. These replace `without_scope_info`,
`without_target_info`, and `with_resource_constant_labels`.

### Stable conversion paths (`specification`)

Stable conversions cover Prometheus counters, gauges, summaries, and classic
histograms to OTLP, and OpenTelemetry sums, gauges, histograms, scope,
attributes, exemplars, and metadata to Prometheus. Exporter host, port,
temporality, version/format, scope-info, default-aggregation,
resource-attribute, and client-library sections are stable. An optional
OpenTelemetry Histogram to Prometheus Native Histogram with Custom Buckets
conversion is also defined.
