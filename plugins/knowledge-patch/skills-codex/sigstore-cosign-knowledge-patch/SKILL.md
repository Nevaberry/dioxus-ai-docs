---
name: sigstore-cosign-knowledge-patch
description: Sigstore Cosign
version: 3.1.2
license: MIT
metadata:
  author: Nevaberry
---


# Sigstore Cosign Knowledge Patch

Use this skill when designing, migrating, debugging, or reviewing Cosign
signing and verification workflows. It is especially relevant to bundles,
trusted roots, signing configurations, transparency-log timestamps,
attestations, OCI signature storage, and legacy-bundle acceptance.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI and module migration](references/cli-and-module-migration.md) | Removed and deprecated commands and flags, Go module major, and migration planning |
| [Bundles and OCI storage](references/bundles-and-storage.md) | Standardized bundles, required output paths, lifecycle operations, local images, attestations, annotations, and storage defaults |
| [Signing and service configuration](references/signing-and-configuration.md) | TUF signing configuration, default services, base configuration, TSA mTLS, Rekor v2 timestamps, certificate signing, algorithms, and key handling |
| [Verification and security](references/verification-and-security.md) | Legacy-bundle advisories, certificate-chain validation, explicit-key and security-key modes, identities, blob attestations, and checksums |

## Start here

1. Determine the installed Cosign CLI version and, for Go integrations, the
   imported module major.
2. Identify whether each artifact is a standardized protobuf bundle or a
   legacy bundle before choosing compatibility behavior.
3. Identify the verification trust path: trusted root, explicit key, security
   key, certificate identity, and transparency-log evidence are distinct.
4. Before accepting a legacy bundle, apply the minimum safe versions in
   [Verification and security](references/verification-and-security.md).
5. For Rekor v2 signing, provision a TSA and expect a signed timestamp to be
   mandatory.
6. Before preserving an old invocation, check
   [CLI and module migration](references/cli-and-module-migration.md) for
   removals and deprecations.

## Breaking changes and deprecations

### Treat the standardized bundle as the default

Cosign v3 enables the standardized protobuf bundle format, trusted-root and
signing-config inputs, and OCI Image 1.1 referring-artifact storage by default.
Older behavior is opt-in compatibility.

Do not assume a legacy bundle or storage workflow remains implicit. Select
compatibility behavior deliberately and test every consumer against the chosen
bundle representation.

### Always name the bundle output

When a command produces a Sigstore bundle, `--bundle` is required. For blob
signing, supply an explicit output path:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

Treat a missing bundle path as an invocation error, not as a request for an
implicit output location.

### Reject legacy bundles on vulnerable releases

Legacy-bundle verification has two version-sensitive security gates:

- Do not use the pre-v3.0.4 legacy-bundle plus trusted-root path. Under
  GHSA-whqx-f9j3-ch6m, an unrelated valid Rekor entry could satisfy
  verification in some conditions.
- GHSA-fx35-mq7g-6g98 covers a bypass involving an unexpected public key in a
  legacy bundle. Where legacy bundles remain accepted, use at least 3.1.3 on
  the v3 line or 2.6.5 on the v2 line.

Upgrade the verifier and rerun verification with the intended trust material.
Do not compensate for either vulnerable path with assumptions about bundle
contents or Rekor entries.

### Remove the deleted initialize option

`cosign initialize --out` has been removed. Delete it from scripts, examples,
wrappers, and generated command lines.

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

The deprecated functionality is slated for removal in v4. Keep compatibility
shims localized so they can be removed without redesigning signing or
verification policy.

### Update Go imports to the v3 module major

The Go module major is v3. A CLI upgrade does not update Go import paths;
migrate module references and compile the integration against the v3 API.

## Bundle and storage quick reference

### Use bundle-aware lifecycle operations

The standardized protobuf bundle format is supported by `clean`, `save`,
`load`, `tree`, download, and attach operations. Preserve the selected format
through the complete lifecycle and test the workflow's save/load or
download/attach round trip.

### Inspect bundles directly

Cosign 3.1.2 adds `cosign bundle inspect`. Use inspection when diagnosing
format, contents, or interoperability; a filename or storage location is not
proof of the representation.

### Handle local-image bundles explicitly

`--local-image` works with `--new-bundle-format` for both v2 and v3 signatures.
This lets a local-image workflow exercise the new representation while
handling signatures from either major generation.

### Validate downloaded attestations

Attestation downloads handle both bundle formats. For a new-format bundle,
the download flow validates predicate type. Do not bypass that validation in
surrounding automation.

### Preserve equals signs in annotations

Cosign 3.1.2 accepts `=` inside annotation values. Keep tokens, encoded values,
and other annotations with embedded equals signs intact.

## Signing and configuration quick reference

### Let signing configuration supply service URLs

Service URLs are fetched from the TUF signing configuration by default.
Trusted-root and signing-config creation can use default services. Avoid
duplicating endpoints in wrappers unless intentionally overriding the
configuration source.

### Understand base-configuration precedence

`--base-config` can seed a signing configuration, but service definitions are
then overridden. Review the effective configuration when endpoint selection
is security-sensitive.

### Configure timestamps before Rekor v2 signing

TSA clients support mutual TLS when a signing configuration is used. Rekor v2
entries automatically require a signed timestamp, and Rekor v2 signing with
Fulcio enforces the TSA requirement. Treat missing TSA configuration or client
authentication as a signing prerequisite failure.

### Select the signing mechanism deliberately

`sign-blob` can sign with a certificate, and signing exposes
`--signing-algorithm`. Cosign 3.1.3 also supports OCI signing with an X.509
certificate chain.

Keep certificate choice, certificate-chain use, algorithm choice, and service
configuration separate. Cosign 3.1.3 auto-detects the default digest algorithm
for public keys, so callers should not impose one assumed default across key
types. A missing matching PKCS#11 key pair returns an error rather than
panicking and should be handled as a normal signing failure.

## Verification quick reference

### Require certificate-chain validation

Cosign 3.0.5 validates the certificate chain rather than only the leaf
certificate. Do not reproduce leaf-only validation in wrappers or alternate
verification code.

### Keep verification modes distinct

- Offline verification with an explicit key does not require a trusted root.
- Security-key verification skips identity validation.
- Verification can accept multiple container identities.

Configure the mode that matches policy. In particular, do not assume identity
validation occurred merely because security-key verification succeeded.
Represent the complete accepted identity set directly and review every listed
identity.

### Fail closed on blob-attestation parsing

GHSA-w6c6-c85g-mmv6 affects `verify-blob-attestation`: on affected releases, a
payload parsing failure can produce a false positive. Treat every parsing
failure as verification failure, and do not use an affected release as a
policy gate.

### Accept equivalent checksum casing

Cosign 3.1.3 compares blob file checksums case-insensitively. Equivalent upper-
and lower-case checksum encodings are accepted.

## Migration checklist

- Pin and record the actual CLI version used in CI and policy enforcement.
- Update Go integrations to the v3 module major.
- Add an explicit `--bundle` path to bundle-producing commands.
- Test standardized-bundle handling across every lifecycle operation in use.
- Decide whether OCI Image 1.1 referring-artifact storage works across every
  registry in the path.
- Remove `cosign initialize --out` immediately.
- Track deprecated flags and commands for removal before v4.
- Review effective service URLs after applying `--base-config`.
- Provision TSA access, including mTLS where required, before Rekor v2 signing.
- Reject vulnerable legacy-bundle verification paths.
- Require certificate-chain validation rather than leaf-only validation.
- Treat blob-attestation payload parse failure as a hard failure.
- Confirm whether the selected verification mode performs identity validation.
- Preserve embedded `=` characters in annotation values.
- Handle PKCS#11 lookup errors as ordinary signing failures.
- Accept checksum values independently of hexadecimal letter case.
