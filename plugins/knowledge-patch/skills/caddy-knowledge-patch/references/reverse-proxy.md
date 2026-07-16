# Reverse proxy

## Upstream request identity

### HTTPS upstream `Host`

Since 2.11.1, `reverse_proxy` automatically sets `Host` to `{upstream_hostport}` for HTTPS upstreams. The formerly common line `header_up Host {upstream_hostport}` is redundant.

```caddyfile
reverse_proxy https://backend.example.com
```

If an upstream intentionally requires a different virtual host, override `Host` explicitly. Do not assume that the downstream request's original host is preserved for an HTTPS upstream.

### Standard proxy metadata

Since 2.10.0, Caddy sets the standard `Via` request header instead of adding a duplicate `Server` header. Update upstream routing, loop detection, tests, and log parsing that previously inspected the duplicate `Server` value.

## Active health checks

Since 2.9.0, active checks can use:

- an HTTP method, exposed in the Caddyfile as `health_method`;
- a distinct health-check destination, exposed as `health_upstream`;
- a request body;
- headers containing placeholders for the target host and network address; and
- an HTTP transport bound to a chosen outbound source address.

```caddyfile
reverse_proxy app:8080 {
	health_uri /healthz
	health_method HEAD
	health_upstream health.internal:8081
}
```

In the 2.11 line, `health_port` is honored by active checks. This matters when service traffic and health probes use different ports.

## Dynamic upstream health

As of 2.11.2, dynamic upstreams are tracked and can participate in passive health checking. Later 2.11 releases can also clear the dynamic-upstream cache while retrying, allowing a retry to rediscover destinations rather than repeatedly using a stale result.

When combining dynamic discovery with health checks, align discovery TTLs, failure windows, and retry duration so an unhealthy cached destination does not occupy the entire retry budget.

## Load balancing and stickiness

- Sticky-cookie load balancing gains a cookie `Max-Age` setting (since 2.9.0).
- `weighted_round_robin` accepts zero weights (since 2.9.0). A zero-weight upstream remains in configuration but is not selected, which supports temporarily parked destinations.
- `{http.reverse_proxy.retries}` exposes the number of retries to downstream handlers and logs (since 2.9.0).
- The 2.11 line adds `lb_retry_match`, which can decide retry eligibility from a response status.

Do not give every upstream weight zero. Use response-based retries only for requests whose semantics and body can safely be repeated.

## Retry behavior and request bodies

The 2.11 line preserves request bodies across dial-failure retries. Later releases in the line can refresh dynamic upstreams during retry and configure the stream-copy buffer size.

Fully buffered proxy request bodies receive `Content-Length` since 2.9.0. If a handler replaces the body with `request_body set`, Caddy also recalculates the length.

Retries can amplify writes. Constrain them with request matchers, idempotency guarantees, upstream-aware retry eligibility, and a finite duration or attempt policy.

## HTTP transports and protocol behavior

### TLS server names with placeholders

Since 2.10.0, an HTTP transport correctly establishes TLS when its configured server name contains a runtime placeholder. Ensure the expanded name is both the intended verification name and covered by the upstream certificate.

### TCP keepalive

As of 2.10.1, reverse-proxy transports use Go's keepalive configuration for their probe interval. A negative interval disables TCP keepalives. The same keepalive mechanism applies to accepted server sockets; server-side controls are described in [Server operations](server-operations.md).

### WebSockets over HTTP/2

Since 2.9.0, WebSocket requests and responses are rewritten for WebSockets carried by HTTP/2 extended CONNECT. Avoid header rewrites that undo the protocol conversion.

### Stream-copy buffering

Later 2.11 releases make the stream-copy buffer size configurable. Treat it as a per-active-stream memory tradeoff: increasing it may improve throughput but multiplies memory use with concurrency.

## FastCGI behavior and hardening

FastCGI requests are buffered by default as of the 2.9.1 fixes accompanying the 2.9.0 line. Security-sensitive changes then tighten execution and path handling:

- 2.11.1 split-path handling accounts for Unicode case-fold length changes.
- 2.11.3 tightens which FastCGI files may be executed.

Do not use permissive path splitting as the only guard around script execution. Resolve the intended script root, use restrictive file matching, and test Unicode and encoded-path cases.

## Forwarded client identity

### Trusted Unix-socket proxies

The 2.11 line adds `trusted_proxies_unix`, allowing `X-Forwarded-*` values to be trusted when a request arrives through a Unix socket. The same line corrects forwarded-header processing for these connections.

### Strict proxy-chain parsing

With trusted network proxies, normal parsing scans forwarded IPs from left to right. `trusted_proxies_strict` scans right to left and selects the first untrusted hop, which is safer for proxies that append to `X-Forwarded-For`.

```caddyfile
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```

When multiple `client_ip_headers` are configured, the first non-empty header wins. The `private_ranges` shortcut includes IPv4 and IPv6 loopback ranges as well as private networks.

Only trust a socket path or address range when untrusted processes cannot inject traffic through it. Listener-level PROXY protocol handling has a separate trust boundary covered in [Server operations](server-operations.md).

## Early data reaching an upstream

Since 2.9.0, a proxied QUIC 0-RTT request includes `Early-Data`. Upstreams should reject or specially handle replayable non-idempotent requests. IP matchers refuse early data, and server configuration in the 2.11 line can disable 0-RTT entirely.

## Transport extension points

The 2.11 line adds interfaces through which reverse-proxy transport modules can modify transport behavior. Core also gains modular `network_proxy` support since 2.10.0. These are extension APIs, not Caddyfile directives; custom modules should provision and validate their behavior explicitly.
