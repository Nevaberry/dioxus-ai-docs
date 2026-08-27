---
name: nginx-knowledge-patch
description: NGINX
version: "1.31.0"
license: MIT
metadata:
  author: Nevaberry
---


# NGINX Knowledge Patch

Use this skill when writing, reviewing, upgrading, or debugging NGINX Open
Source, FreeNGINX, or NGINX Plus configuration. Identify the product line and
exact patch release first; fork-only and commercial directives are not portable
to a standard NGINX Open Source build.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-upgrades.md](references/security-and-upgrades.md) | CVEs, fixed-version boundaries, reporting, and legacy hazards |
| [core-http-and-runtime.md](references/core-http-and-runtime.md) | HTTP parsing, listeners, variables, filters, rate controls, builds, and runtime behavior |
| [upstreams-and-proxying.md](references/upstreams-and-proxying.md) | Discovery, balancing, keepalive, retries, proxy protocols, caches, and backend requests |
| [tls-certificates-and-quic.md](references/tls-certificates-and-quic.md) | Trust, OCSP, certificate caches, ECH, key logs, TLS observability, and QUIC |
| [stream-mail-and-protocols.md](references/stream-mail-and-protocols.md) | Stream and mail proxying, PROXY TLVs, GeoIP2, MQTT, and listener handoff |
| [nginx-plus-operations.md](references/nginx-plus-operations.md) | Plus lifecycle, licensing, platforms, images, OIDC, ACME, API, and key-value data |

## Select the product line first

- Treat NGINX Open Source, FreeNGINX, and NGINX Plus as distinct products.
- Confirm module availability and build flags before adding a directive.
- Do not infer Open Source support from a Plus feature or NGINX support from a
  FreeNGINX change.
- For Plus, check the supported OS matrix, active support window, and license
  reporting path before upgrading.

## Security and upgrade gates

Upgrade to a fixed patch release before attempting configuration mitigation.
Do not assume the first release in a feature series contains later security
fixes.

| Exposure | Minimum fixed boundary |
| --- | --- |
| HTTP/3 CVE-2024-24989 and CVE-2024-24990 | `1.25.4` |
| HTTP/3 CVE-2024-32760, CVE-2024-31079, CVE-2024-35200, and CVE-2024-34161 | `1.26.1` or `1.27.0` |
| MP4 buffer overread, CVE-2024-7347 | `1.26.2` or `1.27.1` |
| CVE-2025-23419 TLS session reuse issue | `1.26.3` or `1.27.4` |
| 1.29-series mail authentication disclosure | `1.29.1` |
| 1.29-series TLS-backend plaintext injection | `1.29.5` |
| 1.29-series WebDAV, MP4, mail, PTR, and stream OCSP issues | `1.29.7` |
| 1.30-series request, rewrite, upstream, charset, QUIC, and OCSP flaws | Use the precise `1.30.1`, `1.30.2`, or `1.30.3` gate in the security reference |
| Crafted HTTP/3 QUIC-session use-after-free | `1.31.2` |

Read [security-and-upgrades.md](references/security-and-upgrades.md) for exact
affected configurations, CVEs, older-branch floors, and the unsanitized
error-log caveat.

## Breaking changes and compatibility defaults

### Upstream keepalive and HTTP version defaults

From 1.29.7, upstream connection caching and proxied keepalive are enabled by
default, `proxy_http_version` defaults to HTTP/1.1, and NGINX no longer sends a
`Connection` proxy header by default. Use `local` to keep an explicitly sized
cache scoped to its upstream usage context.

```nginx
upstream backend {
    server backend.example:8080;
    keepalive 64 local;
}
```

Disable or retune caching explicitly when an application depends on connection
churn or location isolation.

### Strict request parsing and hop-by-hop headers

Current HTTP/2 and HTTP/3 handling rejects `Connection`,
`Proxy-Connection`, `Keep-Alive`, `Transfer-Encoding`, and `Upgrade`. `TE` is
valid only as `trailers`. Protocol translators must remove hop-by-hop fields.

Host and port parsing follows RFC 3986, and a lone LF is rejected in chunked
request or response bodies. Test legacy clients and upstreams during upgrades.

### FreeNGINX proxy compatibility

FreeNGINX rejects proxied HTTP/0.9 responses by default, ignores interim 1xx
responses, and provides narrowly scoped opt-ins for legacy HTTP/0.9 and
duplicate chunked encoding.

```nginx
location /legacy {
    proxy_pass http://legacy;
    proxy_allow_http09 on;
    proxy_allow_duplicate_chunked on;
}
```

### FreeNGINX transfer-rate semantics

FreeNGINX uses a leaky-bucket `limit_rate`; `limit_rate_after` is the allowed
burst. Recheck existing rate tuning, and use `send_min_rate` or
`client_body_min_rate` when a minimum transfer rate is required.

### Safer XSLT behavior

FreeNGINX does not load external character entities declared in an internal
DTD subset by default. Enable `xml_external_entities` only for a trusted
transformation that intentionally requires the legacy behavior.

### Configure and module migrations

- Disable the upstream sticky module with
  `--without-http_upstream_sticky_module`; the shorter legacy option is
  deprecated.
- On Plus, migrate OpenTracing to OpenTelemetry; OpenTracing is no longer
  packaged.
- Replace Plus `mqtt_rewrite_buffer_size` with `mqtt_buffers`.

## High-use configuration patterns

### Resolve ordinary upstreams at runtime

Put dynamically resolved upstream groups in shared memory. Configure an
upstream resolver and mark servers with `resolve`; for SRV discovery, add
`service` and omit the server port.

```nginx
upstream api {
    zone api 64k;
    resolver 192.0.2.53 valid=30s;
    resolver_timeout 5s;
    server api.example.com service=http resolve;
}
```

The lowest numeric SRV priority is primary; later priorities are backups.

### Proxy to an HTTP/2 backend

Select HTTP/2 explicitly for the upstream.

```nginx
location / {
    proxy_http_version 2;
    proxy_pass https://backend;
}
```

### Forward response trailers

Enable trailer forwarding and advertise trailer support to an HTTP/1.1
backend.

```nginx
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "te";
    proxy_set_header TE "trailers";
    proxy_pass_trailers on;
}
```

### Send Early Hints

NGINX can accept HTTP 103 responses from proxy and gRPC backends. Use
`early_hints` to decide whether they reach the client before the final response.

### Cache variable-selected certificates

Both server-side and upstream-client certificate caches are off until
configured. `max` sets LRU capacity; `inactive` and `valid` default to 10 and
60 seconds.

```nginx
ssl_certificate       $ssl_server_name.crt;
ssl_certificate_key   $ssl_server_name.key;
ssl_certificate_cache max=1000 inactive=20s valid=1m;

proxy_ssl_certificate       $proxy_ssl_server_name.crt;
proxy_ssl_certificate_key   $proxy_ssl_server_name.key;
proxy_ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Preserve an explicitly supplied request port

Use the paired variables so an authority without an explicit port does not
gain a trailing colon.

```nginx
proxy_set_header Host $host$is_request_port$request_port;
```

### Balance by observed response time

Use `least_time` inside an upstream when response-time selection is preferable
to round robin or connection count.

```nginx
upstream backend {
    least_time header;
    server 192.0.2.10:8080;
    server 192.0.2.11:8080;
}
```

### Advertise ALPN to a stream TLS upstream

```nginx
proxy_ssl on;
proxy_ssl_alpn h2;
```

Do not confuse upstream `proxy_ssl_alpn` with server-side `ssl_alpn`.

## Operational checks

- Revisit alert rules after QUIC and SSL handshake log-level changes.
- Verify TLS-library and build requirements before enabling certificate
  compression, ECH, signature variables, or QUIC 0-RTT.
- Remember that `max_conns` is per worker without `zone`; cached idle
  connections can also push totals above the configured number.
- Protect `ssl_key_log` and `proxy_ssl_key_log` output as decryption secrets.
- For Plus, an unavailable initial usage report can stop traffic unless the
  optional grace period is deliberately enabled.
