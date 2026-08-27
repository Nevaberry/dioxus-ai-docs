# Verification and security

## Legacy bundle with trusted-root verification

Do not rely on the pre-v3.0.4 legacy-bundle plus trusted-root verification
path. GHSA-whqx-f9j3-ch6m allowed an unrelated valid Rekor entry to satisfy
verification under some conditions.

For policy enforcement:

1. Detect the installed release before verification.
2. Reject the vulnerable path instead of compensating with assumptions about
   the Rekor entry.
3. Upgrade the verifier and rerun verification with the intended trust
   material.

## Unexpected public keys in legacy bundles

The `2.6.5-3.1.3` batch addresses GHSA-fx35-mq7g-6g98, a verification bypass
involving an unexpected public key in a legacy bundle. Cosign 3.1.3 fixes the
v3 line, and 2.6.5 contains the v2 backport. Where legacy bundles remain
accepted, use at least 3.1.3 or 2.6.5 respectively.

Do not infer that a newer standardized-bundle workflow makes an unpatched
legacy acceptance path safe. Remove legacy acceptance when possible; otherwise
enforce the fixed release before evaluating the bundle.

## Certificate-chain validation

Cosign 3.0.5 validates the certificate chain rather than validating only the
leaf certificate. Wrappers and alternate verification implementations must not
reintroduce leaf-only validation.

## Explicit-key offline verification

Offline verification with an explicit key does not require a trusted root.
Keep the explicit key as the trust input for that mode rather than adding a
trusted-root prerequisite copied from another verification path.

The deprecation of the `--offline` flag is a CLI migration concern and does not
make all verification modes equivalent. Review the actual invocation and trust
material together.

## Security-key identity behavior

Security-key verification skips identity validation. A successful security-key
verification therefore does not establish that certificate identity checks
ran. If identity is part of policy, select a verification mode that performs
the required identity validation.

## Multiple container identities

Verification can accept multiple container identities. Express the complete
accepted set directly, confirm every identity is intended, and confirm that the
chosen verification mode actually validates identity. Avoid composing
independent commands whose combined acceptance semantics are unclear.

## Blob-attestation parse failures

On releases affected by GHSA-w6c6-c85g-mmv6,
`verify-blob-attestation` can report a false positive when payload parsing
fails. Treat every parse failure as a verification failure. Do not use an
affected release as a policy gate even if the command reports success after a
payload parse error.

## Blob checksum casing

Cosign 3.1.3 compares blob file checksums without regard to letter case.
Equivalent upper- and lower-case encodings are accepted; surrounding code
should not reject a checksum solely because hexadecimal letter casing differs.

## Trust-boundary checklist

- Determine whether the input is a standardized or legacy bundle.
- Enforce the fixed release when legacy bundles remain accepted.
- Validate the full certificate chain.
- Keep trusted-root, explicit-key, and security-key modes distinct.
- Do not claim identity validation for security-key verification.
- Review every accepted container identity.
- Fail closed on blob-attestation payload parse errors.
- Compare blob checksums independently of letter case.
