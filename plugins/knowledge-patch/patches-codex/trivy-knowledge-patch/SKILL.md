---
name: trivy-knowledge-patch
description: Trivy
version: "0.72.0"
license: MIT
metadata:
  author: Nevaberry
---


# Trivy Knowledge Patch

## Use this patch

Load this patch when a task involves recent Trivy CLI behavior, scanner output,
analyzers, vulnerability matching, misconfiguration evaluation, SBOM or VEX
handling, secret detection, client/server transport, or embedding Trivy as a
library.

Before changing code or configuration:

1. Determine the Trivy version used by the project, image, Helm release, or
   client/server pair.
2. Identify the scan target and enabled scanners.
3. Read the matching topic reference below.
4. Treat report fields, package identities, defaults, and filtering behavior as
   compatibility-sensitive API surface.
5. Prefer the installed version's schema, code, and tests if they disagree with
   this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI, reports, and runtime](references/cli-reports-and-runtime.md) | Flags, defaults, configuration, server behavior, report identities, templates, and metadata |
| [Dependencies and licenses](references/dependencies-and-licenses.md) | Language analyzers, lockfiles, dependency graphs, package identity, and license discovery |
| [Images, registries, and operating systems](references/images-registries-and-os.md) | Image acquisition, histories and layers, OS detection, package vulnerability matching, and lifecycle data |
| [Misconfiguration and infrastructure as code](references/misconfiguration-and-iac.md) | Terraform, OpenTofu, CloudFormation, Azure, GCP, Kubernetes, Helm, Dockerfile, Rego, and check metadata |
| [SBOM, VEX, and attestations](references/sbom-vex-and-attestations.md) | CycloneDX, SPDX, VEX discovery, attestations, graph preservation, and SBOM metadata |
| [Secrets and filtering](references/secrets-and-filtering.md) | Secret inspection, detector rules, ignore semantics, scan exclusions, and result filtering |

## Breaking changes and migrations

### Replace provider-mapping `AVDID` with `ID`

Misconfiguration provider mappings use `ID` rather than `AVDID` (since
0.69.0). Update custom mappings and consumers before upgrading:

```yaml
# Old
AVDID: AVD-AWS-0001

# Current
ID: AVD-AWS-0001
```

Do not add a compatibility fallback that silently accepts both fields unless
the application intentionally supports versions on both sides of the change.
See [Misconfiguration and infrastructure as code](references/misconfiguration-and-iac.md).

### Migrate Docker configuration consumers to `dockers_v2`

The Docker configuration representation moved to `dockers_v2` (since 0.72.0).
Any integration coupled to the previous representation must migrate its
decoding, traversal, and tests. See
[Images, registries, and operating systems](references/images-registries-and-os.md).

### Account for the package-listing default

`--list-all-pkgs` defaults to `true` (since 0.67.0). Automation expecting the
older selective output must opt out explicitly:

```sh
trivy image --list-all-pkgs=false alpine:3.22
```

Expect package counts and downstream report processing to change when the flag
is not pinned.

### Stop passing filesystem skip flags to `sbom`

The `sbom` command disables `--skip-dir` and `--skip-files` (since 0.63.0).
Remove those flags from wrappers rather than assuming they still filter SBOM
inputs.

## High-value CLI and report behavior

### Select an OS or severity source explicitly

Use `--distro` when automatic operating-system detection is missing or
unsuitable (since 0.59.0). Use `--vuln-severity-source` to select the severity
authority (since 0.60.0):

```sh
trivy image --distro "<distribution>" alpine:3.20
trivy image --vuln-severity-source nvd alpine:3.20
```

### Treat reports as identifiable artifacts

Recent reports can carry a UUIDv7 `ReportID`, vulnerability fingerprints, the
image reference, Git repository metadata, and the producing Trivy version.
Scan targets expose an `ArtifactID` whose calculation includes registry and
repository. Persist these fields as identifiers instead of reconstructing them
from display strings.

Repository URLs are sanitized before entering reports, cache hits preserve
repository metadata, and repository scans require the repository-aware
`ROOTPATH` behavior in SARIF. See
[CLI, reports, and runtime](references/cli-reports-and-runtime.md).

### Validate client/server assumptions

Server values are schema-validated. HTTP tracing is available, server mode
sets up an HTTP transport, and client/server reports can include both Trivy and
server versions. Transport now preserves dependency relationships, repository
class, build information, check aliases, and query data where applicable.

If the client and server differ, test the serialized fields your integration
uses rather than assuming local-mode parity.

### Use concurrent database access deliberately

The vulnerability database supports concurrent access (since 0.68.0). If
database contents disappear while metadata remains, Trivy downloads the
database again instead of trusting the stale metadata (since 0.67.0).

## High-value analyzer changes

### Lockfile and workspace coverage

Dependency analysis understands Poetry v2, uv development and optional
dependencies, `bun.lock`, PEP 751 `pylock.toml`, multi-document pnpm lockfiles,
overlapping pnpm workspaces, Yarn workspace relationships, Cargo workspaces and
monorepos, and `.deps.json` dependency graphs. Do not flatten these inputs into
unrelated package lists; preserve root, workspace, relationship, and package-ID
information described in
[Dependencies and licenses](references/dependencies-and-licenses.md).

### Preserve package provenance and identity

Detected packages may expose `AnalyzedBy`. POM package IDs incorporate GAV
coordinates and the root-POM path, pnpm uses the snapshot string as
`Package.ID`, nested JARs have per-file digests, and an OS override also updates
OS-package PURLs. Consumers should treat these emitted identities as canonical.

### Follow Maven configuration

Java analysis can consume environment substitutions, repositories, proxies,
and mirrors from Maven `settings.xml`, plus configured mirrors from
`trivy.yaml`. HTTP 429 during remote POM resolution is fatal rather than a
partial success. Preserve dependency exclusions and inherited model data.

### Keep license expressions intact

License handling distinguishes SPDX identifiers from expressions, preserves
`WITH` exceptions as part of one license, supports compound expressions, and
uses canonical SPDX identifiers. Avoid splitting an expression into unrelated
licenses or normalizing literal `unlicensed` to `Unlicense`.

## High-value image and vulnerability behavior

### Recognize expanded operating-system coverage

Recent analyzers cover Bottlerocket, MinimOS, AlmaLinux 10, Root.io images,
Photon 5.0, CoreOS SBOMs, Ubuntu 26.04 LTS, RapidFort curated images, and other
new lifecycle and package cases. RHEL-derived images can be recognized through
`os-release`, while third-party Debian and Ubuntu packages are excluded from
distribution vulnerability matching.

### Preserve image origin information

Layer metadata is available to report consumers. Custom resources can be
attributed to their origin layer after layers are merged, Docker archives keep
`RepoTags`, and embedded-SBOM scans are deterministic. Image history handling
also normalizes legacy and non-BuildKit instruction forms.

### Handle missing or driver-owned vulnerability data

Packages covered by a detector driver's own advisory feed are no longer
skipped. When vulnerability details are unavailable, results use `UNKNOWN`
severity. Embedders using `ospkg.NewScanner` can expect detector options to be
forwarded.

## High-value IaC behavior

### Evaluate Terraform and OpenTofu with full context

Terraform evaluation handles module instances, block instances, map-based
`for_each`, unknown dynamic iteration, cached remote modules, plan schema
recovery, and filesystem-function traversal boundaries. OpenTofu-specific file
extensions, module detection, and `language` blocks are recognized.

### Apply ignores using current semantics

Inline ignores work for Dockerfiles and Helm content. Chart-subdirectory paths
are respected, ignore IDs are case-insensitive, and `.trivyignore` resolves
check aliases. An ignore-marker expression only applies when its value is both
known and non-null.

### Preserve Rego diagnostics

Embedders can inject a Rego scanner. Policies can consume raw Terraform data,
ignore findings by type, and use a configurable error limit. Diagnostic
snippets include map keys, and check metadata interprets boolean values as
booleans.

## High-value SBOM, VEX, and secret behavior

### Preserve SBOM structure

CycloneDX updates retain the source SBOM's structure, including applications,
OS packages, dependency graphs, file components, hashes, licenses, and build
metadata. SPDX handling tolerates documents without a root component and uses
`NOASSERTION` for non-library package license assertions.

### Discover VEX from supported locations

VEX can be referenced by CycloneDX, stored within the scanned repository, or
published as an OCI artifact through generic in-toto referrers. Apply
repository-specific TLS settings, reject non-local repository names where
required, and do not suppress vulnerabilities merely because a package graph
loops.

### Keep secret scanning transport-safe

Client/server analysis performs secret inspection. Secret inputs are validated
as UTF-8 before protobuf transport, multiline locations use corrected line
numbers, and configured skip folders, files, and extensions are honored. The
scanner excludes its own configuration file and supports newer cloud, Maven,
OpenAI API-key, and GitHub App token patterns.
