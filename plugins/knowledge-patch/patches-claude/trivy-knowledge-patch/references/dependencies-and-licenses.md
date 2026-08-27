# Dependencies and Licenses

Use this reference for language analyzers, package and workspace relationships, repository resolution, package identity, license discovery, and license serialization.

## Node.js, pnpm, Yarn, and Bun

### Node.js peer dependencies (0.59.0)

Node.js dependency trees include peer dependencies, which can change the relationships represented in results.

### Yarn workspace relationships (0.62.0)

Yarn package analysis records root and workspace context.

### Bun lockfiles (0.63.0)

Node.js dependency analysis parses and analyzes `bun.lock`.

### Bun lockfile package arrays (0.64.0)

The `bun.lock` analyzer parses the `packages` array correctly.

### npm constraint comparison (0.65.0)

Constraint comparison does not apply prerelease logic to npm constraints.

### Node.js workspace and pnpm identities (0.67.0)

`package-lock.json` accepts object-form workspace declarations. pnpm uses the snapshot string as `Package.ID`.

### Lockfile dependency metadata (0.69.0)

Node.js analysis reads license data from `package-lock.json`. Composer analysis includes development dependencies.

### Node.js legacy and malformed metadata (0.71.0)

The npm lockfile parser accepts legacy license formats. Invalid names in subdirectory `package.json` files cause those files to be silently skipped rather than aborting analysis.

### Multi-document pnpm lockfiles (0.72.0)

Node.js analysis extracts project dependencies from multi-document `pnpm-lock.yaml` files.

### Overlapping pnpm workspaces (0.74.0)

Node.js analysis supports pnpm workspaces with overlapping package definitions.

## Python packaging

### uv and Poetry dependency coverage (0.59.0)

Python scanning supports uv projects, including uv development and optional dependencies. Poetry development dependencies are supported, while dependencies in Poetry's `dev` group are skipped.

### Poetry v2 (0.60.0)

Python dependency scanning supports Poetry v2 projects.

### Python egg metadata (0.65.0)

The Python Packaging analyzer reads package metadata from `.egg-info/METADATA`.

### PEP 770 SBOM handling (0.69.0)

Python analysis excludes PEP 770 SBOM files under `.dist-info/sboms/` from ordinary SBOM discovery.

### PEP 751 lock files (0.70.0)

Python analysis parses and scans PEP 751 `pylock.toml` lock files.

### Python dependency-file edge cases (0.70.0)

`requirements.txt` parsing supports dependencies with multiple version specifiers. Poetry accepts optional groups with no dependencies without crashing.

### PEP 621 dependency-name normalization (0.74.0)

Python analysis normalizes dependency names from PEP 621 `pyproject.toml` before creating package results.

## Go, Rust, Julia, and Seal

### Go 1.24 main-module versions (0.60.0)

Go analysis parses the main-module version from artifacts built with Go 1.24 or newer.

### Standard Go WebAssembly modules (0.61.0)

WebAssembly modules use standard Go instead of TinyGo. Build them with the standard Go compiler.

### Cargo workspace relationships (0.62.0)

Cargo lockfile analysis records root packages, workspace packages, and their relationships.

### Go license discovery (0.63.0)

License scanning searches dependencies in `GOPATH` and `vendor`. For `go.mod` projects it also searches the vendor directory for licenses.

### Dependency relationship fields (0.63.0)

Julia parsing populates the `Relationship` field, and client/server RPC transports it.

### Go pseudo-version resolution (0.69.0)

Go analysis uses the linker-flags version for every pseudo-version. Build metadata can therefore change the package version reported and matched.

### Cargo monorepos (0.69.0)

Rust analysis expands glob patterns in Cargo workspace members and supports inherited package versions in Cargo monorepos.

### Go binary version discovery (0.70.0)

Go binary analysis can recover versions from the ELF symbol table for `-trimpath` builds. It also understands the version format used with `GOEXPERIMENT` in Go 1.26.

### Vendor-aware Seal detection (0.71.0)

Seal language-file detection retains vendor information.

### Seal support (0.67.0)

Trivy has native `seal` support, so integrations do not need to treat it as unsupported.

### Seal packages without prefixes (0.74.0)

Seal detection recognizes packages without a name prefix by using their version suffix.

## Java, Maven, and Gradle

### Gradle development dependencies (0.63.0)

Gradle lockfile analysis excludes development dependencies.

### Maven settings environment placeholders (0.64.0)

Java analysis dereferences every environment-variable placeholder in Maven `settings.xml`, including settings with multiple placeholders.

### Maven repository settings (0.68.0)

Java analysis reads remote repositories from `settings.xml`. Repository releases and snapshots default to enabled when unset. Fields contributed by multiple dependency-management sources follow corrected resolution precedence.

### Maven model and package identity (0.69.0)

POM analysis inherits properties from parent fields and propagates repositories from upper POMs to dependencies. A `pom.xml` package ID includes a hash of the GAV coordinates and root-POM path to avoid collisions.

### Maven proxy configuration (0.70.0)

Java analysis reads Maven proxy settings from `settings.xml` and uses them for repository access.

### Java dependency exclusions (0.70.0)

Java analysis preserves dependency exclusions rather than overwriting them.

### Maven mirrors and repository throttling (0.71.0)

Java analysis honors Maven `<mirrors>` from `settings.xml`. An HTTP 429 from a remote Maven repository during `pom.xml` scanning is fatal, preventing silent incomplete resolution.

### JAR license discovery (0.72.0)

Java license analysis discovers licenses in packaged `LICENSE` files and embedded `pom.xml` files inside JARs.

### Maven mirrors in `trivy.yaml` (0.74.0)

Java analysis accepts user-defined Maven mirrors from `trivy.yaml` as well as mirrors from Maven `settings.xml`.

### Java license and manifest handling (0.74.0)

Java license analysis reads Jenkins plugin licenses from manifests and maps license URLs in JAR `Bundle-License` metadata and POM `<url>` elements to SPDX IDs. Artifact properties come only from the main `MANIFEST.MF` section, not per-entry sections.

### Nested JAR digests (0.74.0)

Nested JARs receive per-file digests, preserving file-specific package identity.

## .NET dependency graphs

### .NET dependency graphs (0.68.0)

`.deps.json` analysis builds dependency graphs instead of returning an unconnected package list.

### Self-contained .NET runtimes (0.72.0)

`.NET` analysis detects the bundled runtime in a self-contained deployment and includes runtime components in results.

### .NET root-project detection (0.74.0)

`.deps.json` analysis identifies the root .NET project from the dependency graph.

## Package provenance and license behavior

### Non-standard licenses in SPDX (0.59.0)

Licenses outside the SPDX list are emitted through `hasExtractedLicensingInfos`.

### License output cleanup (0.61.0)

Debian `dpkg` results omit empty licenses. SPDX text licenses are stored in `otherLicenses` without normalization, preserving the original text.

### Custom and compound licenses (0.63.0)

Configured custom classifications apply to text licenses. License analysis accepts compound expressions that use SPDX operators.

### Package-type filtering in license scans (0.65.0)

License scanning observes the package-types option; package selection also filters license results.

### CycloneDX hashes and licenses (0.65.0)

CycloneDX SBOM handling accepts SHA-512 hashes and places licenses in the correct report field.

### License identifiers and expressions (0.65.0)

License analysis maps `GFDL-NIV-1.1` and `GFDL-NIV-1.2`. `LaxSplitLicenses` handles the SPDX `WITH` operator.

### SPDX license semantics (0.68.0)

Identifiers are validated against the SPDX ID list, and ignore processing separates identifiers from full expressions. A `WITH` exception stays attached to its license during category detection. The literal `unlicensed` is not normalized to `Unlicense`.

### Package analyzer provenance (0.69.0)

Detected packages expose `AnalyzedBy`, identifying the analyzer that found each package.

### Canonical SPDX identifiers (0.69.0)

License output uses canonical identifiers from the embedded SPDX license data.

### SPDX license assertions (0.70.0)

SPDX output uses `NOASSERTION` for both `licenseDeclared` and `licenseConcluded` on non-library packages.
