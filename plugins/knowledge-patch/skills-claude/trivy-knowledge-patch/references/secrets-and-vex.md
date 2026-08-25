# Secrets and VEX

Use this reference for secret scan inputs, detector formats, filtering and locations, plus VEX discovery, TLS, and package-graph behavior.

## Secret scanning inputs and transport

### Client/server secret inspection (0.60.0)

In client/server mode, the configuration analyzer performs secret inspection.

### Python metadata in secret scans (0.62.0)

Secret scanning ignores `.dist-info` directories.

### Secret input and locations (0.65.0)

Secret scanning validates UTF-8 before protobuf marshalling. Multiline secret findings report corrected line numbers.

### Secret-scan exclusions and detectors (0.71.0)

Skipped folders, files, and extensions are configurable. Detectors include Azure secret rules and passwords or passphrases in Maven `settings.xml` and `settings-security.xml`. The secret-scanner configuration file itself is skipped.

## Detector and match semantics

### Secret match filtering (0.63.0)

Only secrets of meaningful length match, and example strings can remain unflagged.

### Secret detection updates (0.69.0)

Secret scanning detects the Symfony default secret key and uses improved word-boundary handling for Hugging Face tokens.

### OpenAI and GitHub App secrets (0.72.0)

Secret scanning includes OpenAI secret rules and recognizes stateless GitHub App installation tokens.

## VEX loading and discovery

### CycloneDX-referenced VEX (0.60.0)

When scanning CycloneDX SBOMs, Trivy can load external VEX files referenced by the SBOM.

### Per-repository VEX TLS (0.69.0)

Each VEX repository can have its own TLS configuration.

### Repository-local VEX documents (0.72.0)

VEX loading discovers documents within the scanned repository directory.

### OCI-hosted VEX discovery (0.74.0)

VEX discovery finds OCI artifacts, including OpenVEX documents published as generic in-toto OCI referrers. Non-local VEX repository names are rejected.

## VEX graph behavior

### VEX handling of looping package graphs (0.67.0)

VEX processing does not suppress vulnerabilities merely because a package participates in a cyclic package graph.
