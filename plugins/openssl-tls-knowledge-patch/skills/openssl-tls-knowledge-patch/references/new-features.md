# New Features in OpenSSL 3.5–3.6

## QUIC Server (3.5)

OpenSSL 3.5 adds server-side QUIC support (RFC 9000).

### Basic usage

```c
// Create QUIC server context
SSL_CTX *ctx = SSL_CTX_new(OSSL_QUIC_server_method());

// Accept incoming QUIC connection
SSL *conn = SSL_accept_connection(ssl, 0);

// Complete handshake
SSL_do_handshake(conn);
```

**Note**: `SSL_accept()` on accepted connections was broken in 3.5.0 (fixed in 3.5.1). Use `SSL_do_handshake()` instead for portability.

### External QUIC stacks

For integrating OpenSSL's TLS handshake with a custom QUIC implementation:

```c
// Use just the TLS handshake with a custom record layer
SSL_set_quic_tls_cbs(ssl, ...);
```

## Default Cipher Changes (3.5)

`req`, `cms`, and `smime` apps changed default cipher from `des-ede3-cbc` to `aes-256-cbc`.

**Migration**: Existing scripts relying on 3DES default should specify `-aes-256-cbc` explicitly for cross-version portability:

```bash
# Explicit cipher for portability across 3.4 and 3.5+
openssl req -new -key key.pem -out req.pem -aes-256-cbc
openssl cms -encrypt -aes-256-cbc -in msg.txt -out msg.cms cert.pem
```

## OpenSSL 3.6 (Oct 2025)

### LMS Signature Verification

NIST SP 800-208 Leighton-Micali Signature (LMS) verification support in both FIPS and default providers. Hash-based stateful signatures primarily used for firmware and code signing verification.

### EVP_SKEY Expansion

New APIs for opaque symmetric key derivation:

- `EVP_KDF_CTX_set_SKEY()` — set an opaque symmetric key on a KDF context
- `EVP_KDF_derive_SKEY()` — derive an opaque symmetric key from a KDF
- `EVP_PKEY_derive_SKEY()` — derive an opaque symmetric key from a key agreement

### `openssl configutl`

New utility to dump processed configuration files, useful for debugging `openssl.cnf` includes and variable expansion.

```bash
openssl configutl -dump openssl.cnf
```

### FIPS 186-5 Deterministic ECDSA

Deterministic ECDSA (RFC 6979) now available in the FIPS provider, producing reproducible signatures for the same message and key.
