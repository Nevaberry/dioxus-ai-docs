# Security Advisories and Patch Floors

## Contents

- [Minimum patch floors](#minimum-patch-floors)
- [TLS and QUIC](#tls-and-quic)
- [Certificate, PKCS, CMS, and S/MIME processing](#certificate-pkcs-cms-and-smime-processing)
- [Key agreement and elliptic curves](#key-agreement-and-elliptic-curves)
- [ASN.1 and input bounds](#asn1-and-input-bounds)
- [Branch-specific command and validation regressions](#branch-specific-command-and-validation-regressions)

Use upstream advisories and the deployment's exact build configuration for final exposure decisions. The entries below preserve the affected surfaces, minimum fixes, and important configuration qualifiers supplied with this patch.

## Minimum patch floors

| Branch or affected line | Minimum action covered here | Main reasons |
| --- | --- | --- |
| 4.0.0 | Upgrade to 4.0.1 | PKCS#7, OCSP, CMS, PKCS#12, QUIC, CMP/CRMF, DHX, ASN.1, S/MIME, and RSA-recipient flaws |
| 3.5 | Upgrade to 3.5.5; use 3.5.6 for affected custom TLS group lists | Accumulated high-severity and memory-safety fixes; `DEFAULT` tuple flattening |
| 3.4 | Upgrade to 3.4.4 | Accumulated high-severity and memory-safety fixes |
| 3.6.0 | Upgrade to 3.6.1; use 3.6.2 for affected custom TLS group lists | CRL/OCSP regressions; `DEFAULT` tuple flattening |

Do not treat this table as a substitute for later advisories or branch support status.

## TLS and QUIC

### TLS group tuples with `DEFAULT` (CVE-2026-2673)

OpenSSL 3.5.0 through 3.5.5 and 3.6.0 through 3.6.1 TLS 1.3 servers flatten built-in security tuples when `DEFAULT` is interpolated into a custom groups list. This can select a predicted lower-priority classical key share instead of requesting a mutually supported higher-priority group such as X25519MLKEM768.

Use the unmodified default list, spell out the tuples, or update to 3.5.6 or 3.6.2.

### Empty protocol lists in `SSL_select_next_proto()` (CVE-2024-5535)

Passing a zero-length client protocol list to `SSL_select_next_proto()` can return a pointer past the list, causing a crash or disclosure of up to 255 bytes when the result is sent to the peer. Keep the client list nonempty and correctly assigned; libssl already guarantees this for normal ALPN callback input. Update to 3.0.15, 3.1.7, 3.2.3, or 3.3.2.

### TLS 1.3 certificate compression and raw-key fixes

OpenSSL 3.4.4 fixes a memory-safety issue in TLS 1.3 certificate compression among its accumulated fixes. OpenSSL 3.4.1 previously fixed raw-public-key handshakes and ECDSA timing. Deployments on the 3.4 branch should use 3.4.4 (security set attributed to batch `3.4.0`).

OpenSSL 3.5.5 also fixes the TLS 1.3 certificate-compression issue as part of its accumulated branch fixes. Deployments on the 3.5 branch should use 3.5.5 or newer (security set attributed to batch `3.5.0`).

### QUIC denial-of-service fixes

OpenSSL 4.0.1 fixes unbounded memory growth when a peer floods a QUIC endpoint with `PATH_CHALLENGE` frames (CVE-2026-34183). It also fixes a QUIC server NULL dereference caused by an invalid Initial token when address validation is disabled (CVE-2026-42764).

### Stapled OCSP client failures and double-free

OpenSSL 4.0.1 fixes a double-free triggered in TLS clients by a malicious stapled OCSP response (CVE-2026-35188). It also fixes a crash when whole-chain OCSP checking and partial-chain verification are enabled together (CVE-2026-42765).

OpenSSL 3.6.1 fixes stapled-OCSP handshakes that 3.6.0 servers could fail with various clients. Do not remain on 3.6.0 when relying on stapled OCSP interoperability.

## Certificate, PKCS, CMS, and S/MIME processing

### PKCS#7 verification use-after-free

OpenSSL 4.0.1 fixes a high-severity use-after-free when `PKCS7_verify()` processes crafted PKCS#7 or S/MIME `SignedData` (CVE-2026-45447). Upgrade affected 4.0.0 deployments rather than attempting to validate hostile data in a wrapper.

### Authenticated-cipher edge cases

OpenSSL 4.0.1 rejects CMS `AuthEnvelopedData` that substitutes a non-AEAD cipher or an undersized tag (CVE-2026-34182). It honors the caller's IV when AES-OCB is driven through one-shot `EVP_Cipher()` (CVE-2026-45445) and correctly authenticates AAD with an empty AES-SIV or AES-GCM-SIV ciphertext (CVE-2026-45446).

### RSA recipient implicit rejection

OpenSSL 4.0.1 uses implicit rejection for RSA PKCS#1 v1.5 key transport in `CMS_decrypt()` and `PKCS7_decrypt()` to close a Bleichenbacher oracle (CVE-2026-42768). Supply the recipient certificate. Without it, the last `RecipientInfo` that yields a plausibly sized key can be selected, and decryption can return garbage content.

### Password-based PKCS#12 and CMS validation

OpenSSL 4.0.1 rejects PBMAC1-protected PKCS#12 input whose HMAC key is short enough to permit probabilistic forgery (CVE-2026-34181). It also fixes password-based CMS crashes caused by an omitted KDF field (CVE-2026-42766) and by selecting a stream-mode KEK for RFC 3211 unwrap (CVE-2026-9076).

### CMP and CRMF validation

OpenSSL 4.0.1 fixes a CRMF `EncryptedValue` NULL dereference when algorithm parameters are absent (CVE-2026-42767). It restores effective certificate validation for CMP `rootCaKeyUpdate`, preventing an authenticated registration authority from substituting an arbitrary trust anchor (CVE-2026-42769).

### Accumulated 3.4 branch fixes

OpenSSL 3.4.4 fixes high-severity and memory-safety issues in PBMAC1 and PKCS#12, CMS `AuthEnvelopedData`, unknown-cipher lookup, TLS 1.3 certificate compression, line-buffer BIOs, low-level OCB, timestamp verification, and PKCS#7. The covered identifiers are CVE-2025-11187, CVE-2025-15467, CVE-2025-15468, CVE-2025-66199, CVE-2025-68160, CVE-2025-69418 through CVE-2025-69421, CVE-2026-22795, and CVE-2026-22796.

This floor also includes OpenSSL 3.4.3 fixes for RFC 3211 unwrap, SM2, and HTTP `no_proxy` flaws and OpenSSL 3.4.1 fixes for raw-public-key handshakes and ECDSA timing.

### Accumulated 3.5 branch fixes

OpenSSL 3.5.5 fixes high-severity and memory-safety issues in PBMAC1 and PKCS#12, CMS `AuthEnvelopedData`, unknown-cipher lookup, `openssl dgst` inputs larger than 16 MiB, TLS 1.3 certificate compression, line-buffer BIOs, low-level OCB, timestamp verification, and PKCS#7. The covered identifiers are CVE-2025-11187, CVE-2025-15467 through CVE-2025-15469, CVE-2025-66199, CVE-2025-68160, CVE-2025-69418 through CVE-2025-69421, CVE-2026-22795, and CVE-2026-22796.

OpenSSL 3.5.4 fixes out-of-bounds access in RFC 3211 unwrap and HTTP `no_proxy` handling plus an SM2 timing side channel on 64-bit Arm (CVE-2025-9230 through CVE-2025-9232). These fixes are present in later 3.5 releases.

## Key agreement and elliptic curves

### FFC-DH peer validation

OpenSSL 4.0.1 fixes `EVP_PKEY_derive_set_peer()` validation for DHX keys so an attacker cannot supply a forged `q` and recover a long-lived private key through small-subgroup exchanges (CVE-2026-42770). Unlike most 4.0.1 issues in this set, the flaw also affects the FIPS module.

### Explicit binary-field curve parameters (CVE-2024-9143)

Low-level `EC_GROUP_new_curve_GF2m()`, `EC_GROUP_new_from_params()`, and supporting `BN_GF2m_*()` APIs can access memory out of bounds when given an untrusted explicit field polynomial with a zero constant term. Named curves and X.509's X9.62 encoding cannot express the problematic input. Fixes are in 3.0.16, 3.1.8, 3.2.4, and 3.3.3.

## ASN.1 and input bounds

### ASN.1 and S/MIME input bounds

OpenSSL 4.0.1 fixes oversized primitive DER input causing a heap over-read through `d2i_*()` on 64-bit Unix (CVE-2026-34180), crafted email input causing `X509_VERIFY_PARAM_set1_email()` to read out of bounds (CVE-2026-42771), and an integer overflow leading to a heap overflow in ASN.1 multibyte-string conversion (CVE-2026-7383).

### Expected-name checks with `otherName` (CVE-2024-6119)

Comparing an expected DNS name, email address, or IP address with a certificate's malformed `otherName` subject alternative name can terminate the application. Chain validation without an expected-name check is unaffected. Fixes are in 3.0.15, 3.1.7, 3.2.3, and 3.3.2.

## Branch-specific command and validation regressions

### `x509` trust-rejection fix

OpenSSL 3.5.0's `x509` command can add a trusted use when asked to add a rejected use (CVE-2025-4575). Use 3.5.1 or newer for correct trust-purpose output.

### CRL-check-all regression

OpenSSL 3.6.1 restores the behavior of `X509_V_FLAG_CRL_CHECK_ALL` that existed before 3.6.0. Do not remain on 3.6.0 when the application depends on that flag's established whole-chain behavior.
