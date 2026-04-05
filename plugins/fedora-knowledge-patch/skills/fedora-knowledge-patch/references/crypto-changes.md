# Fedora Crypto & TLS Changes

## OpenSSL Distrusts SHA-1 Signatures (Fedora 41)

OpenSSL no longer trusts cryptographic signatures using SHA-1. This affects:

- TLS connections to servers with SHA-1 signed certificates
- Package/document signature verification using SHA-1
- S/MIME signatures using SHA-1

**Symptoms:** Opaque TLS handshake failures, `SSL_ERROR_SSL` errors when connecting to legacy internal services.

**Workarounds:**

```bash
# System-wide revert (reverts all F41 crypto policy changes)
update-crypto-policies --set FEDORA40

# Per-process revert (preferred for targeted exceptions)
runcp FEDORA40 curl https://legacy-server.internal

# Build-time only (for compiling against SHA-1 signed content)
export OPENSSL_ENABLE_SHA1_SIGNATURES=1
```

## OpenSSL ENGINE API Disabled (Fedora 41)

The ENGINE API (deprecated in OpenSSL 3.0) is now disabled. Applications loading OpenSSL engines will fail.

| Old (ENGINE) | New (Provider) |
|-------------|----------------|
| `engine_pkcs11` | `pkcs11-provider` |
| `ENGINE_load_*()` API calls | `OSSL_PROVIDER_load()` |
| `openssl.cnf` engine sections | `openssl.cnf` provider sections |

## fips-mode-setup Removed (Fedora 42)

The `fips-mode-setup` command is removed from `crypto-policies`.

```bash
# Old (breaks on F42+)
fips-mode-setup --enable
fips-mode-setup --check

# New — enable at install time:
# Add fips=1 to kernel command line during installation

# Post-install workaround (not officially recommended):
grubby --update-kernel=ALL --args="fips=1"

# Check FIPS status:
cat /proc/sys/crypto/fips_enabled   # 1 = enabled
```

**Why post-install FIPS is problematic:** LUKS volumes may use Argon2 KDF (not FIPS-approved), and SSH host keys generated pre-FIPS may use non-compliant algorithms. The installer ensures all initial crypto choices are FIPS-compliant.

## CA Certificate Bundle Paths Dropped (Fedora 44)

The following legacy CA bundle files are removed:

- `/etc/pki/tls/cert.pem`
- `/etc/pki/tls/certs/ca-bundle.crt`
- `/etc/pki/tls/certs/ca-certificates.crt`

OpenSSL switches to **directory-hash format** for CA trust.

**Impact:** Any application, script, or config that hardcodes these paths will fail:

```bash
# These break on Fedora 44+
curl --cacert /etc/pki/tls/certs/ca-bundle.crt https://example.com
export SSL_CERT_FILE=/etc/pki/tls/cert.pem

# Use system defaults instead (OpenSSL finds certs automatically)
curl https://example.com  # works — uses system trust store
```

For applications that require an explicit CA bundle path:

```
/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
```

**Temporary workaround** (will be removed in a future release):

```bash
update-ca-trust extract --rhbz2387674
```
