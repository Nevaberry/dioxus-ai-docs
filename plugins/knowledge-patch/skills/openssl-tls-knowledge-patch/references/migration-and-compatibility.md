# Migration and Compatibility

## Contents

- [Removed architecture and APIs](#removed-architecture-and-apis)
- [Opaque and const-correct interfaces](#opaque-and-const-correct-interfaces)
- [Time and lifetime APIs](#time-and-lifetime-apis)
- [Build, packaging, and platform changes](#build-packaging-and-platform-changes)
- [Output and version compatibility](#output-and-version-compatibility)
- [API stability and support policy](#api-stability-and-support-policy)
- [TLS-library integration comparisons](#tls-library-integration-comparisons)

## Removed architecture and APIs

### Permanently disabled ENGINE support

OpenSSL 4.0 removes ENGINE support. Builds behave as if `no-engine` were selected and always define `OPENSSL_NO_ENGINE`. Migrate integrations that provided cryptography through custom engines to providers.

### Removed custom EVP methods

OpenSSL 4.0 removes deprecated custom `EVP_CIPHER`, `EVP_MD`, `EVP_PKEY`, and `EVP_PKEY_ASN1` method support. Implement new algorithms through the provider architecture rather than legacy method hooks.

### Removed fixed-version TLS methods

OpenSSL 4.0 removes deprecated fixed SSL/TLS-version method functions. Use generic TLS methods and configure the minimum and maximum protocol versions.

### Removed compatibility commands and BIO

OpenSSL 4.0 removes the `c_rehash` script; use `openssl rehash`. The `ca` command no longer accepts deprecated `msie-hack`, and `BIO_f_reliable()` is removed without replacement.

### Opaque error state

OpenSSL 4.0 removes `ERR_get_state()`, `ERR_remove_state()`, and `ERR_remove_thread_state()`. `ERR_STATE` is always opaque. Use the supported error-queue APIs and do not retain pointers to internal thread error state.

### Deprecated BIO method getters

All `BIO_meth_get_*()` functions are deprecated as of 3.5.0. Preserve callback metadata within the application or redesign the custom BIO rather than introspecting a `BIO_METHOD` through these getters.

## Opaque and const-correct interfaces

### Opaque `ASN1_STRING`

`ASN1_STRING` is opaque in OpenSSL 4.0. Replace direct field access with public accessors.

### Const-correct API signatures

Numerous public functions, including X.509 APIs, add `const` qualifiers to arguments and return types in OpenSSL 4.0. Update C declarations, wrappers, FFI bindings, and callback types that relied on mutable pointers even when the underlying operation is unchanged.

### Timestamp verification setters

Replace deprecated `TS_VERIFY_CTX_set_*` functions with the corresponding `TS_VERIFY_CTX_set0_*` functions, which have improved ownership semantics (since 3.4.0). Audit ownership rather than mechanically renaming the call.

### Certificate-time checking

Replace deprecated `X509_cmp_time()`, `X509_cmp_current_time()`, and `X509_cmp_timeframe()` with `X509_check_certificate_times()` in OpenSSL 4.0 code.

## Time and lifetime APIs

### Y2038-safe session timestamps

Use `SSL_SESSION_get_time_ex()` and `SSL_SESSION_set_time_ex()`, which take `time_t`, for Y2038-safe session timestamps on 32-bit systems configured with 64-bit time (since 3.3.0).

### Y2038-safe session-cache flushing

Use `SSL_CTX_flush_sessions_ex()` instead of deprecated `SSL_CTX_flush_sessions()` on platforms with Y2038-safe `time_t` (since 3.4.0).

### Global cleanup lifetime

OpenSSL 4.0 no longer cleans globally allocated libcrypto data through `atexit()`. By default, `OPENSSL_cleanup()` runs from a global destructor where one is available, or is not run automatically. Do not assume cleanup executes during library unload, and avoid ordering dependencies between application destructors and OpenSSL global cleanup.

## Build, packaging, and platform changes

### CMake package export

OpenSSL supplies a CMake package exporter on Unix and Windows in addition to pkg-config (since 3.3.0). Prefer the exported package targets over manually reconstructing library paths and transitive settings.

### Runtime OpenSSL directories on Windows

`OPENSSLDIR`, `ENGINESDIR`, and `MODULESDIR` are not necessarily fixed at build time on Windows. Registry keys can define them at runtime (since 3.4.0), so do not assume a compiled path is the effective deployment path.

### Fedora 41 ENGINE development headers

Fedora 41 retains `ENGINE_*` symbols in `libcrypto.so` for ABI compatibility, so existing binaries and engines can continue to run, but moves `<openssl/engine.h>` from `openssl-devel` to the deprecated `openssl-engine-devel` package (source batch `4.0-guide`). Existing RPMs can temporarily add:

```spec
BuildRequires: openssl-engine-devel
```

Do not introduce this dependency for new Fedora packages; packaging rules prohibit new dependencies on deprecated packages, and new integrations must use providers.

### Retired Darwin targets

OpenSSL 4.0 removes the `darwin-i386`, `darwin-i386-cc`, `darwin-ppc`, `darwin-ppc-cc`, `darwin-ppc64`, and `darwin-ppc64-cc` configuration targets.

### Windows VC runtime linkage

OpenSSL 4.0 builds can select static or dynamic Visual C runtime linkage. Match the choice to the rest of the process and packaging model rather than relying on a single implicit runtime variant.

### OpenSSL 3.6 build and platform requirements

An ANSI-C-only compiler is insufficient for OpenSSL 3.6; use a toolchain with C99 support. OpenSSL 3.6 also removes VxWorks platform support.

## Output and version compatibility

### Release-build version-number compatibility

OpenSSL 3.5.4 reverted a synthesized `OPENSSL_VERSION_NUMBER` change because it broke applications relying on the earlier 3.x release-build semantics documented by `OpenSSL_version(3)`. Do not reproduce the short-lived behavior in compatibility code.

### Hexadecimal output changes

OpenSSL 4.0 no longer adds an extra leading `00:` when a printed key value's most-significant byte is at least `0x80`. Hex dumps use 24-byte rows for signatures and 16-byte rows elsewhere. Replace text-layout parsers with structured formats or direct APIs.

### libc-backed `BIO_snprintf()`

`BIO_snprintf()` uses the platform libc `snprintf()` in OpenSSL 4.0 instead of OpenSSL's internal implementation. Expect host-specific formatting behavior at the same edge cases as direct libc calls.

## API stability and support policy

### Public API stability and removal policy

Within a major version at 3.0 or later, OpenSSL guarantees public API and ABI compatibility, although a patch release can backport accessor functions. A public interface cannot be removed until its replacement has shipped in a stable LTS release and the old interface has been deprecated for at least five years. When a structure becomes opaque, newly necessary accessors are added to the extant LTS feature release and all supported intermediate successors.

### Branch support deadlines

OpenSSL 3.3 support ended on 2026-04-09. Published end dates for retained branches are 2026-10-22 for 3.4, 2026-11-01 for 3.6, and 2030-04-08 for 3.5 LTS. Treat an ended support line as requiring migration even when no specific advisory currently affects the deployment.

### Support cadence after OpenSSL 3.5

The policy plans an LTS every two years in April of odd-numbered years. LTS lines receive at least five years of support, but only security fixes are promised in the final year. Post-3.5 non-LTS lines receive 13 months of full support, with at least the latest two releases fully supported regardless of LTS status.

## TLS-library integration comparisons

Use these notes for source and feature compatibility decisions; they are not claims of drop-in equivalence.

### OpenSSL 3.5 QUIC API compatibility

OpenSSL 3.5's native QUIC API is not source-compatible with the de facto BoringSSL QUIC API used by AWS-LC, wolfSSL, LibreSSL, and existing QUIC integrations. A stack targeting the older callback API needs a distinct OpenSSL 3.5 integration rather than a relink.

### HAProxy `limited-quic` on stock OpenSSL

HAProxy's `limited-quic` path provides server-side QUIC on unpatched OpenSSL by obtaining TLS secrets through the keylog callback. It avoids rebuilding the TLS library but does not support 0-RTT.

### HAProxy with AWS-LC

The HAProxy AWS-LC port supports modern TLS and QUIC and otherwise matches its OpenSSL 1.1.1 feature set, except that AWS-LC omits CCM, DHE, and ENGINE support. AWS-LC has no general LTS branch; its FIPS branches are maintained for five years. Plan regular upgrades and rebuilds for non-FIPS use.

### HAProxy with LibreSSL

LibreSSL 3.6.0 implements the BoringSSL QUIC API and is built and tested by HAProxy CI, but incomplete OpenSSL API coverage prevents full HAProxy feature parity.

### HAProxy with wolfSSL

wolfSSL's OpenSSL compatibility layer became viable for simple or embedded HAProxy deployments in 5.6.6, but behavior and configuration can differ. Debian and Ubuntu packages omit build options required by the HAProxy port, so this combination needs a separately maintained wolfSSL build.

### Rustls capabilities and integration boundary

Rustls exposes Rust and C APIs, defaults to `aws-lc-rs`, and supports FIPS operation, post-quantum key exchange, client-side ECH, and OS trust verification. HAProxy's evaluation found the `rustls-openssl-compat` ABI incomplete; using the native Rustls API instead would require an extensive rewrite.
