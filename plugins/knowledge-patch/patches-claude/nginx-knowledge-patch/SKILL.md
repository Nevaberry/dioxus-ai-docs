---
name: nginx-knowledge-patch
description: NGINX
version: "1.31.0"
license: MIT
metadata:
  author: Nevaberry
---


# NGINX Knowledge Patch

Use this skill when configuring, upgrading, building, or operating NGINX Open
Source, FreeNGINX, or NGINX Plus. Select the product line before applying a
directive: fork-specific and commercial features are labeled and are not
portable to a standard open-source build.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-upgrades.md](references/security-and-upgrades.md) | CVEs, fixed-version boundaries, request hardening, unsafe legacy behavior |
| [core-http-and-runtime.md](references/core-http-and-runtime.md) | listeners, core HTTP behavior, variables, filters, limits, builds |
| [upstreams-and-proxying.md](references/upstreams-and-proxying.md) | keepalive, runtime DNS, balancing, retries, HTTP/2 backends, trailers, caches |
| [tls-certificates-and-quic.md](references/tls-certificates-and-quic.md) | trust, OCSP, certificates, ECH, TLS observability, QUIC |
| [stream-mail-and-protocols.md](references/stream-mail-and-protocols.md) | stream TLS, mail proxying, PROXY protocol, GeoIP2, MQTT, listener handoff |
| [nginx-plus-operations.md](references/nginx-plus-operations.md) | support lifecycle, licensing, platforms, images, OIDC, ACME, API, key-value data |

## Upgrade and security gates

Check the exact product, branch, enabled modules, and patch release before
changing configuration. A feature release number alone does not establish that
all later security fixes are present.

- Upgrade HTTP/3 deployments across the applicable memory-safety floors before
  tuning QUIC. In particular, do not run an affected pre-1.31.2 build with
  HTTP/3 enabled.
- Treat initial 1.29 and 1.30 releases as missing later same-branch security
  fixes. Match the affected configuration to the per-CVE table in
  [security-and-upgrades.md](references/security-and-upgrades.md).
- Upgrade TLS client-authentication deployments affected by cross-server
  session reuse before relying on configuration changes as mitigation.
- Preserve the documented older-branch floors when maintaining a legacy
  installation; do not infer them from current release numbering.

## Breaking changes and defaults

### Upstream keepalive and proxy HTTP defaults

Since 1.29.7, upstream and proxied keepalive are enabled by default, HTTP
proxying defaults to HTTP/1.1, and NGINX no longer sends a `Connection` proxy
header by default. The `local` parameter scopes an explicitly configured
upstream keepalive cache. Disable caching explicitly when required.

```nginx
upstream backend {
    server 127.0.0.1:8080;
    keepalive 64 local;
}
```

### Strict protocol parsing

Current HTTP/2 and HTTP/3 handling rejects `Connection`,
`Proxy-Connection`, `Keep-Alive`, `Transfer-Encoding`, and `Upgrade`. `TE` is
valid only as `trailers`. Newer request parsing also validates authority syntax
strictly and rejects a lone LF in chunked bodies. Remove hop-by-hop fields in
protocol translators and test nonconforming peers before upgrading.

### FreeNGINX proxy and rate semantics

FreeNGINX 1.29.1 rejects proxied HTTP/0.9 responses by default, ignores interim
1xx responses, and provides compatibility switches for HTTP/0.9 and duplicate
chunked encoding. FreeNGINX 1.29.0 changes `limit_rate` to a leaky-bucket
algorithm and treats `limit_rate_after` as its burst allowance. Recheck existing
throughput tuning.

### Configure and module migrations

- Use `--without-http_upstream_sticky_module`; the shorter legacy option is
  deprecated.
- In NGINX Plus, replace `mqtt_rewrite_buffer_size` with `mqtt_buffers`.
- In NGINX Plus, migrate OpenTracing packages to OpenTelemetry; OpenTracing is
  unavailable from R34.
- In FreeNGINX, enable `xml_external_entities` only for trusted XSLT workloads
  that intentionally need external entities declared in an internal DTD.

### NGINX Plus licensing

From R33, each instance needs a JWT license token and hourly usage reporting
over a verified connection. The initial report after installation or upgrade
is traffic-critical unless the optional 180-day `enforce_initial_report` grace
period is enabled. Plan a direct path, report proxy, or Instance Manager relay
before deployment.

## High-use configuration patterns

### Resolve ordinary upstreams at runtime

Standard builds support upstream `resolver`, `resolver_timeout`, and server
parameters `resolve` and `service`. Put dynamically resolved groups in shared
memory with `zone`. For SRV discovery, use a portless hostname; the lowest
numeric priority is primary and later priorities are backups.

```nginx
upstream api {
    zone api 64k;
    resolver 192.0.2.53 valid=30s;
    resolver_timeout 5s;
    server api.example.com service=http resolve;
}
```

### Proxy to HTTP/2 backends

Select HTTP/2 upstream proxying explicitly and build with
`ngx_http_v2_module`.

```nginx
location / {
    proxy_http_version 2;
    proxy_pass https://backend;
}
```

### Forward response trailers

Enable trailer forwarding and advertise support to an HTTP/1.1 backend.

```nginx
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "te";
    proxy_set_header TE "trailers";
    proxy_pass_trailers on;
}
```

### Forward Early Hints

NGINX accepts HTTP 103 responses from proxy and gRPC backends. Use
`early_hints` to control whether they reach the client before the final
response.

```nginx
location / {
    proxy_pass http://backend;
    early_hints on;
}
```

### Cache variable-selected certificates

`ssl_certificate_cache` and `proxy_ssl_certificate_cache` avoid loading
variable-selected certificate files for every handshake. Both are off until
configured; `inactive` and `valid` default to 10 seconds and 60 seconds.

```nginx
ssl_certificate       $ssl_server_name.crt;
ssl_certificate_key   $ssl_server_name.key;
ssl_certificate_cache max=1000 inactive=20s valid=1m;

proxy_ssl_certificate       $proxy_ssl_server_name.crt;
proxy_ssl_certificate_key   $proxy_ssl_server_name.key;
proxy_ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Preserve request authority

Use `$host$is_request_port$request_port` to retain an explicitly supplied port
without appending a colon when the request had no port.

```nginx
proxy_set_header Host $host$is_request_port$request_port;
```

### Choose upstreams by response time

Use `least_time` in an `upstream` block when observed response latency is a
better selection signal than round robin or active connection count.

```nginx
upstream backend {
    least_time header;
    server 192.0.2.10:8080;
    server 192.0.2.11:8080;
}
```

### Configure stream ALPN

Use `proxy_ssl_alpn` to advertise ALPN protocols on TLS connections from a
stream proxy to its upstream. Use server-side `ssl_alpn` and
`$ssl_alpn_protocol` when the client-facing stream listener selects a backend.

### Configure ECH carefully

`ssl_ech_file` loads a PEM `ECHConfig` and currently requires the OpenSSL ECH
feature branch. Diagnose negotiation with `$ssl_ech_status` and
`$ssl_ech_outer_server_name`.

## Operational checks

- Revisit log alerts after QUIC and SSL handshake severity changes; failures
  that moved from `crit` or `error` to `info` can otherwise disappear.
- Check TLS-library requirements before enabling certificate compression, ECH,
  signature-algorithm variables, or QUIC 0-RTT.
- Remember that `max_conns` without `zone` is per worker and that cached idle
  connections can make totals exceed the configured number.
- Protect `ssl_key_log` and `proxy_ssl_key_log` output as decryption secrets.
- Confirm the supported operating-system matrix before a Plus upgrade.
