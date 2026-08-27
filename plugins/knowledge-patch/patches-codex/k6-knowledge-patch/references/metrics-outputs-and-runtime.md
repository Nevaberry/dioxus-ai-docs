# Metrics, Outputs, and Runtime

## OpenTelemetry and Prometheus

### Account for the TLS floor

The experimental OpenTelemetry and Prometheus outputs default to TLS 1.3
(since 1.2.0). This was a minor-release breaking change because both outputs
were experimental.

The experimental Prometheus remote-write output later added
`K6_PROMETHEUS_RW_TLS_MIN_VERSION` to configure its minimum TLS version; its
default remains TLS 1.3 (since 1.6.0):

```sh
K6_PROMETHEUS_RW_TLS_MIN_VERSION=1.3 \
  k6 run script.js -o experimental-prometheus-rw
```

### Use the stable OpenTelemetry output name

The stable output is named `opentelemetry` (since 1.4.0). The
`experimental-opentelemetry` alias still works but is deprecated.
`K6_OTEL_EXPORTER_TYPE` is deprecated in favor of
`K6_OTEL_EXPORTER_PROTOCOL`:

```sh
k6 run --out opentelemetry script.js
```

### Authenticate the HTTP exporter

Set HTTP Basic Auth with `K6_OTEL_HTTP_EXPORTER_USERNAME` and
`K6_OTEL_HTTP_EXPORTER_PASSWORD`, or the `username` and `password` output
configuration keys (since 2.1.0):

```sh
K6_OTEL_HTTP_EXPORTER_USERNAME=user \
K6_OTEL_HTTP_EXPORTER_PASSWORD=secret \
k6 run --out opentelemetry script.js
```

## Metric schemas and output correctness

### Consume the labeled Rate shape

Exported Rate metrics use a single counter with a label whose values are
`zero` and `nonzero` (since 1.3.0). Downstream queries and integrations must
handle that labeled shape. In v2, `K6_OTEL_SINGLE_COUNTER_FOR_RATE` is removed,
so the migration can no longer be postponed (since 2.0.0).

### Use native histograms deliberately

The `native-histograms` feature makes trend metrics use experimental native
histograms (since 2.1.0). Enable it through `--features`, `K6_FEATURES`, or
configuration only when consumers support that representation:

```sh
k6 run --features native-histograms script.js
```

### Read Cloud Gauge extrema correctly

Cloud output v2 reports Gauge `min` and `max` in their correct fields (since
1.8.0). Queries no longer receive the peak as the floor or the floor as the
peak.

## gRPC

### Marshal special floating-point values

gRPC float values `NaN` and `Infinity` serialize as their string
representations instead of `null` (since 1.2.0). Existing scripts require no
change.

### Set authority

The gRPC module accepts the `authority` pseudo-header for services that require
it (since 1.2.0).

## Assertions

The URL-hosted `k6-testing` preview library provides `expect()` and
Playwright-style matchers for protocol and browser tests (since 1.2.0). It is
usable but preview coverage and matcher availability may be incomplete:

```javascript
import { expect } from 'https://jslib.k6.io/k6-testing/0.5.0/index.js';
import http from 'k6/http';

export default function () {
  expect(http.get('https://quickpizza.grafana.com/').status).toBe(200);
}
```

## Cryptography and one-time passwords

### Derive keys with PBKDF2

The crypto module supports PBKDF2 password-based key derivation (since 1.6.0).

### Generate and verify TOTP codes

The jslib TOTP package implements RFC 6238 generation and verification from a
base32 secret (since 1.6.0):

```javascript
import { TOTP } from 'https://jslib.k6.io/totp/1.0.0/index.js';

const totp = new TOTP('GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ', 6);
const code = await totp.gen();
const valid = await totp.verify(code);
```

## JavaScript runtime APIs

### Encode and decode text globally

`TextEncoder` and `TextDecoder` are globals in both init and VU contexts
(since 2.2.0):

```javascript
const encoded = new TextEncoder().encode('Hello, world!');
const decoded = new TextDecoder().decode(encoded);
```

### Write to WHATWG streams

`k6/experimental/streams` implements WHATWG-compatible `WritableStream` and
`WritableStreamDefaultWriter`, complementing readable streams (since 2.2.0):

```javascript
import { WritableStream } from 'k6/experimental/streams';

export default async function () {
  const stream = new WritableStream({ write: chunk => console.log(chunk) });
  const writer = stream.getWriter();
  await writer.write('hello');
  await writer.close();
}
```

## HTTP/2 compatibility

Under Go 1.27, k6 keeps VUs on HTTP/2, classifies connection and `GOAWAY`
errors consistently across Go versions, and preserves unknown HTTP/2 error
buckets (since 1.8.1).

## Runtime diagnostics

Nested logging preserves functions, classes, and circular-reference markers
(since 1.5.0). `ArrayBuffer` values and typed arrays include bytes, types,
lengths, and values even when nested (since 1.6.0). See
[CLI, Configuration, and Execution](cli-config-and-execution.md#logging-and-diagnostics)
for the precise render forms.
