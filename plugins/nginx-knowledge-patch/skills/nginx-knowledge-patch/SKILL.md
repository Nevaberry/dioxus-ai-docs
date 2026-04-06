---
name: nginx-knowledge-patch
description: "Nginx changes since training cutoff (latest: 1.29.7) — upstream keepalive defaults, sticky directive, DNS resolve, HTTP/2 proxying, TLS defaults. Load before working with Nginx."
license: MIT
version: "1.29.7"
metadata:
  author: Nevaberry
---

# Nginx Knowledge Patch (1.27.3 – 1.29.7)

Baseline: Nginx 1.26.x stable, basic awareness of 1.27.x mainline.
Covers: 1.27.3 through 1.29.7 (2024-11-26 to 2026-03-24).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Upstream & load balancing | [references/upstream-and-load-balancing.md](references/upstream-and-load-balancing.md) | Sticky sessions, DNS resolve, HTTP/2 proxying |
| TLS & security | [references/tls-and-security.md](references/tls-and-security.md) | ECH, QUIC 0-RTT, ssl_key_log, certificate caching |
| HTTP & transport | [references/http-and-transport.md](references/http-and-transport.md) | Early Hints, header inheritance, MPTCP, new variables |

---

## Breaking Changes

### Upstream keepalive enabled by default (1.29.7)

`keepalive 32 local` is now the default for all upstream blocks. `proxy_http_version` defaults to `1.1` (was `1.0`). The `Connection` header is no longer set to `close` by default.

The classic keepalive boilerplate is now unnecessary:
```nginx
# Before 1.29.7 — required for keepalive to upstreams:
upstream backend {
    server 127.0.0.1:8080;
    keepalive 32;
}
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}

# Since 1.29.7 — keepalive works out of the box:
upstream backend {
    server 127.0.0.1:8080;
}
location / {
    proxy_pass http://backend;
}
```

The `local` parameter (default) means keepalive connections are NOT shared across different `location` blocks. Omit `local` to allow sharing: `keepalive 32;`.

To disable keepalive to upstreams: `keepalive 0;`.

### TLSv1/TLSv1.1 disabled by default (1.27.3)

`ssl_protocols` now defaults to `TLSv1.2 TLSv1.3`. If you need legacy protocol support, set `ssl_protocols` explicitly.

---

## New Directives Quick Reference

| Directive / Parameter | Context | Since | Description |
|---|---|---|---|
| `sticky cookie\|route\|learn` | `upstream` | 1.29.6 | Session affinity (was nginx-plus only) |
| `server ... resolve` | `upstream` | 1.27.3 | DNS-based upstream resolution (was nginx-plus only) |
| `server ... route=` | `upstream` | 1.29.6 | Route identifier for sticky sessions |
| `server ... drain` | `upstream` | 1.29.6 | Graceful server removal |
| `proxy_http_version 2` | `location` | 1.29.4 | HTTP/2 proxying to backends |
| `early_hints` | `server`, `location` | 1.29.0 | Pass 103 Early Hints from backends |
| `add_header_inherit` | `http`, `server`, `location` | 1.29.3 | Control `add_header` inheritance from parent |
| `add_trailer_inherit` | `http`, `server`, `location` | 1.29.3 | Control `add_trailer` inheritance from parent |
| `keepalive_min_timeout` | `http`, `server` | 1.27.4 | Minimum keep-alive connection lifetime |
| `listen ... multipath` | `server` | 1.29.7 | Enable MPTCP (RFC 8684) |
| `proxy_pass_trailers` | `location` | 1.27.2 | Pass HTTP trailer fields from backends |
| `ssl_ech_file` | `server` | 1.29.4 | Encrypted Client Hello support |
| `ssl_key_log` | `http`, `server` | 1.29.1 | TLS key logging for debugging |
| `ssl_certificate_cache` | `http`, `server` | 1.27.4 | Explicit certificate caching control |

## New Variables

| Variable | Since | Description |
|---|---|---|
| `$request_port` | 1.29.3 | Port from the request line |
| `$is_request_port` | 1.29.3 | Whether the port is explicitly specified in the request |
| `$ssl_sigalg` | 1.29.3 | TLS signature algorithm used by server |
| `$ssl_client_sigalg` | 1.29.3 | TLS signature algorithm used by client |

---

## Formerly nginx-plus-only Features Now in Open Source

Three major features previously exclusive to nginx-plus are now available. For full details and all variants, see [references/upstream-and-load-balancing.md](references/upstream-and-load-balancing.md).

### Sticky Sessions (1.29.6)

Cookie-based session affinity (most common pattern):
```nginx
upstream backend {
    server backend1.example.com route=a;
    server backend2.example.com route=b;
    sticky cookie srv_id expires=1h domain=.example.com path=/;
}
```

Three methods: `cookie` (client-side cookie), `route` (maps to existing session IDs), `learn` (server-initiated sessions). The `route` and `drain` parameters on the `server` directive are also now available.

### DNS-based Upstream Resolution (1.27.3)

```nginx
upstream backend {
    zone backend_zone 64k;  # required for resolve
    server backend.example.com resolve;
    server backend.example.com service=http resolve;  # SRV records
    resolver 10.0.0.1 valid=30s;
}
```

A shared memory `zone` is required when using `resolve`.

---

## HTTP/2 Proxying to Backends (1.29.4)

`proxy_http_version` now accepts `2` for HTTP/2 connections to upstream servers:
```nginx
location / {
    proxy_pass https://backend;
    proxy_http_version 2;
}
```
Requires the `ngx_http_v2_module`.

---

## 103 Early Hints (1.29.0)

New `early_hints` directive controls passing 103 responses from backends to clients:
```nginx
map $http_sec_fetch_mode $early_hints {
    navigate $http2$http3;
}

server {
    location / {
        early_hints $early_hints;
        proxy_pass http://backend;
    }
}
```
The 103 response is passed only when all string parameters are non-empty and non-zero.

---

## MPTCP Support (1.29.7)

```nginx
server {
    listen 80 multipath;
    listen 443 ssl multipath;
}
```
Enables Multipath TCP (RFC 8684). Implicitly enables `SO_REUSEPORT`.

---

## Header Inheritance Fix (1.29.3)

`add_header_inherit` and `add_trailer_inherit` control inheritance from parent contexts. Previously, defining any `add_header` in a child block silently dropped all parent headers — a long-standing footgun now fixable.

```nginx
# Parent headers are now inherited even when child defines its own:
server {
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    location /api {
        add_header_inherit on;          # inherit parent add_header directives
        add_header X-API-Version "2.0"; # this no longer drops the parent headers
        proxy_pass http://backend;
    }
}
```

---

## keepalive_min_timeout (1.27.4)

Sets a minimum time a keep-alive connection stays open, preventing premature closure during graceful shutdown or connection reuse:
```nginx
keepalive_min_timeout 10s;  # default: 0
```

---

## TLS Changes

- **TLSv1/TLSv1.1 disabled by default** (1.27.3) — `ssl_protocols` defaults to `TLSv1.2 TLSv1.3`
- **ECH support** (1.29.4) — `ssl_ech_file` directive, requires OpenSSL ECH feature branch
- **QUIC 0-RTT** (1.29.1) — supported with OpenSSL 3.5.1+
- **`ssl_key_log`** (1.29.1) — TLS key logging for Wireshark debugging
- **`ssl_certificate_cache`** (1.27.4) — explicit certificate caching control

For full details, see [references/tls-and-security.md](references/tls-and-security.md).

---

## Reference Files

- **[references/upstream-and-load-balancing.md](references/upstream-and-load-balancing.md)** — Sticky sessions (cookie/route/learn), DNS-based upstream resolution, HTTP/2 proxying details
- **[references/tls-and-security.md](references/tls-and-security.md)** — ECH support, QUIC 0-RTT, TLS key logging, certificate caching, TLS variables
- **[references/http-and-transport.md](references/http-and-transport.md)** — 103 Early Hints, header/trailer inheritance, keepalive_min_timeout, MPTCP, proxy_pass_trailers, new variables
