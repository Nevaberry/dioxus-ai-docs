# Core HTTP and runtime behavior

## Request parsing and protocol behavior

### Strict HTTP/2 and HTTP/3 hop-by-hop headers

Since `1.31.0`, NGINX rejects HTTP/2 and HTTP/3 requests containing
`Connection`, `Proxy-Connection`, `Keep-Alive`, `Transfer-Encoding`, or
`Upgrade`. `TE` is accepted only when its value is `trailers`. Strip other
hop-by-hop fields at protocol-translation boundaries.

### Stricter authority and chunked-body parsing

Since 1.29.4, request-line hosts, `Host`, ports, and HTTP/2 `:authority` follow
RFC 3986 validation. A lone LF is also rejected as a line terminator in
chunked request or response bodies. Retest nonconforming clients and upstreams.

### Configurable header-count limit

Since 1.29.8, `max_headers` limits the number of HTTP header fields.

```nginx
http {
    max_headers 100;
}
```

### WebDAV relationship checks

Since 1.31.0, `ngx_http_dav_module` rejects `COPY` or `MOVE` when source and
destination are identical or have a parent-child collection relationship.
Restructure self-referential or nested collection operations.

### HTTP tunneling and proxy authentication

Since 1.31.0, `ngx_http_tunnel_module` provides HTTP tunneling. `auth_basic`,
`satisfy`, and `auth_delay` can authenticate access to proxies.

## Headers, trailers, and variables

### Early Hints

Starting with `1.29.0`, NGINX accepts HTTP 103 responses from proxy and gRPC
backends. `early_hints` controls whether the preliminary response is forwarded
before the final response.

```nginx
location / {
    proxy_pass http://backend;
    early_hints on;
}
```

### Explicit header and trailer inheritance

Since 1.29.3, `add_header_inherit` and `add_trailer_inherit` let nested
configuration merge inherited fields rather than replace the parent set.

```nginx
add_header_inherit merge;
add_trailer_inherit merge;
```

### Request-port variables

Since 1.29.3, `$request_port` preserves an explicitly supplied request port and
`$is_request_port` emits `:` only when the port exists.

```nginx
proxy_set_header Host $host$is_request_port$request_port;
```

### Complete split-client allocations

Since 1.31.2, a `split_clients` mapping with explicit percentages summing to
100% no longer yields an empty variable.

```nginx
split_clients $request_id $bucket {
    50% a;
    50% b;
}
```

## Connections and listeners

### Minimum reusable-connection lifetime

Since 1.27.4, `keepalive_min_timeout` prevents NGINX from closing a reusable
client connection from the server side during the configured interval,
including graceful worker shutdown. The default is `0`.

```nginx
keepalive_min_timeout 5s;
```

### Multipath listeners

Since 1.29.7, `listen` accepts `multipath`.

```nginx
listen 443 ssl multipath;
```

## Build and module behavior

### GCC 14 and 15 compatibility

The `1.28.0` release fixes GCC 15 failures when building
`ngx_http_v2_module` or `ngx_http_v3_module`. It also fixes GCC 14-or-newer
failures with `-O3 -flto` and `ngx_http_v3_module`.

### Sticky-module configure option

Use `--without-http_upstream_sticky_module` to disable the HTTP upstream sticky
module. `--without-http_upstream_sticky` is deprecated.

## FreeNGINX HTTP and filesystem behavior

### MIME and charset defaults

FreeNGINX 1.27 maps `.js` and `.mjs` to `text/javascript` and `.md` and
`.markdown` to `text/markdown`. Both MIME types are in the default
`charset_types` list, so charset processing applies without extra
configuration.

### Direct I/O for cached responses

FreeNGINX 1.29.0 applies `directio` to responses served from cache.

### Leaky-bucket response rate limiting

FreeNGINX 1.29.0 changes `limit_rate` to a leaky-bucket algorithm and makes
`limit_rate_after` the permitted burst size. Retune configurations whose
throughput assumptions used the earlier behavior.

### Minimum transfer-rate controls

FreeNGINX 1.29.0 adds `send_min_rate` for response sending and
`client_body_min_rate` for request bodies.

### Request timing across clock changes

FreeNGINX 1.29.0 keeps `$request_time` correct when the system clock changes.

### Request-host parsing changes

FreeNGINX 1.29.1 applies stricter `Host` syntax checks, while request-line
parsing accepts hostnames containing `_` and other formerly rejected
characters and accepts zone identifiers in IPv6 addresses.

### External XSLT entities

FreeNGINX 1.29.3 disables external character entities declared in an internal
DTD subset by default. Enable them only for trusted input that requires them.

```nginx
xml_external_entities on;
```

### Corrected relative-path resolution

FreeNGINX 1.29.3 corrects relative paths for `working_directory`,
`google_perftools_profiles`, `geoip_country`, `geoip_city`, `geoip_org`, and
`xml_entities`. Recheck configurations that depended on the former resolution.

### XFS `largeio` cache accounting

FreeNGINX 1.29.4 corrects disk-cache size calculation on XFS filesystems
mounted with `largeio`.

## Maps and observability

### Volatile and wildcard-loaded geo maps

The `geo` block accepts `volatile` since 1.29.3, and its `include` accepts
wildcards since 1.29.8.

```nginx
geo $site_group {
    volatile;
    include /etc/nginx/geo/*.conf;
}
```

### SSL alert log severity

Since 1.31.0, `invalid alert`, `record layer failure`, and numbered SSL alerts
are logged at `info` rather than `crit`. Adjust monitoring that filters on
critical severity.
