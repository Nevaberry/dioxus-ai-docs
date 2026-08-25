# CLI, Reports, and Runtime

## CLI flags and configuration

### OS and severity selection

Vulnerability scans accept `--distro` to override automatic distribution
detection (since 0.59.0). They accept `--vuln-severity-source` to select the
source used for vulnerability severities (since 0.60.0).

```sh
trivy image --distro "<distribution>" alpine:3.20
trivy image --vuln-severity-source nvd alpine:3.20
```

### Generated configuration

`--generate-default-config` omits hidden flags from generated configuration
(since 0.59.0). Configuration-only options track whether the user supplied
them and do not treat their defaults as explicitly set values (since 0.68.0).

The `trivy.yaml` JSON Schema supports editor assistance and validation; enum
constraints for array values live on the schema's item definition (since
0.69.0).

### Package listing

`--list-all-pkgs` defaults to `true` (since 0.67.0). Pin it to `false` if an
integration depends on selective package output:

```sh
trivy image --list-all-pkgs=false alpine:3.22
```

### Cloud scans and custom certificate authorities

The CLI supports `trivy cloud` and the `--cacert` option for supplying a CA
certificate (since 0.68.0).

### Compliance and templates

`--compliance` is not restricted to a predefined allowed-values list (since
0.63.0). Flag validation checks template file extensions and rejects invalid
template files (since 0.70.0).

### Available versions

The CLI can check for available Trivy versions (since 0.63.0).

## Registry, plugin, and database runtime

### Registry authentication

Authenticated GHCR artifact downloads honor `GITHUB_TOKEN` (since 0.59.0).
`trivy registry login` authenticates without requesting a registry scope
(since 0.60.0).

### Plugin index updates

Updating `index.yaml` preserves its existing plugins rather than removing them
(since 0.66.0).

### Database recovery and concurrency

If database contents are absent but metadata remains, Trivy downloads the
database again instead of treating the metadata as a valid cache (since
0.67.0). The vulnerability database supports concurrent access by multiple
scan operations (since 0.68.0).

## Process and server behavior

### Graceful termination

Trivy handles termination signals with graceful shutdown. It does not print a
graceful-shutdown message after a normal exit (since 0.65.0).

### HTTP transport and tracing

HTTP request and response tracing is supported, and server mode initializes an
HTTP transport (since 0.65.0). `--server` values are schema-validated, so an
invalid value fails flag validation rather than surfacing later.

### Client/server version metadata

JSON reports from client/server mode include the server version (since
0.70.0). The server `/version` response omits JavaDB and CheckBundle entries.

Transport preserves these data when relevant:

- Dependency `Relationship` fields (since 0.63.0).
- SBOM build information in `BlobInfo` (since 0.68.0).
- Each package's repository class (since 0.72.0).
- Check aliases and query data for uploaded blobs (since 0.74.0).

### Runtime framework support

Trivy supports Echo (since 0.63.0).

### WebAssembly builds

WebAssembly modules use standard Go instead of TinyGo (since 0.61.0). Build
automation for those modules must provide the standard Go compiler.

## Scan execution

### Static filesystem paths

Filesystem scans invoke post-analyzers for static paths. `--file-patterns`
applies to every post-analyzer, not only a subset (since 0.61.0).

### Kubernetes scans

Kubernetes scanning supports controllers, and `--report all` produces the
requested complete report (since 0.61.0). Artifact version comparison is
correct and scanning no longer relies on the `last-applied-configuration`
annotation (since 0.62.0). Kubernetes summary reports omit passed
misconfigurations.

## Report content and identity

### Summary tables

Reports can include a summary table for an at-a-glance result view (since
0.60.0).

### Stable identifiers

Scan targets expose a unique `ArtifactID`; its calculation includes the
registry and repository (since 0.68.0). Reports expose a UUIDv7 `ReportID`, add
fingerprints to vulnerability findings, and carry the image reference in
report metadata.

### Producing version

JSON report output includes the Trivy version that produced it (since 0.69.0).
In client/server mode, JSON output also includes the server version as
described above.

### Git repository metadata

Repository scans include Git repository metadata in reports (since 0.65.0).
The repository URL is sanitized before storage, and filesystem report cache
hits preserve `RepoMetadata` (since 0.66.0).

When Git information is present, a filesystem artifact is classified as a
repository, changing the artifact type visible to report consumers (since
0.68.0).

### Image and layer metadata

Image scans store layer metadata in reports for downstream consumers (since
0.62.0). Report metadata also carries the image reference as part of the
stable-identity changes in 0.68.0.

## Report formats and templates

### SARIF

SARIF `shortDescription` and `fullDescription` text is not HTML-escaped (since
0.60.0). Vulnerability findings include CVSS vectors (since 0.65.0). For a Git
repository scan, SARIF uses the correct `ROOTPATH` URI (since 0.70.0).

### JUnit

The JUnit template includes source locations for misconfiguration findings
(since 0.63.0).

### GitLab template

The `gitlab.tpl` template produces valid link arrays without a trailing comma
(since 0.71.0).
