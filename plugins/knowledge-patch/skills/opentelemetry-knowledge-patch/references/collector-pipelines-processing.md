# Collector Pipelines and Processing

The details in this reference apply to the Collector 0.157.0 batch.

## OTTL collection functions

OTTL adds collection-oriented functions for slices and maps:

- `When` for conditional evaluation.
- `IsEmpty`.
- Predicate operations `All` and `Any`.
- `Filter` and `Find`.
- Mapping operations `MapEach` and `MapKeys`.
- `Reduce` for folding.

`truncate_all` accepts an optional `truncation_marker`.

## OTTL and pdata test APIs

- OTTL lambda-arity validation is separated for static checking.
- `LambdaActivation.IsArgBound` reports whether an argument is bound.
- Variadic-argument evaluation helpers are available.
- `pmetricassert` snapshot generation adds
  `IncludeHistogramExplicitBounds`, selecting histogram bounds without
  requiring other histogram datapoint values.

## Lookup, Drain, Transform, and normalization

### Lookup processor

The Lookup processor adds a CSV source with:

- Key and value columns selected by name or index.
- Scalar values or full-row values.
- An optional `reload_interval`.

YAML sources also gain periodic reload. After a reload failure, the processor
retains its old data.

### Other processors

- With `extract_parameters`, the Drain processor writes tokens matched by
  `<*>` to `log.record.template.params`.
- The Transform processor adds `ParseCEF`.
- The Generative AI Normalizer can opt into overwriting an existing
  instrumentation-scope schema URL.

## W3C-aware sampling

The Dynamic Sampling processor:

- Composes its sampling rate with an incoming W3C `ot=th`.
- Uses `ot=rv` randomness when present.
- Emits the effective threshold.

The alpha `processor.tailsamplingprocessor.usetracestate` gate gives the Tail
Sampling probabilistic policy corresponding W3C randomness and outgoing
threshold behavior across matched policies.

## Component self-observability

The Resource Detection processor adds:

- `otelcol.resourcedetection.detector.results`.
- `otelcol.resourcedetection.detector.duration`.
- `otelcol.resourcedetection.attributes.detected`.

The Span Pruning processor can enable byte-flow counters through
`enable_bytes_metrics`.

`experimentalmetricmetadata` has feature-gated emission of
specification-format entity-event log records.

## Profile translation

- The pprof translator maps OTLP sample attributes to pprof sample labels.
- The pprof receiver sets instrumentation-scope name and version according to
  whether it runs in file, HTTP client, HTTP server, or self-scraper mode.

## Trace and metric behavior corrections

- Jaeger translation preserves the sampled flag in both directions.
- The beta, default-on Datadog receiver 128-bit trace-ID gate reconstructs
  every span in a payload.
- Metrics Transform skips unsupported Summary aggregation with a warning
  instead of dropping all points.
- Tail Sampling treats `threshold_ms` as an exclusive lower bound when
  `upper_threshold_ms` is unset.
- Podman Stats reports block-I/O byte metrics with unit `By`.
