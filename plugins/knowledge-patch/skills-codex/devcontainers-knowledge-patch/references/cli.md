# CLI Compatibility and Operations

This reference incorporates the versioned compatibility items identified by
`cli-2025` and `cli-2026`.

## Installation and command surface

The standalone installer supports Linux and macOS on x64 and arm64. It
downloads its own Node.js runtime, so Node.js does not need to be installed
first. The default prefix is `$HOME/.devcontainers/bin`; the installer accepts
`--version`, `--prefix`, `--update`, and `--uninstall`.

```sh
curl -fsSL https://raw.githubusercontent.com/devcontainers/cli/main/scripts/install.sh | sh
export PATH="$HOME/.devcontainers/bin:$PATH"
```

The npm installation route requires Python and a C/C++ toolchain.

The CLI does not currently provide `devcontainer stop` or
`devcontainer down`. Do not build teardown automation around those commands.

Use the lockfile maintenance commands directly:

```sh
devcontainer outdated
devcontainer upgrade
```

`outdated` reports outdated locked Features, and `upgrade` updates them. See
[lockfiles.md](lockfiles.md) for the current filename, schema, and build flags.

## Failure handling and restricted environments

- Starting in 0.73.0, a failing lifecycle script has its output logged instead
  of hiding the diagnostic.
- Starting in 0.73.0, an OCI registry 403 response triggers reauthentication.
- Version 0.74.0 ignores `HOME` when it points to a non-writable location,
  allowing operation in restricted environments.
- Version 0.83.0 removes the previous request-body limit, so request size alone
  no longer causes rejection under that former cap.

## Workspace and host integration

- Version 0.81.0 adds an option to mount a Git worktree's common folder. Enable
  it when linked worktrees need the shared Git metadata inside the container.
- Starting in 0.82.0, Dev Container commands use the current directory as the
  workspace folder when no workspace is specified.
- Version 0.86.0 normalizes Windows drive letters to lowercase to align with
  the path form used by VS Code.
- Version 0.88.0 supports WSLc environments.

## Container-engine compatibility

### Podman

Avoid selecting `--uidmap` or `--gidmap` together with a conflicting
`--userns` mode. When running as root, omit `--userns=keep-id`. As of 0.80.0,
CLI-generated Podman invocations use `label=disable` instead of the `z` flag.

### Docker

Version 0.80.2 handles Docker 29.0.0 container `start` events after Docker
removed their deprecated fields.

With Docker Engine 23.0.0 or newer, version 0.80.3 skips downloading and
injecting `dockerfile:1.4`, because the engine package already provides that
frontend version or a later one.

### Debian images

Version 0.80.1 works with Debian `latest` images that no longer contain
`adduser` and `addgroup`.

## Build behavior

- As of 0.83.0, the container Feature build path adds
  `BUILDKIT_INLINE_CACHE`, enabling inline BuildKit cache metadata.
- As of 0.85.0, base-image and user resolution inline Buildx global build- and
  target-platform environment variables. Platform-dependent values therefore
  participate in resolution.
- Starting in 0.86.0, always parse the `devcontainer.metadata` label as a JSON
  array, even when it contains one metadata item.

## Feature reference compatibility

Version 0.79.0 redirects Feature publisher references from
`devcontainers-contrib` to `devcontainers-extra`.

As of 0.86.1, Features passed with `--additional-features` are deliberately
excluded from `.devcontainer-lock.json`. Do not expect those command-line
additions to be pinned.

From 0.87.0, `build` and `up` generate the lockfile by default:

```sh
devcontainer build --frozen-lockfile
devcontainer up --no-lockfile
```

Use `--no-lockfile` to opt out. Use `--frozen-lockfile` to require an existing
lockfile and reject changes. The older `--experimental-lockfile` and
`--experimental-frozen-lockfile` spellings remain accepted but are deprecated
and emit warnings.
