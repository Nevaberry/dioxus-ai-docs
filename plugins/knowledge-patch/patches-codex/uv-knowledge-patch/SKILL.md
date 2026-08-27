---
name: uv-knowledge-patch
description: uv
version: "0.11.32"
license: MIT
metadata:
  author: Nevaberry
---


# uv Knowledge Patch

Use this guidance when changing uv-managed Python projects, environments,
dependency resolution, package indexes, publishing, or CI and container
workflows. Confirm the installed uv version and the repository's manifests,
lockfiles, configuration, and tests before applying compatibility advice.

## Working Method

1. Run `uv self version` to identify uv itself. `uv version` reads or changes
   the current project's version and errors outside a project.
2. Inspect `pyproject.toml`, `uv.toml`, `.python-version`, `uv.lock`, relevant
   `pylock*.toml` inputs, requirements files, and container configuration.
3. Identify which commands and settings are preview behavior. Avoid making a
   durable workflow depend on preview behavior without pinning and testing it.
4. Read the task-specific reference below before choosing flags or settings.
5. Preserve lock intent: use `uv lock --check` or `--locked` for verification;
   reserve `uv lock --refresh` for deliberate canonical regeneration.
6. Treat credentials, certificate overrides, publishing, archive validation,
   environment replacement, and interpreter selection as state-sensitive.
7. Prefer observed project behavior and tests when a newer installed uv
   differs from this guidance.

## Reference Index

| Reference | Topics |
| --- | --- |
| [projects-and-workspaces](references/projects-and-workspaces.md) | Initialization, project versions, builds, workspaces, path members, groups, and project checks |
| [python-environments-and-platforms](references/python-environments-and-platforms.md) | Interpreter discovery, managed Python, virtual environments, platform targets, containers, and tool Python pins |
| [dependency-resolution-and-lockfiles](references/dependency-resolution-and-lockfiles.md) | Resolution controls, constraints, cutoffs, dependency inputs, lock checks, PEP 751, and hashes |
| [indexes-auth-and-publishing](references/indexes-auth-and-publishing.md) | Named indexes, authentication, credentials, certificates, archives, and publishing |
| [tooling-and-operations](references/tooling-and-operations.md) | Release boundaries, subprocesses, `uvx`, formatting, auditing, exports, cache output, and runtime controls |

## Breaking Changes and Deprecations

### Initialization now creates a packaged project

`uv init <name>` creates a `src/` package, project script, and `uv_build`
configuration, then installs the project. Use `--no-package` when the former
unpackaged `main.py` layout is intended. The older `uv init --project` spelling
is deprecated; pass the target path positionally.

### Pre-release resolution can fall back automatically

The default `if-necessary` policy tries stable candidates first and then
permits pre-releases when no stable candidate satisfies active constraints,
including constraints found transitively. Use `--prerelease disallow`,
`allow`, or `explicit` when the policy must be unambiguous. The
`if-necessary-or-explicit` name is deprecated.

### Lock and requirements validation is stricter

- `uv lock --check` and `--locked` reject non-canonically formatted
  `uv.lock`; use `uv lock --refresh` for an intentional rewrite.
- A `--require-hashes` directive inside a requirements file enables hash mode
  for `uv pip install` and `uv pip sync`. Every requirement must then be
  pinned and hashed, and MD5 alone is insufficient.
- PEP 751 files require a `packages` array and a valid `pylock.toml` or
  `pylock.<name>.toml` filename. Declared artifact sizes are checked.
- Nonexistent local extras, missing frozen groups, and unknown group object
  specifiers are errors. Do not combine `--frozen` with `--no-sources`.

### Index and trust failures are fail-closed

With the default `first-index` strategy, a 401 or 403 stops lookup. Set
`authenticate = "always"` when credentials are mandatory, and add
`ignore-error-codes` only for an index whose unusual behavior requires
fallthrough. Explicit invalid `SSL_CERT_FILE` or `SSL_CERT_DIR` values no
longer fall back to default trust roots.

### Archive handling rejects ambiguous or dangerous inputs

ZIP archives with duplicate or ambiguous entries are rejected. Source
distributions must use `.tar.gz` or the accepted legacy `.zip` form, and
wheels are rejected when entry points or data files could overwrite a Python
interpreter. Keep insecure ZIP validation bypasses temporary and exceptional.

### Platform and image defaults moved

- The `linux` platform alias means `manylinux_2_28`; request
  `x86_64-manylinux_2_17` explicitly for the older target.
- Floating container images use Debian 13 Trixie and Alpine 3.22. Removed tags
  include Bookworm, Alpine 3.21, and Python 3.8.
- Derived images default `UV_TOOL_BIN_DIR` to `/usr/local/bin`; override it for
  an unprivileged user that cannot write there.

### Environment replacement is guarded

Interactive `uv venv` prompts before removing an existing environment and
refuses to remove a directory that is not a virtual environment. Use
`--clear` for explicit replacement or `--no-clear` to prohibit it.

## High-Value Workflows

### Check lockfile and environment freshness

```console
uv lock --check
uv sync --check
```

A stale lockfile or environment returns status 1; status 2 is an operational
error. Keep that distinction in CI. Isolated operations do not update
`uv.lock`.

### Target workspace operations precisely

```console
uv workspace list --paths
uv workspace dir
uv check --package my-package
uv check --all-packages
```

Workspace listing and directory discovery are stable scripting interfaces.
Package selection for `uv check` is preview behavior. Workspace metadata can
include best-effort active-environment information, so its output may depend
on the invoking environment.

### Control dependency resolution

- Use `tool.uv.build-constraint-dependencies` for build-time constraints,
  including ephemeral `uv run --with`, tools, and inline scripts.
- Use `default-groups = "all"`, per-group `requires-python`, and
  `tool.uv.required-environments` to control group inclusion and wheel
  coverage.
- Prefer `exclude-dependencies`, selective `--no-sources-package`, bounds,
  and package-specific or relative `exclude-newer` cutoffs over broad global
  workarounds.
- Marker-aware `uv upgrade` can update multiple declarations of one package
  when environment markers distinguish them.

### Exchange standardized results

```console
uv export -o pylock.toml
uv pip compile -o pylock.toml requirements.in
uv pip sync pylock.toml
uv pip install -r pylock.toml
```

uv can generate, export, install, and sync PEP 751 lockfiles. CycloneDX export
produces an SBOM and includes artifact URLs and hashes. Preview sync output can
report package changes as JSON.

### Select Python deliberately

- `uv python install` honors `UV_PYTHON` before `.python-version`.
- In `uv pip compile`, `-p` means `--python`, not `--python-version`.
- Unversioned installation and automatic-download defaults favor Python 3.14.
  Discovery may select a free-threaded 3.14+ interpreter without a `t`
  suffix, while installation still prefers a GIL-enabled build.
- Global Python pins can affect new tool environments, but an existing tool
  retains its interpreter until reinstalled or explicitly changed.

### Run tools and ephemeral requirements safely

`uvx <name>` verifies that the named package or one of its dependencies
provides the executable. Use `uvx --from <package> <command>` when package and
command intentionally differ. `uv run --with` executes in a fresh empty layer
over a cached requirement environment, so runtime inspection or mutation does
not target the cached layer itself.

### Audit, format, and publish with explicit stability choices

- `uv audit`, `uv format`, `uv sync` JSON output, relocatable environments,
  package-level workspace conflicts, and several check, index, publishing,
  and malware-screening features are preview behavior.
- Pin Ruff with `uv format --version` when formatting reproducibility matters;
  the formatter's default style can change.
- Publishing supports stored `uv auth` credentials, PEP 740 attestations,
  Trusted Publishing with pyx, S3 pre-signed URLs, and GCS signing. Verify the
  stability and trust path selected by the workflow.

## Final Checks

- Confirm stable versus preview status for every command added to automation.
- Re-run lock and environment checks after dependency or project-version
  changes.
- Test the intended Python implementation, GIL mode, and target platform for
  cross-platform artifacts.
- Verify index names, authentication policy, credential username, proxy,
  timeout, and certificate settings before diagnosing resolution failures.
- Pin formatter behavior and container tags when reproducibility matters.
- Inspect archive and lockfile inputs before weakening validation.
