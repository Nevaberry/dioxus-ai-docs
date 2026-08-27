# Dependencies and Licenses

## Go

### Main-module and binary versions

Go analysis parses the main-module version in artifacts built with Go 1.24 or
newer (since 0.60.0). For pseudo-versions, it uses the linker-flags version for
all pseudo-version cases, affecting the emitted version and vulnerability
matching when build metadata supplies it (since 0.69.0).

Binary analysis can recover versions from the ELF symbol table for binaries
built with `-trimpath`. It also recognizes the version format produced with
`GOEXPERIMENT` in Go 1.26 (since 0.70.0).

### License discovery

Go license scanning searches dependencies in `GOPATH` and `vendor`. For a
`go.mod` project, it also searches the vendor directory for licenses (since
0.63.0).

## Java and JVM ecosystems

### Maven settings

Maven analysis dereferences every environment-variable placeholder in
`settings.xml`, including files with multiple placeholders (since 0.64.0).
It reads remote repository configuration, treating omitted `releases` and
`snapshots` enablement as enabled, and applies corrected precedence when
resolving package fields from several dependency-management sources (since
0.68.0).

It also reads proxy configuration (since 0.70.0) and `<mirrors>` (since
0.71.0) from `settings.xml`. A 429 response from a remote Maven repository
while scanning a `pom.xml` is fatal; do not consume the scan as if dependency
resolution were complete. User-defined Maven mirrors can also be supplied in
`trivy.yaml` (since 0.74.0).

### Maven models and dependency exclusions

POM analysis inherits properties from parent fields and propagates repositories
from upper POMs to dependencies (since 0.69.0). A `pom.xml` package ID includes
a hash of its GAV coordinates and root-POM path, avoiding collisions. Java
analysis preserves dependency exclusions rather than overwriting them (since
0.70.0).

### JAR identity and licenses

Java license analysis discovers packaged `LICENSE` files and an embedded
`pom.xml` inside JARs (since 0.72.0). It reads Jenkins plugin licenses from
manifests and maps license URLs in JAR `Bundle-License` metadata and POM `<url>`
elements to SPDX identifiers (since 0.74.0). Artifact properties come only
from the main `MANIFEST.MF` section, not per-entry sections.

Nested JARs receive a per-file digest so their identities remain file-specific
(since 0.74.0).

### Gradle development dependencies

Gradle lockfile analysis excludes development dependencies (since 0.63.0).

## JavaScript and TypeScript ecosystems

### npm dependency trees

Node.js dependency trees include peer dependencies, which can alter emitted
relationships (since 0.59.0). Constraint comparison does not apply prerelease
logic to npm constraints (since 0.65.0).

`package-lock.json` accepts object-form workspace declarations (since 0.67.0),
and lockfile analysis reads license metadata (since 0.69.0). The npm lockfile
parser accepts legacy license formats; malformed names in subdirectory
`package.json` files are skipped without stopping analysis (since 0.71.0).

### Yarn workspaces

Yarn analysis records root and workspace context for packages (since 0.62.0).

### pnpm

The pnpm snapshot string is the package's `Package.ID` (since 0.67.0).
Multi-document `pnpm-lock.yaml` files contribute project dependencies (since
0.72.0), and workspaces with overlapping package definitions are supported
(since 0.74.0).

### Bun

Node.js analysis parses `bun.lock` (since 0.63.0), including its `packages`
array shape (since 0.64.0).

## Python

### uv and Poetry

Python scanning supports uv projects, including development and optional
dependencies (since 0.59.0). Poetry development dependencies are supported,
while dependencies in Poetry's `dev` group are skipped. Poetry v2 projects are
supported (since 0.60.0).

Poetry analysis accepts an optional group with no dependencies without
crashing (since 0.70.0).

### Requirements and standardized lock files

`requirements.txt` parsing accepts a dependency with multiple version
specifiers (since 0.70.0). Python analysis parses and scans the PEP 751
`pylock.toml` format (since 0.70.0).

Dependencies declared through PEP 621 in `pyproject.toml` have their names
normalized before package results are created (since 0.74.0).

### Installed-package metadata

The Python Packaging analyzer reads `.egg-info/METADATA` (since 0.65.0).
PEP 770 SBOM files in `.dist-info/sboms/` are excluded from ordinary SBOM
discovery (since 0.69.0).

## Rust

Cargo lockfile analysis records root packages, workspace packages, and their
relationships (since 0.62.0). Cargo monorepo analysis expands glob patterns in
workspace members and supports inherited package versions (since 0.69.0).

## .NET and NuGet

Analysis builds dependency graphs from `.deps.json` rather than emitting an
unconnected package list (since 0.68.0). It detects the bundled runtime in a
self-contained deployment (since 0.72.0), and identifies the root .NET project
from the `.deps.json` dependency graph (since 0.74.0).

Vulnerability matching compares NuGet package names in lowercase, preventing
name-casing-only misses (since 0.67.0).

## Julia, Composer, and Seal

Julia parsing populates dependency `Relationship`, and client/server RPC
transports it (since 0.63.0). Julia packages can be matched for
vulnerabilities (since 0.69.0).

Composer analysis includes development dependencies (since 0.69.0).

Trivy has native Seal support (since 0.67.0). Seal language-file detection
uses vendor information (since 0.71.0) and recognizes packages without a name
prefix by using their version suffix (since 0.74.0).

## Package provenance and filtering

Detected packages expose `AnalyzedBy`, identifying the analyzer that found
them (since 0.69.0). License scanning obeys the package-types option, so
package selection also filters license results (since 0.65.0).

Debian `dpkg` package results omit empty license values (since 0.61.0).

## License classification and expressions

### Custom and compound licenses

Configuration-defined custom classifications apply to text licenses. License
analysis supports compound expressions containing SPDX operators (since
0.63.0).

### SPDX identifiers and exceptions

License analysis maps `GFDL-NIV-1.1` and `GFDL-NIV-1.2`, and
`LaxSplitLicenses` handles the `WITH` operator (since 0.65.0).

Identifiers are validated against the SPDX identifier list. Ignore handling
distinguishes an SPDX ID from a full expression, `WITH` exceptions remain part
of one license during category detection, and literal `unlicensed` is not
normalized to `Unlicense` (since 0.68.0).

License output uses canonical identifiers from the embedded SPDX license data
(since 0.69.0).
