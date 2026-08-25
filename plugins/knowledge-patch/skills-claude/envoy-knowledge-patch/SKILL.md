---
name: envoy-knowledge-patch
description: Envoy Proxy
version: 1.39.0
license: MIT
metadata:
  author: Nevaberry
---


# Envoy Proxy Knowledge Patch

Load this skill when changing Envoy configuration, extending Envoy, or
investigating behavior that may have shifted across recent releases.

Start with the upgrade notes below. Then open only the topic references needed
for the configuration or code under review.
## Reference index

| Reference | Topics |
| --- | --- |
| [Upgrades, builds, and operations](references/upgrades-build-and-operations.md) | Removed guards and extensions, build toolchains, process defaults, admin controls, workers, file watching |
| [HTTP routing and filters](references/http-routing-and-filters.md) | HTTP codecs, routing, matching, rewrites, filter chains, header mutation, compression, custom responses |
| [Authentication and security](references/authentication-and-security.md) | OAuth2, JWT, API keys, credentials, RBAC, identity metadata, hardening |
| [External processing and authorization](references/external-processing-and-authorization.md) | ext-proc, ext-authz, processor lifecycle, failure policies, mutations |
| [TLS, QUIC, and networking](references/tls-quic-and-networking.md) | TLS, certificates, QUIC, listeners, TCP, UDP, PROXY protocol, sockets, namespaces |
| [Discovery, DNS, and load balancing](references/discovery-dns-and-load-balancing.md) | xDS, SDS, RDS, resolvers, DNS caches, clusters, endpoints, host and LB selection |
| [Extensions, Lua, Wasm, and dynamic modules](references/extensions-lua-wasm-and-modules.md) | Extension APIs, Lua, Wasm, Go plugins, composite filters, native modules |
| [Observability and formatting](references/observability-and-formatting.md) | Access logs, formatters, tracing, metrics, taps, exporters, diagnostics |
| [Resilience, rate limits, and overload](references/resilience-rate-limits-and-overload.md) | Rate limits, retries, overload actions, resource monitors, health checks, outlier detection |
| [Application protocols and data filters](references/application-protocols-and-data-filters.md) | Redis, Valkey, PostgreSQL, MySQL, gRPC, GeoIP, Thrift, SSE, MCP |

## Upgrade blockers and irreversible migrations

### Do not rely on expired rollback guards

Many behavior changes initially shipped with runtime guards and later removed
their legacy paths. Before prescribing a rollback, check
[upgrades-build-and-operations.md](references/upgrades-build-and-operations.md)
for the guard's removal and then check the owning topic reference.

In particular:

- Explicit internal-address behavior became mandatory after its rollback guard
  was removed. Configure `internal_address_config`; do not assume RFC1918
  addresses are internal.
- The old HTTP/2 propagation, streaming-shadow, RDS normalization, xDS-copy,
  and empty-host dynamic-forward-proxy paths have also lost their rollback
  guards.
- OAuth2 cookie encryption can no longer be disabled with
  `envoy.reloadable_features.oauth2_encrypt_tokens`; only the filter's explicit
  trusted-environment plaintext mode remains.
- The old TCP-proxy idle-timer behavior is gone.

### Remove deleted extensions before startup

Configuration still naming a removed extension fails at load time.

- Replace the deleted `grpc_credentials/aws_iam` extension.
- Remove the contrib Squash HTTP filter.
- Remove OpenCensus tracing configuration.
- Review every removed-runtime-control list before copying old runtime files.

### Update source-build automation

- Build extension code as C++20.
- Use the supported compiler configurations instead of the removed
  `clang-libstdc++` setup.
- Use `--config=boringssl-fips` for FIPS builds.
- Bazel 8 source builds retain WORKSPACE mode only with
  `--enable_workspace --noenable_bzlmod`; account for the changed external
  runfiles layout.
- Treat `--config=openssl` as a constrained build: it disables HTTP/3 and is
  outside the stated security-policy coverage.

### Treat TLS enforcement as mandatory

Peer RSA certificate `keyUsage` is always enforced. The old
`enforce_rsa_key_usage` option is ignored, so fix incompatible certificates
instead of trying to turn validation off. Also account for TLS Inspector's
ClientHello version checks and the rejection of empty trusted-CA material.

## Security-critical configuration checks

### Migrate OAuth2 cookies in the safe order

For the AES-256-GCM migration:

1. Enable `envoy.reloadable_features.oauth2_use_gcm_encryption`.
2. Wait until every instance can read `gcm.` cookies.
3. Confirm `oauth_legacy_cbc_decrypt` has fallen to zero.
4. Disable `envoy.reloadable_features.oauth2_legacy_cbc_decrypt_compat`.

Reversing the order invalidates newly issued cookies. Leaving CBC fallback
enabled retains the vulnerable path. Review the full OAuth2 sequence in
[authentication-and-security.md](references/authentication-and-security.md).

### Bound dynamic-forward-proxy destinations

Use `DnsCacheConfig.resolved_address_filter` to remove disallowed CIDR ranges
from DNS answers. For defense in depth, apply the upstream RBAC filter after
host selection and default-deny unwanted `upstream_ip_port` values.

### Avoid disclosing transport failures

Do not restore upstream transport failure details to downstream response
bodies. Diagnose with `%UPSTREAM_TRANSPORT_FAILURE_REASON%` in controlled logs
instead.

### Recheck repeated-header policy

`HeaderMatcher` evaluates separately encoded header values individually.
CEL and generic matcher inputs still see comma-joined values. Audit policy
that depended on joined strings.

## High-impact default changes

### Size HTTP/2 explicitly

Safer HTTP/2 defaults cap concurrent streams at `1024`, the initial stream
window at `16MiB`, and the connection window at `24MiB`. Set intentional
values after measuring workload needs instead of retaining the temporary
legacy-default guard.

Cookie reassembly participates in request-header limits. A separate cookie
limit and an nghttp2 Rapid Reset token bucket are configurable.

### Review parser and protocol limits

- HTTP Inspector uses Balsa by default.
- JSON parsing is capped at 1,000 nesting levels.
- Oversized combined PROXY-protocol TLVs are removed.
- HTTP/3 pseudo-headers are validated.
- Strict HTTP/1 chunk parsing remains opt-in.

### Account for effective sampling

The tap filter and tap transport socket now honor `tap_enabled` before their
match predicate. OpenTelemetry tracing gives Envoy's request-entry decision,
including `overall_sampling`, precedence over incoming and tracer-level
sampling signals.

### Revalidate worker and socket sizing

Unset Linux worker concurrency considers hardware threads, CPU affinity, and
cgroup CPU limits. io_uring now applies default write-watermark backpressure.
Use worker CPU affinity and listener CPU-locality balancing only after checking
reuse-port and process-affinity assumptions.

## Common implementation recipes

### External processing

- Choose HTTP or gRPC transport intentionally.
- Select buffered, streamed, or `FULL_DUPLEX_STREAMED` body handling based on
  mutation and failure semantics.
- Set `failure_mode_allow`, `status_on_error`, and per-route overrides
  deliberately.
- Treat gRPC-client creation as a processor failure; fail-open no longer means
  silently ignoring startup failure.
- When chaining processors, account for state updates and `Content-Length`.

See [external processing and authorization](references/external-processing-and-authorization.md)
for lifecycle, local replies, processing effects, and network controls.

### External authorization

- Use per-route backend selection and retry policy where needed.
- Validate mutated request and response header limits.
- Bound denial bodies and decide whether denied headers may reach clients.
- Use shadow mode for evaluation without enforcement.
- For UDP, authorize when the session is created.

### Routing and request mutation

- Refresh route or cluster selection after writing routing-relevant filter
  state.
- Use body-aware on-demand recreation only when filters can replay safely.
- Apply formatter-backed host, path, redirect, and direct-response rewrites
  with explicit trust boundaries.
- Test matcher changes with dynamic metadata and repeated headers.
- When delaying TCP route selection, set early-data and drain behavior
  explicitly.

### DNS and cluster selection

- Prefer typed DNS-cluster configuration over deprecated direct cluster DNS
  fields.
- Recheck resolver inheritance when a DNS cache or filter has empty local
  resolver configuration.
- Use DNS-layer address filtering plus post-selection authorization for
  dynamic destinations.
- Expect EDS hostname-only changes to recreate hosts and drain pools.
- Use `refresh_cluster_on_retry` only when a dynamically selected cluster can
  safely change between attempts.

### Native dynamic modules

Check extension-family and callback coverage before implementing a module.
Loading supports local paths and digest-verified remote artifacts; cache
misses and fetch failures differ. Validate callback signatures and isolation.

Use
[extensions-lua-wasm-and-modules.md](references/extensions-lua-wasm-and-modules.md)
for request, worker, listener, network, bootstrap, load-balancer, transport,
health-check, formatter, stats-sink, and filter-state APIs.

### Rate limiting and overload

- `timeout: 0s` means no timeout for HTTP rate limit and ext-authz.
- A local token bucket with `max_tokens: 0` rejects every match.
- Negative hits refill budget; shadow mode evaluates without enforcing.
- Retry budgets can include requests from a configured interval.
- Fixed-heap maximums can be runtime-adjusted.
- Treat connection-pool, HTTP/2 dispatch, stream flush, idle HTTP/3, and
  high-watermark closures as separate load-shed mechanisms.

## Diagnostic workflow

1. Identify the owning subsystem and open its reference from the index.
2. Search the exact field, extension name, formatter, runtime guard, or stat.
3. If a guard is suggested, verify it was not removed in the upgrade
   reference.
4. Separate default changes from opt-in features and disabled-by-default
   guards.
5. For extensions, check both configuration API changes and callback ABI
   changes.
6. For traffic-policy changes, test request, response, retry, local-reply, and
   stream-close paths independently.
7. For security migrations, stage changes so every instance can read both old
   and new state before disabling compatibility.
8. Prefer observability fields and counters over exposing diagnostic details
   to downstream clients.

## Configuration review checklist

- Removed fields, extensions, and runtime guards are absent.
- TLS secrets are non-empty and key usage is compatible.
- OAuth2 redirect domains, cookie attributes, token forwarding, and encryption
  migration state are explicit.
- Dynamic destinations are constrained before and after DNS resolution.
- Header-count, header-size, cookie, body, metadata, and JSON-depth limits are
  intentional.
- ext-proc and ext-authz failure, timeout, retry, and shadow behavior are
  explicit.
- Route-cache or route-cluster refresh occurs after relevant state mutation.
- Listener namespaces, socket options, keepalive, and connection watermarks
  match the deployment platform.
- Load-shed actions have corresponding metrics and capacity tests.
- Access logs avoid secrets while retaining controlled transport and identity
  diagnostics.
