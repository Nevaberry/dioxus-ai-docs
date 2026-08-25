# Signing and service configuration

Use this reference when constructing trusted roots or signing configurations,
selecting service endpoints, authenticating to a TSA, signing through Rekor
v2, or using certificates and algorithms.

## TUF signing-configuration defaults

Service URLs are fetched from the TUF signing configuration by default (batch
3.1.2). Trusted-root and signing-config creation can also use default services.

Prefer the standard configuration source when the normal Sigstore services are
intended. If a workflow overrides endpoints, make the override explicit and
reviewable instead of duplicating defaults in a wrapper.

## Base-configuration precedence

`--base-config` can seed a signing configuration, but service definitions are
subsequently overridden (batch 3.1.2). Service entries in the base file are
therefore not necessarily authoritative in the effective result.

Inspect the generated configuration after applying a base configuration,
especially when endpoint selection defines a security or compliance boundary.

## TSA mutual TLS

TSA clients support mutual TLS when a signing configuration is used (batch
3.1.2). Supply the required client certificate, private-key material, and
related authentication settings through the signing configuration rather than
constructing an unrelated timestamp transport path.

Validate the effective TSA client setup before signing. A configured TSA URL
alone does not establish that required client authentication is available.

## Rekor v2 timestamp requirement

Rekor v2 entries automatically require a signed timestamp (batch 3.1.2).
Rekor v2 signing with Fulcio enforces the TSA requirement.

Before signing:

1. Resolve the effective signing configuration.
2. Confirm that it contains a usable TSA.
3. Confirm any required mTLS material is available.
4. Treat a missing or unusable TSA as a prerequisite failure.

Do not downgrade the missing timestamp to a warning or assume the transparency
log entry can replace the required signed timestamp.

## Blob signing with a certificate

`sign-blob` can sign with a certificate (batch 3.1.2). Keep certificate choice,
private-key choice, service configuration, and output-bundle path explicit so
that a change in one does not silently alter the others.

## Signing-algorithm selection

Signing exposes `--signing-algorithm` (batch 3.1.2). Use it when policy or
interoperability requires an explicit algorithm. Do not infer the signing
algorithm solely from service configuration.

For public keys, Cosign 3.1.3 auto-detects the default digest algorithm. Avoid
hard-coded assumptions that all key types share one default.

## OCI signing with an X.509 chain

Cosign 3.1.3 supports OCI signing with an X.509 certificate chain (batch
2.6.5-3.1.3). Use the chain-capable signing path when consumers need chain
material, and preserve the distinction between the leaf certificate and its
issuer chain.

Verification policy must still validate the certificate chain. Supplying a
chain during signing is not itself proof that a verifier checked it.

## PKCS#11 lookup failures

When no PKCS#11 key pair matches, Cosign 3.1.3 returns an error instead of
panicking (batch 2.6.5-3.1.3). Treat the result as a recoverable signing error:
report the unmatched selector or key reference, fail the operation, and let the
caller decide whether to retry with corrected input.
