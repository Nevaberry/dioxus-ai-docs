---
name: envoy-knowledge-patch
description: Envoy Proxy
version: 1.39.0
license: MIT
metadata:
  author: Nevaberry
---


# Envoy Proxy Knowledge Patch

Use this skill when writing, reviewing, upgrading, or debugging Envoy bootstrap,
xDS resources, listeners, clusters, routes, filters, protocol proxies, or native
extensions. Start with the project manifest, image tag, build configuration, and
runtime values; then apply only guidance relevant to the deployed version.

## Reference index

| Reference | Topics |
| --- | --- |
| [Upgrade and compatibility](references/upgrade-and-compatibility.md) | Removed guards and extensions, changed defaults, source builds, validation and SDK migrations |
| [HTTP, routing, and filters](references/http-routing-and-filters.md) | HTTP behavior, ext-proc, route matching and mutation, rate limits, compression and responses |
| [Security, authentication, and TLS](references/security-auth-and-tls.md) | TLS and certificates, OAuth2, ext-authz, RBAC, JWT, API keys and cloud credentials |
| [Discovery, DNS, and load balancing](references/discovery-dns-and-load-balancing.md) | xDS, DNS, dynamic forward proxy, clusters, endpoints, load balancing and retries |
| [Networking and protocol proxies](references/networking-and-proxies.md) | Listeners, sockets, TCP, UDP, QUIC, PROXY protocol, Redis, PostgreSQL, MySQL and tunnels |
| [Observability and operations](references/observability-and-operations.md) | Access logs, tracing, metrics, tap, overload management and admin diagnostics |
| [Extensions and programmability](references/extensions-and-programmability.md) | Dynamic modules, Wasm, Lua, CEL, filter state, composite filters and extension APIs |
| [Data and protocol-aware filters](references/data-and-protocol-filters.md) | MCP, gRPC/JSON, Proto Scrubber, Thrift, GeoIP, metadata, SSE and file serving |

## Upgrade triage

Before changing configuration, identify the exact Envoy binary and whether it is
a standard, contrib, mobile, FIPS, OpenSSL, or custom extension build. Runtime
guards are temporary migration tools: verify that a named guard still exists in
the target binary before relying on it.

Check these high-impact behaviors first:

- Configure `internal_address_config`; RFC1918 space is not implicitly internal,
  and the old rollback guard has been removed.
- Treat RSA certificate `keyUsage` enforcement as mandatory. The
  `enforce_rsa_key_usage` setting is deprecated and ignored.
- Expect TLS Inspector to accept only ClientHello versions from TLS 1.0 through
  TLS 1.3 unless its temporary rollback guard is deliberately disabled.
- Expect HTTP Inspector to use Balsa, and expect `HeaderMatcher` to evaluate
  separately encoded header values individually.
- Budget for the safer HTTP/2 defaults: 1,024 concurrent streams, a 16 MiB
  initial stream window, and a 24 MiB initial connection window.
- Account for reassembled HTTP/2 cookies in request-header limits and configure
  the optional cookie-size and reset-rate controls where needed.
- Expect JSON nesting to stop at 1,000 levels and overlong combined
  PROXY-protocol TLVs to be removed.
- Expect upstream transport failure details to remain available to logging but
  not to be disclosed in HTTP response bodies.
- Expect `tap_enabled` runtime fractions to be enforced by HTTP and transport
  tap before their match predicates.
- Review the upgrade reference for removed runtime guards before carrying an
  old emergency rollback into a new deployment.

## TLS and authentication quick reference

For certificate and identity changes:

- Upstream and downstream TLS can fetch certificates on demand through SDS.
  Active health checks wait for required upstream TLS secrets while warming.
- Empty trusted-CA sources are rejected. SPIFFE trust bundles take precedence
  over `trust_domains`, and watched directories support atomic replacement.
- Brotli certificate compression is disabled by default: QUIC uses zlib only,
  while TCP TLS uses no certificate compression unless the guard is enabled.
- Use `connection.peer_certificate_valid` to distinguish a validated peer from
  an untrusted certificate accepted by optional mTLS.
- Use `%UPSTREAM_SERVER_NAME%`, `%DOWNSTREAM_TLS_GROUP%`, and
  `%UPSTREAM_TLS_GROUP%` when SNI and negotiated-group diagnostics are needed.
- `suppress_client_ca_list` hides trusted CA names in `CertificateRequest`
  without changing certificate validation.

For OAuth2 deployments, treat cookie changes as migrations:

- Token cookies are encrypted unless `disable_token_encryption` is explicitly
  set for a trusted environment.
- Migrate the CVE-2026-47775 cookie format by enabling AES-256-GCM everywhere,
  waiting until all instances read `gcm.` cookies and
  `oauth_legacy_cbc_decrypt` reaches zero, then disabling CBC compatibility.
- Do not reverse those two steps: older instances cannot read newly issued GCM
  cookies, while indefinite CBC fallback preserves the vulnerable path.
- `TLS_CLIENT_AUTH` requires mTLS on the token-endpoint cluster and does not use
  `token_secret`; `PRIVATE_KEY_JWT` uses the PEM key in `token_secret`.
- Constrain formatter-derived redirects with `allowed_redirect_domains`.
- `forward_id_token` strips the chosen incoming custom header before inserting
  the validated token, preventing client spoofing.

For policy composition:

- Basic Auth with `allow_missing: true` passes requests lacking credentials for
  OR-composition, but still rejects invalid credentials.
- `emit_dynamic_metadata: true` publishes the authenticated Basic username at
  `envoy.filters.http.basic_auth` for RBAC and later filters.
- Upstream RBAC runs after host selection but before connection, enabling
  default-deny policy over `upstream_ip_port` for SSRF defense.
- Dynamic forward proxy can filter resolved addresses by CIDR with
  `resolved_address_filter` before connecting.
- Extract-only JWT mode can set `verification_status_header` to `false` only
  when an extracted token fails signature verification; valid and absent tokens
  leave the header unset.

## HTTP and routing quick reference

- Route and redirect host/path rewrites accept substitution formatting; mixed
  literal and variable URI-template segments are supported.
- `HeaderMatcher` consumers see repeated encoded values individually, while CEL
  and generic matcher header inputs still see comma-joined values.
- Route-level request-body buffer limits take effect as soon as the route
  matches. Async retries are skipped when their retry buffer limit is exceeded.
- `refresh_cluster_on_retry` can refresh a dynamically selected route cluster
  for each attempt, including weighted-cluster routes.
- A local-rate-limit bucket with `max_tokens: 0` rejects every matching request
  without requiring a fill interval.
- Retry-budget `budget_interval` counts recent new requests in the budget; its
  `0ms` default retains the old calculation.
- The bandwidth-share filter divides request and response bandwidth among
  weighted tenants and supports filter-chain and per-route limits.
- The HTTP filter-chain filter hosts named subchains in one main-chain slot and
  permits per-route selection.
- Custom-response matching can inspect request properties as well as response
  status and headers, and redirect paths can use formatter or CEL output.

For external processing:

- If ext-proc cannot create its gRPC client, it reports `INTERNAL` and follows
  `failure_mode_allow`; the same policy governs spurious responses.
- Multiple ext-proc filters can coexist when state-update data injection is
  enabled, and `allow_content_length_header` controls preservation or mutation
  of the original length.
- Network external processing can close its side stream early with
  `close_stream_to_ext_proc_server`, letting later traffic bypass the filter.
- Use the HTTP reference for processing-mode overrides, streamed body modes,
  local replies, error statuses, request modifiers, metadata and logging effects.

## Discovery and traffic selection quick reference

- The merged strict/logical DNS-cluster implementation is enabled by default;
  use its rollback guard only as a temporary migration aid.
- Identical c-ares configurations share a resolver. `qcache_max_ttl` caps cached
  entries, while `0` keeps qcache disabled.
- `DnsCluster.dns_min_refresh_rate` floors refresh intervals derived from short
  TTLs, and dynamic-forward-proxy subclusters can use explicit DNS-cluster
  settings through `sub_clusters_config.dns_cluster_config`.
- EDS hostname-only changes recreate the host and drain its connection pools so
  settings such as `auto_host_sni` observe the new value.
- Static-route VHDS now sends subscriptions and supports on-demand operation.
- Removing an RTDS override restores a process-wide guard to its underlying
  value rather than leaving the override behind.
- Client-side weighted round robin can consume out-of-band ORCA
  `StreamCoreMetrics`, including through a sidecar selected by transport-socket
  match criteria.
- `Endpoint.observability_name` disambiguates endpoint statistics when multiple
  endpoints share an address.

## Extension quick reference

Dynamic modules now cover HTTP, network, listener, UDP listener, bootstrap,
access logging, load balancing, clusters, transport sockets, certificate
validation, health checking, tracing, matching, formatters and stats sinks.

- Local modules can load from an absolute `.so` path; remote modules require a
  SHA-256 digest and cache by digest.
- A remote module fetch normally fails open by omitting the filter;
  `nack_on_cache_miss` rejects an uncached configuration while fetching in the
  background.
- The extended ABI supports an SDK-built module across the next Envoy release,
  but extension callback signatures still require source-level migration when
  noted in the extension reference.
- `metrics_namespace` controls the Prometheus prefix. Configuration-load failure
  counters remain available even when a listener update is rejected.
- Worker slots and events let a module publish opaque main-thread state to every
  worker, and registered factories allow typed filter-state exchange.
- The Rust SDK `CatchUnwind` wrapper can convert callback panics into fail-closed
  request, stream, or connection errors instead of aborting the process.

For Wasm, do not depend on listener metadata to isolate otherwise identical
downstream plugin configurations. Use distinct plugin names, root IDs, or VM IDs.
Upstream HTTP Wasm metrics use server-wide root scope by default, and changing
only VM environment variables now recreates the VM.

## Operations quick reference

- `/peak_heap_dump` exposes the TCMalloc peak profile, while `/memory/tcmalloc`
  exposes allocator diagnostics.
- `--log-stacktrace-single-entry` preserves a stack trace as one event, and `%N`
  inserts the Envoy version into spdlog patterns.
- The fixed-heap monitor can take its maximum from
  `max_heap_size_bytes_runtime`, so RTDS or `/runtime_modify` can adjust it.
- `enable_worker_cpu_affinity` pins Linux workers; with reuse-port,
  `cpu_locality_balance` can steer accepts to the worker on the receiving CPU.
- io_uring writes now apply backpressure at 128 KiB and resume at 16 KiB by
  default; explicit high and low watermarks can override those values.
- `WatchedDirectory.watch_modify: true` also reacts to in-place `IN_MODIFY`
  writes, including direct certificate-file rotation; rename-only watching
  remains the default.

## Review checklist

When producing or reviewing a change:

1. Confirm the deployed binary variant and exact version.
2. Search the upgrade reference for every runtime guard, deprecated field, and
   removed extension used by the existing configuration.
3. Inspect defaults that affect protocol limits, security checks, sampling,
   retries, timeouts, buffers, cookies and connection draining.
4. Validate bootstrap and dynamic resources with the target binary; validation
   mode now instantiates bootstrap extensions needed by dependent configuration.
5. Confirm that formatter names, filter-state keys, metadata namespaces, and
   per-route overrides match their current consumers.
6. Exercise failure paths: xDS removal, DNS failure, certificate absence,
   ext-proc startup failure, auth denial, overload pressure and retry exhaustion.
7. Verify observability after rollout, especially counters whose attribution or
   scope changed and sampling controls that are now enforced.
