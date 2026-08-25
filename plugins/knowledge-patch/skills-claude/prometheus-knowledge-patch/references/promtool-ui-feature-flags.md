# Promtool, UI, and Feature Flags

## Automatic reload begins experimental (`3.0.0`)

The initial automatic-reload capability was enabled with:

```text
--enable-feature=auto-reload-config
```

It later expands to referenced files and becomes stable; prefer the stable
configuration behavior on versions that provide it. The example console
JavaScript and templates are no longer bundled, so console users supply them.

## Lint and parser controls (`3.2.0`)

`promtool` adds the `too-long-scrape-interval` lint option. Use
`--ignore-unknown-fields` when a newer configuration contains fields the local
tool does not recognize and ignoring them is intentional.

## Piped block creation (`3.3.0`)

`promtool tsdb create-blocks-from openmetrics` accepts OpenMetrics input from a
pipe.

## Feature-aware PromQL checks (`3.4.0`)

`promtool` accepts PromQL feature flags, allowing offline validation to parse
the same gated syntax as the server.

## Fuzzy rule tests (`3.5.0`)

Rule-unit tests can opt into tolerant float64 comparisons:

```yaml
fuzzy_compare: true
```

## Target relabel traces and Remote Write 2 (`3.8.0`)

The target UI displays each relabeling step for a discovered target, explaining
how labels change and why a target is dropped.

`promtool push metrics` sends Remote Write 2 messages when the desired message
type is selected with `--protobuf_message`.

## Time-stable tests and compact dumps (`3.9.0`)

Rule-unit tests accept `start_timestamp`, making time-sensitive tests start at
an explicit instant. Emit labels-only JSON from a TSDB with:

```text
promtool tsdb dump --format seriesjson
```

## Previously gated syntax (`3.10.0`)

`promtool` understands `promql-duration-expr` and
`promql-extended-range-selectors`, so checks can parse queries using those
feature gates.

## Stable stdout for pipelines (`3.11.0`)

`promtool` sends debug diagnostics to stderr. Keep stderr separate when stdout
is parsed as command output.

## Stable reload, maintenance UI, and query headers (`3.12.0`)

Automatic configuration reload is stable. The Status menu includes a UI for
deleting time series and cleaning tombstones.

`promtool query instant` accepts `--header`, matching range-query support.
PromQL test `load` blocks accept `@st` annotations for sample start timestamps.

## HTTP configuration paths (`3.13.0`)

Relative paths inside a `--http.config.file` file resolve from that file's own
directory rather than its parent. The binary serves third-party licenses at
`/assets/third-party-licenses.txt`; release assets no longer include
`npm_licenses.tar.bz2`.

## Current feature-gate behavior (`feature-flags`)

### Prefer configuration for extra scrape metrics

`extra-scrape-metrics` is deprecated. Use `extra_scrape_metrics: true` globally
or per scrape configuration. Stored metrics include `scrape_timeout_seconds`,
`scrape_sample_limit`, and `scrape_body_size_bytes`; zero sample limit means
unlimited, and failed body size is `-1` for a size-limit failure or `0` for
other failures.

### Use the current experimental-function spelling

Use `--enable-feature=promql-experimental-functions`. Experimental function
names, syntax, and semantics can change.

### Pin scrape protocol order with zero injection

Without explicit `scrape_protocols`, `created-timestamp-zero-ingestion` prefers
`PrometheusProto`, `OpenMetricsText1.0.0`, `OpenMetricsText0.0.1`, then
`PrometheusText0.0.4`.

### Satisfy start-timestamp encoding prerequisites

`st-storage` requires float chunks to resolve to XOR2 and needs
`histograms-st-encoding` for native- and float-histogram start timestamps.
`SamplesV2` WAL records need Prometheus 3.11 or later. These block formats can
break downgrade and downstream compatibility.

`use-start-timestamps` enables `start_timestamp()` but is incompatible with
extended selectors. `st-synthesis` rewrites scraped cumulative streams, does
not support remote write or OTLP, and has strict out-of-order and append-failure
state behavior; review the storage reference before enabling it.

### Bound concurrent rule evaluation

`concurrent-rule-eval` applies only to dependency-free rules in a group. Cap
the resulting query load with `--rules.max-concurrent-evals` (default `4`).

### Pick exactly one OTLP delta strategy

`otlp-native-delta-ingestion` and `otlp-deltatocumulative` are mutually
exclusive. Raw deltas need aligned `sum_over_time()` queries and an explicit
label when mixed with cumulative data.

### Protect reserved metadata labels

With `type-and-unit-labels`, ingestion metadata wins over input values for
`__type__` and `__unit__`. Operations that drop `__name__` also drop them.

### Linux direct I/O

`--enable-feature=use-uncached-io` uses direct I/O for chunk writes on Linux,
bypassing the page cache.

### Respect extended-selector limits

`anchored` is limited to `resets`, `changes`, `rate`, `increase`, and `delta`;
`smoothed` is limited to `rate`, `increase`, and `delta`. Neither supports
subqueries. Rules using `smoothed` need `query_offset` of at least one scrape
interval.

### Cap search requests

With `search-api`, `--web.search.max-limit` defaults to `10000`. Larger limits
return HTTP 400; `0` means unbounded and is unsafe on an untrusted endpoint.

## Current promtool compatibility (`3.13.2-3.14.0`)

Duration expressions are enabled by default, so `promql-duration-expr` is a
no-op, and stable `first_over_time` no longer needs the experimental-functions
gate.

`promtool push metrics --remote-write.path` supports backends with a
non-default remote-write endpoint. Validate fill modifiers in rules with
`promtool check rules --enable-feature=promql-binop-fill-modifiers`.

`promtool check config` does not contact AWS IMDS when a supported AWS discovery
configuration omits `region`.
