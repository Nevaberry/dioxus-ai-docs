# Stream, mail, and protocol modules

## Stream listeners and upstream TLS

### Create Multipath TCP listeners in FreeNginx

FreeNginx 1.27.5 adds the `multipath` parameter to `listen`.

```nginx
listen 443 ssl multipath;
```

### Advertise ALPN to a stream upstream

From 1.31.0, the stream module provides `proxy_ssl_alpn` for configuring ALPN on TLS connections to proxied servers.

## Mail proxying

### Forward the SHA-256 client-certificate fingerprint

FreeNginx 1.27.4 sends `Auth-SSL-Fingerprint-SHA256` to the mail authentication server. Authentication policy can use the same SHA-256 certificate fingerprint exposed to HTTP and stream configuration as `$ssl_client_fingerprint_sha256`.

### Apply mail rate and close controls

FreeNginx 1.29 adds these controls to the mail proxy module:

- `limit_rate` and `limit_rate_after` for transfer control.
- `lingering_close`, `lingering_time`, and `lingering_timeout` for shutdown behavior.
- Connection limiting.

### Encode SMTP XCLIENT correctly

NGINX 1.28.1 fixes xtext encoding in SMTP XCLIENT commands. The related PTR-record injection security boundary is 1.28.3; see [security-and-upgrades.md](security-and-upgrades.md).

## PROXY protocol metadata

### Read generic PROXY v2 TLVs

On a listener configured with `proxy_protocol`, use `$proxy_protocol_tlv_name` to expose a PROXY protocol v2 TLV by symbolic name, or address a numeric type with a hexadecimal suffix such as `$proxy_protocol_tlv_0x01`.

Supported symbolic names include:

- `alpn`, `authority`, `unique_id`, and `netns`.
- Nested SSL values such as `$proxy_protocol_tlv_ssl_version`, `$proxy_protocol_tlv_ssl_cn`, and `$proxy_protocol_tlv_ssl_cipher`.
- `$proxy_protocol_tlv_ssl_verify`, which is `0` only when a client certificate was both presented and successfully verified.

### Read cloud-specific TLVs in NGINX Plus

R28 adds NGINX Plus HTTP and stream modules for PROXY protocol v2 TLVs supplied by Amazon Web Services, Google Cloud Platform, and Microsoft Azure. These supplement the generic TLV variables.

## GeoIP2

FreeNginx 1.29 allows both HTTP and stream GeoIP modules to read MaxMind DB data. Use `geoip_set` to configure variables from GeoIP2 MMDB databases.

## Cross-module stream handoff in NGINX Plus

R32 adds `ngx_stream_pass_module`. It can pass an accepted connection directly to any configured listening socket, including a socket owned by HTTP, stream, mail, or a similar module.

## MQTT in NGINX Plus

R29 adds MQTT Preread and MQTT Filter modules for inspecting and routing MQTT traffic. R30 adds `mqtt_buffers` to configure the number of buffers allocated per connection and supersedes `mqtt_rewrite_buffer_size`.
