# Cryptography, TLS, and X.509

## FIPS selection and timing policy

### Build-time and runtime FIPS selection (`1.24.0`)

`GOFIPS140` selects the Go Cryptographic Module used in a build. The `fips140`
`GODEBUG` setting enables FIPS 140-3 mode at runtime, and approved
standard-library algorithms use the module transparently.

### Data-independent timing mode (`1.24.0`)

`subtle.WithDataIndependentTiming` runs a callback with architecture support
for data-value-independent instruction timing. It initially enables PSTATE.DIT
on arm64 and is a no-op elsewhere. `GODEBUG=dataindependenttiming=1` enables
the mode process-wide.

### FIPS enforcement controls (`1.26.0`)

`crypto/fips140.WithoutEnforcement` and `Enforced` support selective strict
checks under `GODEBUG=fips140=only`. `Version` reports the resolved frozen
module version selected with `GOFIPS140`.

### Data-independent timing propagation (`1.26.0`)

`subtle.WithDataIndependentTiming` no longer pins the caller to an OS thread.
Goroutines spawned inside it and descendants inherit the mode for their
lifetimes. The mode propagates into cgo calls, and timing state established by
C is preserved when C calls Go.

## Randomness, ciphers, and signing

### Cipher API compatibility (`1.24.0`)

The concrete AES block from `aes.NewCipher` no longer exposes undocumented
CTR, GCM, or CBC constructors; pass it to `crypto/cipher` functions.
`NewOFB`, `NewCFBEncrypter`, and `NewCFBDecrypter` are deprecated in favor of
authenticated `AEAD` modes, or `NewCTR` when unauthenticated streaming is
unavoidable.

### Deterministic ECDSA signing (`1.24.0`)

`ecdsa.PrivateKey.Sign` produces an RFC 6979 deterministic signature when its
random source is nil.

### Fatal `crypto/rand.Read` failures (`1.24.0`)

`crypto/rand.Read` returns a nil error; a failure of its `Reader` irrecoverably
crashes the process. This chiefly affects programs replacing the package-level
`Reader`.

### Message-level signing (`1.25.0`)

`crypto.MessageSigner` lets a signer hash an entire message, and
`crypto.SignMessage` uses it when available while falling back to
`crypto.Signer`. X.509 certificate, request, and revocation-list creation
accepts either interface.

### Non-injectable cryptographic randomness (`1.26.0`)

Randomness arguments are ignored by DSA, ECDH, and RSA key generation, ECDSA
key generation and signing, `rand.Prime`, and RSA PKCS #1 v1.5 encryption.
`ed25519.GenerateKey(nil)` also bypasses replaceable `crypto/rand.Reader`. Use
`testing/cryptotest.SetGlobalRandom` for deterministic tests, or temporarily
restore the former behavior with `GODEBUG=cryptocustomrand=1`.

### Cryptographic known-answer tests (`1.26.0`)

`crypto/mlkem/mlkemtest` provides deterministic `Encapsulate768` and
`Encapsulate1024` operations for ML-KEM known-answer tests.

### ML-DSA signatures (`1.27.0`)

`crypto/mldsa` implements the FIPS 204 post-quantum signature scheme. X.509
supports ML-DSA keys and signatures, and TLS 1.3 supports ML-DSA signature
algorithms.

## RSA, KEM, HPKE, and hash state

### Minimum RSA key size (`1.24.0`)

RSA key generation and all signing, verification, encryption, and decryption
operations reject keys smaller than 1024 bits.
`GODEBUG=rsa1024min=0` temporarily restores the old behavior, principally for
tests.

### Hybrid public-key encryption (`1.26.0`)

`crypto/hpke` implements RFC 9180 Hybrid Public Key Encryption, including
post-quantum hybrid KEM support.

### Abstract key exchange interfaces (`1.26.0`)

`crypto.Encapsulator` and `crypto.Decapsulator` let APIs accept abstract KEM
keys. `ecdh.KeyExchanger` permits abstract ECDH private keys such as
hardware-backed keys. ML-KEM decapsulation keys implement the decapsulation
interface.

### RSA padding and key validation (`1.26.0`)

`rsa.EncryptOAEPWithOptions` can select different hashes for OAEP and MGF1.
`PrivateKey.Validate` rejects fields changed after `Precompute` and checks `D`
against precomputed values. PKCS #1 v1.5 encryption and direct use of ECDSA
key `big.Int` fields are deprecated.

### Usable SHA-3 zero values (`1.26.0`)

The zero value of `sha3.SHA3` is a usable SHA3-256 instance, and the zero value
of `sha3.SHAKE` is a usable SHAKE256 instance.

## TLS negotiation and compatibility

### TLS negotiation changes (`1.24.0`)

Servers can enable ECH with `Config.EncryptedClientHelloKeys`. With nil
`CurvePreferences`, `X25519MLKEM768` is enabled by default;
`GODEBUG=tlsmlkem=0` is a temporary escape hatch. A populated
`CurvePreferences` selects enabled exchanges, but its ordering is ignored.

### TLS negotiation and ECH controls (`1.25.0`)

`ConnectionState.CurveID` reports the negotiated exchange, and
`Config.GetEncryptedClientHelloKeys` selects server ECH keys dynamically. TLS
1.2 rejects SHA-1 signatures unless `GODEBUG=tlssha1=1`; servers prefer their
highest mutually supported protocol version, and off-spec peers are rejected
more strictly.

### TLS post-quantum defaults (`1.26.0`)

Hybrid `SecP256r1MLKEM768` and `SecP384r1MLKEM1024` exchanges are enabled by
default. Set `Config.CurvePreferences` or `GODEBUG=tlssecpmlkem=0` to disable
them.

### TLS handshake state and signing (`1.26.0`)

`ClientHelloInfo.HelloRetryRequest` and
`ConnectionState.HelloRetryRequest` expose retry state. `QUICConn` has an event
for TLS handshake errors. TLS 1.2 and later uses
`Certificate.PrivateKey.SignMessage` when the key implements
`crypto.MessageSigner`.

### Compatibility switches approaching removal (`1.26.0`)

Go 1.27 removes `tlsunsafeekm`, `tlsrsakex`, `tls10server`, `tls3des`, and
`x509keypairleaf`, making the stricter exporter, RSA key-exchange, minimum TLS
version, cipher, and populated-`Certificate.Leaf` behaviors unconditional. It
ignores `gotypesalias` and `asynctimerchan`, so `go/types` always represents
aliases with `Alias` and timers always use synchronous channels.

## Certificates and verification

### X.509 policy semantics (`1.24.0`)

Certificate creation reads policies from `Certificate.Policies` rather than
`PolicyIdentifiers`, though parsing fills both.
`GODEBUG=x509usepolicies=0` temporarily restores old creation behavior.
`VerifyOptions.CertificatePolicies` can require policy OIDs and makes
`Certificate.Verify` validate the policy graph.

### Stricter RSA certificate handling (`1.24.0`)

X.509 verification rejects SHA-1 signatures, and the former `x509sha1` escape
hatch is gone. PKCS #1 and PKCS #8 parsing validates encoded RSA CRT values and
may reject previously accepted keys; `GODEBUG=x509rsacrt=0` restores
recomputation temporarily.

### X.509 identifiers and parsing (`1.25.0`)

`CreateCertificate` derives a missing subject key identifier from truncated
SHA-256 rather than SHA-1; `GODEBUG=x509sha256skid=0` is a fallback. ASN.1 and
certificate parsing is stricter for malformed T61 or BMP strings and rejects
negative basic-constraints path lengths.

### Platform certificate-file overrides (`1.27.0`)

On Windows and Darwin, X.509 root loading honors `SSL_CERT_FILE` and
`SSL_CERT_DIR`. Setting either loads roots from disk and uses the native Go
verifier instead of platform verification APIs.
`GODEBUG=x509sslcertoverrideplatform=0` disables this behavior.
