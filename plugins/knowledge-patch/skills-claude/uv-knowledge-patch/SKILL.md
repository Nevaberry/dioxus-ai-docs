---
name: uv-knowledge-patch
description: uv
version: 0.11.32
license: MIT
metadata:
  author: Nevaberry
---


# uv Knowledge Patch

Use this guidance for uv-managed Python projects, environments, dependency
resolution, package indexes, publishing, tools, CI, and containers. Inspect the
repository and installed executable before changing a workflow: project files,
lockfiles, and observed behavior take precedence when they differ from this
guidance.

## Working Method

1. Run `uv self version` to identify the uv executable. `uv version` reads or
   changes a project's version and errors outside a project.
2. Inspect `pyproject.toml`, `uv.toml`, `.python-version`, `uv.lock`, relevant
   `pylock*.toml` files, inline-script metadata, and CI or container files.
3. Decide whether each proposed command is stable or preview. Keep preview
   behavior explicit in durable scripts and configuration.
4. Read the task-specific reference from the index before choosing flags or
   settings.
5. Preserve lockfile intent. Use `uv lock --check` or `--locked` to verify;
   reserve `uv lock --refresh` for deliberate canonical regeneration.
6. Treat credential changes, certificate overrides, publishing, environment
   replacement, archive validation bypasses, and malware checks as sensitive.

## Reference Index

| Reference | Use for |
| --- | --- |
| [Projects and workspaces](references/projects-and-workspaces.md) | Project versions, initialization, builds, checks, workspace membership, groups, and metadata |
| [Python, environments, and platforms](references/python-environments-and-platforms.md) | Interpreter discovery and installation, managed Python, virtual environments, platform targets, and tool pins |
| [Dependency resolution and lockfiles](references/dependency-resolution-and-lockfiles.md) | Constraints, groups, cutoffs, upgrades, lock checks, PEP 751, sources, hashes, and pre-releases |
| [Indexes, authentication, and publishing](references/indexes-auth-and-publishing.md) | Index policy, credentials, certificates, archives, publishing, uploads, and local index paths |
| [Tooling and operations](references/tooling-and-operations.md) | Release boundaries, subprocesses, `uvx`, ephemeral runs, formatting, auditing, exports, caches, containers, and networking |

## Breaking Changes and Compatibility Traps

### Distinguish executable and project versions

Use `uv self version` for the executable. Inside a project, `uv version` reads
or updates project metadata and can lock and sync after an update; it is not a
fallback executable-version command.

### Expect packaged initialization

`uv init <name>` creates a `uv_build`-backed `src/<name>` package, project
script, and installed project. Use `--no-package` for the former unpackaged
`main.py` layout. Existing projects do not change automatically, and a pinned
`uv_build` range must admit the version used by newly initialized projects.

### Preserve lockfile formatting and state

`uv lock --check` and `--locked` reject non-canonical `uv.lock` formatting.
Regenerate intentionally with `uv lock --refresh`. Check commands return 1 for
stale state and reserve 2 for operational errors. `--isolated` must not rewrite
the project lockfile.

### Account for stricter validation

Treat these as errors rather than ignored input:

- nonexistent local extras;
- missing frozen dependency groups and unknown group object specifiers;
- `--frozen` combined with `--no-sources`;
- unmatched `project.license-files` globs or non-UTF-8 license files;
- malformed or unsafe archives and invalid `pylock.toml` structure;
- hash-checking requirements that are unpinned, unhashed, or MD5-only.

Arbitrary executable names in `.python-version` are ignored. `uv_build`
rejects invalid classifiers and warns on legacy license classifiers.

### Treat index failures as authoritative

The default `first-index` strategy stops on 401 or 403. Use
`ignore-error-codes` only for an index whose unusual behavior requires
fallthrough. `authenticate = "always"` makes missing credentials fail closed.
Only one index may be `default = true`, and an explicit index needs a name.

### Do not rely on certificate fallback

An explicitly set `SSL_CERT_FILE` or `SSL_CERT_DIR` is authoritative. If it is
missing, inaccessible, empty, or contains no certificates, fix or remove it;
uv does not silently fall back to default trust roots.

### Revisit Python and platform assumptions

Unversioned installation and automatic download now prefer Python 3.14.
Discovery can select a free-threaded 3.14+ interpreter without a `t` suffix,
while installation still prefers a GIL-enabled build. The `linux` platform
alias means `manylinux_2_28`; request `x86_64-manylinux_2_17` explicitly when
that older target is required.

### Pin container and formatter behavior

Floating images now follow Debian 13 Trixie and Alpine 3.22; removed tags
include Bookworm, Alpine 3.21, and Python 3.8. Preview `uv format` moved to Ruff
0.15 and the 2026 style guide. Pin the image tag and formatter version when
reproducibility matters.

## High-Value Workflows

### Verify lockfiles and environments

```console
uv lock --check
uv sync --check
uv lock --refresh
```

Use the first two commands for CI verification. Run the refresh command only
when rewriting the lockfile is the intended repository change.

### Check projects and workspaces

```console
uv check --package my-package
uv check --all-packages
uv workspace list --paths
uv workspace dir
```

Package selection for `uv check` is preview. Workspace listing and directory
discovery are stable scripting interfaces. `uv workspace metadata` includes
best-effort active-environment data by default, so its output can vary with the
invocation environment.

Preview checks also provide `--fix`, `--no-install-project`, and explicit
`--script`. Scripts are not checked unless requested. `uv tool audit` can
inspect installed tools, and configured malware checks can screen locked tools
before cache reuse.

### Control resolution precisely

- Apply build constraints to project builds, `uv run --with`, tools, and
  inline scripts.
- Use per-group Python requirements and `default-groups = "all"` deliberately.
- Require wheel coverage with `tool.uv.required-environments`.
- Prefer package-specific cutoffs, dependency exclusions, selective
  `--no-sources-package`, and stable bounds controls over broad workarounds.
- Use marker-aware `uv upgrade` when repeated declarations differ by markers.
- Override automatic stable-then-prerelease fallback with an explicit global
  or package-specific prerelease policy when the distinction matters.

### Exchange standardized results

Generate, compile, install, and sync PEP 751 files named `pylock.toml` or
`pylock.<name>.toml`. A valid file contains a `packages` array, which may be
empty, and declared artifact sizes are checked.

CycloneDX exports include distribution artifact URLs and hashes. Preview JSON
sync output can describe package changes made by the operation.

### Select indexes and credentials explicitly

```toml
[[tool.uv.index]]
name = "private"
url = "https://packages.example.invalid/simple"
authenticate = "always"
```

Named flat indexes share the same configuration. Under preview
`index-by-name`, `--index` and `--default-index` may select a configured name;
preview index configuration can also choose the lockfile hash algorithm. When
several credentials match a URL, supply the username explicitly.

### Install and discover Python deliberately

`UV_PYTHON` takes precedence over `.python-version` for `uv python install`.
Managed installs add versioned executables to a `PATH` directory and can
register with the Windows launcher; use `--no-bin` or `--no-registry` to
suppress those effects. Changing managed/unmanaged discovery preference can
invalidate and recreate the project environment.

### Run tools and temporary requirements safely

`uvx <name>` verifies that the requested executable comes from that package or
its dependencies. Use `uvx --from <package> <command>` when the package and
command intentionally differ. `uv run --with` executes through a fresh empty
top layer over a cached requirement environment, so runtime mutations do not
modify the cached layer.

### Protect virtual environments

Interactive `uv venv` prompts before clearing an existing virtual environment
and refuses to remove a non-environment directory. State the decision with
`--clear` or `--no-clear`. Preview relocatable environments omit
`activate.csh`; a `.venv` file may instead point to a centralized environment.

### Audit, format, and publish cautiously

`uv audit` and `uv format` are preview commands. Auditing batches OSV queries
and supports linked findings and report formats. Publishing supports stored
credentials, PEP 740 attestations, Trusted Publishing with pyx, and preview S3
or GCS signing flows. Validate archives and authentication before upload.

## Final Checks

- Confirm stable versus preview status for each durable command.
- Re-run lock and environment checks after dependency or version changes.
- Test the intended implementation, GIL mode, and target platform explicitly.
- Verify index names, authentication policy, username, proxy, certificate, and
  upload timeout settings before diagnosing resolution or publishing failures.
- Pin formatter behavior and container tags where reproducibility matters.
- Inspect the relevant reference before changing security, publishing,
  environment-clearing, lockfile, or archive-validation behavior.
