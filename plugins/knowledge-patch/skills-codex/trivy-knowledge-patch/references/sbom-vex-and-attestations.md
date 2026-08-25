# SBOM, VEX, and Attestations

## SBOM command behavior

The `sbom` command disables `--skip-dir` and `--skip-files` (since 0.63.0).
Remove these flags from wrappers; they are not supported filtering controls for
this command.

## Applications, packages, and dependency graphs

### Nested and duplicate applications

Nested packages are attached to their application. Applications of the same
type from different SBOM files are preserved as distinct applications, and an
unknown dependency is associated with a root package when one exists (since
0.59.0).

When an application path cannot otherwise be detected, the SBOM file's path is
used as the application's `FilePath` (since 0.60.0).

### OS packages from multiple inputs

OS packages from multiple SBOM inputs are preserved (since 0.60.0). Results
merge OS packages found inside and outside the dependency graph (since
0.65.0). Duplicate `dpkg` packages found at different paths in separate image
layers are consolidated (since 0.59.0).

### File components and missing roots

CycloneDX components of type `file` are supported (since 0.66.0). The SPDX
marshaler tolerates a document without a root component rather than failing on
a nil value (since 0.72.0).

## Structure and metadata preservation

### CycloneDX structure

When a CycloneDX SBOM file is scanned with vulnerability updates, its existing
structure remains intact for downstream consumers (since 0.67.0).

CycloneDX 1.7 is supported (since 0.71.0).

### Layer and image information

SBOM scan results include image-layer data (since 0.59.0). Docker archive
analysis retains `RepoTags` (since 0.68.0).

Red Hat `BuildInfo` remains available even when an SBOM has no layer
information (since 0.70.0).

### Build metadata

SBOM output exposes `buildInfo` as properties, and client/server RPC carries
the same data through `BlobInfo` (since 0.68.0).

### CoreOS

SBOM scanning supports CoreOS (since 0.67.0).

## CycloneDX serialization

### Tool and component metadata

CycloneDX tool metadata includes `manufacturer` (since 0.64.0). Components can
carry multiple license types (since 0.66.0).

### Hashes and licenses

CycloneDX handling accepts SHA-512 hashes, and generated reports put licenses
in the correct CycloneDX field (since 0.65.0).

### Vulnerability ratings

CycloneDX vulnerability output includes CVSS v4 ratings (since 0.70.0).

## SPDX serialization

### Extracted and text licenses

Licenses outside the SPDX list are represented through
`hasExtractedLicensingInfos` (since 0.59.0). SPDX text licenses are stored in
`otherLicenses` without normalization so their original text is preserved
(since 0.61.0).

### License assertions

For non-library packages, SPDX output sets both `licenseDeclared` and
`licenseConcluded` to `NOASSERTION` (since 0.70.0).

### Hash algorithms

SPDX serialization supports SHA-512 (since 0.71.0).

## SPDX license semantics

License identifiers are validated against the SPDX ID list, while ignore
processing distinguishes identifiers from full expressions. A `WITH` exception
stays attached to the same license for category detection, and literal
`unlicensed` is not rewritten as `Unlicense` (since 0.68.0).

Output uses canonical SPDX license identifiers from the embedded SPDX data
(since 0.69.0).

## VEX loading and application

### CycloneDX references

When scanning a CycloneDX SBOM, Trivy can load an external VEX file referenced
by that SBOM (since 0.60.0).

### Repository-local VEX

VEX discovery finds documents stored under the scanned repository directory
(since 0.72.0). A VEX repository can have repository-specific TLS settings
(since 0.69.0).

### OCI-hosted VEX

VEX discovery finds OCI artifacts, including OpenVEX documents published via
generic in-toto OCI referrers (since 0.74.0). Non-local VEX repository names are
rejected.

### Looping dependency graphs

VEX processing does not suppress vulnerabilities solely because their packages
participate in a looping package graph (since 0.67.0).

## Attestations and embedded SBOMs

Image and SBOM processing supports SBOMs in Sigstore bundles and SPDX
attestations (since 0.68.0). Images with embedded SBOMs produce deterministic
scan output (since 0.69.0).

## Discovery exclusions

PEP 770 SBOM files under `.dist-info/sboms/` are excluded from ordinary SBOM
discovery (since 0.69.0). This prevents standardized installed-package SBOMs
from being mistaken for separately supplied scan inputs.
