# Projects and Workspaces

## Project version commands (0.6-0.8)

`uv version` reads or updates the current project's version, supports
prerelease bumps, and locks and syncs after an update. It errors outside a
project. Use `uv self version` to inspect the uv executable.

```console
uv version
uv version --bump major
uv version --short
uv self version
```

## Initialization and build backends

For `uv init --package` and `uv init --lib`, `uv_build` replaced `hatchling` as
the default backend (0.6-0.8). Select the earlier default explicitly with
`--build-backend hatchling`.

`uv init --project` is deprecated in favor of a positional target path, and
`UV_INIT_BARE` controls bare initialization from the environment (0.9-0.10).

As of 0.12.5, `uv init <name>` creates a packaged project by default: it
declares `uv_build`, creates a `src/<name>` package and project script, and
installs the project into its environment. Existing projects are unchanged.
Use `--no-package` for the former unpackaged `main.py` layout, and widen a
`uv_build` upper bound when needed, for example `uv_build>=0.11.32,<0.13`.

```console
uv init example
uv init --no-package example
```

## Optional project metadata (0.6-0.8)

A `pyproject.toml` may contain supported non-project configuration without a
`[project]` table.

## Path and workspace dependencies (0.6-0.8)

Path dependencies and workspace members used as dependencies are built and
installed even without an explicit build system; the legacy setuptools backend
is used when necessary. Set `package = false` on the source or dependent
project to keep it virtual.

```toml
[tool.uv.sources]
foo = { path = "./foo", package = false }
```

Within a workspace, `uv add <subdirectory>` makes the target a workspace member
by default. Pass `--no-workspace` to add it without that relationship.

## Package-specific builds and install modes (0.6-0.8)

Use `--config-settings-package` to apply build configuration to one package.
Preview configuration can add `extra-build-dependencies` for a package and can
optionally match their versions to runtime requirements.

Preview package-level conflicts can declare mutually exclusive workspace
packages. Workspace sources may set `editable = false`, and `--editable` can
override that annotation. Different editable settings are valid only when the
associated groups are declared conflicting.

## Build metadata validation (0.9-0.10)

`uv build` requires UTF-8 license files and errors when a
`project.license-files` glob matches nothing. `uv_build` rejects invalid
classifiers and warns about legacy license classifiers.

## Workspace discovery and metadata

`uv workspace list`, `uv workspace dir`, and `uv workspace list --paths` are
stable scripting interfaces (0.9-0.10).

```console
uv workspace list --paths
uv workspace dir
```

`uv workspace metadata` includes best-effort active-environment information by
default (0.11.32), so output may depend on the invoking environment.

At 0.12.5, preview `uv workspace metadata --sync --active` can target the
active virtual environment.

## Workspace-root groups and cross-workspace sources (0.12.5)

From a workspace member, commands can address dependency groups defined at the
workspace root, and a workspace source may refer by path to a member of another
workspace. Syncing or exporting a selected member does not include the root's
default groups unless they are requested explicitly.

## Project checks

Preview `uv check` can select one package or every package (0.11.32):

```console
uv check --package my-package
uv check --all-packages
```

At 0.12.5, preview checks add these controls:

- `uv check --fix` applies automatic fixes.
- `--no-install-project` or `UV_NO_INSTALL_PROJECT` installs dependencies
  without building or installing the project.
- Scripts are not checked unless passed explicitly with `--script`.

```console
uv check --fix
uv check --no-install-project
uv check --script script.py
```
