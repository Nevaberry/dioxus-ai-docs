# Verification and security

Use this reference to define verification trust boundaries, select a patched
legacy-bundle verifier, validate certificate chains, and handle blob-attestation
parsing failures.

## Legacy bundle with trusted root

Do not use the old-bundle plus trusted-root verification path from releases
before v3.0.4 (batch 3.1.2). GHSA-whqx-f9j3-ch6m allowed an unrelated valid
Rekor entry to satisfy verification under some conditions.

For policy enforcement:

1. Detect the installed release.
2. Identify whether the input is a legacy bundle.
3. Reject the vulnerable path instead of compensating with assumptions about
   the embedded or referenced Rekor entry.
4. Upgrade and rerun verification with the intended trust material.

## Unexpected public keys in legacy bundles

GHSA-fx35-mq7g-6g98 is a separate legacy-bundle verification bypass involving
an unexpected public key (batch 2.6.5-3.1.3). Cosign 3.1.3 fixes the issue on
the v3 line, and 2.6.5 carries the backport on the v2 line.

Where legacy bundles remain accepted, require at least 3.1.3 or 2.6.5 as
appropriate. Do not treat the earlier v3.0.4 trust-path fix as covering this
later public-key issue.

## Certificate-chain validation

Version 3.0.5 verifies certificate-chain validity rather than validating only
the leaf certificate (batch 3.1.2). Wrappers and alternative implementations
must preserve full chain validation, including the intended roots and
intermediates.

OCI signing can include an X.509 certificate chain in Cosign 3.1.3, but the
presence of chain material does not replace verification. The verifier must
still validate the chain against policy.

## Explicit-key, security-key, and identity modes

These verification capabilities have different trust semantics (batch 3.1.2):

- Offline verification with an explicit key no longer requires a trusted root.
- Security-key verification skips identity validation.
- Container verification can accept multiple identities.

Choose the mode that implements the intended policy. An explicit key can be
sufficient for its offline mode without manufacturing a trusted-root input.
Conversely, success with a security key does not show that certificate identity
was checked.

When multiple container identities are accepted, represent the complete set in
the verification invocation. Review every listed identity and confirm that the
selected verification mode actually performs the identity check the policy
expects.

## Blob-attestation payload parsing

GHSA-w6c6-c85g-mmv6 affects `verify-blob-attestation` (batch 3.1.2). On affected
releases, a payload parse failure can result in a false-positive verification.

Fail closed:

1. Treat every payload parsing error as verification failure.
2. Do not accept command success if diagnostics show parsing failed.
3. Do not deploy an affected release as a policy gate.
4. Upgrade the verifier, then rerun the check on the original payload.

Do not attempt to repair malformed input inside a policy decision. If a
separate normalization step is required, make it explicit and verify the exact
normalized bytes afterward.

## Verification review checklist

- Record the verifier release and bundle format.
- Reject both known vulnerable legacy-bundle paths.
- Distinguish trusted-root, explicit-key, and security-key verification.
- Confirm whether identity validation runs in the selected mode.
- Validate the full certificate chain, not only its leaf.
- Treat attestation parsing errors as failures regardless of exit-status
  anomalies on affected releases.
- Review every accepted container identity as policy input.
