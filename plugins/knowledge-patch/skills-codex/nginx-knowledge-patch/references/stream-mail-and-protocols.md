# Stream, mail, and protocol modules

## Stream and mail proxying

### PROXY protocol v2 to upstream peers

Since `1.31.4`, the `proxy_protocol` directive in stream and mail supports
PROXY protocol version 2, enabling upstream connections to peers that require
the v2 wire format.

### ALPN to stream TLS upstreams

Since `1.31.0`, `proxy_ssl_alpn` advertises ALPN protocols when the stream proxy
negotiates TLS with an upstream.

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

### FreeNGINX mail rate and connection controls

FreeNGINX 1.29.0 adds mail-proxy `limit_rate`, `limit_rate_after`,
`lingering_close`, `lingering_time`, `lingering_timeout`, and connection
limiting.

### SHA-256 fingerprints in mail authentication

FreeNGINX 1.27 mail authentication requests include
`Auth-SSL-Fingerprint-SHA256`, allowing the authentication server to identify
the client certificate using its SHA-256 fingerprint.

## PROXY protocol metadata

### Generic PROXY v2 TLV variables

On a `proxy_protocol` listener, `$proxy_protocol_tlv_name` reads a supported
symbolic or hexadecimal PROXY v2 TLV type. Names include `alpn`, `authority`,
`unique_id`, `netns`, and nested SSL fields. `$proxy_protocol_tlv_ssl_verify`
is `0` only when a client certificate was presented and verification succeeded.

```nginx
listen 443 proxy_protocol;
log_format proxy '$proxy_protocol_tlv_alpn $proxy_protocol_tlv_ssl_cn';
```

### Cloud-provider TLVs

Plus R28 adds HTTP and stream modules that expose supported cloud load
balancer-specific PROXY v2 TLVs as variables.

## GeoIP2

FreeNGINX 1.29.4 adds MaxMind DB GeoIP2 support to both
`ngx_http_geoip_module` and `ngx_stream_geoip_module`, together with the
`geoip_set` directive.

## Stream listener handoff and virtual servers

Plus R32 adds `stream_pass`, which hands an accepted connection to a configured
listening socket in HTTP, stream, mail, or a similar module. The same release
adds name-based stream virtual servers and `deferred`, `accept_filter`, and
`setfib` stream-listener parameters.

## MQTT modules

Plus R29 packages MQTT Preread and MQTT Filter for stream traffic. R30 adds
`mqtt_buffers` for per-connection allocation; use it instead of
`mqtt_rewrite_buffer_size`.
