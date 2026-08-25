# Cryptography and Compression

Use this reference for cryptography and compression work.

## 23.11.1 async-crypto security fix (`23.11.0`)

Node.js 23.11.1 is a security release fixing CVE-2025-23166 in error handling for asynchronous crypto operations. Deployments on 23.11.0 should upgrade to 23.11.1.

## `CryptoKey` input migrations (`25.9.0`)

Passing WebCrypto `CryptoKey` objects to classic `node:crypto` APIs is documentation-deprecated; convert them with `KeyObject.from()` or stay within WebCrypto. QUIC session-key options no longer accept `CryptoKey` values.

```js
import { KeyObject } from 'node:crypto';

const keyObject = KeyObject.from(cryptoKey);
```

## Argon2 in WebCrypto (`24.8.0`)

In addition to the `node:crypto` Argon2 helpers, WebCrypto can now derive key material with Argon2 through `SubtleCrypto.deriveBits()`.

## Bit-granular Web Crypto derivation (`23.4.0`)

`SubtleCrypto.deriveBits()` now accepts requested lengths that are not divisible by eight.

## Brotli Web compression streams (`24.7.0`)

`CompressionStream` and `DecompressionStream` now accept Brotli as a compression format.

```js
const compressed = input.pipeThrough(new CompressionStream('brotli'));
```

## Built-in Argon2 (`24.7.0`)

`node:crypto` adds asynchronous `argon2()` and synchronous `argon2Sync()` methods, making Argon2 password derivation available without a separate native add-on.

## Callback-based Diffie-Hellman (`23.11.0`)

`crypto.diffieHellman()` accepts an optional callback in addition to its synchronous return form, allowing key agreement to complete asynchronously.

```js
import { diffieHellman, generateKeyPairSync } from 'node:crypto';

const alice = generateKeyPairSync('x25519');
const bob = generateKeyPairSync('x25519');
diffieHellman(
  { privateKey: alice.privateKey, publicKey: bob.publicKey },
  (error, secret) => {
    if (error) throw error;
    console.log(secret);
  },
);
```

## Crypto migrations (`25.0.0`)

Default output lengths for `shake128` and `shake256` are runtime-deprecated, so callers should specify `outputLength`. The deprecated `hash` and `mgf1Hash` RSA-PSS option names are removed in favor of `hashAlgorithm` and `mgf1HashAlgorithm`, and `ECDH.setPublicKey()` is runtime-deprecated.

```js
import { createHash } from 'node:crypto';

const digest = createHash('shake256', { outputLength: 32 })
  .update('payload')
  .digest();
```

## Crypto policy and parameter validation (`26.7.0`)

KangarooTwelve customization input is limited to 512 bytes, and Argon2 no longer bypasses FIPS mode. Callers must keep customization data within the limit and expect the active FIPS policy to be enforced for Argon2.

## Direct key data for Diffie-Hellman (`24.18.0`)

`crypto.diffieHellman()` now accepts key data directly for its private- and public-key inputs instead of requiring callers to construct key objects first.

```js
import { diffieHellman } from 'node:crypto';

const secret = diffieHellman({
  privateKey: privateKeyPem,
  publicKey: publicKeyPem,
});
```

## Expanded BoringSSL crypto support (`24.18.0`)

Custom BoringSSL builds now wire ML-DSA and ML-KEM plus WebCrypto ChaCha20-Poly1305 and AES-KW. Feature-detect these algorithms when supporting both OpenSSL- and BoringSSL-based builds.

## Experimental Zstandard compression (`23.8.0`)

`node:zlib` now provides compression and decompression APIs for Zstandard streams. All zstd functions are experimental in this release.

## Explicit short GCM tag lengths (`26.0.0`)

DEP0182 is end-of-life, so callers using short GCM authentication tags must pass `authTagLength` when creating the decipher.

```js
createDecipheriv('aes-128-gcm', key, iv, { authTagLength: tag.length });
```

## Key encapsulation in `node:crypto` (`24.7.0`)

`crypto.encapsulate()` and `crypto.decapsulate()` add key-encapsulation support for ML-KEM, DHKEM, and RSASVE. With ML-KEM, the sender gets a shared key and ciphertext from the public key, and the recipient recovers the same shared key with the private key.

```js
import {
  decapsulate,
  encapsulate,
  generateKeyPairSync,
} from 'node:crypto';

const { publicKey, privateKey } = generateKeyPairSync('ml-kem-768');
const { sharedKey, ciphertext } = encapsulate(publicKey);
const recipientKey = decapsulate(privateKey, ciphertext);
```

## KMAC in WebCrypto (`24.8.0`)

WebCrypto now supports KMAC algorithms through `SubtleCrypto.sign()` and `SubtleCrypto.verify()`, providing keyed message authentication without a separate implementation.

## ML-DSA keys and signatures (`24.6.0`)

`node:crypto` can now represent ML-DSA keys as `KeyObject`s and use them with the built-in signing and verification APIs.

```js
import { generateKeyPairSync, sign, verify } from 'node:crypto';

const { privateKey, publicKey } = generateKeyPairSync('ml-dsa-65');
const data = Buffer.from('post-quantum signature');
const signature = sign(null, data, privateKey);
console.log(verify(null, data, publicKey, signature)); // true
```

## Modern WebCrypto algorithms and capability checks (`24.7.0`)

WebCrypto now supports AES-OCB, ChaCha20-Poly1305, ML-DSA, ML-KEM, SHA-3, and SHAKE. It also adds `subtle.getPublicKey()` and `SubtleCrypto.supports()`; use the latter to check availability before selecting these newer algorithms, especially on nonstandard builds. HMAC configurations using SHA-3 hashes must specify the key length.

## Native crypto and OpenSSL 4 builds (`25.9.0`)

Native addons gain `crypto::GetSSLCtx()` for access to OpenSSL contexts, and Node can now be compiled and linked with OpenSSL 4.0.

## OpenSSL details on asynchronous crypto errors (`26.0.0`)

Errors from asynchronous crypto jobs now include underlying OpenSSL error details, changing the information available to diagnostics and potentially the error shape expected by tests.

## OpenSSL security level 2 default (`24.8.0`)

Node's documented default OpenSSL security level is 2. TLS or crypto configurations using keys, signature algorithms, or ciphers rejected at that level must be modernized or handled explicitly.

## OpenSSL STORE-backed private keys (`26.7.0`)

Private-key loading can now use OpenSSL STORE loaders, allowing provider-backed key stores to supply keys instead of requiring ordinary in-memory key material.

## Post-quantum JWK keys (`24.18.0`)

The crypto APIs now support JWK representations for ML-KEM and SLH-DSA keys, allowing those key types to participate in JWK import and export workflows.

## Post-quantum PKCS#8 imports require a seed (`25.9.0`)

WebCrypto now rejects ML-KEM and ML-DSA PKCS#8 private-key imports whose encoding does not contain the seed. Importers must retain or produce the seed-bearing form.

## Raw keys and Ed25519 contexts (`26.0.0`)

`KeyObject` APIs support raw key formats, and key-generation APIs recognize raw output formats. Ed25519 signing and verification also accept a context, which must match on both operations.

```js
import { generateKeyPairSync, sign, verify } from 'node:crypto';

const { privateKey, publicKey } = generateKeyPairSync('ed25519');
const data = Buffer.from('payload');
const context = Buffer.from('protocol-v1');
const signature = sign(null, data, { key: privateKey, context });
const valid = verify(null, data, { key: publicKey, context }, signature);
```

## Rejecting trailing compressed data (`26.5.0`)

Zlib decoder options now accept `rejectGarbageAfterEnd`, and Web decompression streams reject trailing gzip members.

```js
import { gunzipSync } from 'node:zlib';

const output = gunzipSync(input, { rejectGarbageAfterEnd: true });
```

## RSA-PSS salt-length default (`25.2.0`)

Node.js 25.2.1 corrects RSA-PSS operations to use the documented default `saltLength`; callers that depend on a particular salt policy should set `saltLength` explicitly.

## Seed-only post-quantum private-key exports (`26.0.0`)

PKCS#8 exports of ML-KEM and ML-DSA private keys now default to their seed-only representation. Consumers that expect the previous expanded encoding must account for different exported bytes.

## Signature contexts for Ed448 and ML-DSA (`24.8.0`)

Both `node:crypto` and WebCrypto signing and verification now accept an application-provided context for Ed448 and ML-DSA. The verifier must receive the same context bytes as the signer.

```js
import { generateKeyPairSync, sign, verify } from 'node:crypto';

const { privateKey, publicKey } = generateKeyPairSync('ed448');
const data = Buffer.from('payload');
const context = Buffer.from('protocol-v1');
const signature = sign(null, data, { key: privateKey, context });
console.log(verify(null, data, { key: publicKey, context }, signature));
```

## SLH-DSA in `node:crypto` (`24.8.0`)

`KeyObject` can now represent SLH-DSA keys, and the regular `node:crypto` signing and verification APIs accept them.

## Stricter and broader Zstandard inputs (`26.7.0`)

Zstandard decompression now rejects truncated input, while Zstandard dictionaries accept `ArrayBuffer` values. Callers must handle incomplete data as an error and no longer need to convert an `ArrayBuffer` dictionary first.

## TurboSHAKE and KangarooTwelve in WebCrypto (`25.9.0`)

WebCrypto now supports TurboSHAKE and KangarooTwelve. The output-size member for cSHAKE and KMAC parameters is also renamed from `length` to `outputLength`, so experimental-algorithm callers must update their option objects.

## Variable-length one-shot XOF hashes (`24.4.0`)

`crypto.hash()` now accepts an `outputLength` option for extendable-output functions, allowing callers to choose the digest size without using the streaming hash API.

```js
import { hash } from 'node:crypto';

const digest = hash('shake256', 'payload', { outputLength: 32 });
```

## Zero-length Web Crypto derivations (`23.3.0`)

`SubtleCrypto.deriveBits()` now accepts a length of `0` for HKDF and PBKDF2 instead of rejecting the request.

## Zlib write-buffer bounds (`22.23.2`)

Zlib writes now throw when their write buffer is out of bounds. Callers that construct buffer views or offsets dynamically must validate them or handle the exception.

## Zstandard dictionaries (`24.6.0`)

The one-shot `zstdCompress()` and `zstdDecompress()` APIs now accept a shared `dictionary` option. Decompression must use the same dictionary that was used for compression.

```js
import { promisify } from 'node:util';
import { zstdCompress, zstdDecompress } from 'node:zlib';

const compress = promisify(zstdCompress);
const decompress = promisify(zstdDecompress);
const dictionary = Buffer.from('common application vocabulary');
const compressed = await compress(Buffer.from('application data'), { dictionary });
const restored = await decompress(compressed, { dictionary });
```
