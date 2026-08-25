# Outputs and Observability

## Metric representation

### Rate metrics use a labeled counter (since 1.3.0)

Exported Rate metrics are represented as one counter with a label whose values
are `zero` and `nonzero`. Downstream consumers must handle the labeled shape
instead of expecting separate or unlabeled Rate values.

### Correct Cloud Gauge extrema (since 1.8.0)

Cloud output v2 reports Gauge `min` and `max` in the correct fields. Queries no
longer return a peak as the floor or a floor as the peak. Revisit workarounds
that swapped the two fields.

### Native histograms (since 2.1.0)

The experimental `native-histograms` feature makes trend metrics use native
histograms. Enable it with `--features`, `K6_FEATURES`, or the `features`
configuration key. Feature selections appear in metric tags and are preserved
in archives and Cloud workers.

```sh
k6 run --features native-histograms script.js
```

## OpenTelemetry

### Stable output name (since 1.4.0)

Use the stable `opentelemetry` output. The old `experimental-opentelemetry`
name remains an alias but is deprecated. `K6_OTEL_EXPORTER_TYPE` is deprecated;
use `K6_OTEL_EXPORTER_PROTOCOL`.

```sh
k6 run --out opentelemetry script.js
```

### Rate fallback removed (since 2.0.0)

`K6_OTEL_SINGLE_COUNTER_FOR_RATE` has been removed. Delete it from environment
and deployment configuration; the single labeled-counter Rate representation
can no longer be postponed.

### HTTP Basic Auth (since 2.1.0)

The OpenTelemetry HTTP exporter accepts credentials through
`K6_OTEL_HTTP_EXPORTER_USERNAME` and `K6_OTEL_HTTP_EXPORTER_PASSWORD`, or the
`username` and `password` output configuration keys.

```sh
K6_OTEL_HTTP_EXPORTER_USERNAME=user \
K6_OTEL_HTTP_EXPORTER_PASSWORD=secret \
k6 run --out opentelemetry script.js
```

## Prometheus remote write

### Minimum TLS version (since 1.6.0)

The experimental Prometheus remote-write output defaults to TLS 1.3 and accepts
`K6_PROMETHEUS_RW_TLS_MIN_VERSION` to configure the minimum.

```sh
K6_PROMETHEUS_RW_TLS_MIN_VERSION=1.3 \
k6 run script.js -o experimental-prometheus-rw
```

## Console rendering

### Deep object logging (since 1.5.0)

`console.log()` traverses nested arrays and objects without dropping functions
or classes. Functions and classes render as `"[object Function]"`; circular
references are marked `"[Circular]"` instead of collapsing the whole value to
`[object Object]`.

### Binary values (since 1.6.0)

`console.log()` renders `ArrayBuffer` byte contents and shows typed-array types,
lengths, and values, including binary values nested in other objects.

## Browser and Cloud observability

### Redirect samples (since 1.8.0)

Each browser redirect emits request metrics only for its applicable hop; k6 no
longer re-emits all earlier redirect metrics at every hop.

### Filter browser failures (since 2.1.0)

Browser API failures in Grafana Cloud Logs carry `module=browser`, enabling
source-specific filters.

### Raw header byte accounting (since 2.2.0)

Browser sent/received byte metrics include raw header bytes. Header accessors
expose the wire values for the corresponding redirect hop, including
`Set-Cookie` and security headers.

### Local Cloud log streaming (since 2.2.0)

`k6 cloud run --local-execution` streams logs into the Cloud test run unless
`--no-cloud-logs` is set. Use secret storage and redaction when values might
reach the remote stream.

## Local visualization

### Bundled web dashboard (since 2.0.0)

The web dashboard ships in the k6 binary; a separate xk6-dashboard extension
is unnecessary.

```sh
k6 run --out=web-dashboard script.js
```
