# Dependency Resolution and Lockfiles

Use this reference for dependency declarations, constraints, source handling,
release cutoffs, lock verification, and standardized lockfile inputs.

## Upgrade and Add Operations

### Upgrade marker-specific declarations

As of 0.11.32, preview `uv upgrade` can update multiple declarations of the
same package when environment markers distinguish those declarations.

### Supply constraints, markers, groups, and overrides

In the 0.6-0.8 batch, CLI dependency inputs expanded:

- `uv add` accepts `--marker` and `-c` constraints.
- `uv pip install` and `uv pip compile` accept pip-compatible `--group`.
- `uvx` accepts `--constraints` and `--overrides`.

`uv add --bounds` and the `add-bounds` configuration setting are stable
controls for the constraints uv writes. Bounds also apply when adding
dependencies to inline scripts.

## Build Constraints and Coverage

Constrain build dependencies with
`tool.uv.build-constraint-dependencies`. These constraints apply during sync
and are also supported for `uv run --with`, tool workflows, and PEP 723
scripts.

Use `tool.uv.required-environments` when resolution must provide wheel coverage
for particular target environments. Group-level Python restrictions belong in
`[tool.uv.dependency-groups].<group>.requires-python`, while
`default-groups = "all"` enables all groups by default.

## Exclusions and Source Overrides

The `exclude-dependencies` setting removes named transitive dependencies from
resolution. Exclusions also apply in scripts and tool upgrades.

```toml
[tool.uv]
exclude-dependencies = ["unwanted-package"]
```

Use `--no-sources-package <name>` to ignore `[tool.uv.sources]` overrides for
selected packages without disabling every source override.

## Release Cutoffs

`exclude-newer-package` assigns a package-specific cutoff instead of one date
for the whole resolution.

Across the 0.9-0.10 batch, `exclude-newer` also accepts relative-duration
cooldowns, and individual packages can opt out of the cutoff. Changing a
cutoff retains locked versions that still satisfy it. Add `--upgrade` or
`--upgrade-package` when a version refresh is intended.

## Lockfile Verification and Mutation

### Enforce canonical formatting

At 0.11.32, `uv lock --check` and commands using `--locked` reject a
non-canonically formatted lockfile. `uv lock --refresh` regenerates it in
canonical form.

### Preserve CI exit-code meaning

`uv sync --check` verifies environment freshness. An outdated environment or
lockfile makes `uv sync --check` or `uv lock --check` exit with status 1.
Status 2 remains an error. CI should distinguish stale state from an
operational failure.

### Keep isolated operations separate

Commands using `--isolated` do not update `uv.lock`; temporary isolated work
therefore remains separate from project lock state.

## PEP 751 `pylock.toml`

uv can generate, export, install, and sync standardized PEP 751 lockfiles:

```console
uv export -o pylock.toml
uv pip compile -o pylock.toml requirements.in
uv pip sync pylock.toml
uv pip install -r pylock.toml
```

A custom filename must have the form `pylock.<name>.toml`. Arbitrary TOML
files are rejected instead of being interpreted as requirements files.

## Remote and Script Inputs

Requirement loading supports extensionless scripts containing inline metadata
and scripts at HTTP or HTTPS paths. `pylock.toml` inputs may also be remote.
Git dependency sources expose an LFS toggle through `UV_GIT_LFS`.
