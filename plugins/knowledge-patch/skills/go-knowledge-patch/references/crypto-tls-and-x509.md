# Cryptography, TLS, and X.509

Batch coverage: `1.24.0`, `1.25.0`, `1.26.0`.

## Contents

- [FIPS selection and enforcement](#fips-selection-and-enforcement)
- [Randomness and timing](#randomness-and-timing)
- [Signing and key exchange abstractions](#signing-and-key-exchange-abstractions)
- [RSA, ECDSA, and cipher changes](#rsa-ecdsa-and-cipher-changes)
- [Hash interfaces and SHA-3](#hash-interfaces-and-sha-3)
- [TLS negotiation](#tls-negotiation)
- [X.509 behavior](#x509-behavior)
- [Compatibility switches](#compatibility-switches)

## FIPS selection and enforcement

`GOFIPS140` selects the Go Cryptographic Module version included in a build. The `fips140` `GODEBUG` setting enables FIPS 140-3 mode at runtime; approved standard-library algorithms use the module transparently.

`crypto/fips140.WithoutEnforcement` and `Enforced` support selective handling of strict checks while running with `GODEBUG=fips140=only`. `crypto/fips140.Version` reports the resolved frozen module version chosen through `GOFIPS140`.

## Randomness and timing

### Fatal `crypto/rand.Read` failures

`crypto/rand.Read` is guaranteed to return a nil error. Failure of its `Reader` irrecoverably crashes the process instead. This primarily affects programs that replace the package-level `Reader`.

### Non-injectable cryptographic randomness

In Go 1.26.0, randomness arguments are ignored by:

- DSA, ECDH, and RSA key generation.
- ECDSA key generation and signing.
- `rand.Prime`.
- RSA PKCS #1 v1.5 encryption.

`ed25519.GenerateKey(nil)` also bypasses the replaceable `crypto/rand.Reader`. Use `testing/cryptotest.SetGlobalRandom` for deterministic tests. Set `GODEBUG=cryptocustomrand=1` only as a temporary way to restore the former injection behavior.

### Data-independent timing

`subtle.WithDataIndependentTiming` runs a callback with architecture support for data-value-independent instruction timing. It enables PSTATE.DIT on arm64 and is a no-op on architectures without support. Set `GODEBUG=dataindependenttiming=1` to enable the mode process-wide.

The callback no longer pins its caller to an OS thread. Goroutines started inside it, and their descendants, inherit the mode for their lifetimes. The mode propagates into cgo calls, and timing state established by C is preserved while C calls into Go.

### Experimental secret erasure

`GOEXPERIMENT=runtimesecret` exposes `runtime/secret` for erasing secret-bearing temporaries from registers, stacks, and new heap allocations. It is supported only on Linux amd64 and arm64 in Go 1.26.

## Signing and key exchange abstractions

### Message-level signing

`crypto.MessageSigner` lets a signer hash a complete message itself. `crypto.SignMessage` uses that interface when available and falls back to `crypto.Signer`. X.509 certificate, certificate-request, and revocation-list creation accepts either interface.

TLS 1.2 and later uses `Certificate.PrivateKey.SignMessage` when the key implements `crypto.MessageSigner`.

### Abstract KEM and ECDH keys

`crypto.Encapsulator` and `crypto.Decapsulator` allow APIs to accept abstract KEM keys. `ecdh.KeyExchanger` supports abstract ECDH private keys such as hardware-backed keys. ML-KEM decapsulation keys implement the decapsulation interface.

### Hybrid public-key encryption

The `crypto/hpke` package implements RFC 9180 Hybrid Public Key Encryption, including post-quantum hybrid KEM support.

### Known-answer tests

`crypto/mlkem/mlkemtest` provides deterministic `Encapsulate768` and `Encapsulate1024` operations for ML-KEM known-answer tests.

## RSA, ECDSA, and cipher changes

### Cipher API compatibility

The concrete AES block returned by `aes.NewCipher` no longer exposes undocumented CTR, GCM, or CBC constructor methods. Pass the block to the corresponding `crypto/cipher` functions.

`NewOFB`, `NewCFBEncrypter`, and `NewCFBDecrypter` are deprecated. Prefer authenticated `AEAD` modes, or `NewCTR` when unauthenticated streaming is unavoidable.

### Deterministic ECDSA

Go 1.24.0 made `ecdsa.PrivateKey.Sign` create an RFC 6979 deterministic signature when its random source was nil. Go 1.26.0 supersedes caller control of that source: signing ignores the randomness argument, as described above. Use `testing/cryptotest.SetGlobalRandom` for deterministic tests.

### RSA minimum and validation

RSA key generation, signing, verification, encryption, and decryption reject keys smaller than 1024 bits. Set `GODEBUG=rsa1024min=0` only to restore legacy behavior temporarily, principally in tests.

`rsa.EncryptOAEPWithOptions` can use different hash functions for OAEP and MGF1. `PrivateKey.Validate` rejects fields modified after `Precompute` and checks `D` against precomputed values.

PKCS #1 v1.5 encryption and the `big.Int` fields of ECDSA keys are deprecated.

## Hash interfaces and SHA-3

`hash.XOF` represents arbitrary-length-output hashes such as SHAKE. `hash.Cloner` copies hash state. Every standard-library `hash.Hash` implementation is cloneable, including implementations with new clone methods for SHA-3 and `maphash.Hash`.

The zero value of `sha3.SHA3` is a usable SHA3-256 instance. The zero value of `sha3.SHAKE` is a usable SHAKE256 instance.

## TLS negotiation

### Encrypted Client Hello and curves

Servers can configure Encrypted Client Hello through `Config.EncryptedClientHelloKeys`. `Config.GetEncryptedClientHelloKeys` can select server ECH keys dynamically.

When `CurvePreferences` is nil, `X25519MLKEM768` is enabled by default; `GODEBUG=tlsmlkem=0` is the compatibility escape hatch. A non-empty `CurvePreferences` selects enabled exchanges, but its order is ignored.

The hybrid `SecP256r1MLKEM768` and `SecP384r1MLKEM1024` exchanges are also enabled by default. Set `Config.CurvePreferences` or `GODEBUG=tlssecpmlkem=0` to disable them.

`ConnectionState.CurveID` reports the negotiated key exchange.

### Protocol and signature behavior

TLS 1.2 rejects SHA-1 signatures unless `GODEBUG=tlssha1=1`. Servers prefer their highest mutually supported protocol version, and peers are rejected more strictly for off-spec behavior.

`ClientHelloInfo.HelloRetryRequest` and `ConnectionState.HelloRetryRequest` expose retry state. `QUICConn` emits an event for TLS handshake errors.

## X.509 behavior

### Certificate policies

Certificate creation reads policies from `Certificate.Policies` rather than `PolicyIdentifiers`, although parsing fills both fields. Set `GODEBUG=x509usepolicies=0` to restore old creation behavior temporarily.

`VerifyOptions.CertificatePolicies` can require acceptable policy OIDs and causes `Certificate.Verify` to validate the policy graph.

### RSA certificates and keys

X.509 verification rejects SHA-1 signatures; the former `x509sha1` escape hatch is gone.

PKCS #1 and PKCS #8 parsing validates encoded RSA CRT values and may reject keys previously accepted. Set `GODEBUG=x509rsacrt=0` to restore CRT recomputation temporarily.

### Identifiers and strict parsing

`CreateCertificate` derives a missing subject key identifier from truncated SHA-256 instead of SHA-1. Set `GODEBUG=x509sha256skid=0` for temporary compatibility.

ASN.1 and certificate parsing is stricter for malformed T61 and BMP strings and rejects negative basic-constraints path lengths.

## Compatibility switches

Go 1.27 is scheduled to remove these switches:

- `tlsunsafeekm`
- `tlsrsakex`
- `tls10server`
- `tls3des`
- `x509keypairleaf`

The stricter exporter, RSA key-exchange, TLS-version, cipher, and populated-`Certificate.Leaf` behaviors then become unconditional.
