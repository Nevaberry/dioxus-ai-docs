# Images, Registries, and Operating Systems

## Docker configuration migration

Trivy's Docker configuration representation is `dockers_v2` (since 0.72.0).
This is a breaking change for embedders and consumers tied to the prior Docker
configuration structure. Update decoding, field access, fixtures, and tests as
one migration.

## Image acquisition and limits

### Registry mirrors and contexts

Container image acquisition supports registry mirrors (since 0.59.0). Image
resolution honors Docker contexts when locating an image to scan (since
0.65.0). AWS image access supports dual-stack ECR endpoints (since 0.68.0).

### Unsupported and oversized artifacts

An image whose total layer size exceeds the configured limit is rejected early
instead of being scanned further (since 0.59.0). Remote retrieval rejects
unsupported artifact types rather than treating them as container images
(since 0.64.0).

### Docker archives

Docker archive analysis preserves `RepoTags` (since 0.68.0).

## Image history, users, and layers

### Effective user

For image misconfiguration analysis, `.Config.User` takes precedence over
`USER` entries from `.History` when Trivy determines the effective user (since
0.64.0).

### Buildah and legacy Docker history

`CreatedBy` values from Buildah and the legacy Docker builder are normalized so
instruction-based checks behave consistently (since 0.64.0). Build-metadata
suffixes are removed from history, and legacy `ENV` values are quoted so spaces
remain part of the value (since 0.67.0).

`RUN` instructions are reconstructed correctly for images built without
BuildKit (since 0.71.0).

### Layer attribution

Image reports retain layer metadata (since 0.62.0). After image layers are
merged, analysis can identify the origin layer for custom resources (since
0.72.0).

### Embedded SBOMs

Images containing an embedded SBOM produce deterministic scan results (since
0.69.0).

## Distribution detection and manual overrides

### Explicit distribution selection

Use `--distro` when automatic distribution detection is unavailable or should
be overridden (since 0.59.0). Distribution aliases map to their corresponding
operating systems (since 0.60.0).

When the detected OS is overwritten, emitted OS-package PURLs are updated to
match the replacement OS (since 0.71.0).

### RHEL-family detection and behavior

RHEL-derived images can be detected from `os-release` data (since 0.67.0).
For the CentOS Stream family, unsupported vulnerability detection is skipped
without failing the overall scan (since 0.69.0).

### Lifecycle data

Lifecycle data includes end-of-life dates for RHEL 10, Ubuntu 25.04, and Ubuntu
20.04 ESM (since 0.64.0), plus Ubuntu 25.10 (since 0.70.0). OS detection
recognizes Ubuntu 26.04 LTS (since 0.71.0).

## APK-based operating systems

### Alpine and Wolfi metadata

APK analysis extracts the Alpine package maintainer field (since 0.63.0).
Wolfi scanning recognizes the newer APK database location.

### Bottlerocket and MinimOS

Trivy includes a Bottlerocket OS package analyzer and supports MinimOS (since
0.63.0). Bottlerocket packages can be matched against vulnerability data
(since 0.72.0).

## RPM-based operating systems

### AlmaLinux

OS scanning supports AlmaLinux 10, and the Alma `rpmqa` parser accepts
epoch-qualified package versions (since 0.65.0).

### Red Hat package metadata

Red Hat analysis searches the root layer for build information, retains
`contentSets` for OS packages in filesystem and VM scans, and removes invalid
suffixes from manifest `content_sets` (since 0.63.0).

SBOM scanning preserves Red Hat `BuildInfo` even when the SBOM lacks layer
information (since 0.70.0).

### Rocky Linux

Vulnerability scanning detects findings in Rocky Linux modular packages (since
0.69.0).

## Other image and OS families

### Root.io

Vulnerability scanning supports Root.io container images (since 0.64.0).
Package detection considers the full package version, and vulnerability output
uses corrected severity selection (since 0.65.0).

### ActiveState, Photon, and CoreOS

Vulnerability scanning supports ActiveState images (since 0.69.0) and Photon
5.0 (since 0.68.0). SBOM scanning supports CoreOS (since 0.67.0).

### RapidFort

Vulnerability scanning supports RapidFort curated images (since 0.74.0).

## OS package handling

### Duplicate packages

Duplicate `dpkg` packages discovered at distinct paths in different image
layers are consolidated (since 0.59.0).

### Third-party packages

Debian package classification uses a maintainer list to identify third-party
packages. Distribution vulnerability matching skips packages classified as
third-party on Debian and Ubuntu (since 0.69.0). The common vulnerability
detection path applies the same third-party-package exclusion (since 0.70.0).

### Packages from SBOM graphs

SBOM results merge OS packages found inside and outside the dependency graph
(since 0.65.0).

### Detector result fields and options

Azure and Mariner detectors populate detected-vulnerability fields (since
0.70.0). `ospkg.NewScanner` forwards detector options to OS package detectors
(since 0.72.0).

Packages backed by a detector driver's own advisory feed are not skipped (since
0.74.0). If vulnerability details are unavailable, results fall back to
`UNKNOWN` severity (since 0.72.0).
