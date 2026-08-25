# CLI and module migration

Use this reference when updating command invocations, Go imports, signing
options, or key-provider error handling.

## Required bundle output

Commands that produce a Sigstore bundle require an explicit `--bundle` output
file (batch 3.1.2):

```sh
cosign sign-blob --bundle artifact.sigstore.json artifact.bin
```

Do not preserve wrappers that expect Cosign to select an implicit output path.

## Removed initialize option

`cosign initialize --out` has been removed (batch 3.1.2). Remove the option
from scripts, examples, wrappers, and command builders rather than attempting
to translate its old output behavior.

## Deprecated flags and commands

The following flags are deprecated (batch 3.1.2):

- `--tlog-upload`
- `--offline`
- `--rekor-entry-type`
- `--payload` on sign commands
- `--payload` on verify commands
- `--output-attestation`

The following commands are deprecated:

- `cosign triangulate`
- `cosign copy`

The deprecated surface is slated for removal in v4. Keep any compatibility
adapter localized, document which callers still need it, and keep the policy
logic independent of the deprecated invocation.

The `--offline` deprecation does not mean that explicit-key offline
verification now requires a trusted root. That verification mode no longer
requires one; see
[verification and security](verification-and-security.md#explicit-key-security-key-and-identity-modes).

## Go module major

The Go module major is v3 (batch 3.1.2). Updating the executable alone does not
rewrite Go import paths. Update module requirements and imports, then compile
and test against the v3 API.

## Signing options

`sign-blob` can sign with a certificate, and signing exposes
`--signing-algorithm` (batch 3.1.2). Treat certificate selection and algorithm
selection as explicit, independent inputs. Neither is implied by the chosen
TUF service endpoints.

OCI artifact signing can use an X.509 certificate chain (batch
2.6.5-3.1.3). Preserve the ordered chain material expected by the signing
workflow and distinguish it from a single leaf-certificate input.

## Public-key digest selection

Cosign 3.1.3 auto-detects the default digest algorithm for public keys. Do not
hard-code one supposed default for every public-key type; let Cosign select the
key-appropriate default unless policy requires an explicit algorithm.

## PKCS#11 no-match behavior

When no PKCS#11 key pair matches, Cosign 3.1.3 returns an error instead of
panicking (batch 2.6.5-3.1.3). Callers should handle the condition as a normal
signing failure, preserve the diagnostic, and avoid panic-based recovery logic.
