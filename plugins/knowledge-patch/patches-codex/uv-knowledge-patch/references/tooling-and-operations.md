# Tooling and Operations

Use this reference for release compatibility, subprocess behavior, `uvx`,
ephemeral runs, formatting, audits, exports, caches, and runtime controls.

## Release and API Boundaries

### Treat uv's release scheme as stable but non-semantic

uv is stable despite its `0.x` version. Minor releases may contain breaking
changes, while patch releases contain fixes, enhancements, and other intended
non-breaking changes. The public `uv.lock` schema changes only in a breaking
minor release, but internal cache formats may change in either a minor or
patch release. (Since `0.11.32`.)

### Distinguish Rust crate release numbers from API stability

The `uv`, `uv-build`, and `uv-version` crates follow the CLI's release
numbering. The Rust interfaces of `uv` and `uv-build` do not promise semantic
versioning. Other uv crates have no stability guarantee, use `0.0.x`, and
increment their patch version on every uv release. (Since `0.11.32`.)

## Subprocess and Tool Execution

### Read the invoking uv executable from `UV`

uv sets `UV` to its own executable path in every subprocess it launches and
overwrites any previous value. Child processes should treat it as the uv
executable path, not as caller-owned application configuration. (Batch
`0.6-0.8`.)

### Verify `uvx` command provenance

`uvx <name>` errors unless the named package or one of its dependencies
provides the requested executable, preventing an unrelated command on `PATH`
from running. Use `uvx --from <package> <command>` when the package and command
names intentionally differ. (Batch `0.6-0.8`.)

### Account for the ephemeral top layer

`uv run --with` caches the environment containing requested requirements but
executes through a fresh empty environment layered over that cache. Runtime
inspection or mutation no longer operates directly on the cached layer.
(Batch `0.6-0.8`.)

### Set the child open-file limit

`UV_RUN_RLIMIT_NOFILE` controls the open-file resource limit inherited by
commands launched through `uv run`. (Since `0.12.5`.)

```console
UV_RUN_RLIMIT_NOFILE=4096 uv run python app.py
```

### Use the preferred working-directory variable

Use `UV_WORKING_DIR` as the environment equivalent of `--directory`. (Batch
`0.9-0.10`.)

## Formatting and Auditing

### Run preview formatting from the project root

Preview `uv format` runs from the project root, respects `--project`, and
supports `--no-project` or unmanaged projects. (Batch `0.6-0.8`.)

It accepts Ruff version constraints and `exclude-newer`. The default moved to
Ruff 0.15 and the 2026 style guide, which can alter formatting; pin earlier
behavior with `uv format --version 0.14.14` when required. (Batch
`0.9-0.10`.)

### Audit projects and installed tools

Preview `uv audit` appears in CLI help, queries OSV in batches, and supports
linked findings plus output and report formatting. (Batch `0.9-0.10`.)

Preview `uv tool audit` audits one or all installed tools. Preview malware
screening can check locked tools before cache reuse through
`audit.malware-check` and `audit.malware-check-url`. (Since `0.12.5`.)

## Machine-Readable Output

### Export SBOM and sync changes

`uv export` can produce CycloneDX SBOM data. Preview `uv sync` output can
summarize package changes as JSON, including changes made by the operation.
(Batch `0.9-0.10`.)

CycloneDX exports include distribution artifact URLs and hashes by default.
(Since `0.12.5`.)

### Select cache-size output

`uv cache size --output-format` selects automatic, human-readable, or raw-byte
output for terminal or script consumption. (Since `0.12.5`.)

```console
uv cache size --output-format raw-byte
```

## Operational Checklist

- Confirm whether every formatter, audit, sync-output, tool-audit, malware,
  or other preview feature is acceptable for the workflow.
- Pin formatter and image behavior when output reproducibility matters.
- Keep subprocess assumptions compatible with uv's `UV` overwrite and the
  fresh `uv run --with` top layer.
- Treat cache formats as internal and avoid cross-version cache contracts.
- Validate SBOM provenance fields and JSON output before downstream parsing.
