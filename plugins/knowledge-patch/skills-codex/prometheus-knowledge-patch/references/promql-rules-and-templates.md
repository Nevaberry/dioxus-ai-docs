# PromQL, Rules, and Templates

Use this reference for query semantics, histogram functions, experimental
syntax, rule evaluation, rule tests, and template helpers.

## Core syntax and matching

### Dot matches newlines (3.0.0)

The regular-expression `.` metacharacter matches every character, including
newlines. Audit selectors such as `{label=~"a.b"}` when the broader match is not
intended.

### Use duration literals as scalar values (3.0.0)

PromQL duration and float literals are interchangeable without an experimental
flag. For example, `time() - 1h` is a scalar expression.

### Use UTF-8 label names in `label_replace` (3.3.0)

`label_replace()` supports UTF-8 labels.

### Avoid duplicate `label_join` results (3.3.0)

`label_join()` no longer produces duplicate result series.

## Duration expressions and range precision

### Compute durations arithmetically (3.4.0)

Duration expressions accept arithmetic, including computed durations used in
range selectors.

### Preserve millisecond range precision (3.5.0)

Range selectors no longer round `[1001ms]` to `[1s]`. Boundary-sample inclusion
can therefore change.

### Use step-aware duration helpers (3.6.0)

With the duration-expression feature on releases where it remains gated,
`step()` and `min()`/`max()` over durations let a range follow query resolution
while retaining bounds:

```promql
rate(http_requests_total[max(5m, step())])
```

### Reject invalid duration values (3.12.0)

Duration expressions reject `NaN`, infinity, and out-of-range values instead of
silently creating an out-of-range duration.

### Use query-boundary functions experimentally (3.12.0)

Experimental `start()`, `end()`, and `range()` expose query boundaries.
`range()` is valid in duration expressions:

```promql
foo[5m+range()]
```

### Rename ambiguous helpers (3.13.0)

Experimental duration `min()` and `max()` are now `min_of()` and `max_of()`.
Experimental scalar forms use the same names:

```promql
rate(http_requests_total[max_of(5m, step())])
max_of(2, 5)
```

### Treat duration expressions as default syntax (3.13.2-3.14.0)

Duration expressions no longer require
`--enable-feature=promql-duration-expr`; that flag is a no-op.

## Aggregations, matching, and metadata

### Pass dynamic aggregation parameters (3.5.0)

Aggregations such as `quantile` and `topk` accept non-constant parameter
expressions:

```promql
topk(scalar(desired_series_count), rate(http_requests_total[5m]))
```

### Reject NaN aggregation parameters (3.6.0)

`topk()`, `bottomk()`, `limitk()`, and `limit_ratio()` fail when passed `NaN`.

### Expose type and unit metadata labels (3.5.0)

Enable `--enable-feature=type-and-unit-labels` to expose metric type and unit as
labels in PromQL. These labels are reserved and follow metric-name-style
dropping rules, as described in the OTLP reference.

### Fill unmatched binary-expression series (3.10.0)

Use `fill()`, `fill_left()`, or `fill_right()` to supply values for series
missing from one or both sides:

```promql
left_metric + fill(0) right_metric
```

### Keep fill results with group matching (3.13.0)

`fill_left()` and `fill_right()` retain expected samples in range queries using
`group_left` or `group_right`.

## Histogram query semantics

### Ignore histograms in time and clamp functions (3.1.0)

Time-related functions and clamp functions omit histogram samples from mixed
float-and-histogram inputs.

### Calculate instant deltas and rates (3.3.0)

`idelta()` and `irate()` support native histograms, and native-histogram
counter-reset detection is corrected.

### Ignore histograms in scalar and sort functions (3.3.0)

`scalar()`, `sort()`, and `sort_desc()` ignore native-histogram samples.

### Accept classic buckets in fractions (3.4.0)

`histogram_fraction()` accepts classic bucket histograms as well as native
histograms:

```promql
histogram_fraction(0, 0.2, rate(http_request_duration_seconds_bucket[5m]))
```

### Use arithmetic means for deviation (3.4.0)

`histogram_stddev()` and `histogram_stdvar()` use the arithmetic mean, so
results differ from versions that used another mean.

### Omit mixed classic/native values (3.5.0)

`histogram_fraction()` and `histogram_quantile()` emit no value when classic
and native histograms coexist at the same timestamp.

### Interpret query diagnostics and gauge typing (3.7.0)

Some histogram operations attach warn-level annotations for counter-reset
conflicts. Subtraction, multiplication, or division by a negative factor types
the resulting native histogram as a gauge.

### Reconcile mismatched custom bounds (3.8.0)

Native-histogram addition and subtraction reconcile mismatched NHCB boundaries
instead of requiring identical bounds.

### Count histograms against sample limits (3.8.0)

Histogram samples count toward PromQL sample-limit enforcement. Histogram-heavy
queries can now hit the configured limit.

### Type range-function results as gauges (3.9.0)

`rate()`, `increase()`, and `delta()` return gauge histograms for histogram
inputs.

### Handle a single histogram in averages (3.10.0)

`avg_over_time()` correctly handles a range containing one native histogram.

### Trim native histograms (3.11.0)

The `</` and `>/` operators trim observations from native histograms while
retaining the correct buckets.

### Compute multiple experimental quantiles (3.11.0)

Experimental `histogram_quantiles` is variadic and computes several quantiles
in one call.

## Extended range selectors and timestamp-aware queries

### Enable anchored and smoothed rates (3.7.0)

Use `--enable-feature=promql-extended-range-selectors` for experimental
`anchored` and `smoothed` range-selector modifiers.

### Handle anchored empty ranges (3.9.0)

`resets()` and `changes()` return an empty result for an anchored selector when
all samples are outside the requested range.

### Interpolate smoothed resets correctly (3.10.0)

Smoothed range selectors interpolate across counter resets correctly, changing
affected results.

### Use stored start timestamps in rates (3.12.0)

With `--enable-feature=use-start-timestamps`, `rate()`, `irate()`, and
`increase()` use start timestamps, and `resets()` detects start-timestamp
resets. This mode cannot be combined with `anchored` or `smoothed` selectors.

### Handle smoothed range boundaries (3.12.0)

Smoothed `rate()` and `increase()` return no result rather than zero when all
data lies strictly after the range. Smoothed selectors work in binary
operations using an `@` modifier.

### Extend rates to native histograms (3.13.0)

Experimental smoothed and anchored rate evaluation supports native histograms.

### Correct anchored histogram reset detection (3.13.0)

`resets()` and `changes()` return corrected results for histograms used with
anchored selectors.

### Expose sample start timestamps (feature-flags)

`--enable-feature=use-start-timestamps` also enables `start_timestamp()`. It
does not work with extended range selectors.

### Obey the extended-selector allowlists (feature-flags)

`anchored` is accepted only by `resets`, `changes`, `rate`, `increase`, and
`delta`; `smoothed` is accepted only by `rate`, `increase`, and `delta`.
Extended selectors reject subqueries. Because smoothed evaluation needs a
sample after the interval, recording and alerting rule groups need a
`query_offset` of at least one scrape interval to avoid under-estimation.

## Range functions and `info()` corrections

### Get timestamps of extrema (3.5.0)

On this release, enable `--enable-feature=experimental-promql-functions` and
use `ts_of_min_over_time()`, `ts_of_max_over_time()`, and
`ts_of_last_over_time()` to obtain timestamps associated with range-vector
values. Later releases use the current flag spelling documented below.

### Get the first sample (3.7.0)

With `--enable-feature=experimental-promql-functions` on this release,
experimental functions include `first_over_time(...)` and
`ts_of_first_over_time(...)`. Later releases use the current flag spelling
documented below:

```promql
first_over_time(metric[5m])
ts_of_first_over_time(metric[5m])
```

### Retain more `info()` results (3.10.0)

`info()` retains series without identifying labels and correctly applies a
filter to a label present in both the input metric and `target_info`.

### Warn about range-query sorting (3.12.0)

`sort()`, `sort_by_label()`, and `sort_by_label_desc()` warn in range queries,
where they have no effect.

### Handle negated metric-name matchers in `info()` (3.12.0)

`info()` correctly evaluates negated `__name__` matchers.

### Drop metric names through range functions (3.12.0)

`last_over_time()` and `first_over_time()` drop the metric name when applied to
a subquery containing a name-dropping function such as `abs()`.

### Use the stable first-sample function (3.13.2-3.14.0)

`first_over_time` no longer needs
`--enable-feature=promql-experimental-functions`.

### Apply result corrections (3.13.2-3.14.0)

Case-insensitive regex label matchers no longer omit matching values.
`mad_over_time` returns `NaN`, rather than `0`, when its range includes a `NaN`
sample.

## Rules and templates

### Serialize uncertain rule dependencies (3.1.0)

When dependency analysis is uncertain, rules fall back to serialized rather
than concurrent evaluation.

### Use UTF-8 rule names (3.2.0)

Rule names may contain UTF-8 except `{` and `}`, which common-mistake checks
still reject.

### Use YAML anchors in rule files (3.3.0)

Rule files accept YAML anchors and aliases.

### Apply alert relabeling to drop decisions (3.3.0)

Alert relabeling participates in the decision about whether an alert is
dropped.

### Detect parse errors during startup (3.5.0)

Rule parse errors are found earlier, before normal evaluation starts.

### Use template time and duration helpers (3.6.0)

Templates provide `toDuration()` and `now()`.

### Scope mutating relabel actions per Alertmanager (3.7.0)

Mutations in one `alertmanager_config.alert_relabel_configs` block do not pass
the changed alert into later Alertmanager configuration blocks.

### Escape query values in alert URLs (3.8.0)

Use `urlQueryEscape` when interpolating dynamic values into URL query strings:

```text
{{ urlQueryEscape $labels.instance }}
```

### Handle the unknown alert state (3.8.0)

An alerting rule not yet evaluated has state `unknown`. API and UI consumers
must handle it alongside established states.

### Preserve alert state across edits (3.11.0)

Increasing an alert's `FOR` period no longer resets it incorrectly to pending.
State restoration also works when rule labels contain Go template expressions.

### Set start timestamps in promqltest data (3.12.0)

PromQL test `load` blocks accept `@st` for each sample's start timestamp.

### Use the current experimental-function flag (feature-flags)

Enable unstable functions with
`--enable-feature=promql-experimental-functions`. Their names, syntax, and
semantics can change.

### Bound concurrent rule evaluation (feature-flags)

`--enable-feature=concurrent-rule-eval` runs dependency-free rules in one group
concurrently. Limit the extra query load with
`--rules.max-concurrent-evals`; its default is `4`.
