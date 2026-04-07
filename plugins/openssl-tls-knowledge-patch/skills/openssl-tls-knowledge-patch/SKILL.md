---
name: openssl-tls-knowledge-patch
description: "OpenSSL/TLS changes since training cutoff (3.4–4.0) — post-quantum cryptography, hybrid PQC TLS, QUIC server, OpenSSL 4.0 migration. Load before working with OpenSSL or TLS configuration."
version: "4.0.0"
license: MIT
metadata:
  author: Nevaberry
---

# OpenSSL-TLS Knowledge Patch

Covers OpenSSL 3.4–4.0 (2024-10-22 through 2026-04-07). Claude knows OpenSSL CLI basics through 3.0, TLS 1.2/1.3, certificate generation and management. It is **unaware** of post-quantum cryptography support, QUIC server APIs, and OpenSSL 4.0 breaking changes.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Post-quantum cryptography | [references/pqc-cryptography.md](references/pqc-cryptography.md) | ML-DSA/ML-KEM/SLH-DSA key generation, hybrid PQC TLS groups, group syntax |
| OpenSSL 4.0 migration | [references/openssl4-migration.md](references/openssl4-migration.md) | Engines removed, SSLv3 gone, ECH, opaque ASN1_STRING, deprecated EC curves |
| New features (3.5–3.6) | [references/new-features.md](references/new-features.md) | QUIC server, default cipher changes, LMS verification, EVP_SKEY, configutl |

---

## PQC Algorithm Quick Reference (OpenSSL 3.5+)

OpenSSL 3.5 adds native FIPS 203/204/205 post-quantum algorithms.

| Algorithm | Standard | Type | `genpkey -algorithm` names |
|---|---|---|---|
| ML-DSA | FIPS 204 | Signatures | `ML-DSA-44`, `ML-DSA-65`, `ML-DSA-87` |
| ML-KEM | FIPS 203 | Key encapsulation | `ML-KEM-512`, `ML-KEM-768`, `ML-KEM-1024` |
| SLH-DSA | FIPS 205 | Hash-based signatures | (stateless hash-based) |

Alternate names accepted: `MLKEM768`, `MLDSA65`, etc. (no hyphens).

```bash
# Generate PQC keys
openssl genpkey -algorithm ML-DSA-65 -out mldsa65.pem
openssl genpkey -algorithm ML-KEM-768 -out mlkem768.pem

# Test PQC TLS connection
openssl s_client -connect example.com:443 -groups X25519MLKEM768
```

**Warning**: `openssl dgst` with one-shot algorithms (Ed25519, ML-DSA) silently truncates inputs >16 MiB (CVE-2025-15469, fixed in 3.5.5). Use library APIs for large files.

---

## Hybrid PQC TLS Groups (3.5+)

Default TLS group list changed to prefer hybrid PQC:

```
?*X25519MLKEM768 / ?*X25519:?secp256r1 / ?X448:?secp384r1:?secp521r1 / ?ffdhe2048:?ffdhe3072
```

| Symbol | Meaning |
|---|---|
| `*` | Send keyshare proactively |
| `?` | Optional (tolerate if unsupported) |
| `/` | Keyshare group boundary |

Two keyshares sent by default: `X25519MLKEM768` + `X25519`.

Available hybrid groups: `X25519MLKEM768`, `X448MLKEM1024`, `SecP256r1MLKEM768`, `SecP384r1MLKEM1024`.

---

## OpenSSL 4.0 Breaking Changes Summary

| Change | Migration |
|---|---|
| Engines fully removed | `OPENSSL_NO_ENGINE` always defined; migrate to providers |
| SSLv3 removed | Completely gone, not just disabled |
| `c_rehash` removed | Use `openssl rehash` instead |
| `ASN1_STRING` opaque | Cannot access struct fields directly; use accessor APIs |
| Deprecated EC curves disabled | Use `enable-tls-deprecated-ec` to re-enable |

New in 4.0: **Encrypted Client Hello (ECH)** per RFC 9849, **FFDHE in TLS 1.2** per RFC 7919. See [references/openssl4-migration.md](references/openssl4-migration.md) for details.

---

## QUIC Server (3.5)

OpenSSL 3.5 adds server-side QUIC support (RFC 9000).

```c
// Create QUIC server context
SSL_CTX *ctx = SSL_CTX_new(OSSL_QUIC_server_method());

// Accept incoming QUIC connection
SSL *conn = SSL_accept_connection(ssl, 0);

// Complete handshake
SSL_do_handshake(conn);
```

**Note**: `SSL_accept()` on accepted connections was broken in 3.5.0 (fixed in 3.5.1). Use `SSL_do_handshake()` instead for portability.

External QUIC stacks can use `SSL_set_quic_tls_cbs()` to access just the TLS handshake with a custom record layer.

---

## Default Cipher Change (3.5)

`req`, `cms`, and `smime` changed default cipher from `des-ede3-cbc` to `aes-256-cbc`. Specify `-aes-256-cbc` explicitly in scripts for cross-version portability:

```bash
openssl req -new -key key.pem -out req.pem -aes-256-cbc
openssl cms -encrypt -aes-256-cbc -in msg.txt -out msg.cms cert.pem
```

---

## OpenSSL 3.6 Features (Oct 2025)

- **LMS signature verification** (NIST SP 800-208) in FIPS and default providers — hash-based stateful signatures for firmware/code signing verification
- **EVP_SKEY expansion**: `EVP_KDF_CTX_set_SKEY()`, `EVP_KDF_derive_SKEY()`, `EVP_PKEY_derive_SKEY()` for opaque symmetric key derivation
- **`openssl configutl`**: New utility to dump processed config files — useful for debugging `openssl.cnf` includes and variable expansion
- **FIPS 186-5 deterministic ECDSA** in the FIPS provider (RFC 6979, reproducible signatures)

See [references/new-features.md](references/new-features.md) for full details and code examples.
