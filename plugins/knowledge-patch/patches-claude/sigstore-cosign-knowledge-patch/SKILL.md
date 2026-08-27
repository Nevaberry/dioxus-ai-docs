---
name: sigstore-cosign-knowledge-patch
description: Sigstore Cosign
version: "3.1.2"
license: MIT
metadata:
  author: Nevaberry
---


# Sigstore Cosign Knowledge Patch

Use this skill when designing, migrating, debugging, or reviewing Cosign
signing and verification workflows. It is especially relevant to bundles,
trusted roots, signing configuration, transparency-log timestamps,
attestations, OCI signature storage, PKCS#11 keys, and certificate chains.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI and module migration](references/cli-and-module-migration.md) | Removed and deprecated commands and flags, Go module major, signing options, PKCS#11 behavior |
| [Bundles and OCI storage](references/bundles-and-storage.md) | Standardized bundles, required output, lifecycle commands, local images, attestations, annotations, checksums |
| [Signing and service configuration](references/signing-and-configuration.md) | TUF signing configuration, default services, base configuration, TSA mTLS, Rekor v2 timestamps, certificate chains |
| [Verification and security](references/verification-and-security.md) | Legacy-bundle fixes, certificate-chain validation, explicit-key and security-key modes, blob-attestation parsing |

## Start here

1. Determine the installed Cosign CLI version and, for Go integrations, the
   imported module major.
2. Identify whether each input is a standardized protobuf bundle or a legacy
   bundle before selecting compatibility behavior.
3. Identify the intended verification trust path: a trusted root, explicit
   key, security key, certificate identity, and transparency-log evidence are
   distinct policy inputs.
4. Check [verification and security](references/verification-and-security.md)
   before accepting legacy bundles or using blob-attestation verification as a
   policy gate.
5. For Rekor v2 signing, provision a TSA and expect a signed timestamp to be
   mandatory.
6. Before preserving an older invocation, check
   [CLI and module migration](references/cli-and-module-migration.md) for
   removals and deprecations.

## Breaking changes and deprecations

### Treat standardized bundles as the default

Cosign v3 defaults to the standardized protobuf bundle format, trusted-root
and signing-config inputs, and OCI Image 1.1 referring-artifact storage. Older
behavior is opt-in compatibility.

Select compatibility behavior explicitly when a producer, registry, or
consumer still expects an older representation. Test the full workflow rather
than inferring the format from a filename or storage location.

### Always name bundle output

Commands that produce a Sigstore bundle require `--bundle`. For blob signing,
provide an explicit output path:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

Treat a missing bundle path as an invocation error, not as a request for an
implicit output location.

### Remove the deleted initialize option

`cosign initialize --out` has been removed. Delete it from scripts, wrappers,
examples, and generated command lines.

### Plan replacements for deprecated CLI surface

The deprecated flags are:

- `--tlog-upload`
- `--offline`
- `--rekor-entry-type`
- `--payload` on sign and verify commands
- `--output-attestation`

The deprecated commands are:

- `cosign triangulate`
- `cosign copy`

These deprecated interfaces are slated for removal in v4. Keep any temporary
compatibility shim small and isolated from signing and verification policy.

### Update Go imports to module major v3

The Go module major is v3. A CLI upgrade does not update import paths; migrate
module references and compile the integration against the v3 API.

## Security gates

### Reject vulnerable legacy-bundle verification

Do not rely on the pre-v3.0.4 legacy-bundle plus trusted-root path.
GHSA-whqx-f9j3-ch6m allowed an unrelated valid Rekor entry to satisfy
verification in some conditions.

Where legacy bundles remain accepted, also require a release containing the
GHSA-fx35-mq7g-6g98 fix: at least 3.1.3 on v3 or 2.6.5 on v2. That issue
allowed an unexpected public key in a legacy bundle to bypass verification.

### Require certificate-chain validation

Version 3.0.5 validates the certificate chain rather than only the leaf
certificate. Do not reproduce leaf-only validation in wrappers or alternate
verification implementations.

### Fail closed on blob-attestation parse errors

GHSA-w6c6-c85g-mmv6 affects `verify-blob-attestation`: payload parsing failure
can produce a false positive on affected releases. Treat every parsing failure
as verification failure and do not use an affected release as a policy gate.

### Keep verification modes distinct

- Offline verification with an explicit key does not require a trusted root.
- Security-key verification skips identity validation.
- Container verification can accept multiple identities.

Configure the mode that matches policy. In particular, do not infer that
identity validation occurred merely because security-key verification passed.

## Bundle and storage quick reference

### Preserve bundle format through lifecycle operations

The standardized protobuf bundle works with `clean`, `save`, `load`, `tree`,
download, and attach operations. Do not insert an assumed conversion between
these steps; test the actual round trip used by the workflow.

### Inspect bundles directly

Use `cosign bundle inspect` to diagnose a bundle's format and contents instead
of treating its filename or storage location as proof of representation.

### Handle local-image bundles explicitly

`--local-image` works with `--new-bundle-format` for both v2 and v3 signatures.
This lets local-image workflows exercise the new representation while handling
signatures produced by either major generation.

### Validate downloaded attestations

Attestation downloads handle both bundle formats. For a new-format bundle, the
download path validates predicate type; surrounding automation must preserve
that check.

### Preserve annotation and checksum semantics

Annotation values may contain embedded `=` characters. Preserve them intact
instead of splitting at the first equals sign. Blob checksum comparison is
case-insensitive, so equivalent uppercase and lowercase encodings are valid.

## Signing and configuration quick reference

### Let signing configuration supply services

Service URLs are fetched from the TUF signing configuration by default.
Trusted-root and signing-config creation can use default services. Avoid
duplicating endpoints unless the workflow intentionally overrides them.

### Review base-configuration precedence

`--base-config` seeds a signing configuration, but its service definitions are
then overridden. Inspect the effective configuration whenever endpoint choice
is security-sensitive.

### Configure TSA authentication and Rekor v2 prerequisites

TSA clients support mutual TLS when a signing configuration is used. Put the
required client-authentication material in that configuration.

Rekor v2 entries require a signed timestamp, and Rekor v2 signing with Fulcio
enforces the TSA requirement. Treat a missing usable TSA as a signing
prerequisite failure.

### Select signing inputs deliberately

`sign-blob` can sign with a certificate, and `--signing-algorithm` exposes the
algorithm choice. OCI signing can use an X.509 certificate chain. Keep identity,
algorithm, chain material, and service configuration as separate decisions.

Public-key digest defaults are auto-detected rather than assumed across key
types. If no PKCS#11 key pair matches, Cosign returns a normal error instead of
panicking; handle it as a signing failure.

## Review checklist

- Pin and record the CLI release used for CI and policy enforcement.
- Update Go integrations to the v3 module major.
- Add an explicit `--bundle` path to bundle-producing commands.
- Test bundle handling across every lifecycle operation in use.
- Decide whether OCI Image 1.1 referring-artifact storage works with every
  registry in the path.
- Remove `cosign initialize --out`.
- Track deprecated commands and flags for removal before v4.
- Verify effective service URLs after applying `--base-config`.
- Provision TSA access, including mTLS where required, before Rekor v2 signing.
- Reject vulnerable legacy-bundle verification paths and releases.
- Require certificate-chain validation rather than leaf-only validation.
- Treat blob-attestation payload parse failure as verification failure.
- Confirm whether the chosen verification mode performs identity validation.
- Preserve embedded `=` characters in annotations.
- Handle unmatched PKCS#11 keys as ordinary errors.
