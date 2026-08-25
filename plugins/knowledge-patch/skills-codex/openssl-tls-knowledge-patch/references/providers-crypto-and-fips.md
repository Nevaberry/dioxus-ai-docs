# Providers, Cryptography, and FIPS

## Contents

- [Provider configuration](#provider-configuration)
- [Digest and cipher behavior](#digest-and-cipher-behavior)
- [Key import, generation, and opaque keys](#key-import-generation-and-opaque-keys)
- [Post-quantum algorithms and oqsprovider](#post-quantum-algorithms-and-oqsprovider)
- [FIPS approval and self-tests](#fips-approval-and-self-tests)
- [Random generation](#random-generation)
- [Additional provider algorithms](#additional-provider-algorithms)

## Provider configuration

### Parse provider booleans strictly

Provider `activate` and `soft_load` settings enable only for `1`, `yes`, `true`, or `on`, and disable only for `0`, `no`, `false`, or `off`; matching is case-insensitive (since 3.3.0). Do not depend on arbitrary nonempty values being truthy.

### Pass runtime provider parameters

Use the repeatable common option `-provparam [name:]key=value` to pass a UTF-8 string parameter to one named provider or, without a name, to every loaded provider. Load nondefault providers first. Put initialization-only parameters in configuration because setting them after load cannot affect provider initialization.

## Digest and cipher behavior

### Squeeze SHAKE repeatedly

Use `EVP_DigestSqueeze()` to squeeze the same SHAKE digest context repeatedly with different output lengths (since 3.3.0).

### Set SHAKE output length

SHAKE-128 and SHAKE-256 no longer have a default digest length. Set the `xoflen` parameter before `EVP_DigestFinal()` or `EVP_DigestFinal_ex()` (since 3.4.0). Do not assume a historical default output size.

### Configure BLAKE2s output length

BLAKE2s supports configurable digest lengths, matching the capability of BLAKE2b (since 3.3.0).

### Use cipher pipelining

Provider-supplied cipher algorithms have APIs for pipelining multiple operations (since 3.5.0). Verify that the selected provider and cipher implement the operation before building a throughput design around it.

### Fetch composite signatures directly

Composite signature algorithms such as RSA-SHA2-256 can be fetched directly, with dedicated APIs supporting the operation (since 3.4.0). Keep fetch properties consistent with the provider and FIPS policy used by the rest of the operation.

## Key import, generation, and opaque keys

### Derive CRT parameters during import

`EVP_PKEY_fromdata()` can derive Chinese Remainder Theorem parameters when the caller requests them (since 3.3.0). Use the provider import interface instead of filling legacy key structures.

### Use opaque symmetric-key objects

`EVP_SKEY` represents symmetric keys opaquely, allowing cryptographic operations to use key objects without exposing raw bytes (since 3.5.0).

OpenSSL 3.6 extends opaque symmetric keys to provider key-derivation and key-exchange methods. Use `EVP_KDF_CTX_set_SKEY()`, `EVP_KDF_derive_SKEY()`, and `EVP_PKEY_derive_SKEY()` to consume or produce opaque key objects without materializing their bytes.

### Inspect NIST security categories

OpenSSL 3.6 adds NIST security categories for PKEY objects, allowing key strength to be expressed by a standardized category rather than only algorithm-specific parameters.

## Post-quantum algorithms and `oqsprovider`

### Prefer native standardized algorithms

OpenSSL 3.5 natively supplies ML-KEM, ML-DSA, SLH-DSA, and standardized hybrid post-quantum schemes. On 3.5 or newer, `oqsprovider` disables its copies of those families and their hybrids at runtime to avoid duplicate identifiers and incompatible key representations. Fetch standardized algorithms from OpenSSL's default provider (source batch `3.5-guide`).

### Discover the enabled OQS subset

The usable `oqsprovider` set depends on both its liboqs build and algorithms already supplied by the runtime OpenSSL. Query the loaded provider rather than relying on the full upstream catalog:

```sh
openssl list -kem-algorithms -provider oqsprovider
openssl list -signature-algorithms -provider oqsprovider
```

### Respect provider version gates

OpenSSL 3.0 and 3.1 cannot use provider-backed CMS or provider signature algorithms in TLS 1.3. OpenSSL 3.2 and newer support full TLS 1.3 post-quantum operations, including signatures. OpenSSL 3.4 adds `pkeyutl -encap` and `-decap` testing when `oqsprovider` is built with KEM encoding support, plus `openssl list -tls-signature-algorithms`.

### Use the correct hybrid-signature operation

With OpenSSL 3.4 or newer, hybrid signature components hash input only for `EVP_PKEY_OP_SIGNMSG` and `EVP_PKEY_OP_VERIFYMSG`. The `EVP_PKEY_sign_init()` path expects an appropriately sized message instead of applying those message-hashing semantics.

## FIPS approval and self-tests

### Treat X25519 and X448 as unapproved in the FIPS provider

The FIPS-provider implementations of X25519 and X448 advertise `fips=no` and are unapproved (since 3.4.0). A successful fetch from the FIPS provider does not by itself mean the operation is approved.

### Use FIPS indicators

The FIPS provider supports indicators that let callers distinguish approved operation status when integrating with FIPS 140-3 validations (since 3.4.0). Check the indicator at the point required by the application's compliance boundary.

### Account for stricter FIPS validation

OpenSSL 4.0's FIPS provider enforces lower bounds in `PKCS5_PBKDF2_HMAC()`. Strict X.509 verification adds authority-key-identifier checks, and CRL verification performs additional checks. Existing derivation parameters, certificates, and CRLs can therefore fail after migration.

### Follow pairwise-consistency-test changes

OpenSSL 3.5.3 adds a FIPS 140-3 pairwise consistency test during DH key generation. It removes the temporary OpenSSL 3.5.2 tests on RSA, EC, and ECX key import because the standard does not require them. Do not build application expectations around the short-lived import tests.

### Mix a validated provider with newer components carefully

A FIPS provider built from a validated source release can be used with library, TLS, and non-FIPS providers from a newer OpenSSL release only when the validated build and its Security Policy are followed. Test the newer source tree with the validated `fips.so` and `fipsmodule.cnf`, and verify the reported provider version before deployment.

```sh
./util/wrap.pl -fips apps/openssl list -provider-path providers \
  -provider fips -providers
```

### Generate machine-local FIPS installation state

`openssl fipsinstall` runs module self-tests and writes `fipsmodule.cnf` with the module checksum and, for OpenSSL 3.1.2, self-test status. Generate it on every target machine. Install the validated provider independently with `make install_fips`; do not copy 3.1.2 output containing `install-status` between machines.

```sh
openssl fipsinstall -module /path/to/fips.so -out /path/to/fipsmodule.cnf
```

### Defer installation self-tests only deliberately

OpenSSL 4.0 adds `openssl fipsinstall -defer_tests`, which writes module configuration that defers FIPS self-tests until they are needed.

```sh
openssl fipsinstall -module /path/to/fips.so -out fipsmodule.cnf -defer_tests
```

## Random generation

### Add JITTER as a seed source

`JITTER` is an optional random seed source backed by a statically linked jitterentropy library (since 3.4.0).

### Enable FIPS jitter seeding

Configure with `enable-fips-jitter` to let the FIPS provider use the `JITTER` source (since 3.5.0).

### Configure the random-generation chain

Library configuration can select `CTR-DRBG`, `HASH-DRBG`, or `HMAC-DRBG` and set its cipher or digest, fetch properties, seed source, and seed properties. `random_provider` routes `RAND_bytes()` entropy requests to a provider, defaults to `fips`, and falls back to built-in entropy sources when that provider is not loaded.

```ini
openssl_conf = init
[init]
random = rng
[rng]
random = HMAC-DRBG
digest = SHA256
```

## Additional provider algorithms

### Use PBMAC1 in PKCS#12

PKCS#12 implements the RFC 9579 PBMAC1 construction (since 3.4.0). Apply the security patch-floor requirements in [security.md](security.md#password-based-pkcs12-and-cms-validation) before processing untrusted PBMAC1 input.

### Use cSHAKE and ML-DSA-MU

OpenSSL 4.0 adds SP 800-185 cSHAKE and the `ML-DSA-MU` digest algorithm.

### Use SNMP and SRTP KDFs

OpenSSL 4.0 provider algorithms include SNMP KDF and SRTP KDF implementations.

### Verify LMS signatures

OpenSSL 3.6 default and FIPS providers can verify LMS signatures as specified by SP 800-208.

### Generate deterministic ECDSA in FIPS

The OpenSSL 3.6 FIPS provider supports FIPS 186-5 deterministic ECDSA signature generation.
