# Dependency Resolution and Lockfiles

## Strict request and group validation (0.6-0.8)

uv errors for nonexistent local extras, dependency groups absent from a frozen
lockfile, and unknown dependency-group object specifiers. `--frozen` conflicts
with `--no-sources`.

## Build constraints and CLI inputs (0.6-0.8)

Declare build-time constraints with `tool.uv.build-constraint-dependencies`.
They apply during sync and to ephemeral `uv run --with` environments, tools,
and PEP 723 scripts.

`uv add` accepts `--marker` and `-c` constraints. `uv pip install` and
`uv pip compile` accept pip-compatible `--group`, while `uvx` accepts
`--constraints` and `--overrides`.

## Dependency-group coverage (0.6-0.8)

`default-groups = "all"` enables every group by default.
`[tool.uv.dependency-groups].<group>.requires-python` limits a group by Python
version. `tool.uv.required-environments` makes selected target environments
mandatory for wheel coverage.

## Dependency exclusions and source suppression (0.9-0.10)

`exclude-dependencies` removes named transitive dependencies from resolution;
the exclusions also apply to scripts and tool upgrades.

```toml
[tool.uv]
exclude-dependencies = ["unwanted-package"]
```

Use `--no-sources-package <name>` to ignore `[tool.uv.sources]` for selected
packages while preserving other source overrides.

## Bounds and release cutoffs

`exclude-newer-package` gives individual packages their own release cutoff
(0.6-0.8).

`uv add --bounds` and `add-bounds` are stable controls for constraints written
by `uv add`, including dependencies added to inline scripts (0.9-0.10).

`exclude-newer` accepts relative-duration cooldowns, and packages can opt out
of the cutoff (0.9-0.10). Changing a cutoff retains locked versions that still
satisfy it; use `--upgrade` or `--upgrade-package` to refresh versions.

## Marker-aware upgrades (0.11.32)

Preview `uv upgrade` can update multiple declarations of one package when
environment markers distinguish those declarations.

## Prerelease resolution (0.12.5)

The default `if-necessary` policy tries stable candidates first, then permits
prereleases if no stable candidate satisfies active constraints, including
constraints discovered transitively. Override it with `--prerelease disallow`,
`allow`, or `explicit`. `if-necessary-or-explicit` is a deprecated alias, and
`--prerelease-package` sets package-specific policies.

## Canonical `uv.lock` checks

`uv lock --check` and commands using `--locked` reject non-canonical lockfile
formatting; `uv lock --refresh` regenerates canonical output (0.11.32).

`uv sync --check` verifies environment freshness (0.6-0.8). A stale lockfile
or environment gives `uv lock --check` or `uv sync --check` exit status 1;
status 2 is an operational error.

Commands using `--isolated` do not update `uv.lock` (0.6-0.8).

## PEP 751 workflows and validation

uv can generate, export, install, and sync PEP 751 lockfiles (0.6-0.8).
Custom filenames must be `pylock.<name>.toml`; arbitrary TOML files are not
treated as requirements files.

```console
uv export -o pylock.toml
uv pip compile -o pylock.toml requirements.in
uv pip sync pylock.toml
uv pip install -r pylock.toml
```

At 0.12.5, a PEP 751 file must contain a `packages` array, although
`packages = []` is valid. Its name must be `pylock.toml` or a single-name
variant such as `pylock.dev.toml`. Declared artifact sizes are verified against
downloaded or cached artifacts.

## Requirements-file hash checking (0.12.5)

For `uv pip install` and `uv pip sync`, a `--require-hashes` directive inside a
requirements file enables hash-checking mode. Every requirement must be pinned
and hashed, and MD5 alone is insufficient; include a secure digest such as
SHA-256.

```text
--require-hashes
anyio==4.0.0 --hash=sha256:<digest>
```

## Remote and script inputs (0.9-0.10)

Requirement loading accepts extensionless scripts with inline metadata and
scripts at HTTP(S) paths. `pylock.toml` inputs may be remote. Git sources expose
an LFS toggle through `UV_GIT_LFS`.
