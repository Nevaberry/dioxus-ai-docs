# Cryptography and Compression

Classic crypto, WebCrypto, post-quantum algorithms, key formats, hashing, and compression.

## Contents

- [WebCrypto](#webcrypto)
- [Post-quantum and public-key crypto](#post-quantum-and-public-key-crypto)
- [Hashing, MACs, and password derivation](#hashing-macs-and-password-derivation)
- [Compression](#compression)
- [Compatibility and security](#compatibility-and-security)

## WebCrypto

### Argon2 in WebCrypto (since 24.8.0)

In addition to the existing `node:crypto` Argon2 helpers, WebCrypto now supports the Argon2 algorithms for deriving key material through `SubtleCrypto.deriveBits()`.

### cSHAKE in WebCrypto (since 26.4.0)

WebCrypto now supports cSHAKE and accepts non-byte-aligned length values in the newly covered operations.

### KMAC in WebCrypto (since 24.8.0)

WebCrypto now supports the KMAC algorithms, allowing keyed message authentication through `SubtleCrypto.sign()` and `SubtleCrypto.verify()` with KMAC keys instead of requiring a separate implementation.

### Modern WebCrypto algorithms (since 24.7.0)

`globalThis.crypto.subtle` now supports AES-OCB, ChaCha20-Poly1305, ML-DSA, ML-KEM, SHA-3, and SHAKE. It also adds `subtle.getPublicKey()` and `SubtleCrypto.supports()` for public-key extraction and feature detection; HMAC keys using SHA-3 hashes must specify a length.

### Non-byte-aligned WebCrypto derivation (since 23.4.0)

`SubtleCrypto.deriveBits()` now accepts requested bit lengths that are not divisible by eight.

### Stable Curve25519 WebCrypto algorithms (since 23.5.0)

The WebCrypto `Ed25519` and `X25519` algorithm identifiers are now stable and no longer emit an `ExperimentalWarning` when used.

### TurboSHAKE and KangarooTwelve in WebCrypto (since 25.9.0)

WebCrypto now supports the TurboSHAKE and KangarooTwelve algorithm families. The output-size member in `CShakeParams` and `KmacParams` is now named `outputLength` rather than `length`.


## Post-quantum and public-key crypto

### Callback-based Diffie-Hellman (since 23.11.0)

`crypto.diffieHellman()` now accepts an optional callback, providing a callback-based form alongside the existing synchronous return: `diffieHellman({ privateKey, publicKey }, (error, secret) => { /* ... */ })`.

### Direct key data in Diffie-Hellman operations (since 24.18.0)

`crypto.diffieHellman()` now accepts supported key data directly in its `privateKey` and `publicKey` options instead of requiring preconstructed `KeyObject` values.

### Ed25519 signature contexts (since 26.0.0)

Ed25519 signing and verification now accept an application-provided context. The verifier must use the same context bytes as the signer.

```js
const signature = sign(null, data, { key: privateKey, context });
const valid = verify(null, data, { key: publicKey, context }, signature);
```

### JWK support for post-quantum keys (since 24.18.0)

`node:crypto` now supports JWK representations of ML-KEM and SLH-DSA keys, extending the key formats available for those algorithms.

### Key encapsulation in `node:crypto` (since 24.7.0)

New `crypto.encapsulate()` and `crypto.decapsulate()` APIs support ML-KEM, DHKEM, and RSASVE key-encapsulation mechanisms. ML-KEM keys can also be represented as `KeyObject` values.

### ML-DSA signing and verification (since 24.6.0)

`node:crypto` can now represent ML-DSA keys as `KeyObject` values and use them with its signing and verification APIs.

### Raw `KeyObject` formats (since 26.0.0)

The `node:crypto` `KeyObject` APIs now support raw key formats, and key-generation APIs recognize raw output formats. Callers no longer need to wrap supported raw key material in DER or PEM solely for import or export.

### Seed-only post-quantum private-key exports (since 26.0.0)

PKCS#8 exports of ML-KEM and ML-DSA private keys now default to the seed-only representation. Consumers that assumed the previous expanded encoding must account for the changed exported bytes.

### Signature contexts for Ed448 and ML-DSA (since 24.8.0)

Both `node:crypto` and WebCrypto signing and verification now support an application-provided context for Ed448 and ML-DSA. With the classic API, pass it alongside the key, as in `sign(null, data, { key: privateKey, context })`, and supply the identical context to `verify()`; WebCrypto accepts `context` in the sign or verify algorithm parameters.

### SLH-DSA in `node:crypto` (since 24.8.0)

`KeyObject` can now represent SLH-DSA keys, and the regular `node:crypto` signing and verification APIs accept them.

### X.509 signature algorithms (since 24.9.0)

`X509Certificate.signatureAlgorithm` exposes the algorithm with which a certificate was signed, avoiding manual certificate parsing.


## Hashing, MACs, and password derivation

### `Hmac.digest()` documentation deprecation (since 24.18.0)

`Hmac.prototype.digest()` is now documentation-deprecated as DEP0206; this release does not make it a runtime deprecation.

### Built-in Argon2 (since 24.7.0)

`node:crypto` now exposes asynchronous `argon2()` and synchronous `argon2Sync()` methods for Argon2 password hashing.

### Variable-length one-shot XOF hashes (since 24.4.0)

`crypto.hash()` accepts an `outputLength` option for extensible-output functions such as SHAKE, so the one-shot helper can request a specific digest length: `hash('shake256', 'payload', { outputLength: 32 })`.


## Compression

### Brotli web compression streams (since 24.7.0)

The Web `CompressionStream` and `DecompressionStream` implementations now support Brotli, enabling streaming Brotli transforms without switching to the `node:zlib` APIs.

### Experimental Zstandard compression (since 23.8.0)

`node:zlib` now provides compression and decompression APIs for Zstandard streams. All zstd functions are experimental in this release.

### Removed `zlib.bytesRead` (since 23.0.0)

The deprecated `zlib.bytesRead` property has been removed. Use `zlib.bytesWritten`, of which it was an alias.

### Strict trailing-data decompression (since 26.5.0)

Zlib decoder options now expose `rejectGarbageAfterEnd` for rejecting data after a compressed stream ends—for example, `gunzipSync(data, { rejectGarbageAfterEnd: true })`—and web decompression streams now reject trailing gzip members.

### Zstandard dictionaries (since 24.6.0)

The `zstdCompress()` and `zstdDecompress()` APIs now support compression dictionaries.


## Compatibility and security

### `CryptoKey` input migrations (since 25.9.0)

Using Web Crypto `CryptoKey` values with classic `node:crypto` APIs is deprecated, and QUIC session-key options no longer accept them. WebCrypto also rejects ML-KEM and ML-DSA PKCS#8 imports that omit the seed.

### Async crypto security correction (since 23.11.0)

23.11.1 is a security release that corrects error handling in asynchronous crypto operations for CVE-2025-23166; deployments on 23.11.0 should upgrade to that patch release.

### Crypto removals and deprecations (since 25.0.0)

The implicit output lengths for `shake128` and `shake256` are runtime-deprecated, so XOF hashes should specify `outputLength`. The deprecated RSA-PSS key-generation options `hash` and `mgf1Hash` are removed in favor of `hashAlgorithm` and `mgf1HashAlgorithm`, and `ECDH.setPublicKey()` is now runtime-deprecated.

```js
import { createHash } from 'node:crypto';

const digest = createHash('shake256', { outputLength: 32 })
  .update('payload')
  .digest();
```

### End-of-life short GCM tag handling (since 26.0.0)

DEP0182 has reached end-of-life: code using short GCM authentication tags must explicitly provide `authTagLength` when creating the decipher rather than relying on implicit tag-length handling.

### Native crypto and OpenSSL 4 builds (since 25.9.0)

Native addons can access OpenSSL contexts through the new `crypto::GetSSLCtx` API, and Node source builds can now compile and link against OpenSSL 4.0.

### OpenSSL details on asynchronous crypto errors (since 26.0.0)

Errors from asynchronous crypto jobs now carry underlying OpenSSL error details. Diagnostics can inspect that added information, while tests should not assume the older error shape or exact message.

### OpenSSL security level 2 default (since 24.8.0)

Node's documented OpenSSL default security level is 2. TLS and crypto configurations using keys, signature algorithms, or ciphers rejected at that level must be modernized or explicitly handled rather than assuming level 1 compatibility.
