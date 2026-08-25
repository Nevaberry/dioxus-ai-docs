# Configuration and Lifecycle

## Discovering configurations

Search within the project workspace in this precedence order:

1. `.devcontainer/devcontainer.json`
2. `.devcontainer.json`
3. `.devcontainer/<folder>/devcontainer.json`, exactly one subdirectory deep

More than one configuration may validly exist. A tool may expose a selection
mechanism rather than silently choosing among multiple candidates.

## Merging image metadata

At container creation, merge `devcontainer.metadata` snippets in their source
order and merge `devcontainer.json` last.

| Property group | Merge rule |
| --- | --- |
| `init`, `privileged` | Any `true` value wins |
| Capabilities, security options, forwarded ports | Deduplicated union |
| Entrypoints, mounts, lifecycle commands | Collect values |
| Conflicting mount | Last source wins |
| Scalar setting | Last value wins |
| Environment map | Last value wins per variable |
| Port attributes | Last value replaces the whole port's attributes |
| `hostRequirements` | Use each maximum |
| `customizations` | Tool-defined |

The metadata label itself is always a JSON array on CLI 0.86.0 and later,
including when it holds one snippet.

## Container and remote environments

For image- and Dockerfile-based containers, `containerEnv` is present from
container creation and is visible during `ENTRYPOINT`. For Compose, configure
the creation-time environment through the orchestrator instead.

`remoteEnv` applies after `ENTRYPOINT` to editor, tool, and other
implementation-injected processes. It may change without recreating the
container.

`userEnvProbe` reads shell-profile values and merges them into injected
processes. It avoids requiring that shell to wrap every subprocess.

## Workspace mount and folder

The specification keeps the source outside the container and provides a
default workspace mount at `/workspace`.

For image and Dockerfile configurations, use `workspaceMount` to replace the
mount definition. Normally mount the repository root. Use `workspaceFolder` to
select the working folder, including a nested monorepo project beneath that
mount.

## Users and Linux identity synchronization

`containerUser` controls container operations. `remoteUser` controls lifecycle
scripts plus editor and tool processes; it defaults to the container user.

On Linux, setting `updateRemoteUserUID: true` with either user configured asks
the implementation to update the image before creating the container so that
the selected user's UID and GID match the local user:

```json
{
  "containerUser": "root",
  "remoteUser": "dev",
  "updateRemoteUserUID": true
}
```

An implementation may skip the update if no bind mounts are present or if the
container engine already performs identity translation.

## First creation and resume

Apply container-level mounts, environment, and user settings before lifecycle
commands. On first creation, run these stages in order:

1. `onCreateCommand`
2. `updateContentCommand`
3. `postCreateCommand`

Remote settings affect only processes launched after the container-level
setup. `postCreateCommand` runs in the background by default. `waitFor`
selects the stage through which the caller blocks and defaults to
`updateContentCommand`.

On resume, restart the containers, perform implementation-specific setup, and
also execute `postStartCommand` and `postAttachCommand`.

## Parallel lifecycle commands

A lifecycle property can be an object whose unique keys label independent
commands. Values may be strings or command arrays:

```json
{
  "postCreateCommand": {
    "dependencies": "npm ci",
    "schema": ["npm", "run", "db:migrate"]
  }
}
```

Run the object's entries in parallel. Every entry must succeed for its
lifecycle stage to succeed.
