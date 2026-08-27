---
name: devcontainers-knowledge-patch
description: Dev Containers
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Dev Containers

Use this skill when working with Dev Container configuration, the Dev Container
CLI, Feature packages, Feature lockfiles, or Template packages. Read only the
reference that matches the task, then verify repository-specific configuration
before making changes.

## Working method

1. Locate the active `devcontainer.json` using the discovery rules below.
2. Determine whether the project uses an image, a Dockerfile, or Compose.
3. Separate container-creation settings from remote-process settings.
4. Check the installed CLI version before depending on recently added behavior.
5. Preserve `.devcontainer-lock.json` unless the task deliberately updates
   Feature versions or opts out of locking.
6. When authoring a Feature or Template, validate its package layout, identity,
   option substitution, and dependency behavior as applicable.
7. Keep installers and lifecycle operations safe to repeat.

## Reference index

| Reference | Read for |
| --- | --- |
| [CLI compatibility and operations](references/cli.md) | CLI installation, commands, version-dependent behavior, build compatibility, Podman, Docker, WSLc, and worktrees |
| [Feature lockfiles](references/lockfiles.md) | Lockfile naming, schema, integrity, dependency records, generation controls, and upgrades |
| [Configuration and lifecycle](references/configuration.md) | Discovery, metadata merging, environments, workspace mounts, users, lifecycle stages, and parallel commands |
| [Feature authoring](references/features.md) | Feature layout, options, installer environment, lifecycle contributions, dependencies, ordering, identity, and publishing |
| [Template authoring](references/templates.md) | Template layout, identity, option substitution, optional paths, and OCI references |

## Compatibility and deprecated assumptions

Check these points before relying on familiar but outdated behavior:

- Treat `devcontainer.metadata` as a JSON array, including when it contains one
  entry.
- Use the current `.devcontainer-lock.json` filename. Older material may refer
  to the undotted `devcontainer-lock.json`.
- Expect `build` and `up` to generate the lockfile by default on CLI 0.87.0 and
  later.
- Prefer `--no-lockfile` and `--frozen-lockfile`. The corresponding
  `--experimental-*` flags are deprecated and warn when used.
- Do not script `devcontainer stop` or `devcontainer down`; neither command is
  implemented.
- Do not expect Features supplied with `--additional-features` to appear in the
  lockfile on CLI 0.86.1 and later.
- Handle Docker 29 container `start` events without the fields Docker removed.
- Expect old `devcontainers-contrib` Feature references to redirect to
  `devcontainers-extra` on CLI 0.79.0 and later.
- On Docker Engine 23.0.0 and later, do not assume the CLI must download and
  inject the `dockerfile:1.4` frontend.

## CLI quick reference

| Need | Current guidance |
| --- | --- |
| Build reproducibly | Commit `.devcontainer-lock.json`; use `--frozen-lockfile` in verification |
| Build without a lockfile | Pass `--no-lockfile` |
| Check Feature updates | Run `devcontainer outdated` |
| Upgrade locked Features | Run `devcontainer upgrade` |
| Omit an explicit workspace | CLI 0.82.0 and later use the current directory |
| Use linked worktrees | CLI 0.81.0 adds an option to mount the Git common folder |
| Send large requests | CLI 0.83.0 removes the former request-body cap |
| Cache Feature builds | CLI 0.83.0 adds `BUILDKIT_INLINE_CACHE` on the Feature build path |
| Resolve platform-aware bases | CLI 0.85.0 inlines Buildx build- and target-platform variables |
| Run in WSLc | CLI 0.88.0 adds support |
| Install without Node.js | Use the standalone Linux/macOS installer; it bundles Node.js |

For restricted and alternate-engine environments:

- CLI 0.74.0 ignores an unusable, non-writable `HOME`.
- Avoid combining Podman `--uidmap` or `--gidmap` with conflicting `--userns`
  settings.
- Omit `--userns=keep-id` when running Podman as root.
- Expect Podman invocations to use `label=disable`, rather than `z`, on CLI
  0.80.0 and later.
- CLI 0.80.1 supports Debian `latest` images without `adduser` and `addgroup`.
- Failed lifecycle commands expose their output, and an OCI registry 403
  triggers reauthentication, on CLI 0.73.0 and later.

## Configuration quick reference

Search a workspace in this order:

1. `.devcontainer/devcontainer.json`
2. `.devcontainer.json`
3. `.devcontainer/<folder>/devcontainer.json`, one subdirectory deep

Multiple configurations are valid. Select one explicitly when the tool or
workflow supports more than one.

Keep these roles distinct:

| Setting | Role |
| --- | --- |
| `containerEnv` | Creation-time environment for image or Dockerfile containers, including `ENTRYPOINT` |
| Compose environment | Creation-time environment for Compose-managed services |
| `remoteEnv` | Environment for later tool-injected processes |
| `userEnvProbe` | Shell-profile values merged into injected processes |
| `containerUser` | User for container operations |
| `remoteUser` | User for lifecycle, editor, and tool processes |
| `workspaceMount` | Source mount definition for image and Dockerfile configurations |
| `workspaceFolder` | Working folder, which may be nested below the mounted repository |

On Linux, use `updateRemoteUserUID: true` with a configured container or remote
user when bind-mounted files need matching local UID/GID ownership. An
implementation may skip the rewrite when no bind mounts exist or the engine
already translates identities.

## Lifecycle quick reference

On first creation, apply container-level mounts, environment, and user settings
before these ordered stages:

1. `onCreateCommand`
2. `updateContentCommand`
3. `postCreateCommand`

`postCreateCommand` is backgrounded by default. `waitFor` controls the blocking
stage and defaults to `updateContentCommand`. On resume, restart containers,
perform implementation-specific setup, then also run `postStartCommand` and
`postAttachCommand`.

A lifecycle property may be an object of uniquely named commands. Run those
entries in parallel and require every entry to succeed. For each lifecycle
stage, run Feature contributions sequentially in Feature installation order
before the user's corresponding command.

## Metadata merge quick reference

Merge image metadata snippets in order and apply `devcontainer.json` last:

- Use any-true semantics for `init` and `privileged`.
- Deduplicate and union capabilities, security options, and forwarded ports.
- Collect entrypoints, mounts, and lifecycle commands.
- Resolve conflicting mounts and scalar settings with the last value.
- Merge environment maps with the last value for each variable.
- Replace port attributes as a whole for the affected port.
- Take each maximum in `hostRequirements`.
- Leave `customizations` merging to the implementing tool.

## Feature authoring quick reference

A Feature directory requires `devcontainer-feature.json` and an executable
`install.sh`. Match the manifest `id` to the directory name, keep it lowercase,
and supply at least `id`, `version`, and `name`.

Use only `string` and `boolean` options. Use `proposals` for suggestions with
free-form input or `enum` for a strict set. Every option reaches the installer,
including defaults for omitted options, through `devcontainer-features.env`.

Choose dependency declarations by intent:

| Declaration | Effect |
| --- | --- |
| `dependsOn` | Recursively installs required Features and accepts reference-and-options objects |
| `installsAfter` | Reorders matching queued Features without installing them |
| `overrideFeatureInstallOrder` | Applies user priority without violating hard or soft dependencies |

Do not put options, tags, or digests in `installsAfter` or
`overrideFeatureInstallOrder`. Treat unresolved or circular hard dependencies,
and user ordering that violates dependencies, as errors.

## Template authoring quick reference

A Template contains `devcontainer-template.json` at its root and
`.devcontainer/devcontainer.json` beneath it. Match the manifest `id` to the
Template folder name and keep it unique within the repository or package.

Apply `${templateOption:<optionId>}` substitution to every file before copying
the Template. Prompt separately for every `optionalPaths` entry; use an exact
relative path for a file and a trailing `/*` for recursive directory contents.
Address a published Template as
`<oci-registry>/<namespace>/<template>[:<semantic-version>]`.

## Final checks

- Confirm path and user assumptions on the actual container engine and host OS.
- Keep lockfile references lowercase and digest- or checksum-qualified as
  required by the schema.
- Ensure local Features and differently configured instances remain safe to
  install more than once.
- Avoid `${devcontainerId}` in image-build inputs; use it only for supported
  per-container runtime resources.
- Preserve an existing Feature's semantic-version sequence when renaming it.
- Consult the detailed reference for any field or behavior before encoding it
  into reusable automation.
