# Bundles and OCI storage

## Standardized bundle and storage defaults

In the 3.1.2 batch, Cosign v3 enables these behaviors by default:

- the standardized protobuf bundle format;
- trusted-root and signing-config inputs; and
- OCI Image 1.1 referring-artifact storage.

Older behavior is opt-in compatibility. Select it explicitly where an existing
consumer or registry requires it, and test the resulting representation and
storage path end to end.

## Required bundle destination

`--bundle` is required when producing a Sigstore bundle. For example:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

The output path is part of the command contract; do not infer a destination in
a wrapper.

## Bundle-aware lifecycle operations

The standardized protobuf format is supported by:

- `clean`
- `save`
- `load`
- `tree`
- download operations
- attach operations

Do not insert an assumed format conversion between these operations. Preserve
the selected representation deliberately and test the exact save/load or
download/attach round trip used by the workflow.

## Bundle inspection

Cosign 3.1.2 adds `cosign bundle inspect`. Use the command to diagnose bundle
format, contents, and interoperability. Do not treat a filename extension or
OCI location as proof of the encoded representation.

## Local-image workflows

`--local-image` works with `--new-bundle-format` for both v2 and v3 signatures.
A local-image workflow can therefore exercise the standardized representation
while handling signatures from either major generation. Test each signature
generation that the workflow accepts.

## Attestation downloads

Attestation downloads handle both bundle formats. When the downloaded object
uses the new format, the download flow validates predicate type. Preserve this
validation in automation and treat a mismatch as failure.

## Annotation parsing

Cosign 3.1.2 accepts equals signs inside annotation values. Preserve the entire
value after the annotation key rather than splitting or rejecting it at the
first embedded `=`. This matters for tokens, encoded values, and similar
annotations.

## Compatibility review

Before changing a bundle pipeline, record:

- which bundle format each producer emits;
- which format each consumer accepts;
- whether local-image handling covers v2 signatures, v3 signatures, or both;
- whether predicate-type validation remains active for new-format
  attestations; and
- whether every registry supports the selected OCI referring-artifact storage.
