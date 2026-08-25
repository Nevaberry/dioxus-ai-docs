# Cryptography, TLS, and X.509

## FIPS selection and timing controls

### Build and runtime FIPS modes (1.24.0, 1.26.0)

`GOFIPS140` selects the Go Cryptographic Module version at build time. The
`fips140` `GODEBUG` setting enables FIPS 140-3 mode at runtime, and approved
standard-library algorithms use the selected module transparently.

When running with `GODEBUG=fips140=only`, use
`crypto/fips140.WithoutEnforcement` only for deliberately scoped exceptions;
`Enforced` reports enforcement state and `Version` reports the resolved frozen
module version selected by `GOFIPS140`.

### Data-independent timing (1.24.0, 1.26.0)

`subtle.WithDataIndependentTiming` runs a callback with architecture support
for data-value-independent instruction timing. It initially enabled PSTATE.DIT
on arm64 and was a no-op elsewhere; `GODEBUG=dataindependenttiming=1` enables
the mode process-wide.

The callback no longer pins its caller to an OS thread. Goroutines created
inside it and their descendants inherit the mode for their lifetimes. The mode
propagates into cgo, and timing state established by C is preserved when C
calls Go.

## Symmetric encryption and randomness

### Cipher API compatibility (1.24.0)

The concrete block returned by `aes.NewCipher` no longer exposes undocumented
CTR, GCM, or CBC constructors. Pass it to the corresponding `crypto/cipher`
functions. `NewOFB`, `NewCFBEncrypter`, and `NewCFBDecrypter` are deprecated;
prefer authenticated `AEAD`, or `NewCTR` only when unauthenticated streaming is
unavoidable.

### Randomness failure and determinism (1.24.0, 1.26.0)

`crypto/rand.Read` returns a nil error; a failure of its `Reader` crashes the
process. Avoid replacing the package-level reader.

Randomness arguments are ignored by DSA, ECDH, and RSA key generation, ECDSA
key generation and signing, `rand.Prime`, and RSA PKCS #1 v1.5 encryption.
`ed25519.GenerateKey(nil)` also bypasses replaceable `crypto/rand.Reader`.
Use `testing/cryptotest.SetGlobalRandom` for deterministic tests.
`GODEBUG=cryptocustomrand=1` only temporarily restores prior injection.

`ecdsa.PrivateKey.Sign` uses RFC 6979 deterministic signatures when its random
source is nil.

## Signing, KEMs, and hashing

### Message-level signing (1.25.0, 1.26.0)

`crypto.MessageSigner` lets a key sign an entire message, and
`crypto.SignMessage` uses it when implemented while falling back to
`crypto.Signer`. X.509 certificate, request, and revocation-list creation
accepts either interface. TLS 1.2 and later calls
`Certificate.PrivateKey.SignMessage` when available.

### HPKE and abstract key exchange (1.26.0)

`crypto/hpke` implements RFC 9180 Hybrid Public Key Encryption, including
post-quantum hybrid KEM support. `crypto.Encapsulator` and
`crypto.Decapsulator` abstract KEM keys; `ecdh.KeyExchanger` supports abstract
or hardware-backed ECDH private keys. ML-KEM decapsulation keys implement the
decapsulation interface.

For deterministic ML-KEM known-answer tests, use
`crypto/mlkem/mlkemtest.Encapsulate768` or `Encapsulate1024`.

### ML-DSA and SHA-3 (1.26.0, 1.27.0)

The zero value of `sha3.SHA3` is a usable SHA3-256 instance, and the zero value
of `sha3.SHAKE` is a usable SHAKE256 instance.

`crypto/mldsa` implements the FIPS 204 ML-DSA post-quantum signature scheme.
X.509 supports ML-DSA keys and signatures, and TLS 1.3 supports ML-DSA
signature algorithms.

## RSA and X.509 validation

### Minimum key sizes and parsing (1.24.0)

RSA generation, signing, verification, encryption, and decryption reject keys
smaller than 1024 bits. `GODEBUG=rsa1024min=0` is a temporary test-oriented
escape hatch.

X.509 verification rejects SHA-1 signatures and the former `x509sha1` escape
hatch is gone. PKCS #1 and PKCS #8 parsing validates encoded RSA CRT values and
can reject previously accepted keys; `GODEBUG=x509rsacrt=0` temporarily
recomputes them.

### Certificate policies (1.24.0)

Certificate creation reads policies from `Certificate.Policies`, while parsing
populates both `Policies` and `PolicyIdentifiers`.
`GODEBUG=x509usepolicies=0` restores old creation behavior.
`VerifyOptions.CertificatePolicies` can require acceptable policy OIDs and
causes `Certificate.Verify` to validate the policy graph.

### Identifiers and stricter ASN.1 (1.25.0)

`CreateCertificate` derives a missing subject key identifier from truncated
SHA-256 instead of SHA-1; `GODEBUG=x509sha256skid=0` restores the old derivation.
ASN.1 and certificate parsing is stricter for malformed T61 or BMP strings and
rejects negative basic-constraints path lengths.

### RSA padding and private-key integrity (1.26.0)

`rsa.EncryptOAEPWithOptions` can select different hashes for OAEP and MGF1.
`PrivateKey.Validate` rejects fields mutated after `Precompute` and verifies
`D` against precomputed values. PKCS #1 v1.5 encryption and direct use of the
`big.Int` fields on ECDSA keys are deprecated.

### Platform certificate overrides (1.27.0)

On Windows and Darwin, setting `SSL_CERT_FILE` or `SSL_CERT_DIR` loads roots
from disk and switches verification from platform APIs to the native Go
verifier. `GODEBUG=x509sslcertoverrideplatform=0` disables that override.

## TLS negotiation and compatibility

### ECH and hybrid exchange defaults (1.24.0, 1.25.0, 1.26.0)

Servers can configure ECH through `Config.EncryptedClientHelloKeys`; the newer
`Config.GetEncryptedClientHelloKeys` selects keys dynamically.
`ConnectionState.CurveID` reports the negotiated exchange.

When `CurvePreferences` is nil, `X25519MLKEM768` is enabled by default;
`GODEBUG=tlsmlkem=0` was its compatibility switch. The additional hybrids
`SecP256r1MLKEM768` and `SecP384r1MLKEM1024` are also enabled by default; set
`CurvePreferences` or `GODEBUG=tlssecpmlkem=0` when interoperability requires
disabling them. A non-empty `CurvePreferences` selects enabled exchanges but
its order is ignored.

TLS 1.2 rejects SHA-1 signatures unless `GODEBUG=tlssha1=1`. Servers prefer
their highest mutually supported protocol version and reject off-spec peers
more strictly.

### Handshake state (1.26.0)

`ClientHelloInfo.HelloRetryRequest` and
`ConnectionState.HelloRetryRequest` expose retry state. `QUICConn` emits an
event for TLS handshake errors.

### Escape hatches removed or expiring (1.26.0)

Do not depend on `tlsunsafeekm`, `tlsrsakex`, `tls10server`, `tls3des`, or
`x509keypairleaf`; their stricter behaviors become unconditional. Likewise,
`gotypesalias` and `asynctimerchan` no longer restore old alias representation
or asynchronous timer channels.
