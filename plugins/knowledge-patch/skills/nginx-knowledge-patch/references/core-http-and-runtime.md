# Core HTTP and runtime behavior

## Connections and listeners

### Preserve a minimum keep-alive lifetime

Since 1.27.4, `keepalive_min_timeout` sets a period during which NGINX will not close a keep-alive client connection from the server side. The protection also applies during graceful shutdown.

```nginx
keepalive_min_timeout 5s;
```

### Use portless bracketed IPv6 addresses

Since 1.27.3, a bracketed IPv6 address without a port is valid in `proxy_bind`, `fastcgi_bind`, `grpc_bind`, `memcached_bind`, `scgi_bind`, and `uwsgi_bind`. `ngx_http_realip_module` accepts the same address form.

```nginx
proxy_bind [2001:db8::10];
```

### Enable listener TCP keepalive on macOS

From 1.29.0, macOS supports the `so_keepalive` parameter on `listen`.

```nginx
listen 443 ssl so_keepalive=on;
```

### Measure connection lifetime

`$connection_time` reports the client connection's lifetime in seconds with millisecond resolution. Unlike request time, it spans a long-lived or reused connection and can distinguish connection reuse from a slow individual request.

## Request authority and protocol handling

### Handle Host and authority correctly

NGINX 1.28.1 fixes handling for equal `Host` and `:authority` fields over HTTP/2 and for an explicit port in `Host` over HTTP/3.

### Reconstruct an authority with optional port

Since 1.29.3, `$request_port` prefers the URI authority's port, then the `Host` header's port. `$is_request_port` is `:` only when that result is nonempty. Concatenate the variables to yield either `host:port` or `host` without producing a stray colon:

```nginx
proxy_set_header Host $host$is_request_port$request_port;
```

### Complete explicit split allocations

From 1.31.0, a `split_clients` variable no longer becomes empty when every percentage is explicit and the allocations total exactly 100%.

## Responses, files, and filters

### Serve cached files with direct I/O

In FreeNginx 1.29.0, `directio` also applies to responses served from cache. Cached files therefore follow the configured direct-I/O threshold and behavior.

### Apply leaky-bucket transfer controls

FreeNginx 1.29.0 changes `limit_rate` to a leaky-bucket algorithm and makes `limit_rate_after` the permitted burst size. It also adds:

- `send_min_rate` for a minimum response-send rate.
- `client_body_min_rate` for a minimum request-body receive rate.

Re-evaluate existing rate and burst values during migration because the semantics changed.

### Use current MIME defaults

In the FreeNginx 1.27 line, the defaults map `.js` and `.mjs` to `text/javascript`, and `.md` and `.markdown` to `text/markdown`. Both MIME types are included in the default `charset_types` value.

## Build and runtime compatibility

### Build HTTP/2 and HTTP/3 with current GCC

NGINX 1.28.0 builds with GCC 15 when HTTP/2 or HTTP/3 is enabled. It also builds with GCC 14 or newer under `-O3 -flto` when HTTP/3 is enabled.

### Account for the Windows toolchain baseline

From 1.29.0, the native nginx/Windows binary is built with Windows SDK 10. Use that SDK baseline when reproducing binary behavior or investigating build compatibility.
