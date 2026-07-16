# Upstreams and proxying

## Contents

- [Connection reuse and limits](#connection-reuse-and-limits)
- [Discovery, persistence, and balancing](#discovery-persistence-and-balancing)
- [HTTP protocol features](#http-protocol-features)
- [Retries and response acceptance](#retries-and-response-acceptance)
- [Per-attempt controls](#per-attempt-controls)
- [Upstream TLS configuration](#upstream-tls-configuration)
- [Correctness fixes](#correctness-fixes)

## Connection reuse and limits

### Account for default upstream keepalive

Since 1.29.7, upstream connection caching defaults to `keepalive 32 local;` per worker. The number limits idle cached connections, not every open upstream connection. `local` prevents reuse across different locations even when they resolve to the same server address; omit `local` to permit such reuse, or set `keepalive 0` to disable caching.

```nginx
upstream backend {
    server 127.0.0.1:8080;
    keepalive 64 local;
}
```

HTTP upstream proxying also defaults to HTTP/1.1 from 1.29.7. The older explicit `proxy_http_version 1.1` plus cleared `Connection` header pattern is needed only on earlier versions.

### Understand connection caps

Without an upstream `zone`, `max_conns` is enforced separately by each worker. Even with a zone, cached idle connections mean the total of active and idle connections can exceed `max_conns`.

NGINX Plus `queue` holds requests when no server can be selected immediately. NGINX returns 502 if the queue fills or its timeout expires.

```nginx
upstream backend {
    zone backend 64k;
    server 192.0.2.10:8080 max_conns=100;
    queue 200 timeout=10s;
}
```

In a group containing only one server, NGINX ignores `max_fails`, `fail_timeout`, and `slow_start` and never marks that server unavailable.

## Discovery, persistence, and balancing

### Resolve upstream servers at runtime

From 1.27.3, ordinary builds support upstream-level `resolver` and `resolver_timeout`, plus server parameters `resolve` and SRV-oriented `service`. A dynamically resolved group must use shared memory with `zone`.

```nginx
upstream api {
    zone api 64k;
    resolver 10.0.0.53 valid=30s;
    resolver_timeout 5s;
    server api.example.com resolve;
}
```

For SRV discovery, add a service such as `service=http` to query `_http._tcp`. Records at the lowest numeric priority become primary servers; records at other priorities become backups.

### Persist dynamically managed servers in NGINX Plus

The NGINX Plus `state` directive persists a dynamically managed upstream's server list and parameters. Do not combine it with static `server` directives or edit its file manually. Changes made during reload or binary upgrade can be lost.

```nginx
upstream backend {
    zone backend 64k;
    state /var/lib/nginx/state/servers.conf;
}
```

### Use sticky sessions and draining in standard builds

Since 1.29.6, `sticky` and the upstream-server parameters `route` and `drain` are available outside NGINX Plus. `sticky` can use an NGINX-generated cookie, an application-provided route, or a learned server-created session. A drained server receives only requests already bound to it.

```nginx
upstream backend {
    server backend1.example.com route=a;
    server backend2.example.com route=b;
    sticky cookie srv_id httponly secure samesite=lax;
}
```

Use the configure option `--without-http_upstream_sticky_module` to disable the module. The older `--without-http_upstream_sticky` spelling is deprecated from 1.31.0.

### Balance by response time

From 1.31.0, `least_time` is available in `upstream` blocks for response-time-based backend selection.

### Inspect the final selected endpoint in NGINX Plus

NGINX Plus provides:

- `$upstream_last_addr` since 1.29.3: address or UNIX socket of the last selected server.
- `$upstream_last_server_name` since 1.25.3: configured name of the last selected server.

Use the configured name for upstream TLS SNI when selection and retries can change the target.

```nginx
proxy_ssl_server_name on;
proxy_ssl_name $upstream_last_server_name;
```

## HTTP protocol features

### Proxy to HTTP/2 backends

Since 1.29.4, `proxy_http_version 2;` sends proxied requests to HTTP/2 backends. Include `ngx_http_v2_module` in the build.

### Forward response trailers

Since 1.27.2, `proxy_pass_trailers on;` allows upstream response trailers to reach the client. Advertise trailer handling to the upstream as well.

```nginx
proxy_set_header Connection "te";
proxy_set_header TE "trailers";
proxy_pass_trailers on;
```

### Pass Early Hints

From 1.29.0, NGINX handles HTTP 103 responses from proxy and gRPC backends. Use `early_hints` to control whether an upstream's preliminary hints are delivered before its final response.

### Authenticate HTTP proxy use and tunnel traffic

From 1.31.0, NGINX includes `ngx_http_tunnel_module`. The `auth_basic`, `satisfy`, and `auth_delay` directives can also authenticate proxy use.

## Retries and response acceptance

### Count a terminal response as a failure

Since FreeNginx 1.29.5, a 500, 502, 503, 504, or 429 named in `proxy_next_upstream` still marks the upstream failed when no next server is available. In the same situation, FreeNginx honors the `stale-if-error` Cache-Control extension.

### Control legacy or malformed backend responses

FreeNginx 1.29.1 rejects HTTP/0.9 responses from proxied servers by default; `proxy_allow_http09` opts in. It ignores interim 1xx responses and adds `proxy_allow_duplicate_chunked` to control acceptance of duplicate chunked encoding.

## Per-attempt controls

### Recreate the request for every backend

NGINX Plus `proxy_request_dynamic on;` creates a separate request instance for every attempted backend. Request fields can therefore depend on the selected server rather than being frozen before retries.

```nginx
proxy_request_dynamic on;
proxy_set_header Host $upstream_last_server_name;
```

### Admit backends conditionally

NGINX Plus `proxy_allow_upstream` evaluates each variable-capable condition before a connection attempt. It allows the backend only when every value is nonempty and not `0`. A denial counts as an unsuccessful attempt; include `denied` in `proxy_next_upstream` to try another server.

```nginx
proxy_allow_upstream $allow;
proxy_next_upstream error timeout denied;
```

### Bind each connection attempt

NGINX Plus `proxy_bind_dynamic on;` performs the configured `proxy_bind` operation for every connection attempt instead of once for the entire proxied request.

### Set a variable read limit

Since 1.27.0, `proxy_limit_rate` accepts variables. It limits upstream response reads per request and takes effect only when proxy response buffering is enabled.

```nginx
proxy_limit_rate $upstream_read_rate;
```

## Upstream TLS configuration

### Cache variable-selected client certificates

Since 1.27.4, `proxy_ssl_certificate_cache` caches client certificates and keys whose file names use variables. `max` sets the LRU capacity; `inactive` and `valid` default to 10 seconds and 60 seconds.

```nginx
proxy_ssl_certificate       $proxy_ssl_server_name.crt;
proxy_ssl_certificate_key   $proxy_ssl_server_name.key;
proxy_ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Load encrypted variable-selected keys

NGINX 1.27.5 fixes variable-based certificate and encrypted-key loading when passwords come from `grpc_ssl_password_file`, `proxy_ssl_password_file`, or `uwsgi_ssl_password_file`. This dynamic upstream TLS setup had been broken since 1.23.1.

### Log upstream TLS keys in NGINX Plus

Since 1.27.2, NGINX Plus `proxy_ssl_key_log` writes proxied HTTPS connection secrets in SSLKEYLOGFILE format for tools such as Wireshark. Protect the output as key material.

```nginx
proxy_ssl_key_log /var/log/nginx/upstream.keys;
```

## Correctness fixes

### Avoid configuration and failover crashes

- NGINX 1.28.1 fixes a worker crash when `try_files` is combined with a URI-bearing `proxy_pass`.
- NGINX 1.28.2 fixes a use-after-free after switching to the next gRPC or HTTP/2 backend.

### Retain HTTP/2 backend connections

NGINX 1.30.1 restores caching of HTTP/2 backend connections when `proxy_set_body` or `proxy_pass_request_body` is used.
