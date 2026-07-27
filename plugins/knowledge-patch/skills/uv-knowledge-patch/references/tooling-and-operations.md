# Tooling and Operations

Use this reference for release compatibility, process behavior, command
provenance, formatting, auditing, machine-readable results, containers, and
network configuration.

## Release and Stability Boundaries

uv is stable despite its `0.x` version. Under the custom release scheme,
minor releases may contain breaking changes, while patch releases contain
fixes, enhancements, and other non-breaking changes.

The public `uv.lock` schema changes only in a breaking minor release. Cache
versions are internal and may change in a minor or patch release. This
distinction is explicit at 0.11.32: lockfiles are an interoperability surface;
caches are not.

The `uv`, `uv-build`, and `uv-version` Rust crates follow the CLI release
version. The Rust interfaces of `uv` and `uv-build` do not follow semantic
versioning. Other uv crates have no stability guarantee, use `0.0.x`, and
increment their patch version on every uv release.

## Process Environment and Command Provenance

### Locate the invoking uv executable

Since the 0.6-0.8 batch, uv sets `UV` to its own executable path in every
subprocess it launches, overwriting an existing value. Child processes should
treat `UV` as the path of the invoking uv, not as user-preserved input.

### Verify executables launched through `uvx`

`uvx <name>` errors unless the requested executable is supplied by the named
package or one of its dependencies. This prevents an unrelated executable on
`PATH` from being launched. The provenance check is intentionally skipped
when package and command are separated explicitly:

```console
uvx --from <package> <command>
```

## Checking, Formatting, and Auditing

### Select packages for `uv check`

At 0.11.32, preview `uv check` supports one package or every workspace package:

```console
uv check --package my-package
uv check --all-packages
```

### Run the preview formatter predictably

`uv format` runs from the project root, honors `--project`, and supports
`--no-project` or unmanaged projects.

Across the 0.9-0.10 batch, it gained Ruff version constraints and
`exclude-newer`. Its default moved to Ruff 0.15 and the 2026 style guide, which
can change formatting. Pin the earlier behavior when required:

```console
uv format --version 0.14.14
```

### Audit dependencies

Preview `uv audit` appears in CLI help, queries OSV in batches, and supports
linked findings plus output and report formatting.

## Machine-Readable Operations

`uv export` can produce CycloneDX SBOM data. Preview `uv sync` output can
summarize package changes as JSON, including changes made by the operation.

Use these formats for automation rather than parsing human-oriented output,
while retaining a preview-status guard for sync JSON.

## Containers and Installed Tools

Derived uv Docker images set `UV_TOOL_BIN_DIR=/usr/local/bin`, so executables
from `uv tool install` are on `PATH`. Override the variable for an unprivileged
image user that cannot write to `/usr/local/bin`.

In the 0.9-0.10 batch, floating Debian and Alpine images moved to Debian 13
Trixie and Alpine 3.22. Version 0.10 stopped publishing Bookworm, Alpine 3.21,
and Python 3.8 image tags. Prebuilt big-endian PPC64 binaries were also
removed; PPC64LE remains supported.

## Working Directory, Network, and Mirrors

Prefer `UV_WORKING_DIR` as the environment equivalent of `--directory`.

- Uploads honor `UV_UPLOAD_HTTP_TIMEOUT` and `UV_HTTP_TIMEOUT`.
- uv supports `SSL_CERT_DIR`.
- Proxy variables may be set in global or user configuration.
- Managed CPython and installer downloads use Astral-hosted mirrors by
  default in 0.10, which can require firewall or allow-list changes.
