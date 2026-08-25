# Projects and Workspaces

Use this reference for initialization, project metadata, builds, workspace
membership, dependency groups, and project checks.

## Project Version and Initialization

### Distinguish project and executable versions

`uv version` reads or updates the current project's version, supports
pre-release bumps, and locks and syncs after an update. It errors outside a
project rather than reporting the uv executable's version; use
`uv self version` for that. (Batch `0.6-0.8`.)

```console
uv version
uv version --bump major
uv version --short
uv self version
```

### Choose packaged or unpackaged initialization

For `uv init --package` and `uv init --lib`, `uv_build` replaced `hatchling`
as the default backend; select `--build-backend hatchling` when that backend
is required. (Batch `0.6-0.8`.)

`uv init <name>` later became packaged by default: it declares `uv_build`,
creates `src/<name>` plus a project script, and installs the project into its
environment. Existing projects do not change. Use `--no-package` for the
former unpackaged `main.py` layout, and widen an existing `uv_build` upper
bound to admit 0.12 when appropriate, for example
`uv_build>=0.11.32,<0.13`. (Since `0.12.5`.)

```console
uv init example
uv init --no-package example
```

`uv init --project` is deprecated; use `uv init <target>` instead.
`UV_INIT_BARE` supplies environment-level control for bare initialization.
(Batch `0.9-0.10`.)

### Use configuration-only pyproject files

A `pyproject.toml` can contain supported non-project configuration without a
`[project]` table. Do not add placeholder project metadata merely to make uv
read its configuration. (Batch `0.6-0.8`.)

## Build Configuration and Validation

### Configure one package's build

`--config-settings-package` applies build settings to one package. Preview
configuration can extend a package's build requirements with
`extra-build-dependencies` and can optionally match those requirements to
runtime versions. (Batch `0.6-0.8`.)

### Validate build metadata strictly

`uv build` requires UTF-8 license files and errors when a
`project.license-files` glob matches nothing. `uv_build` rejects invalid
classifiers and warns about legacy license classifiers. (Batch `0.9-0.10`.)

## Workspace Membership and Path Sources

### Package path and workspace dependencies by default

Path dependencies and workspace-member dependencies are built and installed
even without an explicit build system; uv uses the legacy setuptools backend
when needed. Set `package = false` on the source or dependent project when it
must remain virtual. (Batch `0.6-0.8`.)

```toml
[tool.uv.sources]
foo = { path = "./foo", package = false }
```

### Control implicit workspace membership

Inside a workspace, `uv add <subdirectory>` adds the target as a workspace
member by default. Pass `--no-workspace` to add the path dependency without
that relationship. (Batch `0.6-0.8`.)

### Model conflicting installation modes

Preview package-level workspace conflicts can express mutually exclusive
packages. Workspace sources may set `editable = false`, and `--editable` can
override that annotation. Different editable settings are allowed only when
their groups are declared conflicting. (Batch `0.6-0.8`.)

### Request root groups explicitly for selected members

From a workspace member, commands can address dependency groups defined at
the workspace root. Workspace sources can also reference a member of another
workspace by path. Syncing or exporting a selected member does not include the
root's default groups unless those groups are requested explicitly. (Since
`0.12.5`.)

## Workspace Discovery and Metadata

### Use stable workspace discovery commands

`uv workspace list` and `uv workspace dir` are stable scripting interfaces;
`uv workspace list --paths` emits member paths. (Batch `0.9-0.10`.)

```console
uv workspace list --paths
uv workspace dir
```

### Treat active-environment metadata as invocation-dependent

`uv workspace metadata` includes best-effort information about the active
environment by default. Its output can therefore vary with the environment
from which it is invoked. (Since `0.11.32`.)

Preview `uv workspace metadata --sync --active` can explicitly target the
active virtual environment. A `.venv` file may point to a centralized project
environment, including when a workspace is reached through symlinks. (Since
`0.12.5`.)

## Project and Script Checks

### Select workspace packages in `uv check`

Preview `uv check --package <name>` checks one workspace package, and
`uv check --all-packages` checks every package instead of only the default
target. (Since `0.11.32`.)

```console
uv check --package my-package
uv check --all-packages
```

### Apply fixes and control project installation

Preview `uv check --fix` applies automatic fixes.
`--no-install-project` or `UV_NO_INSTALL_PROJECT` installs dependencies
without building or installing the project. Scripts are checked only when
`--script` is provided. (Since `0.12.5`.)

```console
uv check --fix
uv check --no-install-project
uv check --script script.py
```
