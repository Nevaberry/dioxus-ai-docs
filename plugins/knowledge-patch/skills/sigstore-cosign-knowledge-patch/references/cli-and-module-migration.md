# CLI and module migration

## Removed CLI surface

`cosign initialize --out` has been removed. Delete the option from shell scripts, CI templates, documentation, and command builders rather than attempting to preserve it as a no-op.

## Deprecated commands and flags

The following flags are deprecated:

- `--tlog-upload`
- `--offline`
- `--rekor-entry-type`
- `--payload` on sign and verify commands (deprecated in 3.1.2)
- `--output-attestation` (deprecated in 3.1.2)

The following commands are deprecated:

- `cosign triangulate`
- `cosign copy`

Deprecated functionality is slated for removal in v4. Inventory direct invocations as well as wrappers that synthesize these options. Keep any temporary fallback isolated from policy logic so the fallback can be removed without changing what is signed or trusted.

## Go module major

The Cosign Go module major is v3. Update import paths and module requirements together, then compile and test the integration against the new API. Do not infer library migration from the installed CLI version.

## Signing capabilities

`sign-blob` can sign with a certificate. Signing commands also expose `--signing-algorithm` for an explicit algorithm choice.

Treat these as independent inputs:

1. the material or certificate used to sign;
2. the selected signing algorithm;
3. the configured transparency-log, certificate-authority, and timestamp services;
4. the bundle output location.

## Verification identities

Verification can accept multiple container identities. Prefer one invocation that expresses the intended accepted set over multiple loosely combined invocations.

Multiple accepted identities do not change the semantics of the selected verification mode. Security-key verification skips identity validation, so an identity list must not be treated as enforced in that mode.

## Migration review

- Search commands, scripts, CI configuration, and generated argument lists for removed and deprecated surface.
- Update Go module paths separately from CLI deployment changes.
- Add tests for certificate-backed blob signing if that capability is selected.
- Test explicit algorithm selection against the actual signing path.
- Review every accepted container identity as part of the verification policy.
