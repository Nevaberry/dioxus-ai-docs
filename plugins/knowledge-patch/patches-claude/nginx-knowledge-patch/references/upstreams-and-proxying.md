# Upstreams and proxying

## Connection reuse and protocol selection

### Keepalive and HTTP version defaults

Since 1.29.7, NGINX enables upstream and proxied keepalive by default, defaults
`proxy_http_version` to 1.1, and no longer sends a `Connection` proxy header by
default. The new `local` parameter scopes an explicitly configured upstream
keepalive cache.

```nginx
upstream backend {
    server backend.example:8080;
    keepalive 64 local;
}
```

### HTTP/2 proxy backends

Since 1.29.4, `ngx_http_proxy_module` can use HTTP/2 to an upstream backend
when `ngx_http_v2_module` is built in.

```nginx
location / {
    proxy_http_version 2;
    proxy_pass https://backend;
}
```

### Protocol-appropriate authority headers

Since 1.31.4, requests to HTTP/2 and gRPC backends always carry `:authority`,
while requests to HTTP/1.1 backends always carry `Host`. Upstream routing and
validation can rely on the header appropriate to the selected protocol.

## Discovery and selection

### Runtime DNS and SRV discovery

Since 1.27.3, ordinary open-source upstreams support `resolver`,
`resolver_timeout`, and the server parameters `resolve` and `service`.
Dynamically resolved groups require `zone`. For SRV discovery, give `server` a
portless hostname with `resolve`; the lowest numeric SRV priority is primary
and later priorities are backups.

```nginx
upstream api {
    zone api 64k;
    resolver 192.0.2.53 valid=30s;
    resolver_timeout 5s;
    server api.example.com service=http resolve;
}
```

### Sticky HTTP upstreams

Since 1.29.6, HTTP upstreams have `sticky`, while individual servers have
`route` and `drain`.

```nginx
upstream app {
    sticky cookie route;
    server app1.example route=a;
    server app2.example route=b;
    server app3.example route=c drain;
}
```

### Response-time balancing

NGINX 1.31 provides `least_time` inside `upstream` to select a backend using
observed response time.

```nginx
upstream backend {
    least_time header;
    server 192.0.2.10:8080;
    server 192.0.2.11:8080;
}
```

### Connection caps and overflow queues

Without `zone`, `max_conns` is per worker. Even with a zone, several workers
and cached idle connections can make the combined active and idle total exceed
the configured value. NGINX Plus `queue` holds requests when no server is
selectable and returns 502 when its capacity or timeout is exceeded. A
one-server group ignores `max_fails`, `fail_timeout`, and `slow_start`.

```nginx
upstream backend {
    zone backend 64k;
    server 192.0.2.10:8080 max_conns=100;
    queue 200 timeout=10s;
}
```

## Responses, retries, and caching

### Forward response trailers

Since 1.27.2, `proxy_pass_trailers on` forwards trailer fields from a proxied
response. Advertise trailer support to an HTTP/1.1 backend too.

```nginx
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "te";
    proxy_set_header TE "trailers";
    proxy_pass_trailers on;
}
```

### Partial upstream first lines

NGINX 1.30.1 corrects transfer of proxied HTTP/0.9, SCGI, and uWSGI responses
when the first response line is not completely read in one operation.

### FreeNGINX proxy response compatibility

FreeNGINX 1.29.1 rejects proxied HTTP/0.9 responses by default and ignores
interim 1xx responses. Enable `proxy_allow_http09` only for a known legacy
backend; use `proxy_allow_duplicate_chunked` only for an upstream that needs
that compatibility behavior.

```nginx
location /legacy {
    proxy_pass http://legacy;
    proxy_allow_http09 on;
    proxy_allow_duplicate_chunked on;
}
```

### Failure and stale-cache handling without a retry target

From FreeNGINX 1.29.5, an upstream is still marked failed after a configured
`proxy_next_upstream` status of 500, 502, 503, 504, or 429 even when no server
switch is possible. `stale-if-error` cache control also applies in that case.

### Direct I/O for cached responses

FreeNGINX 1.29.0 makes `directio` effective for cache-served responses, so the
configured direct-I/O policy applies to cached as well as uncached output.

## Per-request proxy controls

### Variable upstream read-rate limits

Since 1.27.0, `proxy_limit_rate` accepts variables. It limits bytes per second
only when response buffering is enabled, applies separately to each request,
and is disabled by `0`.

```nginx
map $request_uri $upstream_read_rate {
    default  0;
    ~^/bulk/ 512k;
}

proxy_limit_rate $upstream_read_rate;
```

### Conditional admission in NGINX Plus

NGINX Plus 1.29.3 adds `proxy_allow_upstream`. Before every connection attempt,
all its condition values must be nonempty and not `0`. A denial can fail over
through the `denied` value of `proxy_next_upstream`.

```nginx
geo $upstream_last_addr $allow_backend {
    volatile;
    default        0;
    10.10.0.0/24  1;
}

proxy_allow_upstream $allow_backend;
proxy_next_upstream error timeout denied;
```

### Dynamic binding in NGINX Plus

NGINX Plus 1.29.3 adds `proxy_bind_dynamic`; it repeats `proxy_bind` for every
connection attempt, including later attempts for the same request.

```nginx
proxy_bind $remote_addr transparent;
proxy_bind_dynamic on;
```

### Per-server request instances in NGINX Plus

NGINX Plus 1.29.3 adds `proxy_request_dynamic`. It creates a separate request
instance for each selected server, allowing fields to use server-specific
values.

```nginx
proxy_request_dynamic on;
proxy_set_header Host $upstream_last_server_name;
```

## NGINX Plus upstream state and identity

### Persistent dynamic state

The NGINX Plus `state` directive persists a dynamically managed upstream's
server list and parameters. It cannot coexist with static `server` directives;
do not edit the state file directly. Changes made during a reload or binary
upgrade can be lost.

```nginx
upstream backend {
    zone backend 64k;
    state /var/lib/nginx/state/servers.conf;
}
```

### Last selected endpoint variables

In NGINX Plus, `$upstream_last_addr` contains the address or UNIX socket of the
last selected server, and `$upstream_last_server_name` contains its configured
name. The latter is suitable for upstream TLS SNI.

```nginx
proxy_ssl_server_name on;
proxy_ssl_name $upstream_last_server_name;
```

## Upstream client certificates and key logs

### Variable-selected certificate cache

Since 1.27.4, `proxy_ssl_certificate_cache` caches upstream client certificates
and keys selected by variable-bearing filenames. The cache is off until
configured. `max` is its LRU capacity; `inactive` and `valid` default to 10 and
60 seconds.

```nginx
proxy_ssl_certificate       $proxy_ssl_server_name.crt;
proxy_ssl_certificate_key   $proxy_ssl_server_name.key;
proxy_ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Certificates for IP-address backends

FreeNGINX 1.29.1 can verify TLS certificates issued for backend IP addresses.

### Upstream TLS key logging

NGINX Plus 1.27.2 provides `proxy_ssl_key_log` in SSLKEYLOGFILE format. Its
contents can decrypt captured upstream TLS traffic; restrict and remove the
file as secret material.

```nginx
proxy_ssl_key_log /var/log/nginx/upstream.keys;
```
