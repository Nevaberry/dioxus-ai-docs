# BuildKit and Dockerfile Frontend

## Bundled frontend and compatibility

BuildKit 0.28.0 bundles Dockerfile frontend 1.22.0. Check the explicitly chosen
frontend syntax when present; otherwise use the bundled version when deciding
whether frontend behavior is available.

Buildx project-scoped named contexts require Dockerfile 1.22.0 or later.
Buildx per-build CPU/memory resources require BuildKit 0.31.0 or later and
Dockerfile 1.25.0 or later.

## Provenance

### SLSA version

BuildKit 0.28.0 defaults provenance attestations to SLSA v1.0 rather than
v0.2. Set the provenance `version` attribute when a downstream consumer still
requires v0.2.

### Source metadata

Since 0.28.0, a Source metadata request can pull an image's provenance
attestation directly. Buildx policies can consume image provenance and its
materials as secondary inputs when used with BuildKit 0.28.0 or later.

### JSON field casing

BuildKit 0.28.0 changes provenance JSON key `InvocationID` to `InvocationId` to
match SLSA. BuildKit and Buildx Go tooling handles it, but case-sensitive
third-party parsers must accept the new spelling.

## Source protocols and verification

### Raw blobs

BuildKit 0.28.0 LLB can address raw registry and OCI-layout blobs through
`docker-image+blob://` and `oci-layout+blob://` source identifiers.

### HTTP checksums

The 0.28.0 LLB API supports HTTP-source checksum algorithms beyond SHA-256 and
optional checksum suffixes. Preserve algorithm identity; do not compare only
the digest payload.

### PGP signatures

BuildKit 0.28.0 adds PGP verification for HTTP sources and accepts combined
public keys when defining the required signer. Git sources already supported
PGP verification. Buildx 0.33.0 exposes HTTP PGP verification to Rego policy
through `verify_http_pgp_signature`.

### Policy and build-step traffic

Buildx source policies expand from local contexts to Git, HTTP, images,
Sigstore evidence, provenance, and PGP. With BuildKit 0.31.0 or later, a policy
can opt into the exec proxy so `input.http` rules govern build-step traffic.
Keep source acquisition checks and execution-network checks explicit.

## Deployment environments

BuildKit 0.28.0 supports cgroup handling on hosts and Kubernetes deployments
without a dedicated cgroup namespace.

The Kubernetes Buildx driver can later use a StatefulSet and persistent volume
claim. Decide whether cached and runtime state should survive pod replacement
before enabling persistence.

## Security fixes in the 0.28 line

BuildKit 0.28.1 validates Git URL `#ref:subdir` fragments so they cannot escape
the checked-out repository root to restricted files. It also stops untrusted
custom frontends from writing outside the BuildKit state directory. Upgrade the
0.28 line rather than attempting to reproduce these boundaries in build input.

## Dockerfile and ignore behavior

### Invalid ignore patterns

BuildKit 0.28.1 no longer panics on an invalid `.dockerignore` pattern during
`COPY`. The pattern is still invalid; report and correct it rather than relying
on the absence of a panic.

### Negated patterns

Dockerfile frontend 1.22.0 stops a false linter warning that a `COPY` source is
ignored when a negated `.dockerignore` rule re-includes it. A deliberately
re-included source no longer needs warning suppression.

### Extended attributes during ADD

Since Engine 26.0.0, Dockerfile `ADD` archive extraction does not fail with
`lsetxattr ... operation not supported` solely because the destination
filesystem lacks xattr support. This differs from runtime image-layer unpack,
which can reject loss of layer xattrs.

## CLI ergonomics

BuildKit 0.28.0 adds Bash completion to `buildctl`.

Buildx's DAP debugger is generally available from 0.33.0. Use its protocol for
build debugging rather than depending on the old experimental opt-in.

## BuildKit-related Engine behavior

Windows daemons can use BuildKit when they advertise support from Engine
27.0.1. Engine 28.0.0 can manage containerd as a Windows child process. Treat
both as detected capabilities, not universal Windows defaults.

Builder configuration in Engine 29.3 accepts the `device` entitlement and can
use CDI for supported devices. Grant it only to builds that require devices.

## Verification checklist

1. Resolve the actual BuildKit and Dockerfile frontend pair.
2. Pin expected SLSA version and JSON field casing in provenance consumers.
3. Validate URL, blob, checksum, signer, and attestation identity at the source
   boundary.
4. Test cgroup namespace, persistent builder state, and device entitlements in
   the deployment environment.
5. Keep BuildKit security patch releases current within the selected line.
