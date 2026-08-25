# Core HTTP and runtime behavior

## Request parsing and protocol conformance

### Strict HTTP/2 and HTTP/3 connection headers

Since 1.31.0, NGINX rejects HTTP/2 and HTTP/3 requests containing
`Connection`, `Proxy-Connection`, `Keep-Alive`, `Transfer-Encoding`, or
`Upgrade`. It accepts `TE` only when its value is `trailers`. Strip other
hop-by-hop fields when translating protocols.

### Authority and chunked-body parsing

Since 1.29.4, request-line host and port syntax, `Host`, and `:authority` are
validated according to RFC 3986. A lone LF is rejected as a line terminator in
chunked request and response bodies. Test clients and upstreams that relied on
the older permissive parser.

### Header-count limits

Since 1.29.8, `max_headers` sets an explicit limit on HTTP header-field count.

```nginx
http {
    max_headers 100;
}
```

### FreeNGINX host parsing

FreeNGINX 1.29.1 applies stricter syntax checks to the `Host` header. In the
request line it also accepts host names containing `_` and other formerly
rejected characters, plus zone identifiers in IPv6 addresses.

## Response behavior

### Early Hints

Since 1.29.0, proxy and gRPC backends may supply HTTP 103 responses. Use
`early_hints` to decide whether to forward preliminary hints before the final
response.

```nginx
location / {
    proxy_pass http://backend;
    early_hints on;
}
```

### Explicit header and trailer inheritance

Since 1.29.3, `add_header_inherit` and `add_trailer_inherit` can merge a nested
configuration's fields with its inherited parent set rather than replacing the
parent set.

```nginx
add_header_inherit merge;
add_trailer_inherit merge;
```

### FreeNGINX MIME and charset defaults

FreeNGINX 1.27 maps `.js` and `.mjs` to `text/javascript`, and `.md` and
`.markdown` to `text/markdown`. Both media types are in the default
`charset_types` list, so charset processing applies without extra setup.

## Variables and mappings

### Explicit request-port reconstruction

Since 1.29.3, `$request_port` holds an explicitly supplied request port and
`$is_request_port` expands to `:` only when that value is nonempty.

```nginx
proxy_set_header Host $host$is_request_port$request_port;
```

### Volatile and wildcard-loaded geo maps

The `geo` block accepts `volatile` since 1.29.3, and its `include` accepts
wildcards since 1.29.8.

```nginx
geo $site_group {
    volatile;
    include /etc/nginx/geo/*.conf;
}
```

### Complete split-client allocations

Since 1.31.2, a `split_clients` mapping no longer produces an empty value when
all percentages are explicit and total 100%.

```nginx
split_clients $request_id $bucket {
    50% a;
    50% b;
}
```

### Request timing across clock changes

FreeNGINX 1.29.0 keeps `$request_time` correct across system clock changes, so
clock adjustments do not distort recorded durations.

## Rate and connection controls

### Minimum keep-alive lifetime

Since 1.27.4, `keepalive_min_timeout` prevents NGINX from closing a reusable
client connection from the server side during the configured interval,
including during graceful worker shutdown. The default is `0`.

```nginx
keepalive_min_timeout 5s;
```

### FreeNGINX leaky-bucket response limits

FreeNGINX 1.29.0 changes `limit_rate` to a leaky-bucket algorithm and makes
`limit_rate_after` the allowed burst size. Review previous tuning because its
transmission pattern changes. `send_min_rate` and `client_body_min_rate` add
minimum rates for response sending and request-body receipt.

## Listeners, modules, and builds

### Multipath listeners

Since 1.29.7, `listen` accepts `multipath`.

```nginx
listen 443 ssl multipath;
```

### HTTP tunneling and proxy authentication

NGINX 1.31 adds `ngx_http_tunnel_module` for HTTP tunneling. `auth_basic`,
`satisfy`, and `auth_delay` can authenticate access to proxies.

### WebDAV relationship checks

NGINX 1.31 rejects `COPY` or `MOVE` when source and destination are identical
or have a parent-child collection relationship. Restructure self-referential
or nested collection moves.

### Sticky-module configure option

Use `--without-http_upstream_sticky_module`. The older
`--without-http_upstream_sticky` option is deprecated.

### HTTP/2 and HTTP/3 compiler compatibility

NGINX 1.28.0 fixes GCC 15 build failures with `ngx_http_v2_module` or
`ngx_http_v3_module`, and GCC 14-or-newer failures with `-O3 -flto` and
`ngx_http_v3_module`.

## FreeNGINX filters, paths, and filesystem behavior

### External XSLT entities

FreeNGINX 1.29.3 no longer loads external character entities declared in an
internal DTD subset by default. Enable the old behavior only when a trusted
transformation requires it.

```nginx
xml_external_entities on;
```

### Corrected relative paths

FreeNGINX 1.29.3 corrects relative-path handling for `working_directory`,
`google_perftools_profiles`, `geoip_country`, `geoip_city`, `geoip_org`, and
`xml_entities`. Recheck configurations that relied on earlier resolution.

### XFS largeio cache accounting

FreeNGINX 1.29.4 corrects disk-cache size calculation on XFS filesystems
mounted with `largeio`.
