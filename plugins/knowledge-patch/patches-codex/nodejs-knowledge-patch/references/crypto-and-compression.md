# Cryptography and Compression

## API migrations and failure behavior

- In 23.0.0, `zlib.bytesRead` is removed. The `crypto.fips` property is
  runtime-deprecated; use `crypto.getFips()` and `crypto.setFips()`.
- In 23.11.0, `crypto.diffieHellman()` accepts an optional callback for
  asynchronous key agreement in addition to its synchronous return form.
- In 25.0.0, callers of SHAKE hashes should specify `outputLength`; default
  output sizes for `shake128` and `shake256` are runtime-deprecated. RSA-PSS
  option names `hash` and `mgf1Hash` are removed; use `hashAlgorithm` and
  `mgf1HashAlgorithm`. `ECDH.setPublicKey()` is runtime-deprecated.
- In 25.2.0, the 25.2.1 correction makes RSA-PSS use its documented default
  `saltLength`. Set `saltLength` explicitly when a particular policy matters.
- In 25.9.0, passing WebCrypto `CryptoKey` objects to classic `node:crypto`
  functions is documentation-deprecated; use `KeyObject.from()` or remain in
  WebCrypto. QUIC session-key options no longer accept `CryptoKey`.
- In 26.0.0, short GCM authentication tags require `authTagLength` when
  creating a decipher. Errors from asynchronous crypto jobs include underlying
  OpenSSL details, which can change diagnostics and test expectations.
- In 24.18.0, `crypto.diffieHellman()` accepts key data directly as its private
  and public inputs rather than requiring preconstructed key objects.

## Hashes, password derivation, and authentication

- In 24.4.0, one-shot `crypto.hash()` accepts `outputLength` for
  extendable-output functions.
- In 24.13.0, the 24.13.1 release promotes `crypto.hash()` to stable.
- In 24.7.0, `node:crypto` adds asynchronous `argon2()` and synchronous
  `argon2Sync()` password derivation.
- In 24.8.0, WebCrypto supports KMAC through `SubtleCrypto.sign()` and
  `verify()`, and supports Argon2 through `deriveBits()`.
- In 25.9.0, WebCrypto adds TurboSHAKE and KangarooTwelve. The cSHAKE and KMAC
  parameter member for output size is renamed from `length` to `outputLength`.
- In 26.7.0, KangarooTwelve customization input is limited to 512 bytes and
  Argon2 obeys the active FIPS policy instead of bypassing it.

## Modern and post-quantum keys

- In 24.6.0, `KeyObject` and the classic sign/verify APIs support ML-DSA keys
  and signatures.
- In 24.7.0, `crypto.encapsulate()` and `crypto.decapsulate()` support ML-KEM,
  DHKEM, and RSASVE. With ML-KEM, the sender obtains a shared key and
  ciphertext from a public key, and the recipient recovers the same shared key
  with the private key.
- Also in 24.7.0, WebCrypto supports AES-OCB, ChaCha20-Poly1305, ML-DSA,
  ML-KEM, SHA-3, and SHAKE, and adds `subtle.getPublicKey()` and
  `SubtleCrypto.supports()`. Check support for newer algorithms, especially on
  nonstandard builds. HMAC with SHA-3 must specify key length.
- In 24.8.0, `KeyObject` and classic signing APIs support SLH-DSA.
- In 25.9.0, ML-KEM and ML-DSA PKCS#8 private-key imports must contain the seed;
  seedless encodings are rejected.
- In 26.0.0, `KeyObject` and key generation support raw formats. ML-KEM and
  ML-DSA PKCS#8 private-key exports default to seed-only form, so consumers of
  the previous expanded encoding must account for different bytes.
- In 24.18.0, crypto APIs support JWK representations for ML-KEM and SLH-DSA.
  Custom BoringSSL builds wire ML-DSA, ML-KEM, WebCrypto
  ChaCha20-Poly1305, and AES-KW; feature-detect when supporting both OpenSSL-
  and BoringSSL-based builds.
- In 26.4.0, Argon2 and key encapsulation/decapsulation are stable.
- In 26.7.0, private keys can load through OpenSSL STORE loaders, including
  provider-backed stores rather than ordinary in-memory material.

## Signature contexts

- In 24.8.0, classic crypto and WebCrypto signing and verification accept an
  application context for Ed448 and ML-DSA. Verification must use the same
  context bytes as signing.
- In 26.0.0, Ed25519 signing and verification also accept a context, with the
  same matching requirement.

## WebCrypto derivation details

- In 23.3.0, `SubtleCrypto.deriveBits()` accepts a length of `0` for HKDF and
  PBKDF2.
- In 23.4.0, `SubtleCrypto.deriveBits()` accepts lengths not divisible by eight.

## Compression formats and validation

- In 23.8.0, `node:zlib` adds experimental Zstandard compression and
  decompression APIs.
- In 24.6.0, one-shot `zstdCompress()` and `zstdDecompress()` accept a shared
  `dictionary`; decompression must use the same dictionary as compression.
- In 24.7.0, `CompressionStream` and `DecompressionStream` accept Brotli.
- In 22.23.2, zlib writes throw when their write buffer is out of bounds.
  Validate dynamically constructed views and offsets or handle the exception.
- In 26.5.0, zlib decoder options accept `rejectGarbageAfterEnd`, and Web
  decompression streams reject trailing gzip members.
- In 26.7.0, Zstandard decompression rejects truncated input, while Zstandard
  dictionaries accept `ArrayBuffer` without conversion.

## TLS trust stores and cryptographic policy

- In 23.2.0, the bundled root store moves to NSS 3.104, adding FIRMAPROFESIONAL
  CA ROOT-A WEB, TWCA CYBER Root CA, and SecureSign Root CA12, CA14, and CA15.
- In 23.8.0, `--use-system-ca` enables the operating-system trust store on
  macOS and Windows. In 23.9.0, it works on additional platforms. In 23.10.0,
  it can use intermediate certificates from the system store.
- In 23.10.0, `tls.getCACertificates()` exposes CA certificates available to
  TLS. The bundled store moves to NSS 3.108.
- In 24.5.0, `tls.setDefaultCACertificates()` replaces both the list returned
  by `tls.getCACertificates('default')` and the CA set used by clients that do
  not supply `ca`. To extend the bundled Mozilla roots, include the existing
  default list in the replacement.
- In 24.7.0, the bundled store moves to NSS 3.114, adding TrustAsia TLS ECC and
  RSA roots and SwissSign RSA TLS Root CA 2022 - 1. It removes GlobalSign Root
  CA, Entrust.net Premium 2048 Secure Server CA, Baltimore CyberTrust Root,
  Comodo AAA Services root, XRamp Global CA Root, Go Daddy Class 2 CA, and
  Starfield Class 2 CA.
- In 24.8.0, the documented default OpenSSL security level is 2. Modernize or
  explicitly handle keys, signatures, or ciphers rejected at that level.
- In 24.13.0, the 24.13.1 bundled store moves to NSS 3.119.
- In 25.9.0, the bundled store moves to NSS 3.121 and Node can be built with
  OpenSSL 4.0. Native addons can access an OpenSSL context through
  `crypto::GetSSLCtx()`.
- In 24.18.0, the bundled store moves to NSS 3.123.1.

## Security hardening

- The 23.11.1 release fixes CVE-2025-23166 in asynchronous-crypto error
  handling; upgrade from 23.11.0.
- In 24.13.0, the 24.13.1 security fixes route exceptions from TLS callbacks
  through error handlers and give `TLSSocket` a default error handler
  (CVE-2025-59465 and CVE-2026-21637). Attach explicit error listeners when
  logging or recovery is needed.
- The same 24.13.1 release makes stack-overflow exceptions in `async_hooks`
  rethrow (CVE-2025-59466) and removes reliance on the zero-fill toggle for
  unsafe Buffer creation (CVE-2025-55131). Upgrade rather than implement
  application-level workarounds.
- In 24.17.0, TLS normalizes hostnames for identity checks, matches SNI
  contexts case-insensitively, and binds reusable sessions to the authenticated
  host. WebCrypto cipher operations guard output length.
- In 24.14.0, the 24.14.1 release hardens HMAC and KMAC comparison.
