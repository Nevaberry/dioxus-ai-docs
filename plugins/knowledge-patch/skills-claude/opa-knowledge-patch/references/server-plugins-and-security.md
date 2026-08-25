# Server, Plugins, and Security

Use this reference for server network behavior, security fixes, runtime
configuration, REST and bundle plugins, cloud credentials, TLS, shutdown, and
container resource handling.

## Network and HTTP behavior

### Bind non-loopback addresses explicitly (`1.0-migration`)

`opa run --server` binds to localhost instead of every interface. A service
that must be reached from its host, another container, or a remote client needs
an explicit address:

```sh
opa run --server --addr 0.0.0.0:8181
```

### Update outbound `User-Agent` filters (`1.18.0`)

All outbound HTTP traffic—including bundle, discovery, decision-log, status,
`http.send`, and AWS KMS/ECR requests—uses a valid product token:

```text
User-Agent: Open-Policy-Agent/<version> (<os>, <arch>)
```

Update WAF rules, log filters, and other exact matchers that expect
`Open Policy Agent/<version>`.

### Account for the request-header deadline (`1.19.0`)

Every OPA HTTP server sets `ReadHeaderTimeout` to 32 seconds. A client or
intermediary that takes longer to transmit request headers can be disconnected.

## Configuration and lifecycle

### Honor the runtime Rego mode for REST uploads (`1.0.0`)

Policies uploaded through the REST Policy API use the runtime's configured
Rego version. API-loaded policy and file-loaded policy therefore follow the
same v0 or v1 mode.

### Handle bundle trigger errors at the call site (`1.0.0`)

The bundle plugin trigger method returns errors directly. Integrations can and
should handle trigger failures where the trigger is invoked.

### Bound status-plugin shutdown (`1.5.0`)

The status plugin supports a graceful-shutdown timeout. Configure it when
shutdown must complete within a known bound.

### Validate bundle polling intervals (`1.12.0`)

The bundle plugin validates polling intervals, preventing a bad configuration
from causing nanosecond-scale polling.

### Surface unknown options (`1.19.0`)

OPA warns about unrecognized configuration options instead of silently
ignoring them. Intentionally extensible sections remain exempt. Go embedders
using `config.ParseConfig` can inspect the same messages in `Config.Warnings`.
Review startup warnings so a typo such as `decision_log` instead of
`decision_logs` is not missed.

### Preserve custom build provenance (`1.5.0`)

The runtime keeps user-supplied `commit` and `timestamp` fields in version
information instead of overwriting them.

## REST credentials and TLS

### Use AWS SSO credentials (`1.5.0`)

OPA REST plugins can source AWS credentials from AWS SSO. Deployments no
longer need to substitute another credentials provider solely because the REST
plugin could not consume SSO credentials.

### Sign Azure client assertions in Key Vault (`1.5.0`)

REST clients can have Azure Key Vault sign client assertions, allowing signing
keys to remain in the vault rather than being loaded into OPA.

### Move per-request HTTP auth to `Prepare` (`1.15.0`)

`HTTPAuthPlugin.NewClient()` runs once for each `Client` and is cached. Move
request counters, transport wrapping, logging and metric side effects, and any
other per-request authentication work into `Prepare()`; otherwise it runs only
once.

### Control client-certificate reloads (`1.15.0`)

REST plugins expose `cert_reread_interval_seconds`. The backward-compatible
default rereads client certificates on every request. REST TLS settings also
inherit the server's configured minimum TLS version and cipher suites.

### Sign AWS requests with web identity (`1.15.0`)

REST-plugin AWS signing supports service-account Web Identity credentials when
obtaining Assume Role credentials.

## Resource use and input bounds

### Reject excessive parser recursion (`1.5.0`)

The parser has a recursion-depth guard. Handle a parse error for excessively
nested input rather than assuming arbitrary nesting depth succeeds.

### Honor container CPU and memory limits (`1.18.0`)

OPA automatically derives `GOMAXPROCS` from container-aware CPU limits and
`GOMEMLIMIT` from container-aware memory limits. Include these selected limits
when sizing or diagnosing container deployments.

## Security and patched artifacts

### Close Data API path injection (`1.4.0`)

OPA 1.4.0 fixes CVE-2025-46569 in earlier standalone-server releases. The
issue applies when attacker-controlled text reaches a Data API HTTP path: the
injected Rego can redirect the requested path, force success or failure, or
consume excessive compute. Exposure includes authorization policies that do
not exactly match `input.path` and intermediaries that put unsanitized
third-party text into the path. Upgrade exposed standalone servers.

### Recognize `rego_v1` in v0 capabilities (`1.4.0`)

Capabilities generated for `--v0-compatible` include the `rego_v1` feature.
Consumers inspecting capability metadata must not assume that v0 compatibility
excludes it.

### Use the complete patched 1.4 release (`1.4.0`)

OPA 1.4.1 updates Go to 1.24.2 for CVE-2025-22870 and CVE-2025-22871, but
omits `capabilities/v1.4.1.json`. Version 1.4.2 restores the capability file.
Tooling that consumes versioned capability files should move directly to
1.4.2.

### Choose fixed 1.16 and 1.17 point releases (`1.17.0`)

OPA 1.16.0 restores bundle-download, `print()`, and other plugin-originated
logs that 1.15.x dropped, but its plugin manager can hang during shutdown.
Version 1.16.1 fixes the shutdown regression.

For the 1.17 line, use 1.17.1 distributed binaries or images. Its Go 1.26.4
toolchain fixes standard-library vulnerabilities exercised through the HTTP
handler and crypto built-ins. Self-built artifacts depend on their chosen Go
version.

### Fix the annotation memory leak (`1.18.0`)

OPA 1.18.1 fixes an `AnnotationSet` memory leak introduced in 1.17.0. Upgrade
long-running servers with excess memory use instead of remaining on 1.18.0.

## Authentication token performance

### Configure JWT token caching (`1.1.0`)

The `io.jwt` token-verification built-ins support a configurable token cache.
Repeated verification workloads can trade additional cache memory for less
verification work.
