# BuildKit and Dockerfile Frontend

Use this reference for Dockerfile frontend behavior, BuildKit source handling,
provenance, runtime compatibility, and BuildKit security changes.

## Dockerfile and build-context behavior

### Dockerfile `ADD` on filesystems without xattrs (26.0.0)

Extracting an archive with extended attributes through `ADD` no longer fails
with `lsetxattr ... operation not supported` when the destination filesystem
cannot store those attributes.

### Bundled Dockerfile frontend 1.22.0 (0.28.0)

BuildKit 0.28.0 updates its built-in Dockerfile frontend to v1.22.0;
compatibility checks against the bundled frontend should use that version.

### Invalid `.dockerignore` patterns (0.28.0)

BuildKit 0.28.1 no longer panics while processing an invalid `.dockerignore`
pattern during `COPY`.

### Negated ignore patterns no longer trigger false copy warnings (1.22.0)

Dockerfile frontend 1.22.0 no longer emits an incorrect linter warning that a
`COPY` source is ignored when a negated `.dockerignore` pattern re-includes it.
Builds that intentionally re-include files should no longer treat this warning
as actionable.

## Provenance and source metadata

### SLSA v1 provenance by default (0.28.0)

Provenance attestations now default to SLSA v1.0 instead of v0.2. Set the
provenance `version` attribute when legacy v0.2 output is required.

### Provenance through source metadata (0.28.0)

An image's provenance attestation can now be pulled directly with a Source
metadata request.

### Provenance JSON key casing (0.28.0)

The provenance attestation key `InvocationID` is now `InvocationId` to match
SLSA. BuildKit and Buildx Go tooling is unaffected, but case-sensitive
third-party JSON parsers must accept the new spelling.

## LLB source capabilities

### Raw registry and OCI-layout blob sources (0.28.0)

LLB definitions can access raw blobs from image registries and OCI layouts
through the new `docker-image+blob://` and `oci-layout+blob://` source identifier
protocols.

### Custom HTTP-source checksums (0.28.0)

The LLB API can request HTTP-source checksums using algorithms other than the
default SHA-256 and can include optional checksum suffixes.

### HTTP-source PGP verification (0.28.0)

LLB HTTP sources can now be validated with PGP signatures, as Git sources
already could. PGP verification also accepts combined public keys when defining
the required signer.

## Runtime and tooling

### Cgroups without a dedicated namespace (0.28.0)

BuildKit's cgroup handling now supports environments, including Kubernetes
deployments, that do not have their own cgroup namespace.

### Bash completion for `buildctl` (0.28.0)

The `buildctl` binary now supports Bash completion.

## Security fixes

### 0.28.1 security hardening (0.28.0)

The follow-up release validates Git URL `#ref:subdir` fragments so they cannot
access restricted files outside the checked-out repository root, and prevents
untrusted custom frontends from writing outside the BuildKit state directory.
