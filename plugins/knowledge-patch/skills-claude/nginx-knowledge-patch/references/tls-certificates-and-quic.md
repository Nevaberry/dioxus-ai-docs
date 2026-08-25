# TLS, certificates, and QUIC

## Client-certificate trust and OCSP

### Auxiliary trust data in CA files

Since 1.27.2, `ssl_client_certificate` accepts certificates with OpenSSL
auxiliary trust information, including `TRUSTED CERTIFICATE` PEM data. Such CA
files no longer need their trust attributes stripped.

### Verification without advertising a CA list

Client verification no longer requires `ssl_client_certificate`. A trust store
can be configured with `ssl_trusted_certificate` without sending its CA list to
clients.

```nginx
ssl_verify_client on;
ssl_trusted_certificate /etc/nginx/tls/client-ca.pem;
```

### Stream client-certificate OCSP validation

Since 1.27.2, stream TLS can check a client certificate's revocation status.
Enable verification and `ssl_ocsp`, and configure a resolver for responder
hostnames.

```nginx
ssl_client_certificate /etc/nginx/tls/client-ca.pem;
ssl_verify_client on;
ssl_ocsp on;
resolver 192.0.2.53;
```

### OCSP caching and responder override

`ssl_ocsp_cache shared:name:size` caches client-certificate status across
workers and virtual servers and is off by default. `ssl_ocsp_responder`
overrides the certificate's Authority Information Access URL but supports only
`http://`. These controls exist for HTTP since 1.19.0 and stream since 1.27.2.

```nginx
ssl_verify_client on;
ssl_ocsp on;
ssl_ocsp_cache shared:client_ocsp:10m;
ssl_ocsp_responder http://ocsp.example.com/;
resolver 192.0.2.53;
```

## Server-certificate stapling and loading

### OCSP stapling in stream servers

Since 1.27.2, stream TLS servers support the same server-certificate stapling
controls as HTTP TLS servers.

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/tls/issuer-chain.pem;
resolver 192.0.2.53;
```

### Variable-selected server certificate cache

Since 1.27.4, `ssl_certificate_cache` caches variable-selected server
certificates and keys in HTTP and stream. It is off by default. `max` controls
LRU capacity; `inactive` and `valid` default to 10 and 60 seconds.

```nginx
ssl_certificate       $ssl_server_name.crt;
ssl_certificate_key   $ssl_server_name.key;
ssl_certificate_cache max=1000 inactive=20s valid=1m;
```

### Provider and TLS-library support

NGINX 1.29.0 can load hardware-token secret keys through an OpenSSL provider.
Build compatibility extends to AWS-LC in 1.29.2 and OpenSSL 4.0 in 1.29.8.
FreeNGINX 1.29.3 separately supports loading both certificates and secret keys
from hardware tokens through the OpenSSL STORE API.

### Certificate compression

Certificate compression is disabled by default since 1.29.1. Enable it with
`ssl_certificate_compression`. Version 1.29.3 adds BoringSSL support and
disables compression when OCSP stapling is active.

```nginx
ssl_certificate_compression on;
```

## Encrypted ClientHello

### ECH configuration

Since 1.29.4, `ssl_ech_file` loads a PEM `ECHConfig` when NGINX is built with
the OpenSSL ECH feature branch.

```nginx
ssl_ech_file /etc/nginx/tls/ech-config.pem;
```

### ECH observability

Since 1.29.4, `$ssl_ech_status` is `FAILED`, `BACKEND`, `GREASE`, `SUCCESS`, or
`NOT_TRIED`. `$ssl_ech_outer_server_name` contains the public SNI only when ECH
was accepted. Both require the OpenSSL ECH feature branch and otherwise remain
empty.

```nginx
log_format tls '$remote_addr ech=$ssl_ech_status outer=$ssl_ech_outer_server_name';
```

## Signature algorithms and certificate fingerprints

### Signature-algorithm variables

Since 1.29.3, `$ssl_sigalg` and `$ssl_client_sigalg` expose the negotiated
server and client signature algorithms. Since 1.31.2, `$ssl_sigalgs` exposes
the signature-algorithm list and is distinct from the singular variables.

```nginx
log_format tls '$remote_addr sigalg=$ssl_sigalg client_sigalg="$ssl_client_sigalg" sigalgs="$ssl_sigalgs"';
```

### FreeNGINX SHA-256 client fingerprint

FreeNGINX 1.27.4 adds `$ssl_client_fingerprint_sha256` for logging and policy
without relying on an older digest.

```nginx
log_format client_cert '$remote_addr fingerprint=$ssl_client_fingerprint_sha256';
```

### FreeNGINX hybrid-group reporting

With OpenSSL 3.5, FreeNGINX `$ssl_curve` and `$ssl_curves` report the
`X25519MLKEM768` group name, making hybrid key exchange visible to logs and
configuration logic.

## Session isolation and QUIC

### FreeNGINX client-auth session isolation

FreeNGINX 1.27.5 prevents SSL session reuse between virtual servers whose
client-verification trust differs, including different
`ssl_trusted_certificate` files. With OpenSSL 1.1.1e or newer, its TLS 1.3
handling also prevents reuse across server contexts with differing settings
such as `ssl_client_certificate`.

### QUIC 0-RTT with OpenSSL

Since 1.29.1, QUIC can use 0-RTT when NGINX is built with OpenSSL 3.5.1 or
newer.

## TLS logging

### QUIC handshake severities

Since 1.29.0, critical QUIC SSL handshake failures log at `crit`, other SSL
handshake failures at `info`, and unsupported QUIC transport parameters at
`debug`. Update monitoring that expected the former `error` or `info` levels.

### SSL alert severity

Since 1.31.0, `invalid alert`, `record layer failure`, and numbered SSL alerts
log at `info` instead of `crit`. Do not let critical-only alerting hide them.

### Client-facing key logging in NGINX Plus

NGINX Plus 1.27.2 provides `ssl_key_log` in HTTP and stream, writing
SSLKEYLOGFILE data that can decrypt captured traffic. Restrict the file as
secret material.

```nginx
ssl_key_log /var/log/nginx/client.keys;
```
