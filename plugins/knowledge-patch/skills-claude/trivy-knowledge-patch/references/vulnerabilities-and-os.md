# Vulnerabilities and Operating Systems

Use this reference for severity selection, package matching and provenance, advisory filtering, OS detection and overrides, lifecycle data, and supported distributions.

## Detection and severity controls

### Manual OS distribution selection (0.59.0)

Use `--distro` to override automatic OS distribution detection when detection is missing or unsuitable.

### Vulnerability severity source selection (0.60.0)

Use `--vuln-severity-source` to select the source of vulnerability severities:

```sh
trivy image --vuln-severity-source nvd alpine:3.20
```

### OS aliases (0.60.0)

OS detection maps distribution aliases to their corresponding operating systems.

### Third-party package filtering (0.70.0)

The common vulnerability detection path skips packages identified as third-party.

### OS package detector options (0.72.0)

`ospkg.NewScanner` forwards detector options to the OS package detectors, allowing embedders to rely on those options.

### Missing vulnerability details (0.72.0)

When detail records are unavailable, vulnerability results use `UNKNOWN` severity.

### Driver-specific advisory coverage (0.74.0)

Packages covered by a detector driver's own advisory feed are no longer skipped.

## Distribution detection and lifecycle

### Bottlerocket and MinimOS coverage (0.63.0)

Trivy includes a Bottlerocket OS package analyzer and supports MinimOS.

### OS lifecycle data (0.64.0)

Lifecycle data includes EOL dates for RHEL 10, Ubuntu 25.04, and Ubuntu 20.04 ESM.

### AlmaLinux 10 and RPM epochs (0.65.0)

OS scanning supports AlmaLinux 10. AlmaLinux's `rpmqa` parser accepts epoch-qualified package versions.

### RHEL-derived image detection (0.67.0)

Trivy detects RHEL-derived images from `os-release` data.

### Photon 5.0 (0.68.0)

OS vulnerability scanning supports Photon 5.0.

### Ubuntu 25.10 lifecycle data (0.70.0)

OS lifecycle data includes Ubuntu 25.10 end-of-life information.

### Ubuntu 26.04 LTS (0.71.0)

OS detection recognizes Ubuntu 26.04 LTS.

### OS override package identities (0.71.0)

When the detected OS is overwritten, OS-package PURLs are updated to match the selected distribution.

## Package metadata and advisory matching

### Alpine package maintainers (0.63.0)

APK analysis extracts the maintainer field from Alpine packages.

### Red Hat package metadata (0.63.0)

Red Hat analysis searches the root layer for build information, retains `contentSets` for OS packages in filesystem and VM scans, and trims invalid suffixes from manifest `content_sets`.

### Wolfi APK databases (0.63.0)

Wolfi scanning supports the new APK database location.

### Root.io version and severity handling (0.65.0)

Root.io detection checks the full package version, and results use corrected severity selection.

### Case-insensitive NuGet matching (0.67.0)

Vulnerability analysis lowercases NuGet package names for matching.

### Debian and Ubuntu third-party packages (0.69.0)

Debian packages are classified as third-party using a maintainer list. Distribution vulnerability data is not applied to third-party packages on Debian or Ubuntu.

### Julia vulnerability scanning (0.69.0)

Julia packages are included in vulnerability matching in addition to package and relationship analysis.

### Rocky Linux modular packages (0.69.0)

Vulnerability scanning detects vulnerabilities in Rocky Linux modular packages.

### CentOS Stream vulnerability behavior (0.69.0)

For CentOS Stream, unsupported vulnerability detection is skipped without failing the overall scan.

### Azure and Mariner vulnerability fields (0.70.0)

Azure and Mariner detectors populate detected-vulnerability fields in their results.

### Bottlerocket vulnerability matching (0.72.0)

Packages from Bottlerocket OS can be matched against vulnerability data.
