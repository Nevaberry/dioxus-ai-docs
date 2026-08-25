# Collector Pipelines and Processing

## OTTL functions and test APIs

### Collection and lambda converters (`collector-0.157.0`)

OTTL provides `When`, `IsEmpty`, `All`, `Any`, `Filter`, `Find`, `MapEach`,
`MapKeys`, and `Reduce` for conditional, predicate, mapping, and folding
operations over slices and maps. `truncate_all` accepts an optional
`truncation_marker`.

### Static checks and pdata snapshots (`collector-0.157.0`)

OTTL lambda-arity validation is separated for static checking.
`LambdaActivation.IsArgBound` and variadic-argument evaluation helpers are
available. `pmetricassert` snapshot generation has
`IncludeHistogramExplicitBounds`, which selects bounds without requiring other
histogram datapoint values.

### Value comparison and semantic-convention transforms (`2026-08-stable`)

OTTL compares `pcommon.Value` with all six ordering/equality operators. The
default-off `ottl.set.allowNil` gate lets `set` pass `nil` to its target.
`set_semconv_span_name()` supports semantic-convention versions 1.41.0
through 1.43.0.

## Lookup, parsing, and transforms

### Lookup processor sources (`collector-0.157.0`)

The Lookup processor accepts CSV with key/value columns selected by name or
index, scalar or full-row values, and optional `reload_interval`. YAML sources
also support periodic reload and retain old data after a failed reload.

### Drain, CEF, and schema-URL transforms (`collector-0.157.0`)

With `extract_parameters`, the Drain processor writes tokens matched by `<*>`
to `log.record.template.params`. The Transform processor adds `ParseCEF`.
The GenAI Normalizer can opt into overwriting an existing scope schema URL.

## Sampling and tail storage

### W3C-aware sampling (`collector-0.157.0`)

Dynamic Sampling composes its rate with an incoming W3C `ot=th`, uses `ot=rv`
randomness when present, and emits the effective threshold. The alpha
`processor.tailsamplingprocessor.usetracestate` gate gives the Tail Sampling
probabilistic policy corresponding W3C randomness and outgoing-threshold
behavior across matched policies.

### Dynamic Sampling decisions and shutdown (`2026-08-stable`)

Dynamic Sampling rejects rule names that collide with reserved,
underscore-prefixed decision labels. Its no-match label is `_unmatched`, not
`unmatched`. On shutdown, it decides buffered traces instead of discarding
them, forwards kept traces with `ot=th`, and records `trigger="shutdown"`
without double-counting earlier decisions.

## Processor self-observability and profiles

### Component metrics and entity events (`collector-0.157.0`)

Resource Detection emits `otelcol.resourcedetection.detector.results`,
`otelcol.resourcedetection.detector.duration`, and
`otelcol.resourcedetection.attributes.detected`. Span Pruning can opt into
byte-flow counters with `enable_bytes_metrics`. `experimentalmetricmetadata`
has feature-gated emission of specification-format entity-event log records.

### Resource Detection migration and new detectors (`2026-08-stable`)

Two alpha gates migrate Elastic Beanstalk from `deployment.environment` and
`service.instance.id` to `deployment.environment.name` and `deployment.id` in
two stages. First enable
`processor.resourcedetection.elasticbeanstalk.EmitV1DeploymentConventions`,
then enable
`processor.resourcedetection.elasticbeanstalk.DontEmitV0DeploymentConventions`.
Enabling only the second gate is a startup error. Resource Detection also has
global retry configuration, an Azure Container Apps detector, and the
default-off `processor.resourcedetection.consul.prefixMetaAttributes` gate for
`consul.meta.<key>` attributes.

### Profile translation metadata (`collector-0.157.0`)

The pprof translator maps OTLP sample attributes to pprof sample labels. The
pprof receiver sets instrumentation scope name and version according to file,
HTTP client, HTTP server, or self-scraper mode.

## Corrected trace and metric behavior

### Translation, sampling, and aggregation fixes (`collector-0.157.0`)

Jaeger translation preserves the sampled flag in both directions. The beta,
default-on Datadog receiver 128-bit trace-ID gate reconstructs every span in a
payload. Metrics Transform skips unsupported Summary aggregation with a
warning instead of dropping all points. Tail Sampling treats `threshold_ms`
as an exclusive lower bound when `upper_threshold_ms` is unset. Podman Stats
reports block-I/O byte metrics with unit `By`.
