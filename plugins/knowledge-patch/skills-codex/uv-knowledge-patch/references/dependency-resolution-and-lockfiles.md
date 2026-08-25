# Dependency Resolution and Lockfiles

Use this reference for resolver policy, constraints, source controls,
dependency groups, requirement inputs, uv lockfiles, and PEP 751 workflows.

## Resolver Policy and Candidate Selection

### Control automatic pre-release fallback

The default `if-necessary` policy first tries stable candidates, then permits
pre-releases when no stable candidate satisfies active constraints. This
includes constraints discovered transitively. Override with `--prerelease
disallow`, `allow`, or `explicit`; `if-necessary-or-explicit` is a deprecated
alias. `--prerelease-package` sets package-specific policies. (Since
`0.12.5`.)

### Exclude unwanted transitive dependencies

`exclude-dependencies` removes named transitive dependencies from resolution;
the exclusions also apply to scripts and tool upgrades. Use
`--no-sources-package <name>` to ignore selected `[tool.uv.sources]` entries
without disabling every source override. (Batch `0.9-0.10`.)

```toml
[tool.uv]
exclude-dependencies = ["unwanted-package"]
```

### Write dependency bounds deliberately

`uv add --bounds` and `add-bounds` are stable controls for the constraints uv
writes. Bounds also apply when adding dependencies to inline scripts. (Batch
`0.9-0.10`.)

### Use marker-aware upgrades

Preview `uv upgrade` can update multiple declarations of the same package
when environment markers distinguish those declarations. Review every marker
branch after the operation. (Since `0.11.32`.)

## Constraints, Groups, and Coverage

### Constrain build dependencies across workflows

`tool.uv.build-constraint-dependencies` constrains build-time dependencies
during sync and in `uv run --with`, tools, and PEP 723 script workflows.
(Batch `0.6-0.8`.)

### Pass dependency inputs through CLI workflows

`uv add` accepts `--marker` and `-c` constraints. `uv pip install` and
`uv pip compile` accept pip-compatible `--group`, while `uvx` accepts
`--constraints` and `--overrides`. (Batch `0.6-0.8`.)

### Define group defaults and Python applicability

`default-groups = "all"` enables every dependency group by default.
`[tool.uv.dependency-groups].<group>.requires-python` limits an individual
group by Python version. `tool.uv.required-environments` marks target
environments as mandatory for wheel coverage. (Batch `0.6-0.8`.)

### Validate groups, extras, and source flags

uv errors for nonexistent local extras, dependency groups absent from a
frozen lockfile, and unknown dependency-group object specifiers. `--frozen`
and `--no-sources` conflict and must not be combined. (Batch `0.6-0.8`.)

Workspace-root groups can be addressed from a member, but syncing or exporting
a selected member does not include root default groups unless explicitly
requested. (Since `0.12.5`.)

## Release Cutoffs

### Set package-specific cutoffs

`exclude-newer-package` gives individual packages their own release cutoff
instead of applying one date to the entire resolution. (Batch `0.6-0.8`.)

### Use cooldowns without forcing upgrades

`exclude-newer` accepts relative-duration cooldowns, and individual packages
can opt out. Changing a cutoff retains locked versions that still satisfy it;
pass `--upgrade` or `--upgrade-package` when refresh is intended. (Batch
`0.9-0.10`.)

## uv.lock Integrity and Compatibility

### Enforce canonical formatting

`uv lock --check` and commands using `--locked` reject a non-canonically
formatted lockfile. `uv lock --refresh` regenerates canonical formatting.
(Since `0.11.32`.)

### Preserve isolated project state

Commands using `--isolated` do not update `uv.lock`; temporary isolated work
stays separate from project state. (Batch `0.6-0.8`.)

### Interpret lock and environment check statuses

`uv sync --check` verifies environment freshness. An outdated environment or
lockfile makes `uv sync --check` or `uv lock --check` exit with status 1;
status 2 remains an operational error. Preserve the distinction in CI. (Batch
`0.6-0.8`.)

### Respect schema and cache stability boundaries

uv is stable even with `0.x` numbering: a minor release may contain breaking
changes, while patch releases are intended for fixes, enhancements, and other
non-breaking changes. The public `uv.lock` schema changes only in a breaking
minor release. Cache versions are internal and may change in either a minor
or patch release. (Since `0.11.32`.)

## PEP 751 and Requirements Files

### Generate and consume pylock files

uv can generate, export, install, and sync PEP 751 lockfiles. Custom names
must follow `pylock.<name>.toml`; arbitrary TOML files are not parsed as
requirements. (Batch `0.6-0.8`.)

```console
uv export -o pylock.toml
uv pip compile -o pylock.toml requirements.in
uv pip sync pylock.toml
uv pip install -r pylock.toml
```

### Validate pylock structure and artifacts

A PEP 751 file must contain a `packages` array, although `packages = []` is
valid. Its filename must be `pylock.toml` or a single-name variant such as
`pylock.dev.toml`. Declared artifact sizes are verified against downloaded or
cached artifacts. (Since `0.12.5`.)

### Enforce in-file hash directives

For `uv pip install` and `uv pip sync`, `--require-hashes` inside a
requirements file enables hash-checking mode. Every requirement must be
pinned and hashed; MD5 alone is insufficient, so provide a secure digest such
as SHA-256. (Since `0.12.5`.)

```text
--require-hashes
anyio==4.0.0 --hash=sha256:<digest>
```

## Remote and Script Inputs

Requirement loading accepts extensionless inline-metadata scripts and scripts
at HTTP(S) paths; `pylock.toml` inputs may also be remote. Git sources expose
an LFS toggle through `UV_GIT_LFS`. Treat remote inputs as network and trust
boundaries. (Batch `0.9-0.10`.)
