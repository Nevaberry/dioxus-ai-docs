# Collector Pipelines and Processing

## OTTL collections and lambdas

OTTL adds the following collection-oriented functions:

- `When`
- `IsEmpty`
- `All` and `Any`
- `Filter`
- `Find`
- `MapEach` and `MapKeys`
- `Reduce`

These provide conditional, predicate, mapping, and folding operations over
slices and maps. `truncate_all` also accepts an optional
`truncation_marker`.

Static checking validates OTTL lambda arity separately. Runtime and test APIs
add `LambdaActivation.IsArgBound` and variadic-argument evaluation helpers.
`pmetricassert` snapshot generation adds `IncludeHistogramExplicitBounds`,
which selects bounds without requiring other histogram datapoint values.

OTTL can compare `pcommon.Value` with all six ordering/equality operators. The
default-off `ottl.set.allowNil` gate lets `set` pass `nil` to its target, and
`set_semconv_span_name()` supports semantic-convention versions 1.41.0 through
1.43.0 (batch `2026-08-stable`).

## Lookup, Drain, and Transform

### Lookup processor

The Lookup processor accepts a CSV source with key/value columns selected by
name or index. Values may be scalars or complete rows, and `reload_interval`
can periodically reload the source. YAML sources also support periodic reload;
a failed reload retains the old data.

### Drain and Transform processors

- With `extract_parameters`, Drain writes tokens matched by `<*>` to
  `log.record.template.params`.
- Transform adds `ParseCEF`.
- The GenAI Normalizer can opt into overwriting an existing scope schema URL.

## W3C-aware sampling

Dynamic Sampling composes its rate with an incoming W3C `ot=th` threshold,
uses `ot=rv` randomness when present, and emits the effective threshold.

The alpha `processor.tailsamplingprocessor.usetracestate` gate gives the Tail
Sampling probabilistic policy matching W3C randomness and outgoing-threshold
behavior across matched policies.

Dynamic Sampling also has these decision rules:

- Reject user rule names that collide with reserved underscore-prefixed
  decision labels.
- The no-match metric label is `_unmatched`, replacing `unmatched`.
- At shutdown, decide buffered traces instead of dropping them.
- Forward kept shutdown traces with `ot=th` and record
  `trigger="shutdown"` without double-counting earlier decisions.

## Component self-observability and entity events

Resource Detection emits:

- `otelcol.resourcedetection.detector.results`
- `otelcol.resourcedetection.detector.duration`
- `otelcol.resourcedetection.attributes.detected`

Span Pruning enables byte-flow counters with `enable_bytes_metrics`.
`experimentalmetricmetadata` can emit specification-format entity-event log
records behind its feature gate.

## Resource Detection migrations

Two alpha Elastic Beanstalk gates stage the migration from
`deployment.environment` and `service.instance.id` to
`deployment.environment.name` and `deployment.id`:

1. Enable
   `processor.resourcedetection.elasticbeanstalk.EmitV1DeploymentConventions`.
2. Then enable
   `processor.resourcedetection.elasticbeanstalk.DontEmitV0DeploymentConventions`.

Enabling only the second gate is a startup error. Resource Detection also
adds global retry configuration, an Azure Container Apps detector, and the
default-off `processor.resourcedetection.consul.prefixMetaAttributes` gate for
`consul.meta.<key>` attributes.

## Profile translation

The pprof translator maps OTLP sample attributes to pprof sample labels. The
pprof receiver sets instrumentation scope name and version according to file,
HTTP client, HTTP server, or self-scraper mode.

## Processing behavior corrections

- Jaeger translation preserves the sampled flag in both directions.
- Metrics Transform warns and skips unsupported Summary aggregation instead
  of dropping every point.
- Tail Sampling treats `threshold_ms` as an exclusive lower bound when
  `upper_threshold_ms` is unset.
