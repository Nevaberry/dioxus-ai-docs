# Bundles and OCI storage

Use this reference when choosing a bundle representation, moving bundles
through lifecycle operations, storing signatures in OCI registries, or
processing annotations, attestations, and blob checksums.

## Standardized bundle and storage defaults

Cosign v3 enables the standardized protobuf bundle format by default (batch
3.1.2). Trusted-root and signing-config inputs also become defaults, as does
OCI Image 1.1 referring-artifact storage. Older behavior remains available as
explicit compatibility rather than as the implicit path.

Decide the representation and storage mode at each interoperability boundary.
Check registry support for referring artifacts and test all producers and
consumers against the selected bundle format.

## Required bundle destination

When a command produces a Sigstore bundle, `--bundle` is required. For blob
signing, always provide the destination explicitly:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

A missing path is an invocation error, not a request for a default filename.

## Bundle-aware lifecycle operations

The standardized protobuf format is supported across these operation families
(batch 3.1.2):

- `clean`
- `save`
- `load`
- `tree`
- download
- attach

Preserve the chosen format deliberately through the full workflow. Do not
insert a conversion based only on assumptions about older behavior. Test the
actual save/load and download/attach round trips used in production.

## Bundle inspection

Version 3.1.2 adds `cosign bundle inspect`. Use it to determine format and
contents during interoperability diagnosis. A `.json` suffix, OCI location,
or other naming convention does not prove which bundle representation is
present.

## Local-image workflows

`--local-image` works with `--new-bundle-format` for both v2 and v3 signatures
(batch 3.1.2). This permits local-image workflows to exercise the standardized
representation while processing signatures produced by either major
generation.

Test both generations if the local workflow is a migration bridge. Do not
assume that enabling the new bundle format changes the generation of the
signature it contains.

## Attestation downloads

Attestation downloads handle both legacy and standardized bundle formats
(batch 3.1.2). For a new-format bundle, predicate type is validated during the
download flow.

Do not bypass or discard that predicate-type check in surrounding automation.
Treat a mismatch as a failed attestation selection rather than accepting the
payload based only on its storage location.

## Annotation parsing

Cosign 3.1.2 accepts `=` inside annotation values. Tokens, base64-like values,
and other encoded content may therefore contain embedded equals signs.

Split an annotation only at the separator that divides its key from its full
value. Preserve every later `=` character instead of truncating or rejecting
the value.

## Blob checksum comparison

Cosign 3.1.3 compares blob file checksums case-insensitively (batch
2.6.5-3.1.3). Equivalent upper- and lower-case checksum encodings are accepted.
Automation may normalize case for display, but must not treat a case-only
difference as a checksum mismatch.
