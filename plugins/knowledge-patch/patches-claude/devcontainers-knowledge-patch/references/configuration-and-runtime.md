# Configuration and Runtime

## Configuration discovery

Source batch: `core-configuration`.

Within a project workspace, implementations search in this order:

1. `.devcontainer/devcontainer.json`
2. `.devcontainer.json`
3. `.devcontainer/<folder>/devcontainer.json`, exactly one subdirectory deep

More than one configuration can validly exist. An implementation may therefore
offer a selection mechanism instead of silently choosing among multiple matches.

## Image metadata merge rules

At container creation, merge `devcontainer.metadata` snippets in their order,
then apply `devcontainer.json` last.

| Setting | Merge behavior |
| --- | --- |
| `init`, `privileged` | Any `true` value wins |
| Capabilities, security options, forwarded ports | Deduplicated union |
| Entrypoints, mounts, lifecycle commands | Collected; a conflicting mount uses the last source |
| Scalar settings | Last value wins |
| Environment maps | Last value wins per variable |
| Port attributes | Last value wins for the entire port, not per attribute |
| `hostRequirements` | Maximum value per requirement |
| `customizations` | Tool-defined |

The `devcontainer.metadata` label is always a JSON array as of CLI 0.86.0, even
for one metadata entry (`cli-2026`). Metadata consumers should accept the array
shape unconditionally.

## Container and remote environments

For image- and Dockerfile-based containers, `containerEnv` is present from
container creation, including during `ENTRYPOINT`. Compose configurations use
their orchestrator environment settings rather than `containerEnv`.

`remoteEnv` is applied after `ENTRYPOINT` to editor, tool, and other
implementation-injected processes. It can change without container recreation.
`userEnvProbe` gathers shell-profile values and merges them into those processes
without requiring every subprocess to use that shell.

## Workspace mount and working folder

The specification expects source to remain outside the container and provides a
default mount at `/workspace`.

For image and Dockerfile configurations:

- `workspaceMount` changes the source mount.
- The mount should normally be the repository root.
- `workspaceFolder` can point at a nested project, such as one package in a
  monorepo.

From CLI 0.82.0, commands use the current directory as the workspace folder when
none is explicitly supplied (`cli-2026`).

CLI 0.81.0 can also mount a Git worktree's common folder so linked worktrees can
reach their shared Git metadata (`cli-2026`).

## Users and Linux identity

`containerUser` governs operations performed in the container. `remoteUser`
governs lifecycle scripts, editor processes, and tool processes; it defaults to
the container user.

```json
{
  "containerUser": "root",
  "remoteUser": "dev",
  "updateRemoteUserUID": true
}
```

On Linux, setting `updateRemoteUserUID: true` with either user asks the
implementation to update the image before container creation so the chosen
user's UID and GID match the local user. This can be skipped when bind mounts are
absent or when the container engine handles translation itself.

## Lifecycle and readiness

On first creation, container-level mounts, environment, and user settings are
applied before these ordered stages:

1. `onCreateCommand`
2. `updateContentCommand`
3. `postCreateCommand`

Remote settings affect only processes launched afterward. `postCreateCommand`
is backgrounded by default. `waitFor` blocks readiness through the selected
stage and defaults to `updateContentCommand`.

On resume, the implementation restarts the containers, performs its own setup,
then also runs `postStartCommand` and `postAttachCommand`.

A lifecycle property can be an object. The keys are unique labels for
independent commands; values are command strings or argument arrays. Entries run
in parallel, and every entry must succeed for the stage to succeed.

```json
{
  "postCreateCommand": {
    "dependencies": "npm ci",
    "schema": ["npm", "run", "db:migrate"]
  }
}
```

CLI 0.73.0 prints output from failed lifecycle scripts, making a stage failure
diagnosable (`cli-2025`).

## Engine, registry, and host compatibility

The `cli-2025` compatibility changes include:

- CLI 0.73.0 reauthenticates with an OCI registry after a 403 response.
- CLI 0.74.0 ignores a non-writable `HOME`, so an unusable home directory does
  not prevent operation in a restricted environment.
- Podman invocations avoid incompatible combinations of `--uidmap`/`--gidmap`
  with `--userns`, and omit `--userns=keep-id` for root.
- As of CLI 0.80.0, Podman uses `label=disable` instead of the `z` flag.
- CLI 0.79.0 redirects `devcontainers-contrib` Feature publisher references to
  `devcontainers-extra`.
- CLI 0.80.1 supports Debian `latest` images without `adduser` and `addgroup`.
- CLI 0.80.2 handles Docker 29.0.0 `start` events after deprecated event fields
  were removed.
- On Docker Engine 23.0.0 or newer, CLI 0.80.3 does not download and inject
  `dockerfile:1.4`, because the engine package already provides that frontend or
  a newer one.

## Build, path, and environment compatibility

The `cli-2026` compatibility changes also include:

- CLI 0.83.0 removes the request-body cap; large requests are no longer rejected
  solely for exceeding the old limit.
- CLI 0.83.0 sets `BUILDKIT_INLINE_CACHE` on the container Feature build path,
  enabling inline BuildKit cache metadata.
- CLI 0.85.0 inlines Buildx global build- and target-platform environment
  variables while resolving the base image and user. Platform-dependent values
  therefore participate in resolution.
- CLI 0.86.0 lowercases Windows drive letters to match the path form used by
  Visual Studio Code.
- CLI 0.88.0 supports WSLc environments.
