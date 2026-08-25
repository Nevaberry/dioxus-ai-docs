# SBOM and Reports

Use this reference when generating, enriching, transporting, or consuming SBOM, JSON, SARIF, JUnit, template, and summary output.

## Package graphs and SBOM application structure

### Package and SBOM result structure (0.59.0)

Duplicate `dpkg` packages found at different paths or layers are consolidated. Nested packages attach to their application, applications of the same type from different SBOM files remain distinct, image-layer data is retained, and unknown dependencies attach to a root package when one exists.

### SBOM application paths (0.60.0)

If an application's path cannot otherwise be detected, the SBOM file path becomes the application's `FilePath`.

### OS packages from multiple SBOMs (0.60.0)

OS packages collected from multiple SBOM inputs are preserved.

### OS packages from SBOM graphs (0.65.0)

SBOM results merge OS packages found inside and outside the dependency graph.

### CycloneDX structure preservation (0.67.0)

Enriching a CycloneDX SBOM with vulnerability updates preserves the input SBOM's structure.

### CoreOS SBOM support (0.67.0)

SBOM scanning supports CoreOS.

### SBOM build metadata (0.68.0)

SBOM output exposes `buildInfo` as properties. Client/server RPC transports the same data through `BlobInfo`.

### Red Hat build information from SBOMs (0.70.0)

SBOM scanning preserves Red Hat `BuildInfo` even when layer information is absent.

## CycloneDX support

### CycloneDX tool manufacturer (0.64.0)

CycloneDX tool metadata includes `manufacturer`.

### CycloneDX license variants (0.66.0)

CycloneDX handling accepts components with multiple license types.

### CycloneDX file components (0.66.0)

SBOM scanning supports CycloneDX components of type `file`.

### CycloneDX CVSS v4 ratings (0.70.0)

CycloneDX vulnerability output includes CVSS v4 ratings.

### CycloneDX 1.7 (0.71.0)

SBOM scanning supports CycloneDX 1.7.

## SPDX support

### SPDX SHA-512 hashes (0.71.0)

SPDX serialization supports the SHA-512 hash algorithm.

### SPDX documents without a root component (0.72.0)

The SPDX marshaler tolerates a missing root component instead of failing on a nil value.

## Report content and templates

### Report summary table (0.60.0)

Reports can include a summary table for an at-a-glance view.

### SARIF description text (0.60.0)

SARIF `shortDescription` and `fullDescription` text is not HTML-escaped.

### Misconfiguration locations in JUnit (0.63.0)

The JUnit template includes source locations for misconfiguration findings.

### CVSS vectors in SARIF (0.65.0)

SARIF vulnerability findings include CVSS vectors.

### Git repository paths in SARIF (0.70.0)

SARIF uses the correct `ROOTPATH` URI when the scan target is a Git repository.

## Client/server and result metadata

### Repository class in client/server scans (0.72.0)

Client/server transport preserves each package's repository class.
