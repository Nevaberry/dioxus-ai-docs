# Verification and security

## Old bundles with a trusted root

GHSA-whqx-f9j3-ch6m affected the old-bundle plus trusted-root verification path before v3.0.4. Under some conditions, an unrelated valid Rekor entry could satisfy verification.

Do not use that affected path for a policy decision. Upgrade the verifier and verify the bundle again with the intended trust material; the existence of some valid transparency-log entry is not sufficient evidence for the artifact being checked.

## Certificate-chain validation

Version 3.0.5 verifies the validity of the certificate chain rather than checking only the leaf certificate.

Wrappers and alternate implementations must preserve full chain validation. A successful leaf check alone must not be promoted to an equivalent verification result.

## Blob-attestation parsing

GHSA-w6c6-c85g-mmv6 affects `verify-blob-attestation`. On affected releases, payload parsing can fail while the command reports a false-positive result.

Use fail-closed handling:

1. determine whether the verifier release is affected;
2. treat payload parsing failure as verification failure regardless of the reported success result;
3. do not use an affected release as a policy gate;
4. rerun verification with a non-affected release before accepting the attestation.

Do not catch a parsing error and replace it with an empty or partially decoded payload. The verification decision depends on successfully parsing the payload that was actually attested.

## Offline explicit-key verification

Offline verification with an explicit key no longer requires a trusted root. Model this as a distinct verification path rather than fabricating or fetching trusted-root material that the mode does not need.

This does not make other verification modes independent of their trust inputs. Choose the mode first, then supply the material that mode requires.

## Security-key verification

Security-key verification skips identity validation. A successful cryptographic verification in this mode must not be described as proof that a configured certificate or container identity matched.

If identity is a policy requirement, select a verification path that actually validates it and test a nonmatching identity as a negative case.

## Multiple container identities

Verification can accept multiple container identities. Review the full accepted set as one policy boundary.

Avoid implementing an ambiguous series of independent checks whose success combination differs from the intended accepted-identity semantics. Also confirm that the chosen verification mode performs identity validation at all.

## Trust-boundary checklist

- Record the exact verifier release used by the policy gate.
- Reject the pre-v3.0.4 old-bundle/trusted-root path.
- Preserve full certificate-chain validation from v3.0.5 behavior.
- Treat every blob-attestation payload parsing failure as verification failure.
- Do not use a release affected by GHSA-w6c6-c85g-mmv6 as a policy gate.
- Do not require a trusted root for offline verification that uses an explicit key.
- Do not claim identity validation for security-key verification.
- Review every accepted container identity and test negative identity cases.
