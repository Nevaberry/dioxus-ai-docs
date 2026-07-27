# Projects and Workspaces

Use this reference for project metadata, initialization, workspace membership,
package build behavior, and project-oriented commands.

## Contents

- [Project Versions and Initialization](#project-versions-and-initialization)
- [Workspace Inspection and Selection](#workspace-inspection-and-selection)
- [Workspace and Path Dependencies](#workspace-and-path-dependencies)
- [Dependency Groups and Request Validation](#dependency-groups-and-request-validation)
- [Build Configuration and Metadata](#build-configuration-and-metadata)

## Project Versions and Initialization

### Manage the project version explicitly

In the 0.6-0.8 batch, `uv version` became the project-version command. It reads
or updates the current project's version, locks and syncs after an update, and
supports pre-release bumps.

```console
uv version
uv version --bump major
uv version --short
uv self version
```

Outside a project, `uv version` is an error; it no longer falls back to uv's
own version. Use `uv self version` for the installed uv executable.

### Initialize with current defaults

`uv init --package` and `uv init --lib` use `uv_build` rather than `hatchling`
as their default backend. Select the earlier default explicitly when needed:

```console
uv init --package --build-backend hatchling
```

Across the 0.9-0.10 batch, `uv init --project` was deprecated in favor of a
positional target path. `UV_INIT_BARE` is the environment-level control for
bare initialization.

### Project metadata is optional

A `pyproject.toml` may contain supported non-project configuration without a
`[project]` table. Do not assume every uv configuration file describes a
Python package.

## Workspace Inspection and Selection

### Use stable workspace utilities

`uv workspace list` and `uv workspace dir` are stable scripting commands.
Request paths when scripts need member locations:

```console
uv workspace list --paths
uv workspace dir
```

`uv workspace metadata` includes best-effort information about the active
environment by default as of 0.11.32. Its output can therefore reflect the
environment from which the command is invoked.

### Select projects for checks

Preview `uv check` can target one workspace package or all packages rather
than only the default target:

```console
uv check --package my-package
uv check --all-packages
```

Treat package-selection support as preview behavior.

## Workspace and Path Dependencies

### Expect dependencies to be installed

Path dependencies and workspace members used as dependencies are built and
installed by default even when they have no explicit build system. uv uses the
legacy setuptools backend when necessary. To keep a source or dependent
project virtual, mark it non-package:

```toml
[tool.uv.sources]
foo = { path = "./foo", package = false }
```

### Control automatic membership

Inside a workspace, `uv add <subdirectory>` adds that target as a workspace
member by default. Pass `--no-workspace` when the dependency should remain
outside the workspace relationship.

### Express package-level installation conflicts

Preview workspace conflicts can make packages mutually exclusive, not just
features or groups. A workspace source may set `editable = false`, and
`--editable` can override the annotation. Different editable settings are
allowed only when the corresponding groups are declared conflicting.

## Dependency Groups and Request Validation

`default-groups = "all"` activates every dependency group by default. A group
can declare its own Python requirement:

```toml
[tool.uv.dependency-groups]
docs = { requires-python = ">=3.11" }
```

`tool.uv.required-environments` marks target environments as mandatory for
wheel coverage.

Request validation is deliberately strict:

- A nonexistent local extra is an error.
- A dependency group absent from a frozen lockfile is an error.
- An unknown dependency-group object specifier is an error.
- `--frozen` conflicts with `--no-sources`.
- Arbitrary executable-name requests in `.python-version` files are ignored.

## Build Configuration and Metadata

`--config-settings-package` applies build configuration to one package.
Preview configuration can add `extra-build-dependencies` for a package and can
optionally match their versions to runtime dependency versions.

Build metadata validation is stricter in the 0.9-0.10 batch:

- `uv build` requires license files to be UTF-8.
- A `project.license-files` glob that matches nothing is an error.
- `uv_build` rejects invalid classifiers.
- `uv_build` warns about legacy license classifiers.
