# Signing and service configuration

## Default service discovery

In the 3.1.2 batch, Cosign fetches service URLs from the TUF signing
configuration by default. Trusted-root and signing-config creation can use
default services. Prefer those defaults for standard configuration; make any
endpoint override explicit and reviewable.

Do not duplicate service URLs in a wrapper merely to reproduce the configured
defaults. The effective signing configuration is the source to inspect when
troubleshooting endpoint selection.

## Base-configuration precedence

`--base-config` can seed a signing configuration, but its service definitions
are subsequently overridden. Do not assume the base file remains authoritative
for endpoints. Generate the configuration, inspect the effective service
definitions, and review them whenever endpoint choice is security-sensitive.

## TSA mutual TLS

TSA clients support mutual TLS when a signing configuration is used. Put the
required client-authentication material in that configuration and validate the
effective timestamp service setup before signing.

## Rekor v2 timestamp requirement

Rekor v2 entries automatically require a signed timestamp. Rekor v2 signing
with Fulcio enforces the TSA requirement. Before starting either workflow,
verify that the effective service configuration provides a usable TSA and any
required mTLS credentials. Missing TSA configuration is a signing prerequisite
failure.

## Blob signing with a certificate

`sign-blob` can sign with a certificate. Keep certificate choice distinct from
the selected service endpoints and signing algorithm; configuring services
does not select the intended signing identity.

## Explicit signing algorithm

Signing exposes `--signing-algorithm`. Use it when the workflow needs an
explicit algorithm choice, and test consumers against the resulting signature.

## OCI X.509 certificate-chain signing

The `2.6.5-3.1.3` batch adds OCI signing with an X.509 certificate chain in
Cosign 3.1.3. This supports certificate-chain-based signing workflows for OCI
artifacts. Treat the chain and the signing certificate as deliberate inputs,
then verify with the intended trust policy.

## Public-key digest defaults

Cosign 3.1.3 auto-detects the default digest algorithm for public keys. Callers
should not assume a single default across key types. Allow Cosign to select the
key-appropriate default unless policy requires an explicit supported choice.

## Missing PKCS#11 key pairs

When no PKCS#11 key pair matches, Cosign 3.1.3 returns an error instead of
panicking. Handle the result as a normal signing failure: surface the lookup
error, avoid emitting a partial success, and allow the caller's ordinary retry
or failure policy to run.

## Configuration review

Before signing:

1. Inspect the effective services after applying `--base-config`.
2. Confirm TSA availability and mTLS material for Rekor v2.
3. Select the intended certificate or certificate chain.
4. Decide whether the signing algorithm must be explicit.
5. Let public-key digest defaults be key-aware.
6. Treat a missing PKCS#11 match as an ordinary error path.
