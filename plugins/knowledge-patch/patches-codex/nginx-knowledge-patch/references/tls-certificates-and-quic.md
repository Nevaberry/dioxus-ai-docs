# TLS, certificates, and QUIC

## Client certificate trust and revocation

### Stream client-certificate OCSP

Since `1.27.2`, stream TLS can validate a client certificate's revocation
status with OCSP. Enable client verification and `ssl_ocsp`, and provide a
resolver for the responder hostname.

```nginx
ssl_client_certificate /etc/nginx/tls/client-ca.pem;
ssl_verify_client on;
ssl_ocsp on;
resolver 192.0.2.53;
```

### Stream server OCSP stapling

Since 1.27.2, stream TLS servers use the familiar stapling controls for their
own certificates.

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/tls/issuer-chain.pem;
resolver 192.0.2.53;
```

### Auxiliary trust data in CA files

Since 1.27.2, `ssl_client_certificate` accepts OpenSSL auxiliary trust data,
including `TRUSTED CERTIFICATE` PEM files, without stripping the attributes.

### Verification without a sent CA list

Since 1.27.2, client-certificate verification no longer requires
`ssl_client_certificate`. Use `ssl_trusted_certificate` alone when the server
should trust a CA without sending that CA list to clients.

```nginx
ssl_verify_client on;
ssl_trusted_certificate /etc/nginx/tls/client-ca.pem;
```

### Shared OCSP cache and responder override

`ssl_ocsp_cache shared:name:size` caches client-certificate OCSP status across
workers and virtual servers and is off by default. `ssl_ocsp_responder`
overrides AIA but accepts only `http://` responders. HTTP has these controls
since 1.19.0 and stream since 1.27.2.

```nginx
ssl_verify_client on;
ssl_ocsp on;
ssl_ocsp_cache shared:client_ocsp:10m;
ssl_ocsp_responder http://ocsp.example.com/;
resolver 192.0.2.53;
```

## Certificate loading and caching

### Server certificate cache

Since 1.27.4, HTTP and stream `ssl_certificate_cache` cache variable-selected
server certificates and keys. The cache is off by default. `max` sets LRU
capacity; `inactive` and `valid` default to 10 and 60 seconds.

```nginx
ssl_certificate       $ssl_server_name.crt;
ssl_certificate_key   $ssl_server_name.key;
ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Hardware-token keys and certificates

NGINX 1.29.0 can load hardware-token secret keys through an OpenSSL provider.
FreeNGINX 1.29.3 can load both certificates and secret keys from hardware
tokens through the OpenSSL STORE API.

### TLS library compatibility

Build compatibility expands to AWS-LC in NGINX 1.29.2 and OpenSSL 4.0 in
1.29.8. Verify build and module requirements before changing TLS libraries.

## Certificate compression and QUIC

### Opt-in certificate compression

Certificate compression is disabled by default from NGINX 1.29.1. Enable it
with `ssl_certificate_compression`. Version 1.29.3 adds BoringSSL support and
disables compression when OCSP stapling is active.

```nginx
ssl_certificate_compression on;
```

### QUIC 0-RTT with OpenSSL

From NGINX 1.29.1, QUIC supports 0-RTT when built with OpenSSL 3.5.1 or newer.

### QUIC handshake log levels

Starting in `1.29.0`, critical QUIC SSL handshake failures log at `crit`, other
SSL handshake failures at `info`, and unsupported QUIC transport parameters at
`debug`. Update alerts that expected previous `error` or `info` severities.

## Encrypted ClientHello

### ECH configuration

Since 1.29.4, `ssl_ech_file` enables ECH using the OpenSSL ECH feature branch.

```nginx
ssl_ech_file /etc/nginx/tls/ech-config.pem;
```

### ECH negotiation variables

With the same ECH build requirement, `$ssl_ech_status` reports `FAILED`,
`BACKEND`, `GREASE`, `SUCCESS`, or `NOT_TRIED`. `$ssl_ech_outer_server_name`
contains the public SNI only when ECH succeeds. Both variables are otherwise
empty.

```nginx
log_format tls '$remote_addr ech=$ssl_ech_status outer=$ssl_ech_outer_server_name';
```

## TLS observability and session behavior

### Signature-algorithm variables

Since 1.29.3, `$ssl_sigalg` and `$ssl_client_sigalg` expose selected signature
algorithms. Since 1.31.2, `$ssl_sigalgs` exposes the algorithm list and is
distinct from the singular variables.

```nginx
log_format tls '$remote_addr sigalg=$ssl_sigalg client="$ssl_client_sigalg" list="$ssl_sigalgs"';
```

### Client-facing TLS key logging

Plus `ssl_key_log`, added in 1.27.2 for HTTP and stream, writes
SSLKEYLOGFILE-format connection secrets. Treat the file as secret material
that permits captured traffic decryption.

```nginx
ssl_key_log /var/log/nginx/client.keys;
```

### FreeNGINX SHA-256 client fingerprints

FreeNGINX 1.27.4 adds `$ssl_client_fingerprint_sha256` for logs and policy.

```nginx
log_format client_cert '$remote_addr fingerprint=$ssl_client_fingerprint_sha256';
```

### FreeNGINX client-auth session isolation

FreeNGINX 1.27.5 prevents session reuse between virtual servers with different
client-verification trust, including different `ssl_trusted_certificate`
values. With OpenSSL 1.1.1e or newer, its TLS 1.3 handling also isolates server
contexts with settings such as `ssl_client_certificate`.

### Hybrid-group reporting

With OpenSSL 3.5, FreeNGINX `$ssl_curve` and `$ssl_curves` report the
`X25519MLKEM768` hybrid group name.

## Server-side stream ALPN

Stream `ssl_alpn` advertises protocols accepted by a TLS server. If the client
sends ALPN, a listed protocol must be negotiated. Use `$ssl_alpn_protocol` to
select a destination.

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
