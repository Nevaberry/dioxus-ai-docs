---
name: openssl-tls-knowledge-patch
description: OpenSSL
license: MIT
version: 4.0.0
metadata:
  author: Nevaberry
---

# OpenSSL and TLS Knowledge Patch

Use this skill to design, migrate, debug, build, or secure software that depends on OpenSSL, libssl, libcrypto, the OpenSSL CLI, native QUIC, or Linux kernel TLS.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI, configuration, and PKI](references/cli-config-and-pki.md) | Configuration loading and diagnostics, command behavior, certificate and request workflows, CMP |
| [Migration and compatibility](references/migration-and-compatibility.md) | Removed and deprecated APIs, opaque types, build/platform changes, API policy, TLS-library integration tradeoffs |
| [Providers, cryptography, and FIPS](references/providers-crypto-and-fips.md) | Provider configuration, EVP and digest changes, PQC, opaque symmetric keys, random generation, FIPS behavior and installation |
| [TLS and QUIC](references/tls-and-quic.md) | TLS behavior, groups and key shares, ECH, native and external-stack QUIC, stream and BIO contracts |
| [Linux kernel TLS](references/kernel-tls.md) | Record boundaries, ancillary data, key updates, zero-copy, record-size limits, observability |
| [Security advisories and patch floors](references/security.md) | CVEs, affected configurations, branch-specific minimum fixes, operational mitigations |

## Start here

1. Identify the exact runtime, headers, provider modules, and branch patch release; do not infer capabilities from the `openssl` executable alone.
2. Check [security.md](references/security.md) before debugging surprising behavior on an old patch release.
3. For a major-version build failure, inspect [migration-and-compatibility.md](references/migration-and-compatibility.md) before adding casts, compatibility macros, or legacy packages.
4. For algorithm availability or FIPS decisions, inspect the loaded providers and properties, then read [providers-crypto-and-fips.md](references/providers-crypto-and-fips.md).
5. Treat TLS, OpenSSL-native QUIC, external QUIC TLS callbacks, and kernel TLS as distinct I/O models; open the matching reference before adapting code between them.

## Breaking changes and removals

### Migrate ENGINE integrations to providers

OpenSSL 4.0 permanently disables ENGINE support, defines `OPENSSL_NO_ENGINE`, and removes the legacy custom EVP method hooks. Do not make a new build depend on `<openssl/engine.h>` or custom `EVP_CIPHER`, `EVP_MD`, `EVP_PKEY`, or `EVP_PKEY_ASN1` methods. Implement algorithms and key custody through providers.

Fedora 41 keeps ENGINE symbols in `libcrypto.so` for existing ABI users but moves the header to the deprecated `openssl-engine-devel` package. Use that package only as a temporary build bridge for an existing RPM.

### Replace removed TLS and utility interfaces

- Replace fixed-version SSL/TLS methods with generic TLS methods plus minimum and maximum protocol bounds.
- Replace `c_rehash` with `openssl rehash`.
- Remove use of `BIO_f_reliable()`; it has no replacement.
- Remove the `ca -msie-hack` option.
- Stop using `ERR_get_state()`, `ERR_remove_state()`, and `ERR_remove_thread_state()`; error state is opaque.
- Do not expect SSLv3 or an SSLv2-format ClientHello to be accepted.

### Stop accessing structures directly

`ASN1_STRING` and `ERR_STATE` are opaque. Use public accessors. Audit wrappers and callbacks for newly const-correct X.509 and other API signatures; changing a mutable pointer declaration may be required even when runtime behavior is unchanged.

### Update certificate-time checks

Replace `X509_cmp_time()`, `X509_cmp_current_time()`, and `X509_cmp_timeframe()` with `X509_check_certificate_times()`. Replace `TS_VERIFY_CTX_set_*` with the corresponding `TS_VERIFY_CTX_set0_*` functions.

### Do not parse human-readable output as a stable wire format

OpenSSL 4.0 changes leading-zero and row-width behavior in printed hex data. `BIO_snprintf()` now inherits the platform libc implementation. Parse structured data or use APIs instead of depending on old text layout and formatting quirks.

### Account for stricter validation

Expect some previously accepted inputs to fail:

- FIPS PBKDF2 enforces lower bounds.
- Strict X.509 verification checks authority key identifiers more closely.
- CRL verification performs additional checks.
- ASN.1 time parsing rejects undersized encodings.
- SHAKE finalization requires an explicit `xoflen`.

### Revisit cleanup ownership

OpenSSL 4.0 no longer performs global libcrypto cleanup through `atexit()`. A global destructor calls `OPENSSL_cleanup()` where supported; otherwise automatic cleanup may not occur. Do not assume the older unload-time callback model.

## High-impact deprecations and behavior shifts

### Use Y2038-safe session APIs

Use `SSL_SESSION_get_time_ex()` and `SSL_SESSION_set_time_ex()` for `time_t` session timestamps. Prefer `SSL_CTX_flush_sessions_ex()` over deprecated `SSL_CTX_flush_sessions()` on platforms with Y2038-safe `time_t`.

### Avoid BIO method getters

All `BIO_meth_get_*()` functions are deprecated. Keep the state needed by a custom BIO integration instead of discovering its method callbacks through these getters.

### Set SHAKE length explicitly

SHAKE-128 and SHAKE-256 have no default output length. Set the `xoflen` parameter before `EVP_DigestFinal()` or `EVP_DigestFinal_ex()`. Use `EVP_DigestSqueeze()` when squeezing a SHAKE context repeatedly.

### Pin command behavior when output compatibility matters

- `req`, `cms`, and `smime` now default to AES-256-CBC instead of 3DES.
- `openssl speed hmac` now defaults to SHA-256 instead of MD5.
- `openssl crl -verify` and `openssl req -verify` return status 1 on verification failure.
- Release-build `OPENSSL_VERSION_NUMBER` behavior was restored in OpenSSL 3.5.4 after an incompatible change.

## Security-first patch checks

Treat these as immediate branch-floor checks, not optional hardening:

- Move affected 4.0.0 deployments to 4.0.1 for PKCS#7, OCSP, CMS, PKCS#12, QUIC, CMP/CRMF, DHX, ASN.1, S/MIME, and RSA-recipient fixes.
- Move 3.5 deployments to at least 3.5.5 for the accumulated high-severity and memory-safety fixes; use 3.5.6 when a TLS 1.3 server interpolates `DEFAULT` into a custom group list.
- Move 3.4 deployments to 3.4.4 for the accumulated security fixes.
- Do not remain on 3.6.0 when relying on CRL-check-all behavior or stapled OCSP; use 3.6.1 or newer.

Read [security.md](references/security.md) for exact affected versions, CVEs, configuration-dependent exposure, and mitigations.

## Provider, FIPS, and cryptography quick reference

### Prefer provider-native standardized PQC

OpenSSL 3.5 provides ML-KEM, ML-DSA, SLH-DSA, and standardized hybrid schemes. With `oqsprovider`, query the actually loaded algorithms; it disables overlapping standardized families at runtime to prevent duplicate identifiers and incompatible key representations.

```sh
openssl list -kem-algorithms -provider oqsprovider
openssl list -signature-algorithms -provider oqsprovider
```

### Treat FIPS properties and approval as runtime facts

X25519 and X448 implementations in the FIPS provider advertise `fips=no`. Use FIPS indicators where approval status matters. A validated FIPS module can be paired with newer non-FIPS library components only when the validated build and Security Policy are followed and the exact provider is tested and verified.

### Keep `fipsmodule.cnf` machine-local

Run `openssl fipsinstall` on every target machine. Do not copy machine-bound installation state, especially output containing `install-status`. Use `-defer_tests` only when deliberately deferring module self-tests.

### Use opaque symmetric keys where raw bytes should not escape

Use `EVP_SKEY` for provider-backed opaque symmetric keys. Newer derivation and exchange APIs can consume or produce these objects without materializing raw key bytes.

### Inspect provider and RNG configuration precisely

Provider `activate` and `soft_load` accept only canonical case-insensitive booleans. Use repeated `-provparam [name:]key=value` for runtime UTF-8 provider parameters, but keep initialization-only parameters in configuration. Configure the DRBG type, primitive, properties, and seed source explicitly when defaults are unsuitable.

## TLS quick reference

### Expect hybrid key establishment by default

The default supported-groups list prefers hybrid post-quantum KEM groups, and the default key shares include X25519MLKEM768 and X25519. OpenSSL can offer multiple key shares and provides finer controls for group configuration.

If a custom list uses `DEFAULT`, check the security advisory first: affected servers can flatten security tuples and choose a lower-priority classical share.

### Re-enable legacy EC only as an explicit compatibility decision

TLS curves deprecated by RFC 8422 and explicit EC curves are disabled at build time by default. A compatibility build can opt in:

```sh
./Configure enable-tls-deprecated-ec enable-ec_explicit_curves
```

At runtime, `no-tls-deprecated-ec` disables deprecated TLS groups.

### Use the new protocol capabilities deliberately

OpenSSL adds Encrypted Client Hello, negotiated FFDHE for TLS 1.2, RFC 9150 integrity-only TLS 1.3 suites, ShangMi TLS identifiers, and hybrid `curveSM2MLKEM768`. Verify peer and policy compatibility before enabling specialized suites or groups.

## QUIC quick reference

### Choose one integration model

- Use OpenSSL-native QUIC connection and stream objects for built-in client/server transport.
- Use `SSL_set_quic_tls_cbs()` when an external QUIC stack owns packet protection and the record layer while OpenSSL performs the TLS handshake.
- Do not assume source compatibility with the BoringSSL-style QUIC callback API.

### Disable default-stream mode for new multi-stream code

Before connection initiation, call `SSL_set_default_stream_mode(..., SSL_DEFAULT_STREAM_MODE_NONE)`, then create and accept streams explicitly. Creating or accepting a stream before default-stream association permanently prevents later default-stream creation.

### Keep network and application blocking separate

The QUIC network BIO is always a nonblocking datagram BIO. SSL-level reads and writes default to blocking and are controlled separately with `SSL_set_blocking_mode()`. `SSL_ERROR_WANT_READ` and `SSL_ERROR_WANT_WRITE` describe stream state, not UDP socket readiness; poll through the QUIC network-interest APIs.

### Handle version-specific handshake and shutdown edges

On an OpenSSL 3.5.0 object returned by `SSL_accept_connection()`, call `SSL_do_handshake()` rather than `SSL_accept()`. Use `SSL_shutdown_ex()` when a prompt QUIC exit is more important than a fully RFC-conformant extended shutdown.

## Kernel TLS quick reference

After installing `TLS_TX`, remember that each `send()` closes a record unless `MSG_MORE` is set. Install new TLS 1.3 RX keys promptly after KeyUpdate; reads otherwise fail with `EKEYEXPIRED` while TX continues. Set `TLS_TX_MAX_PAYLOAD_LEN` to the negotiated limit for TLS 1.2 and one byte less for TLS 1.3.

Use ancillary `SOL_TLS` record-type control messages for non-application records, keep zero-copy source bytes immutable until transmission completes, and inspect `/proc/net/tls_stat` plus socket diagnostics when offload or rekey behavior is unclear.

## CLI and PKI quick reference

- Set `OPENSSL_CONF` to an empty string to suppress configuration loading.
- Enable `config_diagnostics=1` when invalid SSL-module configuration must fail `SSL_CTX_new()`.
- Use `openssl no-XXX` carefully: success means command `XXX` is absent; status 1 means it is present.
- Prefer named DH groups such as `group:ffdhe3072` over freshly generated parameters.
- Remember that `req -CA` does not copy CSR extensions unless `-copy_extensions copy` or `copyall` is explicit.
- Use `openssl configutl` to process and inspect the equivalent OpenSSL configuration.

Open [cli-config-and-pki.md](references/cli-config-and-pki.md) for exact syntax and certificate-generation defaults.
