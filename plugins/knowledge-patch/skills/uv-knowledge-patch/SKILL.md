---
name: uv-knowledge-patch
description: uv
version: 0.11.32
license: MIT
metadata:
  author: Nevaberry
---

# uv Knowledge Patch

Apply this guidance when changing uv-managed Python projects, environments,
dependency resolution, package indexes, publishing, or CI and container
workflows. Confirm the installed uv version and the project's own manifests,
lockfiles, configuration, and tests before relying on compatibility guidance.

## Working Method

1. Run `uv self version` to identify uv itself. Do not use `uv version` for
   that purpose; inside a project it reads or changes the project version.
2. Inspect `pyproject.toml`, `uv.toml`, `.python-version`, `uv.lock`, and any
   `pylock*.toml` inputs that are relevant to the task.
3. Distinguish stable behavior from preview behavior. Do not design a critical
   workflow around a preview command without acknowledging that status.
4. Read the task-specific reference from the index below before proposing
   flags or configuration keys.
5. Prefer the repository's observed behavior and tests if they disagree with
   this patch, especially when the installed uv is newer than the frontmatter
   version.
6. Preserve lockfile intent: use `--locked` or `uv lock --check` to verify,
   and use `uv lock --refresh` only when canonical regeneration is intended.
7. Treat authentication, environment replacement, virtual-environment
   clearing, and publishing as security- or state-sensitive operations.

## Reference Index

| Reference | Read for |
| --- | --- |
| [projects-and-workspaces](references/projects-and-workspaces.md) | Project versions, initialization, workspaces, path members, builds, groups, and project checks |
| [python-environments-and-platforms](references/python-environments-and-platforms.md) | Interpreter selection, managed Python, virtual environments, platform targeting, and tool Python pins |
| [dependency-resolution-and-lockfiles](references/dependency-resolution-and-lockfiles.md) | Resolution controls, constraints, cutoffs, source suppression, lock checks, PEP 751, and remote inputs |
| [indexes-auth-and-publishing](references/indexes-auth-and-publishing.md) | Named indexes, fail-closed authentication, stored credentials, publishing, and archive validation |
| [tooling-and-operations](references/tooling-and-operations.md) | Release compatibility, process environment, `uvx`, formatting, auditing, exports, containers, and networking |

## Breaking Changes and Compatibility Traps

### Release and storage boundaries

- Treat uv as stable even though its version begins with `0`. A minor release
  may break behavior; a patch release may add fixes and enhancements but is
  intended to remain non-breaking.
- The public `uv.lock` schema changes only with a breaking minor release.
  Cache formats are internal and may change in either minor or patch releases;
  do not build cross-version guarantees around cache internals.
- Rust consumers must distinguish release numbering from API stability. The
  `uv` and `uv-build` Rust interfaces do not promise semantic versioning, and
  other internal crates do not promise stability.

### Project version and initialization commands

- Use `uv version` only for a project's version. It errors outside a project
  and may lock and sync after an update. Use `uv self version` for the uv
  executable's version.
- New packaged projects and libraries use `uv_build` by default. Request
  `--build-backend hatchling` when the prior backend is required.
- Prefer `uv init <target>` over deprecated `uv init --project`. Use
  `UV_INIT_BARE` when bare initialization needs environment-level control.

### Python discovery and installation

- `uv python install` honors `UV_PYTHON`, which takes precedence over
  `.python-version`.
- In `uv pip compile`, `-p` means `--python`, not `--python-version`.
  A missing path or requested implementation is an error; only a missing
  version request may be satisfied by another interpreter with overridden
  tags.
- Managed installs create versioned executables on `PATH` by default and may
  register with the Windows `py` launcher. Use `--no-bin` or `--no-registry`
  to suppress those effects.
- Discovery enforces managed/unmanaged Python preferences for interpreters on
  `PATH`. A preference change can invalidate and recreate the project
  environment.
- Unversioned installation and automatic-download defaults now favor Python
  3.14. On Python 3.14+, discovery may select free-threaded Python without a
  `t` suffix, while installation still prefers a GIL-enabled build.

### Validation became stricter

- Expect errors for nonexistent local extras, groups absent from a frozen
  lockfile, and unknown dependency-group object specifiers.
- Do not combine `--frozen` with `--no-sources`.
- Arbitrary executable names in `.python-version` are ignored.
- `uv build` requires UTF-8 license files and rejects an unmatched
  `project.license-files` glob. `uv_build` rejects invalid classifiers and
  warns about legacy license classifiers.

### Index lookup and credentials

- With the default `first-index` strategy, a 401 or 403 stops lookup instead
  of falling through. Configure `ignore-error-codes` only for an index whose
  nonstandard behavior requires fallthrough.
- Use `authenticate = "always"` when credentials are mandatory; missing
  credentials then fail closed.
- Configuration rejects multiple indexes marked `default = true`, and an
  `explicit = true` index must have a name.
- If several stored credentials match a URL, pass the username explicitly
  rather than relying on match order.

### Execution and environment safety

- `uvx <name>` verifies that the package or one of its dependencies provides
  the executable. Use `uvx --from <package> <command>` when intentionally
  separating package and command names.
- `uv run --with` executes in a fresh empty layer over a cached requirement
  environment. Runtime inspection or mutation no longer targets the cached
  layer itself.
- Interactive `uv venv` prompts before removing an existing environment and
  refuses to remove a directory that is not a virtual environment. Make
  removal intent explicit with `--clear` or `--no-clear`.
- `--isolated` operations do not rewrite `uv.lock`.

### Platform and container migrations

- The `linux` platform alias targets `manylinux_2_28`. Request
  `x86_64-manylinux_2_17` explicitly for the older compatibility target.
- Floating Debian and Alpine container images moved to Debian 13 Trixie and
  Alpine 3.22. Removed tags include Bookworm, Alpine 3.21, and Python 3.8;
  prebuilt big-endian PPC64 binaries are also gone.
- Derived uv images set `UV_TOOL_BIN_DIR=/usr/local/bin`. Override it when an
  unprivileged container user cannot write there.

## High-Value Current Workflows

### Verify lockfiles and environments

```console
uv lock --check
uv sync --check
uv lock --refresh
```

- Canonical lockfile formatting is enforced by `uv lock --check` and
  `--locked`. Refresh rewrites non-canonical formatting.
- A stale environment or lockfile produces exit status 1 from the check
  commands; status 2 remains an operational error. Preserve that distinction
  in CI.

### Work with one or all workspace packages

```console
uv check --package my-package
uv check --all-packages
uv workspace list --paths
uv workspace dir
```

- Package selection for `uv check` is preview behavior.
- Workspace listing and directory discovery are stable scripting interfaces.
- `uv workspace metadata` includes best-effort active-environment information
  by default, so output can depend on the invoking environment.

### Control dependency resolution precisely

- Use build constraints for build-time dependencies, including ephemeral
  `uv run --with`, tools, and inline-script workflows.
- Use dependency-group Python requirements and `default-groups = "all"` to
  control group inclusion. Use required environments to demand wheel coverage.
- Use package-specific or relative `exclude-newer` cutoffs, dependency
  exclusions, selective `--no-sources-package`, and stable bounds controls
  instead of broad global workarounds.
- Marker-aware `uv upgrade` can update multiple declarations of the same
  package when markers distinguish them.

### Exchange standardized and machine-readable results

- Generate, compile, install, or sync PEP 751 `pylock.toml` files. Custom
  names must follow `pylock.<name>.toml`.
- Export CycloneDX SBOM data when downstream tooling needs a software bill of
  materials.
- Preview sync output can report package changes as JSON.

### Audit, format, and publish

- `uv audit` is preview functionality backed by batched OSV queries and
  supports linked findings and report formatting.
- `uv format` is preview functionality. It runs from the project root and can
  pin Ruff with `--version`; pinning avoids unexpected style changes.
- Publishing can use stored `uv auth` credentials, PEP 740 attestations,
  Trusted Publishing with pyx, S3 pre-signed URLs, or GCS request signing.

## Final Checks

- Confirm stable versus preview status for every command introduced in a
  durable workflow.
- Re-run lock and environment checks after dependency or project-version
  changes.
- Test the intended Python implementation, GIL mode, and target platform
  explicitly when producing cross-platform artifacts.
- Verify index names, authentication policy, credential username, proxy and
  certificate settings before diagnosing resolution failures.
- Pin formatter behavior and container tags when reproducibility matters.
- Read the relevant reference file for edge cases before changing security,
  publishing, virtual-environment, or lockfile behavior.
