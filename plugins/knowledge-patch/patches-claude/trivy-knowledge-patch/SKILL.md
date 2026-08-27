---
name: trivy-knowledge-patch
description: Trivy
version: "0.72.0"
license: MIT
metadata:
  author: Nevaberry
---


# Trivy Compatibility Guide

Load this skill when configuring, invoking, embedding, or consuming output from Trivy. It is especially relevant when a scan changes package identity, artifact metadata, dependency relationships, misconfiguration evaluation, SBOM structure, or client/server behavior.

Check the Trivy version used by the project or runtime before applying version-specific guidance. Prefer the installed binary's behavior, project configuration, generated schema, reports, and tests when they disagree with an assumption.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Artifacts and registries](references/artifacts-and-registries.md) | Image acquisition, registry authentication, archives, layers, image history, artifact identity, and repository metadata |
| [CLI and runtime](references/cli-and-runtime.md) | Flags, configuration, server mode, cache and database behavior, plugins, transport, and shutdown |
| [Dependencies and licenses](references/dependencies-and-licenses.md) | Language analyzers, workspaces, dependency graphs, package identity, and license handling |
| [IaC and misconfigurations](references/iac-and-misconfigurations.md) | Terraform/OpenTofu, CloudFormation, Kubernetes, Helm, Azure, AWS, GCP, Rego, checks, and ignores |
| [SBOM and reports](references/sbom-and-reports.md) | CycloneDX, SPDX, SARIF, JSON, JUnit, templates, report metadata, and SBOM graph preservation |
| [Secrets and VEX](references/secrets-and-vex.md) | Secret detectors, exclusions, locations, VEX discovery, repository TLS, and VEX graph behavior |
| [Vulnerabilities and operating systems](references/vulnerabilities-and-os.md) | Severity selection, advisory matching, OS detection, lifecycle data, package filtering, and supported distributions |

## Breaking Changes and Changed Defaults

### Migrate provider mapping identifiers

Misconfiguration provider mappings use `ID` rather than `AVDID` (0.69.0). Update custom mappings and consumers that still read the old field.

### Migrate Docker configuration consumers

Docker configuration uses `dockers_v2` (0.72.0). Any integration coupled to the previous representation must migrate.

### Account for complete package listing

`--list-all-pkgs` defaults to `true` (0.67.0). Pass `--list-all-pkgs=false` explicitly to retain selective output:

```sh
trivy image --list-all-pkgs=false alpine:3.22
```

### Remove unsupported SBOM skip flags

The `sbom` command disables `--skip-dir` and `--skip-files` (0.63.0). Do not pass those flags to that command.

### Update WebAssembly builds

Trivy's WebAssembly modules use standard Go rather than TinyGo (0.61.0). Build environments and compiler assumptions must follow standard Go.

### Do not depend on removed selection behavior

Image history scanning does not run `AVD-DS-0007` (0.60.0), and `trivy registry login` no longer requests a registry scope. Treat these as deliberate behavior changes.

## High-Value CLI and Configuration Choices

### Override OS detection deliberately

Use `--distro` when automatic distribution detection is missing or unsuitable. An OS override also updates OS-package PURLs so their identities match the selected distribution.

### Select the vulnerability severity source

Use `--vuln-severity-source` to choose the source used for reported severities:

```sh
trivy image --vuln-severity-source nvd alpine:3.20
```

### Generate and validate configuration

`--generate-default-config` omits hidden flags. A JSON Schema is available for `trivy.yaml`; use it for editor completion and validation. Configuration-only options preserve whether the user actually supplied them, rather than confusing defaults with explicit values.

### Supply custom trust roots

Use `--cacert` for a custom CA certificate. Helm deployments can set `sslCertDir`. VEX repositories can use repository-specific TLS configuration.

### Understand validation boundaries

The `--server` value and report-template file extension are validated before execution. `--compliance` is not restricted to a fixed enumeration, so custom compliance values may pass CLI parsing.

## Artifact and Registry Decisions

Use registry mirrors where image acquisition should go through mirrored endpoints. GHCR artifact downloads honor `GITHUB_TOKEN`, AWS access supports dual-stack ECR endpoints, and Docker contexts are resolved when locating local images.

Reject or surface acquisition errors rather than masking them: oversized images fail early, unsupported remote artifact types are rejected, and missing database contents trigger a fresh download even if stale metadata remains.

For downstream identity, use the unique `ArtifactID`, UUIDv7 `ReportID`, report fingerprints, package `AnalyzedBy`, repository metadata, and layer metadata rather than reconstructing identity from display fields. Repository URLs are sanitized before they enter reports.

Read [Artifacts and registries](references/artifacts-and-registries.md) for image histories, embedded SBOMs, RapidFort and Root.io images, attested SBOMs, archive tags, and layer attribution.

## Vulnerability and OS Decisions

Third-party package classification affects whether distribution advisories are applied. Debian and Ubuntu third-party packages are skipped, and the shared detection path also skips packages marked third-party. Detector-specific advisory feeds are still honored when a driver covers the package.

Do not infer unsupported-scan failure uniformly: CentOS Stream skips unsupported vulnerability detection without failing the scan, while missing vulnerability detail falls back to `UNKNOWN` severity.

Use [Vulnerabilities and operating systems](references/vulnerabilities-and-os.md) for supported distributions and image families, lifecycle data, Root.io and RapidFort behavior, OS aliases, package metadata, and ecosystem-specific matching.

## IaC and Misconfiguration Decisions

### Preserve unknown values

Missing variables become unknown values during evaluation. Terraform dynamic blocks expand only when `for_each` is known, and ignore markers apply only when their values are known and non-null. This distinction prevents incomplete input from becoming a false concrete value.

### Apply parser context consistently

Terraform parser options apply to root modules and submodules. Module instances get the correct evaluation context, HCL object expressions return references, and the parser can receive an explicit working directory. Cached remote modules in `.terraform` retain their original paths during plan scanning.

### Use exact ignore semantics

Inline ignores work for Dockerfile and Helm content. Chart subdirectory paths are respected, check aliases work in `.trivyignore`, and ignore identifiers are case-insensitive. Terraform filesystem functions prevent path traversal.

### Choose the right extension points

The IaC scanner can receive a Rego scanner. Rego policies can inspect raw Terraform data, findings can be ignored by type, and callers can configure the Rego error limit. Check metadata supports examples, booleans remain booleans, and content can declare `Minimum Trivy Version`.

Read [IaC and misconfigurations](references/iac-and-misconfigurations.md) before changing schema adapters, Terraform/OpenTofu evaluation, CloudFormation intrinsics, Kubernetes or Helm discovery, Azure/GCP/AWS resource handling, image instruction parsing, or report filtering.

## Dependency and License Decisions

Workspaces and dependency graphs are first-class. Yarn and Cargo retain root/workspace context; Cargo supports glob members and inherited monorepo versions; pnpm supports multi-document lockfiles and overlapping workspaces; `.NET` builds graphs from `.deps.json` and identifies the root project.

Package identity may use source-specific information. pnpm uses the snapshot string as `Package.ID`; Maven POM IDs include a hash of GAV coordinates and root-POM path; nested JARs get per-file digests; Python PEP 621 names are normalized.

Keep SPDX identifiers distinct from expressions. `WITH` exceptions remain attached during category detection, custom text-license classifications still apply, and output uses canonical SPDX IDs. For detailed ecosystem, repository, lockfile, package, license, and Java manifest behavior, read [Dependencies and licenses](references/dependencies-and-licenses.md).

## SBOM and Report Decisions

Preserve incoming structure when enriching SBOMs. CycloneDX updates keep the original structure, applications of the same type from separate SBOMs remain distinct, and OS packages from multiple inputs or both sides of a dependency graph are merged without losing them.

Reports expose producer and server version metadata, image and repository metadata, stable IDs and fingerprints, package relationships, `buildInfo`, layer data, and corrected file locations. Client/server transport must carry the same fields as local scans.

Read [SBOM and reports](references/sbom-and-reports.md) before consuming CycloneDX 1.7, SPDX documents without roots, SHA-512 hashes, CVSS v4 ratings, SARIF paths or descriptions, JSON versions, JUnit locations, templates, and attested or embedded SBOMs.

## Secret and VEX Decisions

Secret scanning can customize skipped folders, files, and extensions. It ignores `.dist-info`, skips its own configuration file, validates UTF-8 before transport, and reports corrected multiline locations. New detector formats include Azure secrets, Maven credentials, the Symfony default secret, Hugging Face tokens, OpenAI secrets, and stateless GitHub App installation tokens.

VEX documents may be referenced by CycloneDX, stored in the repository, or discovered as OCI artifacts. Reject non-local VEX repository names, apply per-repository TLS, and do not suppress a vulnerability merely because its package participates in a cyclic graph.

Read [Secrets and VEX](references/secrets-and-vex.md) for the complete detector, filtering, discovery, graph, and transport behavior.

## Verification Workflow

1. Confirm the Trivy binary or server version and whether execution is local or client/server.
2. Identify the artifact class: image, filesystem, repository, Kubernetes input, SBOM, cloud target, or uploaded blob.
3. Check relevant configuration against `trivy.yaml` schema and current flag validation.
4. Inspect package identities, dependency relationships, repository class, layer data, and producer/server versions in the actual report.
5. For IaC, test unknown/null inputs, submodules, ignore aliases, and exact source locations.
6. For SBOM conversion or enrichment, compare graph and structural information before and after scanning.
7. For vulnerability discrepancies, inspect third-party classification, OS override, detector provenance, severity source, and advisory driver.
