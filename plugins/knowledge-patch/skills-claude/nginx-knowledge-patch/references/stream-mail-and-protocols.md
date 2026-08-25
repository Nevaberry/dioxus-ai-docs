# Stream, mail, and protocol modules

## Stream TLS protocol selection

### Client-facing ALPN selection

The stream SSL module's `ssl_alpn` advertises protocols supported by a TLS
server. If the client offers ALPN, one of those protocols must be negotiated.
Use `$ssl_alpn_protocol` to select a destination.

```nginx
map $ssl_alpn_protocol $backend {
    h2       127.0.0.1:8001;
    http/1.1 127.0.0.1:8002;
}

server {
    listen 443 ssl;
    ssl_alpn h2 http/1.1;
    proxy_pass $backend;
}
```

### Upstream ALPN

Since 1.31.0, `proxy_ssl_alpn` advertises ALPN protocols on a stream proxy's
TLS connection to its upstream.

```nginx
stream {
    server {
        listen 8443;
        proxy_pass 192.0.2.10:443;
        proxy_ssl on;
        proxy_ssl_alpn h2;
    }
}
```

## PROXY protocol

### Named TLV variables

On a `proxy_protocol` listener, `$proxy_protocol_tlv_name` exposes a PROXY v2
TLV by supported symbolic name or hexadecimal type. Names include `alpn`,
`authority`, `unique_id`, `netns`, and nested SSL fields.
`$proxy_protocol_tlv_ssl_verify` is `0` only when a client certificate was
present and verification succeeded.

```nginx
listen 443 proxy_protocol;
log_format proxy '$proxy_protocol_tlv_alpn $proxy_protocol_tlv_ssl_cn';
```

### PROXY v2 from stream and mail proxies

Since 1.31.4, the `proxy_protocol` directive in stream and mail supports
PROXY protocol version 2, allowing those proxy paths to send the v2 wire format
to peers that require it.

### Cloud metadata in NGINX Plus

NGINX Plus R28 adds HTTP and stream modules that expose cloud-provider-specific
PROXY protocol v2 TLVs as variables. Use them only when a supported cloud load
balancer supplies the matching metadata.

## Mail proxy controls

### SHA-256 certificate identity in auth requests

FreeNGINX 1.27 mail authentication requests include
`Auth-SSL-Fingerprint-SHA256`, allowing the authentication server to identify
a presented client certificate with its SHA-256 fingerprint.

### Rates, lingering close, and connections

FreeNGINX 1.29.0 adds `limit_rate`, `limit_rate_after`, `lingering_close`,
`lingering_time`, and `lingering_timeout` to the mail proxy module, together
with connection limiting. Revalidate throughput and close behavior after
enabling them.

## GeoIP2

FreeNGINX 1.29.4 adds MaxMind DB GeoIP2 support to both
`ngx_http_geoip_module` and `ngx_stream_geoip_module`, together with the
`geoip_set` directive.

## NGINX Plus stream handoff and virtual servers

R32 adds `stream_pass`, which hands an accepted connection directly to a
configured listening socket in HTTP, stream, mail, or a similar module. It also
adds name-based stream virtual servers. Stream listeners gain `deferred`,
`accept_filter`, and `setfib` parameters.

## NGINX Plus MQTT modules

R29 packages MQTT Preread and MQTT Filter modules for stream traffic. R30 adds
`mqtt_buffers` for per-connection allocation; use it instead of the older
`mqtt_rewrite_buffer_size`.
