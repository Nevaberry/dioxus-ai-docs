# Post-Quantum Cryptography in OpenSSL (3.5+)

OpenSSL 3.5 adds native support for FIPS 203/204/205 post-quantum algorithms in both the default and FIPS providers.

## Key Generation

Algorithm names for `openssl genpkey -algorithm`:

```bash
# ML-DSA (FIPS 204) — post-quantum signatures
openssl genpkey -algorithm ML-DSA-44 -out mldsa44.pem
openssl genpkey -algorithm ML-DSA-65 -out mldsa65.pem
openssl genpkey -algorithm ML-DSA-87 -out mldsa87.pem

# ML-KEM (FIPS 203) — key encapsulation
openssl genpkey -algorithm ML-KEM-512 -out mlkem512.pem
openssl genpkey -algorithm ML-KEM-768 -out mlkem768.pem
openssl genpkey -algorithm ML-KEM-1024 -out mlkem1024.pem

# SLH-DSA (FIPS 205) — stateless hash-based signatures
# Also available via alternate names: MLKEM768, MLDSA65, etc. (no hyphens)
```

**Warning**: `openssl dgst` with one-shot algorithms (Ed25519, ML-DSA) silently truncates inputs >16 MiB (CVE-2025-15469, fixed in 3.5.5). Use library APIs for large files.

## Hybrid PQC TLS Groups

Default TLS group list changed in 3.5 to prefer hybrid PQC key exchange:

```
?*X25519MLKEM768 / ?*X25519:?secp256r1 / ?X448:?secp384r1:?secp521r1 / ?ffdhe2048:?ffdhe3072
```

### Group syntax

| Symbol | Meaning |
|---|---|
| `*` | Send keyshare proactively |
| `?` | Optional (tolerate if peer doesn't support) |
| `/` | Keyshare group boundary |

Two keyshares are sent by default: `X25519MLKEM768` + `X25519`.

### Available hybrid groups

| Group name | Components |
|---|---|
| `X25519MLKEM768` | X25519 + ML-KEM-768 |
| `X448MLKEM1024` | X448 + ML-KEM-1024 |
| `SecP256r1MLKEM768` | P-256 + ML-KEM-768 |
| `SecP384r1MLKEM1024` | P-384 + ML-KEM-1024 |

### Testing PQC TLS

```bash
# Connect using a specific hybrid group
openssl s_client -connect example.com:443 -groups X25519MLKEM768

# Force classical-only (disable PQC)
openssl s_client -connect example.com:443 -groups X25519:secp256r1
```
