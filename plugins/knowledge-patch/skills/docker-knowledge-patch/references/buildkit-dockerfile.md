# BuildKit and Dockerfile Frontend

Use this reference for BuildKit provenance, source protocols and verification, deployment constraints, Dockerfile frontend behavior, and linting.

## Frontend versions

- BuildKit 0.28.0 bundles Dockerfile frontend v1.22.0.
- Buildx cross-project named-context isolation requires Dockerfile 1.22.0 or later.
- Buildx resource limits introduced later require Dockerfile v1.25.0 or later together with BuildKit 0.31.0 or later.

## Provenance

- BuildKit 0.28.0 emits SLSA v1.0 provenance by default instead of v0.2. Set the provenance `version` attribute when an integration still requires v0.2.
- An image's provenance attestation can be fetched directly through a Source metadata request.
- The provenance JSON key is `InvocationId`, not `InvocationID`, matching the SLSA specification. Update case-sensitive consumers.

## Registry and OCI raw-blob sources

LLB definitions can retrieve raw blobs from registries and OCI layouts using protocols added in 0.28.0:

- `docker-image+blob://`
- `oci-layout+blob://`

## HTTP source verification

BuildKit 0.28.0 expands LLB HTTP-source verification:

- Request checksums using algorithms other than the default SHA-256.
- Use optional checksum suffixes.
- Validate sources with PGP signatures.
- Supply combined public keys when defining the required signer for PGP verification.

Buildx Rego policy adds higher-level Sigstore, provenance, PGP, and network-request checks; see [buildx.md](buildx.md).

## Deployment environments

- BuildKit 0.28.0 cgroup support works in environments without their own cgroup namespace, including such Kubernetes deployments.

## Dockerfile archive extraction

- Starting with Engine 26.0.0, Dockerfile `ADD` does not fail with `lsetxattr ... operation not supported` merely because an input archive has extended attributes that the destination filesystem cannot store.
- This is narrower than general image-layer extraction: Engine 25.0.0 makes layer unpacking fail when extended attributes cannot be preserved. Do not treat the `ADD` exception as a global xattr policy.

## Dockerfile linting

- Dockerfile frontend 1.22.0 stops reporting a false copy warning when a negated ignore pattern has re-included a path used by `COPY`.

## buildctl shell integration

- `buildctl` supports Bash completion starting with BuildKit 0.28.0.
