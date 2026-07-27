# Bundles and OCI storage

## Default representation and storage

Cosign v3 uses the standardized protobuf bundle format by default. Trusted-root and signing-config inputs, along with OCI Image 1.1 referring-artifact storage, are also default behavior. Older behavior remains available only through opt-in compatibility.

Audit workflows that silently depended on an older bundle representation or storage model. Make compatibility selection explicit at the boundary where the old consumer or registry requires it.

## Required output path

`--bundle` is required when producing a Sigstore bundle. A blob-signing invocation therefore names the bundle output directly:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

Do not rely on a default destination. Pass the resulting path explicitly to the next workflow step.

## Bundle-aware lifecycle operations

The standardized protobuf bundle format is supported by:

- `clean`
- `save`
- `load`
- `tree`
- download operations
- attach operations

Test the particular operation chain used by the application. For example, a successful save is not the complete check when a later load, attach, or tree operation consumes the result.

## Inspection

Version 3.1.2 adds the `cosign bundle inspect` command. Use it to inspect the bundle itself when diagnosing bundle-format and content questions.

Do not infer representation solely from a filename extension, the signature generation, or whether the artifact came from local or remote storage.

## Local images and mixed signature generations

`--local-image` works with `--new-bundle-format` for both v2 and v3 signatures. Test both generations when a local-image workflow consumes signatures produced on both sides of a migration.

## Attestation downloads

Attestation downloads handle both bundle formats. For new-format bundles, the download path validates predicate type.

Preserve that validation result as a security-relevant outcome. Do not turn a predicate-type mismatch into an ignored warning or a successful download step.

## Annotation parsing

Since 3.1.2, annotation values may contain `=`. Values such as tokens or encoded data must be retained in full instead of being split on every equals sign or rejected at the first embedded one.

When a wrapper parses an annotation argument, separate the key from the value only at the intended boundary and pass the remainder unchanged.

## Bundle workflow review

- Identify the format of every incoming and outgoing bundle.
- Pass an explicit `--bundle` output whenever a bundle is produced.
- Decide explicitly whether older compatibility behavior is required.
- Test all used clean, save, load, tree, download, and attach paths.
- Verify registry support for the selected referring-artifact storage path.
- Exercise local-image handling for every signature generation the workflow accepts.
- Preserve predicate-type validation for new-format attestation downloads.
- Round-trip annotation values containing embedded equals signs.
