# Upstream & Load Balancing

## Sticky Sessions (1.29.6)

Session affinity was previously nginx-plus only. Three methods are available in open-source nginx:

### Cookie-based (most common)

```nginx
upstream backend {
    server backend1.example.com route=a;
    server backend2.example.com route=b;
    sticky cookie srv_id expires=1h domain=.example.com path=/;
}
```

### Route-based (uses existing session IDs)

```nginx
upstream backend {
    server backend1.example.com route=a;
    server backend2.example.com route=b;
    sticky route $route_cookie $route_uri;
}
```

### Learn-based (server-initiated sessions)

```nginx
upstream backend {
    server backend1.example.com;
    server backend2.example.com;
    sticky learn
           create=$upstream_cookie_examplecookie
           lookup=$cookie_examplecookie
           zone=client_sessions:1m;
}
```

### Related server parameters (1.29.6)

The `route` and `drain` parameters on the `server` directive are also now available in open-source:

- `route=<id>` — assigns a route identifier for sticky cookie/route matching
- `drain` — puts server in draining mode (stops accepting new sessions, finishes existing ones)

---

## DNS-based Upstream Resolution (1.27.3)

The `resolve` parameter and `resolver`/`resolver_timeout` directives in `upstream` blocks were nginx-plus only. Now available in open-source:

```nginx
upstream backend {
    zone backend_zone 64k;  # required for resolve
    server backend.example.com resolve;
    server backend.example.com service=http resolve;  # SRV records
    resolver 10.0.0.1 valid=30s;
}
```

Requirements:
- A shared memory `zone` is required when using `resolve`
- `resolver` must be specified in the upstream block
- `service=` enables SRV record lookups

---

## HTTP/2 Proxying to Backends (1.29.4)

`proxy_http_version` now accepts `2` for HTTP/2 connections to upstream servers:

```nginx
location / {
    proxy_pass https://backend;
    proxy_http_version 2;
}
```

Requires the `ngx_http_v2_module`. Useful for gRPC backends or when backends benefit from HTTP/2 multiplexing.

---

## Upstream Keepalive Defaults (1.29.7)

`keepalive 32 local` is now the default for all upstream blocks.

Key details:
- `proxy_http_version` defaults to `1.1` (was `1.0`)
- The `Connection` header is no longer set to `close` by default
- The `local` parameter means connections are NOT shared across different `location` blocks
- Omit `local` to share connections: `keepalive 32;`
- Disable keepalive to upstreams: `keepalive 0;`
