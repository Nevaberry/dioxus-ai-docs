# CLI and Runtime

Use this reference for CLI behavior, configuration generation and validation, filesystem and cloud scans, server mode, databases, plugins, transport, and process lifecycle.

## Configuration and flag behavior

### Generated default configuration (0.59.0)

`--generate-default-config` omits hidden flags from the generated configuration.

### Compliance values (0.63.0)

The CLI does not constrain `--compliance` to a predefined allowed-values list.

### Server flag validation (0.65.0)

The `--server` flag is schema-validated, so invalid values fail flag validation.

### Package listing default (0.67.0)

`--list-all-pkgs` defaults to `true`. Set it explicitly to `false` for the previous selective package output:

```sh
trivy image --list-all-pkgs=false alpine:3.22
```

### Configuration-only flags (0.68.0)

Configuration-only options track whether the user supplied them; default values are not treated as explicitly set.

### `trivy.yaml` JSON Schema (0.69.0)

A JSON Schema is available for `trivy.yaml`. Use it for editor support and configuration validation. For array-valued enums, the enum is defined on the schema's item definition.

### Template file validation (0.70.0)

Flag validation checks report-template file extensions and rejects invalid template files.

## Commands and scan targets

### Static-path filesystem analysis (0.61.0)

Filesystem scans run post-analyzers for static paths. `--file-patterns` applies to every post-analyzer rather than a subset.

### Available-version checks (0.63.0)

The CLI can check whether a newer Trivy version is available.

### SBOM skip flags (0.63.0)

The `sbom` command disables `--skip-dir` and `--skip-files`. Callers must not supply those flags to this command.

### Echo support (0.63.0)

Trivy includes Echo support. Integrations using Echo do not need to treat it as unsupported.

### Cloud scans and custom CAs (0.68.0)

Use `trivy cloud` for cloud scans. Use `--cacert` to provide a custom CA certificate.

## Process and server lifecycle

### Graceful shutdown (0.65.0)

Termination signals trigger graceful shutdown. A normal exit does not emit the graceful-shutdown message.

### HTTP tracing and server transport (0.65.0)

HTTP request and response tracing is supported. Server mode establishes an HTTP transport.

### Concurrent vulnerability database access (0.68.0)

The vulnerability database supports concurrent access by multiple scan operations.

### Client/server version metadata (0.70.0)

JSON reports produced in client/server mode include the server version. The server `/version` response omits JavaDB and CheckBundle entries.

### Uploaded server metadata (0.74.0)

Uploaded blobs preserve check aliases and query data, so client/server scans retain this metadata.

## Plugin and output-runtime details

### Plugin index updates (0.66.0)

Updating `index.yaml` preserves existing plugins rather than deleting them.

### Trivy version in JSON reports (0.69.0)

JSON report output includes the producing Trivy version.

### Valid GitLab template link arrays (0.71.0)

The `gitlab.tpl` report template does not emit a trailing comma in link arrays.
