# Migration and Compatibility

## Compatibility policy

k6 follows Semantic Versioning: breaking changes occur only in major releases
and receive advance deprecation warnings (since 1.0.0). Each major receives
critical fixes for at least two years, and the supported public API for
extensions and integrations is explicitly delineated.

## Build toolchains

Building k6 requires Go 1.24 or newer from 1.4.0. From 1.7.0, the minimum is
Go 1.25 and the default toolchain is Go 1.26. Pin the toolchain to the k6 line
being built rather than applying the newest requirement to an older branch.

## Script and execution migration

### Replace removed live control

The v2 line removes the `externally-controlled` executor and the `k6 pause`,
`resume`, `scale`, and `status` commands (since 2.0.0). There are no direct
replacements. Choose an executor such as `ramping-vus`, `constant-vus`, or
`constant-arrival-rate`; scripts that keep `externally-controlled` do not
start.

### Opt in to the HTTP API

The v2 HTTP API does not listen on `localhost:6565` by default (since 2.0.0).
Enable it explicitly with `--address` or `K6_ADDRESS`:

```sh
k6 run --address=localhost:6565 script.js
```

## Cloud migration

### Replace removed commands and options

The v2 CLI removes top-level `k6 login`, positional `k6 cloud script.js`, and
`--upload-only` (since 2.0.0). Use `k6 cloud login`, `k6 cloud run`, and
`k6 cloud upload`. Supply InfluxDB credentials through `K6_INFLUXDB_*`
variables rather than `k6 login influxdb`.

Move `options.ext.loadimpact` fields to `options.cloud`; the old namespace is
not accepted in v2 (since 2.0.0).

### Update CI exit handling

A v2 Cloud run aborted by the system, a limit, a script error, the user, or a
timeout exits `97` rather than `0` (since 2.0.0). Success stays `0` and a
threshold abort stays `99`.

### Decide whether to use Cloud secrets

In v2, local Cloud execution enables the built-in Cloud secret source unless
`--no-cloud-secrets` is passed (since 2.0.0). On the maintained v1 line, that
implicit source was later disabled by default (since 1.8.1). Make the desired
source explicit in cross-major automation.

## Configuration paths

The v2 line no longer reads, migrates, or falls back to
`{USER_CONFIG_DIR}/loadimpact/config.json` (since 2.0.0). Move the file to
`{USER_CONFIG_DIR}/k6/config.json` or regenerate it with `k6 cloud login`.

## Output and metric migration

### Remove the Rate fallback

Delete `K6_OTEL_SINGLE_COUNTER_FOR_RATE`; it is removed in v2 (since 2.0.0).
Consumers must accept the single Rate counter labeled with `zero` and
`nonzero`.

### Replace deprecated output names

Use `opentelemetry` instead of `experimental-opentelemetry`, and use
`K6_OTEL_EXPORTER_PROTOCOL` instead of `K6_OTEL_EXPORTER_TYPE` (since 1.4.0).

### Replace browser FID

Move thresholds and integrations from `browser_web_vital_fid` to
`browser_web_vital_inp`; FID was planned for removal in v2 (since 1.3.0).

## Extension migration

### Update Go imports

The v2 Go module path is `go.k6.io/k6/v2` (since 2.0.0). Update every k6 import
in extensions and external Go packages:

```go
import "go.k6.io/k6/v2/js/modules"
```

### Replace generated JSON methods

Public v2 k6 Go types no longer provide easyjson-generated `MarshalJSON` and
`UnmarshalJSON` methods (since 2.0.0). Use standard `encoding/json` marshaling.

### Remove provisioning switches

Delete `K6_BINARY_PROVISIONING` and `K6_ENABLE_COMMUNITY_EXTENSIONS`; both are
removed in v2 (since 2.0.0). Community extensions use the default build
service. `K6_AUTO_EXTENSION_RESOLUTION` is needed only to turn automatic
resolution off.

### Preserve archive dependencies

The v2 archive format records pre-manifest `k6/x/` constraints in the
`dependencies` field of `metadata.json` (since 2.0.0). Provisioned `k6 x`
commands receive `K6_PROVISION_HOST_VERSION`, enabling compatibility decisions
based on the invoking host.

## Module deprecations

- Replace `k6/experimental/redis` with the official Redis extension (since
  1.5.0).
- Replace `k6/experimental/websockets` with `k6/websockets`; the API is
  unchanged (since 1.6.0).
- Treat the URL-hosted `k6-testing` assertion library as preview, with possibly
  incomplete matchers and coverage (since 1.2.0).

## Distribution and dashboard migration

The web dashboard is part of the v2 binary and runs with
`k6 run --out=web-dashboard`; remove the separate xk6-dashboard dependency
(since 2.0.0).

Prereleases and maintenance releases from older majors no longer update
Docker `:latest` or GitHub's latest-release marker in the v2 release scheme.
Use floating `:vN` tags such as `grafana/k6:v1` to follow a selected major, or
pin an exact image for reproducibility (since 2.0.0).
