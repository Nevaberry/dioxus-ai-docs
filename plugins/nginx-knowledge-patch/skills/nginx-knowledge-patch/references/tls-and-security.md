# TLS & Security

## TLSv1/TLSv1.1 Disabled by Default (1.27.3)

`ssl_protocols` now defaults to `TLSv1.2 TLSv1.3` (previously included TLSv1 and TLSv1.1).

If you need legacy protocol support:
```nginx
ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
```

---

## Encrypted Client Hello — ECH (1.29.4)

New `ssl_ech_file` directive enables ECH support:

```nginx
server {
    ssl_ech_file /path/to/ech_config;
}
```

Requires the OpenSSL ECH feature branch (not yet in mainline OpenSSL).

---

## QUIC 0-RTT (1.29.1)

QUIC 0-RTT is now supported. Requires OpenSSL 3.5.1+.

---

## TLS Key Logging (1.29.1)

New `ssl_key_log` directive enables TLS key logging for debugging (e.g., with Wireshark):

```nginx
ssl_key_log /path/to/keylog.txt;
```

---

## Certificate Caching (1.27.4)

New `ssl_certificate_cache` directive provides explicit control over SSL certificate caching behavior.

---

## TLS Signature Algorithm Variables (1.29.3)

Two new variables expose the TLS signature algorithms used in the handshake:

| Variable | Description |
|---|---|
| `$ssl_sigalg` | Signature algorithm used by the server |
| `$ssl_client_sigalg` | Signature algorithm used by the client |
