# TLS, certificates, and QUIC

## Contents

- [Client trust, OCSP, and sessions](#client-trust-ocsp-and-sessions)
- [Keys and certificate identity](#keys-and-certificate-identity)
- [TLS 1.3 features](#tls-13-features)
- [TLS variables and fingerprints](#tls-variables-and-fingerprints)
- [TLS and QUIC observability](#tls-and-quic-observability)
- [Library compatibility](#library-compatibility)

## Client trust, OCSP, and sessions

### Use OCSP in stream TLS

From 1.27.2, the stream module can validate client certificates with OCSP and staple OCSP responses for its own server certificates. Both client-side validation and server-side stapling are therefore available for TCP/UDP TLS proxying.

### Configure client trust without a client CA bundle

From 1.27.2, `ssl_client_certificate` accepts certificates that carry auxiliary information. Client-certificate verification no longer requires this directive to be configured, allowing other trust configuration patterns.

### Keep resumed sessions within the trust context

FreeNginx 1.27 prevents SSL session reuse between virtual servers whose `ssl_trusted_certificate` certificates differ when client-certificate verification is enabled. A resumed session remains associated with the applicable verification store.

### Cache larger shared sessions

NGINX 1.27.5 raises the maximum SSL session size stored in a shared-memory cache to 8192, allowing larger TLS sessions to remain cacheable.

## Keys and certificate identity

### Keep private keys in an OpenSSL provider

From 1.29.0, secret keys can be loaded from hardware tokens through an OpenSSL provider. Use provider-backed keys when private key material must remain in hardware rather than ordinary key files.

### Verify an upstream by IP address

FreeNginx 1.29 supports backend certificates issued for IP addresses. Verified HTTPS proxying can use an IP identity instead of requiring a DNS name.

### Cache variable-selected server certificates

Since 1.27.4, `ssl_certificate_cache` works in both HTTP and stream servers. It caches server certificates and keys selected through variables. `max` is the LRU capacity; `inactive` and `valid` default to 10 seconds and 60 seconds. The cache is off until configured.

```nginx
ssl_certificate       $ssl_server_name.crt;
ssl_certificate_key   $ssl_server_name.key;
ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

For variable-selected client certificates used toward an upstream, configure `proxy_ssl_certificate_cache`; see [upstreams-and-proxying.md](upstreams-and-proxying.md).

## TLS 1.3 features

### Compress server certificates

Since 1.29.1, `ssl_certificate_compression on;` enables TLS 1.3 server-certificate compression in HTTP and stream servers. It is off by default and requires OpenSSL 3.2 or newer. BoringSSL support includes `zlib` from 1.29.3.

```nginx
ssl_certificate_compression on;
```

### Configure NGINX ECH shared mode

NGINX 1.29.4 adds `ssl_ech_file` in HTTP and stream servers. It loads a PEM `ECHConfig` for TLS 1.3 Encrypted ClientHello shared mode and currently requires the OpenSSL ECH feature branch.

```nginx
ssl_ech_file /etc/nginx/echconfig.pem;
```

Use the ECH variables for observability:

- `$ssl_ech_outer_server_name` exposes the public SNI name only when ECH is accepted.
- `$ssl_ech_status` reports `FAILED`, `BACKEND`, `GREASE`, `SUCCESS`, or `NOT_TRIED`.

### Distinguish FreeNginx ECH support

FreeNginx 1.29.2 adds TLS 1.3 ECH separately. Do not assume that NGINX's `ssl_ech_file`, status values, or build constraint apply unchanged to the fork.

## TLS variables and fingerprints

### Inspect TLS signature algorithms

From 1.31.0, `$ssl_sigalgs` exposes TLS signature-algorithm information to configuration.

### Inspect certificate signature algorithms

Since 1.29.3, `$ssl_sigalg` reports the server certificate's signature algorithm and `$ssl_client_sigalg` reports the client certificate's signature algorithm in HTTP and stream. Both variables require OpenSSL 3.5 or newer, are populated only for new sessions, and remain empty with older OpenSSL releases.

```nginx
log_format tls '$ssl_sigalg $ssl_client_sigalg';
```

Do not confuse the singular certificate variables with the plural `$ssl_sigalgs` handshake information.

### Record a SHA-256 client-certificate fingerprint

FreeNginx 1.27.4 adds `$ssl_client_fingerprint_sha256` for configuration and logging. The mail proxy also forwards the value to its authentication server; see [stream-mail-and-protocols.md](stream-mail-and-protocols.md).

### Recognize OpenSSL 3.5 hybrid groups

With OpenSSL 3.5, FreeNginx reports `X25519MLKEM768` through `$ssl_curve` and `$ssl_curves`, allowing curve logging and policy to recognize the hybrid group.

## TLS and QUIC observability

### Protect client-facing key logs

Since 1.27.2, NGINX Plus `ssl_key_log` writes client-connection secrets in SSLKEYLOGFILE format from HTTP and stream servers. Treat this output as sensitive key material.

```nginx
ssl_key_log /var/log/nginx/client.keys;
```

Use NGINX Plus `proxy_ssl_key_log` for the upstream side.

### Update QUIC log-level expectations

From 1.29.0, critical SSL errors during a QUIC handshake are logged at `crit`, while other SSL errors are logged at `info`. Unsupported QUIC transport parameters move from `info` to `debug`. Adjust monitoring that matched the previous levels.

### Update generic SSL alert expectations

From 1.31.0, `invalid alert`, `record layer failure`, and numbered `SSL alert number N` errors are logged at `info` instead of `crit`.

## Library compatibility

FreeNginx 1.29.7 adds OpenSSL 4.0 compatibility. Check this boundary when building or upgrading against the new OpenSSL major release.
