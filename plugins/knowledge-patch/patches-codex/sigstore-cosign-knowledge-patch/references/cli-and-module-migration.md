# CLI and module migration

## Required bundle output

In the 3.1.2 batch, commands that produce a Sigstore bundle require an explicit
`--bundle` output file. A blob-signing invocation should name the destination:

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

Do not preserve wrappers that expect an implicit bundle output location.

## Removed initialization option

`cosign initialize --out` has been removed. Remove the option from shell
scripts, command builders, documentation, and tests instead of attempting to
translate it at runtime.

## Deprecated flags

The following CLI flags are deprecated:

- `--tlog-upload`
- `--offline`
- `--rekor-entry-type`
- `--payload` on sign and verify commands
- `--output-attestation`

Do not mistake the deprecation of the `--offline` flag for removal of explicit-
key offline verification behavior. Verification modes and their trust inputs
are covered in [Verification and security](verification-and-security.md).

## Deprecated commands

The following commands are deprecated:

- `cosign triangulate`
- `cosign copy`

The deprecated flags and commands are slated for removal in v4. Inventory their
use now, isolate any temporary compatibility shims, and plan supported
replacements before upgrading to that major.

## Go module major

The Go module major is v3. Update module references and import paths in Go
integrations, then compile and test against the v3 API. Installing a v3 CLI
does not migrate library imports automatically.

## Migration review

For each invocation or integration:

1. Add the required `--bundle` destination to bundle-producing commands.
2. Delete `initialize --out` use.
3. Identify every deprecated command and flag.
4. Separate CLI rollout from the Go module-major migration.
5. Run command-level and integration tests after each migration step.
