# Upstreams and proxying

## Backend protocols and response handling

### Forward proxied response trailers

Since `1.27.2`, `proxy_pass_trailers on` forwards trailer fields to the client.
For an HTTP/1.1 upstream, advertise trailer support.

```nginx
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "te";
    proxy_set_header TE "trailers";
    proxy_pass_trailers on;
}
```

### HTTP/2 backends

Since 1.29.4, `ngx_http_proxy_module` can use HTTP/2 to an upstream. Set the
version explicitly.

```nginx
location / {
    proxy_http_version 2;
    proxy_pass https://backend;
}
```

### Protocol-appropriate authority headers

Since `1.31.4`, HTTP/2 and gRPC backend requests always carry `:authority`,
and HTTP/1.1 backend requests always carry `Host`. Routing and validation can
rely on the appropriate authority header being present.

### Partial upstream response first lines

Version 1.30.1 correctly transfers proxied HTTP/0.9, SCGI, and uWSGI responses
whose first response line is not read in one operation.

## Discovery, state, and server selection

### Runtime DNS and SRV discovery

Since 1.27.3, ordinary upstreams support `resolver`, `resolver_timeout`, and
the `resolve` and `service` server parameters. A dynamically resolved group
requires `zone`. For SRV, use a portless hostname; the lowest numeric priority
is primary and later priorities are backups.

```nginx
upstream api {
    zone api 64k;
    resolver 192.0.2.53 valid=30s;
    resolver_timeout 5s;
    server api.example.com service=http resolve;
}
```

### Persistent dynamic upstream state

The Plus `state` directive persists a dynamically managed server list and its
parameters. Do not combine it with static `server` directives or edit its file
directly. Changes made during reload or binary upgrade can be lost.

```nginx
upstream backend {
    zone backend 64k;
    state /var/lib/nginx/state/servers.conf;
}
```

### Connection caps and overflow queues

Without `zone`, `max_conns` is per worker. Even with a zone, multiple workers
and cached idle connections can put active plus idle totals above the limit.
The Plus `queue` holds requests while no server is selectable and returns 502
on capacity or timeout. A one-server group ignores `max_fails`, `fail_timeout`,
and `slow_start`.

```nginx
upstream backend {
    zone backend 64k;
    server 192.0.2.10:8080 max_conns=100;
    queue 200 timeout=10s;
}
```

### Response-time balancing

Since `1.31.0`, `least_time` selects backends using observed response time.

```nginx
upstream backend {
    least_time header;
    server 192.0.2.10:8080;
    server 192.0.2.11:8080;
}
```

### Session affinity

Since 1.29.6, HTTP upstreams support `sticky`; upstream servers support
`route` and `drain`.

```nginx
upstream app {
    sticky cookie route;
    server app1.example route=a;
    server app2.example route=b;
    server app3.example route=c drain;
}
```

## Keepalive and retry behavior

### Keepalive and HTTP/1.1 defaults

Since 1.29.7, upstream and proxied keepalive are enabled by default,
`proxy_http_version` defaults to 1.1, and no `Connection` proxy header is sent
by default. The `local` parameter scopes an explicitly configured upstream
keepalive cache.

```nginx
upstream backend {
    server backend.example:8080;
    keepalive 64 local;
}
```

### FreeNGINX failure and stale-cache handling

Since FreeNGINX 1.29.5, a server is marked failed for a configured
`proxy_next_upstream` status of 500, 502, 503, 504, or 429 even when no retry
target is available. `stale-if-error` is applied in that situation too.

## Dynamic Plus request controls

### Conditional admission of selected servers

Plus 1.29.3 adds `proxy_allow_upstream`. Before each connection attempt, every
condition must be nonempty and not `0`; denial can fail over through
`proxy_next_upstream denied`.

```nginx
geo $upstream_last_addr $allow_backend {
    volatile;
    default        0;
    10.10.0.0/24  1;
}

proxy_allow_upstream $allow_backend;
proxy_next_upstream error timeout denied;
```

### Bind every connection attempt

Plus 1.29.3 adds `proxy_bind_dynamic`, which repeats `proxy_bind` for every
connection attempt, including retries for one proxied request.

```nginx
proxy_bind $remote_addr transparent;
proxy_bind_dynamic on;
```

### Per-server proxy request instances

Plus 1.29.3 adds `proxy_request_dynamic`. It creates a new request instance for
each selected server, allowing server-specific request fields.

```nginx
proxy_request_dynamic on;
proxy_set_header Host $upstream_last_server_name;
```

### Last selected upstream variables

Plus `$upstream_last_addr` contains the last selected address or UNIX socket;
`$upstream_last_server_name` contains its configured name and can drive SNI.

```nginx
proxy_ssl_server_name on;
proxy_ssl_name $upstream_last_server_name;
```

## Rate limits and certificate material

### Variable upstream read-rate limit

Since 1.27.0, the byte-per-second `proxy_limit_rate` accepts variables. It works
only with response buffering, applies per request, and is disabled by `0`.

```nginx
map $request_uri $upstream_read_rate {
    default  0;
    ~^/bulk/ 512k;
}

proxy_limit_rate $upstream_read_rate;
```

### Cache variable-selected client certificates

Since 1.27.4, `proxy_ssl_certificate_cache` caches variable-selected upstream
client certificates and keys. `max` sets LRU capacity; `inactive` and `valid`
default to 10 and 60 seconds.

```nginx
proxy_ssl_certificate       $proxy_ssl_server_name.crt;
proxy_ssl_certificate_key   $proxy_ssl_server_name.key;
proxy_ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Upstream TLS key logging

Plus `proxy_ssl_key_log`, added in 1.27.2, writes upstream TLS secrets in
SSLKEYLOGFILE format. Protect the file as secret data because it permits
captured traffic to be decrypted.

```nginx
proxy_ssl_key_log /var/log/nginx/upstream.keys;
```

## FreeNGINX backend compatibility

### Proxy response defaults

FreeNGINX 1.29.1 rejects HTTP/0.9 upstream responses by default, ignores
interim 1xx responses, and provides opt-ins for legacy HTTP/0.9 and duplicate
chunked encoding.

```nginx
location /legacy {
    proxy_pass http://legacy;
    proxy_allow_http09 on;
    proxy_allow_duplicate_chunked on;
}
```

### Certificates for IP-address backends

FreeNGINX 1.29.1 can verify TLS backend certificates issued for IP addresses.
