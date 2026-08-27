# Tooling and Operations

## Release, lockfile, cache, and crate boundaries (0.11.32)

uv is stable despite a `0.x` version. Minor releases may break behavior; patch
releases contain fixes, enhancements, and other intended non-breaking changes.
The public `uv.lock` schema changes only in a breaking minor release. Cache
versions are internal and may change in a minor or patch release.

The `uv`, `uv-build`, and `uv-version` crates follow CLI release numbering, but
the Rust interfaces of `uv` and `uv-build` do not promise semantic versioning.
Other uv crates have no stability guarantee, use `0.0.x`, and increment their
patch version on every uv release.

## Subprocess environment (0.6-0.8)

Every process launched by uv receives `UV` set to the uv executable path; any
existing value is overwritten.

Prefer `UV_WORKING_DIR` as the environment equivalent of `--directory`
(0.9-0.10).

At 0.12.5, `UV_RUN_RLIMIT_NOFILE` sets the open-file limit inherited by a
command launched through `uv run`.

```console
UV_RUN_RLIMIT_NOFILE=4096 uv run python app.py
```

## `uvx` command provenance (0.6-0.8)

`uvx <name>` errors unless the requested executable is provided by that
package or one of its dependencies, preventing execution of an unrelated
program on `PATH`. `uvx --from <package> <command>` intentionally skips the
same-name relationship.

## Ephemeral `uv run --with` layers (0.6-0.8)

`uv run --with` caches the environment containing requested requirements but
executes through a fresh empty environment layered over the cache. Runtime
inspection and mutation therefore target the ephemeral top layer, not the
cached requirement environment.

## Formatter orchestration

Preview `uv format` runs from the project root, respects `--project`, and
supports `--no-project` and unmanaged projects (0.6-0.8).

It accepts Ruff version constraints and `exclude-newer` (0.9-0.10). The
default moved to Ruff 0.15 and the 2026 style guide, which can change output.
Pin the earlier behavior when required:

```console
uv format --version 0.14.14
```

## Vulnerability and tool auditing

Preview `uv audit` appears in CLI help, batches OSV queries, and supports
linked findings plus output and report formatting (0.9-0.10).

At 0.12.5, preview `uv tool audit` audits one or all installed tools. Preview
malware checking can screen locked tools before cache reuse through
`audit.malware-check` and `audit.malware-check-url`.

```console
uv tool audit
```

## Machine-readable exports and sync results

`uv export` can emit CycloneDX SBOM data, while preview `uv sync` can report
package changes as JSON, including changes made by the operation (0.9-0.10).

At 0.12.5, CycloneDX exports include distribution artifact URLs and hashes by
default.

## Cache reporting (0.12.5)

`uv cache size --output-format` selects automatic, human-readable, or raw-byte
output for terminal or script use.

```console
uv cache size --output-format raw-byte
```

## Container images and tool installation

Derived uv images set `UV_TOOL_BIN_DIR=/usr/local/bin`, placing installed tools
on `PATH` (0.6-0.8). Override it for an unprivileged user that cannot write to
that directory.

Floating Debian and Alpine images moved to Debian 13 Trixie and Alpine 3.22
(0.9-0.10). The Bookworm, Alpine 3.21, and Python 3.8 tags are no longer
published. Prebuilt big-endian PPC64 binaries were removed; PPC64LE remains
supported.

## Uploads, certificates, proxies, and download mirrors (0.9-0.10)

Uploads honor `UV_UPLOAD_HTTP_TIMEOUT` and `UV_HTTP_TIMEOUT`. uv supports
`SSL_CERT_DIR`, and global or user configuration can set proxy variables.
Managed CPython and installer downloads use Astral-hosted mirrors by default,
which may require network allow-list changes.
