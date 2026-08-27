# Migrations and Compatibility

## Release and API guarantees

### Semantic Versioning (since 1.0.0)

k6 follows Semantic Versioning. Breaking changes are confined to major
releases and receive deprecation warnings in advance. Each major receives
critical fixes for at least two years, and k6 delineates the supported public
API surface for extensions and integrations. Treat undocumented Go internals
as outside that support guarantee.

### Stable core modules (since 1.0.0)

`k6/browser`, `k6/net/grpc`, and `k6/crypto` are stable and suitable for
production use.

## v2 removals

### Live test control (since 2.0.0)

The `externally-controlled` executor and the `k6 pause`, `resume`, `scale`, and
`status` commands have been removed without replacements. A script using that
executor will not start. Choose an executor such as `ramping-vus`,
`constant-vus`, or `constant-arrival-rate`.

### Extension and Cloud migration surface (since 2.0.0)

For a complete v2 migration, also verify these topic-specific changes:

- Go imports use `go.k6.io/k6/v2` and extension JSON handling uses
  `encoding/json`.
- Cloud commands are explicit, Cloud options live under `options.cloud`, and
  the old `loadimpact` configuration path is not read.
- The local HTTP API is opt-in, and aborted Cloud runs exit with status `97`.
- The old OpenTelemetry Rate fallback and extension-provisioning environment
  switches are removed.

See the corresponding extension, CLI, and output references for the exact
commands and environment variables.

## Build toolchain

### Go requirements by line

- Since 1.4.0, building k6 requires Go 1.24 or newer.
- Since 1.7.0, building k6 requires Go 1.25 or newer, and the default build
  toolchain is Go 1.26.

Use the requirement associated with the k6 line being built. Release binaries
may use a newer toolchain than the minimum accepted for source builds.

## Containers

### Numeric runtime user (since 1.1.0)

The container image selects numeric UID `12345` rather than the named `k6`
user. Kubernetes workloads no longer need to set `runAsUser` merely to resolve
the image's configured user, but volume ownership and security policy should
still permit UID `12345`.

### Major-line image selection (since 2.0.0)

Prereleases and maintenance releases from older major lines do not update
Docker `:latest`. Floating tags such as `grafana/k6:v1` track a selected major
line. Pin a full image version for deterministic CI and deployments.

## HTTP compatibility

### Extra argument warnings (since 1.8.0)

`http.get()` and `http.head()` warn when extra positional arguments are
provided. The extra values remain ignored, but the warning identifies a call
whose arguments do not match the supported signature; correct the call rather
than suppressing the warning.

### HTTP/2 under Go 1.27 (since 1.8.1)

When built with Go 1.27, k6 keeps VUs on HTTP/2, classifies connection and
`GOAWAY` errors consistently with other Go versions, and preserves unknown
HTTP/2 error buckets.

## Experimental-output compatibility

### TLS 1.3 default (since 1.2.0)

The experimental OpenTelemetry and Prometheus outputs default to TLS 1.3. This
was a minor-release breaking change because the outputs were experimental.
Legacy endpoints may require an explicit output-specific minimum-TLS setting
where one is available.
