---
name: caddy-knowledge-patch
description: Caddy
license: MIT
version: "2.11.1"
metadata:
  author: Nevaberry
---

# Caddy Knowledge Patch

Baseline: Caddy through 2.8.x. Covered range: 2.9.0, 2.10.0, 2.11.1 and later 2.11 fixes, plus the `automatic-https` and `global-and-tls-options` topic batches.

Use this patch when writing or reviewing Caddyfile or JSON configuration, upgrading Caddy, building custom binaries, or operating Caddy's HTTP, proxy, certificate, and telemetry features.

## Reference index

| Reference | Topics |
| --- | --- |
| [HTTP and Caddyfile](references/http-and-caddyfile.md) | Imports, matchers, placeholders, headers, bodies, encoding, file serving, authentication, and security behavior |
| [Reverse proxy](references/reverse-proxy.md) | HTTPS upstreams, health checks, retries, load balancing, transports, FastCGI, trusted proxies, and forwarding |
| [Automatic HTTPS and ECH](references/automatic-https-and-ech.md) | Activation, redirects, ACME, issuers, On-Demand TLS, shared storage, local HTTPS, ECH, and wildcard selection |
| [TLS and PKI](references/tls-and-pki.md) | Handshake policies, certificate selection, client authentication, trust pools, internal PKI, renewal, CA pools, and diagnostics |
| [Server operations](references/server-operations.md) | Global server options, listeners, protocols, timeouts, socket activation, admin API, shutdown, storage, and runtime limits |
| [Observability and extensions](references/observability-and-extensions.md) | Logs, metrics, tracing, CLI changes, build requirements, embedding, and module APIs |

## Upgrade hazards and breaking behavior

### Remove obsolete TLS storage rate limits

Caddy 2.9.0 removes the deprecated TLS JSON fields `rate_limit` and `burst`. Delete them before loading an older configuration in 2.9 or newer.

### Update wildcard automation policy

Caddy 2.10.0 automatically prefers a managed wildcard certificate for covered subdomains and removes the experimental global `auto_https prefer_wildcard` option introduced in 2.9. To force a separate certificate for the literal site name, configure the site with:

```caddyfile
foo.example.com {
	tls force_automate
}
```

### Account for HTTPS upstream Host rewriting

Since 2.11.1, an HTTPS `reverse_proxy` sets `Host` to `{upstream_hostport}` automatically. Remove redundant `header_up Host {upstream_hostport}` lines. Explicitly override `Host` if the upstream intentionally needs a different value.

```caddyfile
reverse_proxy https://backend.example.com
```

### Expect `Via`, not a duplicate `Server`

Since 2.10.0, the reverse proxy emits the standard `Via` request header instead of adding another `Server` header. Update upstream checks and header policies accordingly.

### Upgrade custom builds and DNS modules together

Caddy 2.10 moved to libdns 1.0-beta APIs, which are source-incompatible with older DNS provider modules. It also changed build policy to require the latest Go minor; 2.10.1 and later in that line require Go 1.25.0 or newer. Caddy 2.11 custom builds require Go 1.26, and 2.11.2 artifacts use Go 1.26.1.

### Replace deprecated log compression configuration

In the 2.11 line, file logs support time-based rotation and `zstd`. Replace `roll_gzip` with `roll_compression`; configured file modes also apply to rotated files, and directory modes are configurable.

### Do not depend on repeated placeholder expansion

Hardening in 2.11.2 stops `vars_regexp` from expanding placeholders twice. Version 2.11.3 stops placeholder expansion in `vars` values, and 2.11.4 prevents re-expansion in injected query strings. Treat values produced from request data as literal data, not a second template.

### Review path, header, FastCGI, and admin assumptions

Security-sensitive 2.11 changes normalize escaped paths and Windows backslashes, sanitize file-match glob metacharacters, tighten FastCGI file execution and Unicode split-path handling, canonicalize remote-admin paths and indices, harden `stripHTML`, and ignore HTTP header fields containing underscores. Browser `no-cors` admin requests are blocked. Configurations that relied on the earlier permissive behavior must be corrected.

### Fail closed on client-auth CA mistakes

Since 2.11.1, a missing or malformed client-auth CA file fails provisioning instead of silently disabling client authentication. Treat that failure as a configuration error.

## High-value Caddyfile additions

### Pass directive blocks to imported snippets

Since 2.9.0, an `import` can pass a block and the snippet can expand it with `{block}`. Since 2.11.1, omitting the block is a safe no-op, so the body may be optional. Deploy at least 2.10.2 when using nested tokens inside the block because it fixes a 2.10.1 regression.

```caddyfile
(wrapped) {
	{block}
}
:80 {
	import wrapped {
		respond "ok"
	}
}
```

### Match responses before changing headers

The 2.9.0 `header` directive accepts a `match` block for response status and other response matchers:

```caddyfile
header {
	match {
		status 2xx
	}
	Cache-Control "public, max-age=60"
}
```

### Preserve an optional query string

`{?query}` includes the leading `?` only when a query exists:

```caddyfile
redir /new-location{?query}
```

### Replace a request body

Since 2.10.0, `request_body set` replaces the incoming body and recalculates `Content-Length`:

```caddyfile
request_body {
	set "replacement body"
}
```

### Use modern authentication hashes

The 2.11 line adds Argon2id verification to `basic_auth`.

## High-value TLS and HTTPS additions

### Configure a global DNS provider

Since 2.10.0, global `dns` supplies the default DNS module for ACME DNS challenges, ECH publication, and other TLS operations. In JSON, use the TLS app's `dns` field. A site-specific `acme_dns` still overrides the global provider.

```caddyfile
{
	dns cloudflare {env.CLOUDFLARE_API_KEY}
}
```

### Enable Encrypted ClientHello

The global `ech` option generates, publishes, and serves ECH configuration. It requires a DNS provider; the public name must point to Caddy and receives its own certificate.

```caddyfile
{
	dns cloudflare {env.CLOUDFLARE_API_KEY}
	ech ech.example.net
}

example.com {
	respond "Hello there!"
}
```

ECH keys rotate automatically in the 2.11 line. Verify real ECH by observing the public name, rather than the protected name, in ClientHello SNI; the mere presence of an ECH extension may be GREASE.

### Use the post-quantum default

Since 2.10.0, TLS enables the standardized `x25519mlkem768` hybrid post-quantum key-exchange group by default. No configuration is needed.

### Select global DNS challenge resolvers

Since 2.11.2, `tls_resolvers` selects DNS resolvers for ACME DNS challenges across sites. Later 2.11 releases also expand placeholders in DNS challenge `override_domain` and ACME credentials.

### Tune renewal without confusing cadence and window

The 2.11 line adds global `renewal_window_ratio`; internal PKI authorities also have independent `maintenance_interval` and `renewal_window_ratio`. `renew_interval` controls how often managed certificates are scanned, not the renewal window.

## High-value reverse-proxy additions

### Configure richer active health checks

Since 2.9.0, active checks can set a method, a distinct health-check upstream, a body, interpolated target headers, and an outbound source address. The 2.11 line honors `health_port` and tracks dynamic upstreams for passive health checks.

```caddyfile
reverse_proxy app:8080 {
	health_uri /healthz
	health_method HEAD
	health_upstream health.internal:8081
}
```

### Design retries for dynamic upstreams

The 2.11 line preserves request bodies across dial-failure retries, can clear the dynamic-upstream cache during retries, adds response-status eligibility through `lb_retry_match`, and makes the stream-copy buffer configurable. `{http.reverse_proxy.retries}` exposes the retry count.

### Use trusted Unix-socket proxies explicitly

`trusted_proxies_unix` trusts forwarded headers received through Unix sockets. For IP-based proxy chains, prefer `trusted_proxies_strict`, which scans `X-Forwarded-For` from right to left and selects the first untrusted hop.

## Operational defaults worth knowing

- HTTP servers default `ReadHeaderTimeout` to one minute since 2.9.0.
- Bare `encode` and bare `file_server { precompressed }` select useful default formats since 2.9.0.
- `caddy run` sets `GOMEMLIMIT` automatically since 2.10.0; other subcommands do not.
- The 2.11 line adds `keepalive_idle` and `keepalive_count`, and can disable QUIC 0-RTT.
- `SIGUSR1` reloads the original file only if Caddy started with a config file and the admin API has not replaced that configuration.
- Access logs redact cookies and authorization headers by default; `log_credentials` deliberately disables that safeguard.
- Setting `QLOGDIR` writes QUIC qlogs for protocol diagnostics.

## Before deploying

1. Read the reference matching the subsystem being changed; quick reference intentionally omits edge cases.
2. Run `caddy adapt` when applicable, then `caddy validate` against the exact binary and module set to be deployed.
3. Verify custom modules against the required Go and libdns versions before rebuilding.
4. Exercise TLS issuance, reloads, proxy health checks, log rotation, and forwarded-client handling in a staging environment.
5. Distribute the local CA root explicitly when clients run outside the host trust store, especially in containers and unprivileged services.
