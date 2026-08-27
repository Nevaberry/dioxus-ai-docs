# PromQL

## Regular expressions and duration literals (`3.0.0`)

The `.` metacharacter now matches every character, including newlines, so a
matcher such as `{label=~"a.b"}` can select more series. Duration and float
literals are interchangeable without an experimental gate; for example,
`time() - 1h` is valid.

## Histogram omission in general functions (`3.1.0`)

Time-related and clamp functions ignore histogram samples. Mixed
float/histogram inputs therefore omit histogram points rather than treating
them as floats.

## Histogram rates and label functions (`3.3.0`)

`idelta()` and `irate()` support native histograms, with corrected counter-reset
detection. `label_replace()` supports UTF-8 labels and `label_join()` no longer
produces duplicate results. `scalar()`, `sort()`, and `sort_desc()` ignore
native-histogram samples.

## Duration arithmetic and histogram math (`3.4.0`)

The parser accepts arithmetic in duration expressions, including computed
range durations. `histogram_fraction()` accepts classic buckets:

```promql
histogram_fraction(0, 0.2, rate(http_request_duration_seconds_bucket[5m]))
```

`histogram_stddev()` and `histogram_stdvar()` use the arithmetic mean, changing
results produced by their earlier mean.

## Dynamic parameters and precision (`3.5.0`)

Enable `--enable-feature=type-and-unit-labels` for PromQL to expose metric
metadata as labels. Experimental range functions include
`ts_of_min_over_time()`, `ts_of_max_over_time()`, and
`ts_of_last_over_time()`. Their v3.5-era gate spelling was
`experimental-promql-functions`; use the current spelling documented under
feature-gate constraints below on later versions.

Aggregation parameters such as those for `quantile` and `topk` can be dynamic:

```promql
topk(scalar(desired_series_count), rate(http_requests_total[5m]))
```

`histogram_fraction()` and `histogram_quantile()` return no value when classic
and native histograms coexist at the same timestamp. Millisecond range
selectors such as `[1001ms]` retain precision rather than rounding to `[1s]`.

## Step-aware duration expressions (`3.6.0`)

Enable the v3.6 behavior with `--enable-feature=promql-duration-expr`. It adds
`step()` and originally added duration `min()` and `max()` helpers, allowing a
range to follow query resolution while retaining a lower bound. Current syntax
uses `min_of()` and `max_of()`; see the later rename below.

`topk()`, `bottomk()`, `limitk()`, and `limit_ratio()` reject `NaN` parameters.

## Extended selectors and first-sample functions (`3.7.0`)

Enable `anchored` and `smoothed` rate range modifiers with
`--enable-feature=promql-extended-range-selectors`. Experimental functions add
`first_over_time()` and `ts_of_first_over_time()`; the v3.7-era function gate
spelling was `experimental-promql-functions`, while later guidance standardizes
the current spelling below.

## Custom-bucket arithmetic (`3.8.0`)

Native-histogram addition and subtraction reconcile mismatched custom bucket
boundaries instead of requiring identical NHCB bounds. Histogram samples count
toward query sample limits.

## Anchored boundaries and histogram types (`3.9.0`)

`resets()` and `changes()` return an empty result for an anchored selector when
every sample is outside the requested range. `rate()`, `increase()`, and
`delta()` return gauge histograms for histogram input.

## Fill modifiers and corrected edge cases (`3.10.0`)

Binary expressions can provide defaults for missing series with `fill()`,
`fill_left()`, and `fill_right()`:

```promql
left_metric + fill(0) right_metric
```

`info()` retains series without identifying labels and handles a filter on a
label shared by the input and `target_info`. Smoothed selectors interpolate
correctly over counter resets. `avg_over_time()` correctly processes a range
containing one native histogram.

## Histogram trimming and quantiles (`3.11.0`)

The `</` and `>/` operators trim observations from native histograms while
retaining the proper buckets. Experimental `histogram_quantiles` computes
multiple quantiles in one variadic call.

## Query boundaries and start timestamps (`3.12.0`)

PromQL warns when `sort()`, `sort_by_label()`, or `sort_by_label_desc()` appears
in a range query, where it has no effect. Experimental `start()`, `end()`, and
`range()` expose query boundaries; `range()` is valid in a duration expression:

```promql
foo[5m+range()]
```

With `use-start-timestamps`, `rate()`, `irate()`, and `increase()` use start
timestamps and `resets()` detects start resets. It cannot combine with
`anchored` or `smoothed`.

Smoothed `rate()` and `increase()` return no result when all data lies strictly
after the query range. Smoothed selectors work in binary expressions using an
`@` modifier. Invalid duration expressions—NaN, infinite, or out of range—are
rejected.

`info()` handles negated `__name__` matchers. `last_over_time()` and
`first_over_time()` drop the metric name when their subquery contains a
name-dropping function such as `abs()`.

## Current duration helpers and query accounting (`3.13.0`)

Experimental duration `min()` and `max()` are renamed `min_of()` and `max_of()`;
the same names also provide scalar forms:

```promql
rate(http_requests_total[max_of(5m, step())])
max_of(2, 5)
```

Experimental `smoothed` and `anchored` rate evaluation supports native
histograms. `fill_left()` and `fill_right()` retain samples in range queries
using `group_left` or `group_right`. Histogram `resets()` and `changes()` return
corrected results with anchored selectors.

Range subqueries stop at the parent's last actual step when the query end is not
step-aligned, preventing inflated `peakSamples`, max-sample enforcement, and
storage reads. `@`-modified ranges under at-unsafe functions correctly count
`totalQueryableSamples` after the first step.

## Feature-gate constraints (`feature-flags`)

Use the current `promql-experimental-functions` spelling. Experimental names,
syntax, and semantics are unstable.

`anchored` is accepted only by `resets`, `changes`, `rate`, `increase`, and
`delta`; `smoothed` only by `rate`, `increase`, and `delta`. Extended selectors
do not support subqueries. Because `smoothed` needs a sample after the interval,
alerting and recording groups need `query_offset` of at least one scrape
interval to avoid underestimation.

For raw OTLP deltas, use an interval-aligned `sum_over_time()` rather than
counter functions. `type-and-unit-labels` are dropped in the same operations
that drop `__name__`.

## Stabilizations and result corrections (`3.13.2-3.14.0`)

Duration expressions are enabled by default, making
`promql-duration-expr` a no-op. `first_over_time` is stable and no longer needs
the experimental-functions gate.

Case-insensitive regular-expression label matchers retain matching values.
`mad_over_time` returns `NaN`, not `0`, when its range contains a NaN sample.
