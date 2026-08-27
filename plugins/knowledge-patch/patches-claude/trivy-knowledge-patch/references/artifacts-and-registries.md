# Artifacts and Registries

Use this reference for image acquisition, registry behavior, artifact classification and identity, image archives, layers, histories, and repository metadata.

## Registry acquisition and authentication

### Registry mirrors (0.59.0)

Container image acquisition can use registry mirrors. Configure mirrored endpoints when scans must avoid or proxy the origin registry.

### Authenticated GHCR artifact downloads (0.59.0)

Artifact downloads from GHCR honor `GITHUB_TOKEN`.

### Registry login scope handling (0.60.0)

`trivy registry login` does not use a registry scope during authentication. Do not require the old scope request in authentication integrations.

### Dual-stack ECR endpoints (0.68.0)

AWS image access supports dual-stack ECR endpoints.

### Docker context resolution (0.65.0)

Image handling resolves Docker contexts when locating images for scans.

## Acquisition failures and recovery

### Oversized image rejection (0.59.0)

Image scans reject an image early when the total size of its layers exceeds the limit. Surface the resulting error instead of expecting a partial scan.

### Unsupported remote artifacts (0.64.0)

Remote image retrieval rejects unsupported artifact types rather than trying to process them as container images.

### Missing database recovery (0.67.0)

If database contents are missing but metadata remains, Trivy downloads the database again instead of accepting stale metadata as a valid cache.

## Image families and sources

### Root.io container images (0.64.0)

Vulnerability scanning supports Root.io container images. See the vulnerability reference for their package-version and severity semantics.

### ActiveState image scanning (0.69.0)

Vulnerability scanning supports ActiveState images.

### RapidFort curated image scanning (0.74.0)

Vulnerability scanning supports RapidFort curated images.

## Archive, embedded-SBOM, and attestation behavior

### Image archives and attested SBOMs (0.68.0)

Docker archive analysis preserves `RepoTags`. Image and SBOM handling accepts SBOMs carried in Sigstore bundles and SPDX attestations.

### Embedded-SBOM image determinism (0.69.0)

Images containing an embedded SBOM produce deterministic scan results.

## Layers, history, and effective configuration

### Image layer metadata in reports (0.62.0)

Image scanning saves layer metadata in reports for downstream consumers.

### Buildah and legacy Docker histories (0.64.0)

Misconfiguration analysis normalizes `CreatedBy` values from Buildah and legacy Docker builder histories so instruction-based checks behave consistently.

### Effective image user precedence (0.64.0)

When determining the effective image user, `.Config.User` always takes precedence over `USER` entries in `.History`.

### Image-history normalization (0.67.0)

Misconfiguration analysis strips build-metadata suffixes from image history. It also quotes legacy `ENV` values so spaces are preserved.

### Non-BuildKit `RUN` reconstruction (0.71.0)

Image analysis reconstructs `RUN` instructions correctly for images built without BuildKit.

### Custom-resource layer attribution (0.72.0)

After image layers are merged, image analysis can still identify the origin layer for custom resources.

## Artifact and repository identity

### Git repository metadata (0.65.0)

Repository scans add Git repository metadata to reports.

### Cached filesystem report metadata (0.66.0)

Filesystem scan cache hits preserve `RepoMetadata` in reports.

### Sanitized repository metadata (0.66.0)

Repository scans sanitize the Git repository URL before adding it to report metadata.

### Stable scan and report identities (0.68.0)

Scan targets expose a unique `ArtifactID`; its calculation includes registry and repository. Reports expose a UUIDv7 `ReportID`, add vulnerability fingerprints, and carry the image reference in report metadata.

### Repository-aware filesystem artifacts (0.68.0)

When a filesystem scan detects Git information, it classifies the artifact as a repository. Report consumers must allow the artifact type to change accordingly.
