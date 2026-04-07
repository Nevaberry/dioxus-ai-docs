# OpenSSL 4.0 Migration Guide

OpenSSL 4.0 is a major release with several breaking changes. Code targeting OpenSSL 3.x may need updates.

## Breaking Changes

### Engines fully removed

`OPENSSL_NO_ENGINE` is always defined. All engine-based code must be migrated to the provider API. Engine headers and functions are gone — not deprecated, removed.

### SSLv3 removed

SSLv3 is completely removed from the codebase, not just disabled. Any code referencing SSLv3 methods or constants will fail to compile.

### `c_rehash` removed

The Perl `c_rehash` script is gone. Use the built-in command instead:

```bash
openssl rehash /path/to/certs
```

### `ASN1_STRING` opaque

The `ASN1_STRING` struct can no longer be accessed directly. Use accessor functions:
- `ASN1_STRING_get0_data()` instead of direct `.data` access
- `ASN1_STRING_length()` instead of direct `.length` access

### Deprecated EC curves disabled by default

Previously deprecated EC curves are now disabled. To re-enable for legacy compatibility:

```
# In openssl.cnf or build config
enable-tls-deprecated-ec
```

## New Features in 4.0

### Encrypted Client Hello (ECH)

RFC 9849 support. ECH encrypts the ClientHello SNI extension, preventing network observers from seeing which server name the client is connecting to. See `doc/designs/ech-api.md` in the OpenSSL source for API details.

### FFDHE in TLS 1.2

Negotiated finite-field Diffie-Hellman ephemeral key exchange per RFC 7919, now available in TLS 1.2 (previously TLS 1.3 only).
