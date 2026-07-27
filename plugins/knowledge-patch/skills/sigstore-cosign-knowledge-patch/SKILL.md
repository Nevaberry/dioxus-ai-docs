---
name: sigstore-cosign-knowledge-patch
description: Sigstore Cosign
license: MIT
version: 3.1.2
metadata:
  author: Nevaberry
---

# Sigstore Cosign Knowledge Patch

Use this skill when designing, migrating, debugging, or reviewing Cosign signing and verification workflows, especially workflows that handle bundles, trusted roots, signing configurations, transparency-log timestamps, attestations, or OCI signature storage.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI and module migration](references/cli-and-module-migration.md) | Removed and deprecated commands and flags, Go module major, signing and identity options |
| [Bundles and OCI storage](references/bundles-and-storage.md) | Standardized bundles, required bundle output, lifecycle commands, local images, attestations, annotations |
| [Signing and service configuration](references/signing-and-configuration.md) | TUF signing configuration, trusted roots, default services, base configuration, TSA mTLS, Rekor v2 timestamps |
| [Verification and security](references/verification-and-security.md) | Old-bundle trust boundaries, certificate-chain validation, offline and security-key verification, blob-attestation parsing advisories |

## Start here

1. Determine the installed Cosign CLI version and, for Go integrations, the imported module major.
2. Identify whether each artifact is a standardized protobuf bundle or an older bundle before choosing compatibility behavior.
3. Identify the verification trust path: trusted root, explicit key, security key, certificate identity, and transparency-log evidence are not interchangeable.
4. Check [verification-and-security.md](references/verification-and-security.md) before accepting an old bundle or using blob-attestation verification as a policy gate.
5. For signing through Rekor v2, provision a TSA and expect a signed timestamp to be mandatory.
6. Before preserving an old invocation, check [cli-and-module-migration.md](references/cli-and-module-migration.md) for removals and deprecations.

## Breaking changes and deprecations

### Treat the standardized bundle as the default

Cosign v3 defaults to the standardized protobuf bundle format. It also defaults to trusted-root and signing-config inputs and to OCI Image 1.1 referring-artifact storage.

Do not assume an older bundle or storage workflow remains the implicit behavior. Select compatibility behavior explicitly when an integration still needs it, and test every consumer against the selected bundle format.

### Always name the bundle output

When a command produces a Sigstore bundle, `--bundle` is required. For blob signing, use an explicit output path:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

Treat a missing bundle path as an invocation error, not as a request for an implicit output location.

### Remove the already-deleted initialize option

`cosign initialize --out` has been removed. Do not retain it in scripts, examples, wrappers, or generated command lines.

### Plan replacements for deprecated CLI surface

The following flags are deprecated:

- `--tlog-upload`
- `--offline`
- `--rekor-entry-type`
- `--payload` on sign and verify commands
- `--output-attestation`

The following commands are deprecated:

- `cosign triangulate`
- `cosign copy`

Currently deprecated functionality is slated for removal in v4. Keep compatibility shims localized so they can be removed without redesigning the signing or verification policy.

### Update Go imports to the v3 module major

The Go module major is v3. A CLI upgrade does not by itself update Go import paths; migrate module references and compile the integration against the v3 API.

Read [cli-and-module-migration.md](references/cli-and-module-migration.md) for the complete migration inventory.

## Security gates

### Reject the vulnerable old-bundle trust path

Do not rely on the old-bundle plus trusted-root verification path from releases before v3.0.4. GHSA-whqx-f9j3-ch6m allowed an unrelated valid Rekor entry to satisfy verification under some conditions.

For policy enforcement:

1. Detect the installed release before verification.
2. Reject the vulnerable path rather than compensating with assumptions about the Rekor entry.
3. Upgrade the verifier and rerun verification with the intended trust material.

### Require certificate-chain validation

Version 3.0.5 validates the certificate chain rather than validating only the leaf certificate. Do not reproduce leaf-only validation in wrappers or alternate verification code.

### Fail closed on blob-attestation parse errors

GHSA-w6c6-c85g-mmv6 affects `verify-blob-attestation`: a payload parsing failure can produce a false positive on affected releases.

Treat every parsing failure as a verification failure. Do not use an affected release as a policy gate, even if its command reports success after failing to parse the payload.

### Keep verification modes distinct

- Offline verification with an explicit key no longer requires a trusted root.
- Security-key verification skips identity validation.
- Verification can accept multiple container identities.

Configure the mode that matches the policy. In particular, do not assume identity validation occurred merely because security-key verification succeeded.

See [verification-and-security.md](references/verification-and-security.md) for the trust-boundary checklist.

## Bundle and storage quick reference

### Use bundle-aware lifecycle operations

The standardized protobuf bundle format is supported across these operation families:

- `clean`
- `save`
- `load`
- `tree`
- download
- attach

Do not insert a format-conversion assumption between these operations. Preserve the bundle format deliberately and test the complete save/load or download/attach round trip used by the workflow.

### Inspect bundles directly

Cosign 3.1.2 adds `cosign bundle inspect`. Use bundle inspection when diagnosing format, contents, or interoperability instead of treating a filename or storage location as proof of the bundle representation.

### Handle local-image bundles explicitly

`--local-image` works with `--new-bundle-format` for both v2 and v3 signatures. This permits a local-image workflow to exercise the new representation while handling signatures from either major generation.

### Validate downloaded attestations

Attestation downloads handle both bundle formats. For a new-format bundle, predicate type is validated during the download flow; do not remove or bypass that check in surrounding automation.

### Preserve equals signs in annotation values

Cosign 3.1.2 accepts `=` inside annotation values. Tokens, encoded values, and other annotations containing embedded equals signs should remain intact rather than being split at the first `=`.

Read [bundles-and-storage.md](references/bundles-and-storage.md) before adapting a mixed-format or local-image workflow.

## Signing and configuration quick reference

### Let the signing configuration supply services

Service URLs are fetched from the TUF signing configuration by default. Avoid duplicating service endpoints in a wrapper unless the workflow intentionally overrides the configuration source.

Trusted-root and signing-config creation can use default services. Prefer those defaults when constructing standard configuration, then make deviations explicit and reviewable.

### Understand base-configuration precedence

`--base-config` can seed a signing configuration, but service definitions are subsequently overridden. Do not assume service entries in the base file remain authoritative after configuration creation.

Review the generated configuration whenever endpoint selection is security-sensitive.

### Configure TSA client authentication when required

When a signing configuration is used, TSA clients support mutual TLS. Supply the required client authentication material through that configuration rather than building a separate timestamp transport path.

### Make timestamps mandatory for Rekor v2

Rekor v2 entries automatically require a signed timestamp. Rekor v2 signing with Fulcio enforces the TSA requirement.

Before starting a Rekor v2 signing operation, verify that a usable TSA is present in the effective service configuration. Treat missing timestamp service configuration as a signing prerequisite failure.

See [signing-and-configuration.md](references/signing-and-configuration.md) for configuration precedence and signing capabilities.

## Signing and identity capabilities

### Select the signing mechanism deliberately

`sign-blob` can sign with a certificate. Signing also exposes `--signing-algorithm`, allowing the algorithm choice to be made explicit where the workflow needs it.

Keep certificate selection, algorithm selection, and service configuration as separate decisions. A configured service endpoint does not replace the need to choose the intended signing identity and algorithm.

### Express all accepted container identities

Verification can accept multiple container identities. Represent the complete accepted set directly rather than running independent verification commands whose combined semantics may be unclear.

When reviewing such a policy, confirm that every listed identity is intended and that the chosen verification mode actually performs identity validation.

## Migration checklist

- Pin and record the actual CLI version used in CI and policy enforcement.
- Update Go integrations to the v3 module major.
- Add an explicit `--bundle` path to bundle-producing commands.
- Test standardized-bundle handling across every lifecycle operation the workflow uses.
- Decide whether OCI Image 1.1 referring-artifact storage is acceptable for every registry in the path.
- Remove `cosign initialize --out` immediately.
- Track all deprecated flags and commands for removal before v4.
- Verify effective service URLs after applying `--base-config`.
- Provision TSA access, including mTLS where needed, before Rekor v2 signing.
- Reject pre-v3.0.4 old-bundle/trusted-root verification.
- Require certificate-chain validation rather than leaf-only validation.
- Treat blob-attestation payload parse failure as a hard verification failure.
- Confirm whether the selected verification mode performs identity validation.
- Preserve embedded `=` characters in annotation values.
