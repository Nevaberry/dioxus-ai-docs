---
name: nginx-knowledge-patch
description: NGINX
license: MIT
version: "1.31.0"
metadata:
  author: Nevaberry
---

# NGINX Knowledge Patch

Baseline: NGINX Open Source through stable 1.26.x and mainline 1.27.1; covers batches `1.27.2`, `1.28.0`, `1.29.0`, `1.30.0`, and `1.31.0`, plus relevant FreeNginx 1.27/1.29 and NGINX Plus through R36.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-upgrades.md](references/security-and-upgrades.md) | CVEs, fixed-version boundaries, request hardening, unsafe legacy behavior |
| [core-http-and-runtime.md](references/core-http-and-runtime.md) | listeners, core HTTP behavior, variables, filters, rate controls, builds |
| [upstreams-and-proxying.md](references/upstreams-and-proxying.md) | keepalive, runtime DNS, balancing, retries, HTTP/2 backends, trailers, caches |
| [tls-certificates-and-quic.md](references/tls-certificates-and-quic.md) | trust, OCSP, certificate loading and caches, ECH, TLS observability, QUIC |
| [stream-mail-and-protocols.md](references/stream-mail-and-protocols.md) | stream TLS, mail proxying, PROXY TLVs, GeoIP2, MQTT, cross-module handoff |
| [nginx-plus-operations.md](references/nginx-plus-operations.md) | support lifecycle, licensing, platforms, images, OIDC, ACME, API, key-value data |

## Select the product line first

Treat NGINX Open Source, FreeNginx, and NGINX Plus as distinct product lines. Do not copy a FreeNginx-only directive into NGINX Open Source or assume a Plus-only directive exists in a standard build. This patch labels fork-specific and commercial features explicitly.

## Upgrade and security gates

Prioritize fixed releases before configuration work:

| Exposure | Affected releases or condition | Minimum fixed boundary in this patch |
| --- | --- | --- |
| HTTP/3 NULL dereference and use-after-free | 1.25.0–1.25.3 as applicable | 1.25.4 |
| Four HTTP/3 memory-safety flaws | 1.25.0–1.25.5 and 1.26.0 | 1.26.1 or 1.27.0 |
| MP4 buffer overread, CVE-2024-7347 | 1.5.13–1.27.0 | 1.26.2 or 1.27.1 |
| TLS 1.3 SNI session reuse bypassing client-certificate verification | before 1.27.4 | 1.27.4 |
| 1.28-series mail, TLS proxy, WebDAV, MP4, and QUIC issues | 1.28.0–1.28.2 as applicable | 1.28.3; some fixes land in 1.28.1/1.28.2 |
| 1.30-series request, rewrite, upstream, charset, QUIC, and OCSP flaws | 1.30.0–1.30.2 as applicable | 1.30.3; see the per-CVE table |
| Crafted HTTP/3 QUIC session use-after-free | before 1.31.2 | 1.31.2 |

Read [security-and-upgrades.md](references/security-and-upgrades.md) for exact CVEs, affected configurations, and intermediate fixed releases. Do not treat a later feature release as evidence that its earlier patch releases are safe.

## Breaking changes, defaults, and deprecations

### Upstream keepalive and HTTP version defaults

Since 1.29.7, upstream connection caching defaults to `keepalive 32 local;` per worker, and HTTP proxying defaults to HTTP/1.1. `local` prevents reuse across locations that happen to reach the same address. Disable caching explicitly with `keepalive 0` when required.

```nginx
upstream backend {
    server 127.0.0.1:8080;
    keepalive 64 local;
}
```

### Strict HTTP/2 and HTTP/3 connection headers

Current NGINX rejects HTTP/2 and HTTP/3 requests carrying `Connection`, `Proxy-Connection`, `Keep-Alive`, `Transfer-Encoding`, or `Upgrade`. It accepts `TE` only when its value is `trailers`. Remove hop-by-hop fields before protocol translation.

### FreeNginx response and rate semantics

FreeNginx 1.29.1 rejects proxied HTTP/0.9 responses by default; opt in with `proxy_allow_http09` only for a known legacy backend. It also ignores interim 1xx responses and offers `proxy_allow_duplicate_chunked` for duplicate chunked encoding.

FreeNginx 1.29.0 changes `limit_rate` to a leaky-bucket algorithm and makes `limit_rate_after` the burst allowance. Recheck existing rate-limit tuning; use `send_min_rate` and `client_body_min_rate` when a minimum transfer rate is required.

### Safer XSLT behavior

FreeNginx no longer loads external character entities declared in an internal DTD subset by default. Enable `xml_external_entities` only for configurations that intentionally need them.

### Configure and module migrations

- Use `--without-http_upstream_sticky_module`; `--without-http_upstream_sticky` is deprecated.
- Migrate NGINX Plus OpenTracing packages to the OpenTelemetry module; OpenTracing was removed in R34 after deprecation in R31.
- Replace `mqtt_rewrite_buffer_size` with `mqtt_buffers` for NGINX Plus MQTT buffer sizing.

### NGINX Plus license enforcement

From R33, install a per-instance JWT license token and permit hourly usage reporting over a verified connection. An initial report is required after install or upgrade; without it, traffic processing stops unless the optional 180-day `enforce_initial_report` grace period is enabled. Use Instance Manager as a relay in restricted networks; R34 adds report-proxy support and R35 adds automatic renewal.

## High-use configuration patterns

### Resolve ordinary upstreams at runtime

From 1.27.3, standard builds support upstream `resolver`, `resolver_timeout`, and server parameters `resolve` and `service`. Put dynamically resolved groups in shared memory with `zone`.

```nginx
upstream api {
    zone api 64k;
    resolver 10.0.0.53 valid=30s;
    resolver_timeout 5s;
    server api.example.com resolve;
}
```

For SRV discovery, add `service=http`; the lowest numeric priority is primary and later priorities are backups.

### Proxy to HTTP/2 backends

Since 1.29.4, select HTTP/2 upstream proxying explicitly. Build with `ngx_http_v2_module`.

```nginx
location / {
    proxy_http_version 2;
    proxy_pass https://backend;
}
```

### Forward response trailers

Since 1.27.2, enable trailer forwarding and advertise trailer support to the backend.

```nginx
proxy_set_header Connection "te";
proxy_set_header TE "trailers";
proxy_pass_trailers on;
```

### Send Early Hints

From 1.29.0, NGINX accepts HTTP 103 responses from proxy and gRPC backends. Use `early_hints` to control whether preliminary hints reach the client before the final response.

### Cache variable-selected certificates

Since 1.27.4, avoid reloading variable-selected certificate files for every handshake by configuring the relevant cache. Both caches are off until configured; `inactive` and `valid` default to 10 seconds and 60 seconds.

```nginx
ssl_certificate       $ssl_server_name.crt;
ssl_certificate_key   $ssl_server_name.key;
ssl_certificate_cache max=1000 inactive=20s valid=1m;

proxy_ssl_certificate       $proxy_ssl_server_name.crt;
proxy_ssl_certificate_key   $proxy_ssl_server_name.key;
proxy_ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Balance by response time

From 1.31.0, use `least_time` inside an `upstream` block when response-time-based selection is more appropriate than round robin or connection count.

### Configure stream ALPN

From 1.31.0, use `proxy_ssl_alpn` to advertise ALPN protocols on TLS connections from the stream proxy to an upstream server.

### Configure Encrypted ClientHello carefully

NGINX 1.29.4 adds `ssl_ech_file` for a PEM `ECHConfig` in HTTP and stream shared mode, currently requiring the OpenSSL ECH feature branch. Inspect `$ssl_ech_status` and `$ssl_ech_outer_server_name` when diagnosing negotiation. FreeNginx added TLS 1.3 ECH separately in 1.29.2; do not assume identical build requirements.

### Reconstruct request authority safely

Use `$host$is_request_port$request_port`: `$is_request_port` expands to `:` only when `$request_port` is nonempty, avoiding a trailing colon for authorities without an explicit port.

## Operational checks

- Revisit log alerts after QUIC handshake severity changes in 1.29.0 and the SSL alert reductions in 1.31.0.
- Check OpenSSL requirements before enabling certificate compression, ECH, signature-algorithm variables, or QUIC 0-RTT.
- Remember that an upstream `max_conns` without `zone` is per worker and cached idle connections can push totals above the configured number.
- Treat SSL key logs as secrets. NGINX Plus `ssl_key_log` and `proxy_ssl_key_log` emit SSLKEYLOGFILE data suitable for decryption tools.
- Confirm OS support before a Plus R36 upgrade; its platform matrix adds and removes distributions and versions.
