---
name: devcontainers-knowledge-patch
description: Dev Containers
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Dev Containers Knowledge Patch

Use this skill when configuring, building, running, or publishing Dev Containers,
Features, and Templates. It is especially useful for lifecycle ordering,
environment and user selection, metadata merging, lockfiles, dependency ordering,
and current CLI behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/configuration-and-runtime.md](references/configuration-and-runtime.md) | Configuration discovery, metadata merging, environments, workspaces, users, lifecycle, engines, paths, and runtime compatibility |
| [references/lockfiles-and-cli.md](references/lockfiles-and-cli.md) | Feature lockfile format, frozen builds, maintenance commands, installation, and CLI limitations |
| [references/feature-authoring.md](references/feature-authoring.md) | Feature packages, options, installers, users, lifecycle contributions, dependencies, ordering, idempotency, and publishing |
| [references/template-authoring.md](references/template-authoring.md) | Template layout, option substitution, optional paths, and OCI references |

## Start with current behavior

### Use the current lockfile name and flags

The generated Feature lockfile is `.devcontainer-lock.json`, beside
`devcontainer.json`. Current `build` and `up` commands generate it by default.

```sh
devcontainer build --frozen-lockfile
devcontainer up --no-lockfile
```

Use `--frozen-lockfile` in reproducible automation: it requires an existing
lockfile and rejects changes. Use `--no-lockfile` only when intentionally opting
out. The old `--experimental-lockfile` and
`--experimental-frozen-lockfile` spellings are deprecated and warn.

Features passed through `--additional-features` are deliberately excluded from
the lockfile. Do not rely on the lockfile to pin those additions.

### Do not assume stop or down commands

The CLI does not implement `devcontainer stop` or `devcontainer down`. Teardown
automation must call the underlying container engine or orchestrator instead.

### Parse metadata labels as arrays

`devcontainer.metadata` is always serialized as a JSON array, including when it
contains one entry. Consumers must not special-case a single object.

### Keep environment scopes distinct

For image and Dockerfile configurations, `containerEnv` exists from container
creation and is visible to `ENTRYPOINT`. Compose configurations use the
orchestrator's environment settings instead.

`remoteEnv` affects tool-injected processes after `ENTRYPOINT` and can change
without container recreation. `userEnvProbe` collects shell-profile values for
those processes without forcing every subprocess through that shell.

## Configuration quick reference

### Discover configurations in the defined order

Within a workspace, check:

1. `.devcontainer/devcontainer.json`
2. `.devcontainer.json`
3. `.devcontainer/<folder>/devcontainer.json`, one subdirectory deep

Multiple valid configurations can coexist, so tools may need to let the user
select one.

### Separate mount root from working folder

The source stays outside the container and is mounted at `/workspace` by
default. For image and Dockerfile configurations, `workspaceMount` changes the
mount itself. Keep that mount at the repository root in normal use, and use
`workspaceFolder` to select a nested project.

### Choose users deliberately

`containerUser` controls container operations. `remoteUser` controls lifecycle,
editor, and tool processes and defaults to the container user.

On Linux, `updateRemoteUserUID: true` asks the implementation to align the
selected user's UID and GID with the local user before creation. The
implementation may skip this when there are no bind mounts or the engine
performs identity translation.

```json
{
  "containerUser": "root",
  "remoteUser": "dev",
  "updateRemoteUserUID": true
}
```

### Respect lifecycle readiness

Initial creation applies container mounts, environment, and user settings before
`onCreateCommand`, `updateContentCommand`, and `postCreateCommand`, in that
order. Remote settings apply only to subsequently launched processes.

`postCreateCommand` is backgrounded by default. `waitFor` chooses the readiness
barrier and defaults to `updateContentCommand`. Resume also runs
`postStartCommand` and `postAttachCommand` after restart and implementation
setup.

A lifecycle property can be an object of independently named commands. Its
entries run in parallel, and all must succeed:

```json
{
  "postCreateCommand": {
    "dependencies": "npm ci",
    "schema": ["npm", "run", "db:migrate"]
  }
}
```

## Feature authoring quick reference

### Meet the package contract

A Feature directory contains `devcontainer-feature.json` and executable
`install.sh`; other files are packaged beside them. The required manifest
fields are `id`, `version`, and `name`. Keep `id` lowercase and equal to the
directory name. The installer runs directly as root during image build.

Feature options are only `string` or `boolean`. `proposals` suggests values but
allows other input; `enum` rejects values outside its list. Defaults are exported
even when the user omits an option. Option IDs become uppercase shell variables
after non-word characters are replaced and a leading digit/underscore run is
collapsed, so `tool-version` becomes `TOOL_VERSION`.

### Use the intended user variables

Although installation runs as root, use `_CONTAINER_USER`, `_REMOTE_USER`,
`_CONTAINER_USER_HOME`, and `_REMOTE_USER_HOME` to target the development
account. Without an explicit `remoteUser`, the remote values identify the
container user.

### Model dependencies correctly

Use `dependsOn` for recursive hard dependencies, including options and
version/digest pins. Unresolvable or circular hard dependencies fail creation.

Use `installsAfter` only as a soft ordering hint for an already queued Feature.
Its entries are unversioned IDs and cannot carry options, tags, or digests.

`overrideFeatureInstallOrder` prioritizes user-requested IDs only after hard and
soft dependencies. It cannot violate the dependency graph or include options,
tags, or digests.

### Make repeated installation safe

The same Feature requested with different options is installed as distinct
instances, and local Features are always unique. Make installers and shared-state
changes idempotent.

`${devcontainerId}` is stable per container host across rebuilds and can make
`entrypoint`, `mounts`, and `customizations` resources unique. Never use it as an
image-build input because it is unavailable while prebuilding an image.

## Template authoring quick reference

A Template has `devcontainer-template.json` at its root and
`.devcontainer/devcontainer.json` beneath it. Its `id` equals the Template
folder name and must be unique in the repository or package.

`${templateOption:<optionId>}` substitution applies to every file before the
Template is copied. Treat substitutions as whole-template text replacement,
not as JSON-only interpolation.

List optional files by exact relative path in `optionalPaths`; use a trailing
`/*` for a directory's recursive contents. Tooling must ask whether to include
each listed path before applying the Template.

Published Templates use
`<oci-registry>/<namespace>/<template>[:<semantic-version>]`.

## Operational checklist

Before creating or rebuilding:

- Resolve the intended configuration when the workspace contains several.
- Keep repository mount placement separate from the nested working directory.
- Verify `containerUser`, `remoteUser`, and Linux UID/GID behavior.
- Decide whether automation requires a frozen lockfile.
- Treat metadata labels as arrays.

Before publishing a Feature:

- Validate the package filenames, executable bit, required fields, and ID.
- Test every default and option-derived environment variable.
- Test dependency cycles, ordering, repeated instances, and idempotency.
- Preserve the existing semantic-version line when renaming with `legacyIds`.

Before publishing a Template:

- Validate the root and `.devcontainer` layout.
- Exercise default and selected substitutions across every packaged file.
- Confirm every optional path prompt and OCI reference.
