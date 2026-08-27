# CLI, Configuration, and PKI

## Contents

- [Configuration loading and diagnostics](#configuration-loading-and-diagnostics)
- [Provider and random configuration](#provider-and-random-configuration)
- [Command discovery and output behavior](#command-discovery-and-output-behavior)
- [Key and request generation](#key-and-request-generation)
- [Certificate creation and inspection](#certificate-creation-and-inspection)
- [CMP and attribute certificates](#cmp-and-attribute-certificates)
- [Certificate parsing and store access](#certificate-parsing-and-store-access)
- [HTTP client behavior](#http-client-behavior)

## Configuration loading and diagnostics

### Suppress configuration loading

Set `OPENSSL_CONF` to the empty string to disable configuration loading completely.

### Control includes and variable parsing

Prefix relative `.include` paths with `.pragma includedir:value` or set `OPENSSL_CONF_INCLUDE`. Use `.pragma abspath:on` to require the resulting include path to be absolute. On POSIX, a directory include reads only immediate files ending in `.cnf` or `.conf`; it does not recurse. Use `.pragma dollarid:on` when an unbraced `$` must remain part of an identifier.

```ini
.pragma includedir:/etc/ssl
.pragma abspath:on
.include openssl.d
```

### Fail on invalid SSL configuration

Set `config_diagnostics=1` to make `SSL_CTX_new()` and `SSL_CTX_new_ex()` return errors when SSL-module configuration is invalid (since 3.4.0).

```ini
config_diagnostics = 1
```

### Configure cleanup registration

Use the `atexit` configuration switch to control whether `OPENSSL_cleanup()` is automatically registered when libcrypto is unloaded (introduced in 3.3.0). Account separately for the OpenSSL 4.0 global-cleanup changes described in [migration and compatibility](migration-and-compatibility.md#global-cleanup-lifetime).

### Inspect configuration with `configutl`

OpenSSL 3.6 adds `openssl configutl` to process an OpenSSL configuration file and dump the equivalent configuration. Use it to diagnose includes, expansion, and section selection rather than reproducing the parser in application code.

## Provider and random configuration

### Pass runtime provider parameters

Use the common repeatable `-provparam [name:]key=value` option to set a UTF-8 string parameter on one named provider or, without the prefix, on every loaded provider. Load a nondefault provider before applying its parameter. Keep parameters needed only during provider initialization in the configuration file, because a later CLI option is too late.

### Configure the random-generation chain

Select `CTR-DRBG`, `HASH-DRBG`, or `HMAC-DRBG` in library configuration and set its cipher or digest, fetch properties, seed source, and seed properties as needed. `random_provider` redirects `RAND_bytes()` entropy requests to a provider, defaults to `fips`, and falls back to built-in entropy sources when that provider is not loaded.

```ini
openssl_conf = init
[init]
random = rng
[rng]
random = HMAC-DRBG
digest = SHA256
```

See [providers, cryptography, and FIPS](providers-crypto-and-fips.md#provider-configuration) for provider boolean rules and FIPS implications.

## Command discovery and output behavior

### Probe command availability safely

`openssl no-XXX` returns success and prints `no-XXX` when command `XXX` is absent. It returns status 1 and prints `XXX` when the command is present. Extra arguments are ignored, and pseudo-commands such as `list` cannot be tested with this mechanism.

### Treat verification failure as command failure

`openssl crl -verify` and `openssl req -verify` return exit status 1 when verification fails (since 3.3.0). Let scripts use the process status rather than parsing the diagnostic text.

### Pin the HMAC benchmark digest

`openssl speed hmac` defaults to SHA-256 rather than MD5 (since 3.3.0). Select the digest explicitly when historical benchmark comparability matters.

### Pin application encryption when compatibility matters

The `req`, `cms`, and `smime` commands default to AES-256-CBC rather than `des-ede3-cbc` (since 3.5.0). Select 3DES explicitly only when an existing interchange format requires it.

## Key and request generation

### Generate restricted RSA-PSS keys

`genpkey -algorithm RSA-PSS` creates an unrestricted RSA-PSS key by default. Use `rsa_pss_keygen_md`, `rsa_pss_keygen_mgf1_md`, and `rsa_pss_keygen_saltlen` to encode signing restrictions into the key. The salt-length value is a minimum, not an exact required length.

```sh
openssl genpkey -algorithm RSA-PSS \
  -pkeyopt rsa_pss_keygen_md:sha256 \
  -pkeyopt rsa_pss_keygen_mgf1_md:sha256 \
  -pkeyopt rsa_pss_keygen_saltlen:32 -out pss.pem
```

### Prefer named DH groups

Select a fixed named group with `-pkeyopt group:name` for DH keys and parameters. This avoids a parameter file or fresh parameter generation. Selecting a named group causes other parameter-generation options to be ignored.

```sh
openssl genpkey -algorithm DH -pkeyopt group:ffdhe3072 -out dh-key.pem
```

### Reuse request profiles

`openssl req -newkey` accepts `[rsa:]bits`, `algorithm:file`, `param:file`, or a bare algorithm supplemented by `-pkeyopt`; it also implies `-new`. Use `-section name` to select a request configuration section other than `[req]`, allowing multiple profiles in one file.

```sh
openssl req -newkey ec:ec-params.pem -keyout server.key \
  -config openssl.cnf -section server -out server.csr
```

## Certificate creation and inspection

### Override subject and issuer fields

Use `openssl x509 -set_subject` and `-set_issuer` to override those fields while creating a certificate. `-subj` is an alias for `-set_subject` (since 3.3.0).

### Set explicit validity dates

Use `req` or `x509` with `-not_before` and `-not_after` to set the validity dates of generated certificates (since 3.4.0).

### Use `req` as a micro-CA deliberately

Passing `-CA` makes `openssl req` emit a certificate, take the issuer from the CA certificate, and sign with the matching `-CAkey`. It can sign an input CSR or a request created in the same invocation. CSR extensions are not copied unless `-copy_extensions copy` or `copyall` is supplied.

```sh
openssl req -in leaf.csr -CA ca.pem -CAkey ca.key -out leaf.pem
```

### Account for generated-certificate defaults

Since OpenSSL 3.2, certificates generated by `req` are version 3 and include key-identifier extensions by default. `-x509v1` implies `-x509`, but specifying any extension still forces version 3. Subject key identifier defaults to the public-key hash. Authority key identifier defaults to none for a self-signed certificate and to `keyid, issuer` otherwise.

### Do not parse key hex layout

OpenSSL 4.0 removes an extra leading `00:` when a printed key value's most-significant byte is at least `0x80`. It also uses 24-byte rows for signatures and 16-byte rows elsewhere. Do not depend on the older textual layout; use structured formats or library APIs.

## CMP and attribute certificates

### Use CMPv3 capabilities

OpenSSL implements CMPv3 features from RFC 9480 and RFC 9483 (since 3.3.0).

### Request CRLs through CMP

CMP clients can request certificate revocation lists (since 3.4.0).

### Use central key generation in CMP

The CMP implementation supports central key generation (since 3.5.0). Treat the resulting key-delivery path as a sensitive protocol and validate the surrounding CMP trust configuration.

### Handle attribute certificates

OpenSSL provides initial RFC 5755 Attribute Certificate support and related X.509v3 extensions (since 3.4.0).

## Certificate parsing and store access

### Use safe certificate-store snapshots

Use `X509_STORE_get1_objects()` instead of accessing store contents through `X509_STORE_get0_objects()` when concurrent access is possible. The `get1` form avoids the multithreading hazards of the borrowed internal collection (since 3.3.0).

### Expect strict ASN.1 time parsing

Generalized-time and UTC-time decoders and validators reject values shorter than the X.690 minimum lengths (since 3.3.0). Fix malformed producers instead of padding or accepting the input ad hoc.

## HTTP client behavior

### Bound response headers

The OpenSSL HTTP client limits responses to 256 header lines by default (since 3.3.0). Account for this limit when interoperating with unusually verbose or adversarial servers.
