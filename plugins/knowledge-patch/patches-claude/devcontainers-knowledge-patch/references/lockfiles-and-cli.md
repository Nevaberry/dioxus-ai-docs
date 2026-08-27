# Feature Lockfiles and CLI

## Current filename and generation

The current generated Feature lockfile is `.devcontainer-lock.json`, including
the leading dot, and it sits beside `devcontainer.json`
(`cli-current-usage`). Earlier guidance in `lockfile-stable` and `cli-2026`
used the undotted `devcontainer-lock.json` spelling; use the current dotted
filename.

Starting with CLI 0.87.0, `build` and `up` generate the lockfile by default
(`cli-2026`).

```sh
devcontainer build --frozen-lockfile
devcontainer up --no-lockfile
```

- `--frozen-lockfile` requires an existing lockfile and fails if the operation
  would change it.
- `--no-lockfile` disables generation.
- Deprecated `--experimental-lockfile` and
  `--experimental-frozen-lockfile` flags remain accepted but emit a warning.
- As of CLI 0.86.1, Features supplied with `--additional-features` are not
  written to the lockfile and are not pinned there.

## Lockfile purpose and coverage

The `lockfile-stable` format pins OCI and tarball Features for reproducible,
cache-stable builds. Checksums detect a release artifact that changed after
publication.

The lockfile does not record:

- Local Features
- Deprecated GitHub Releases Features
- Features passed through `--additional-features`

## Record format

The top-level `features` object uses lowercased Feature references as keys. Each
record contains:

- `version`: the full selected version
- `resolved`: an OCI digest-qualified Feature ID or an HTTPS tarball URL
- `integrity`: the artifact checksum in `sha256:<hex>` form

```json
{
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "1.0.4",
      "resolved": "ghcr.io/devcontainers/features/node@sha256:567d704b3f4d3eca3acee51ded7c460a8395436d135d53d1175fb565daff42b8",
      "integrity": "sha256:567d704b3f4d3eca3acee51ded7c460a8395436d135d53d1175fb565daff42b8"
    }
  }
}
```

A record can include `dependsOn`, an array of lowercased Feature identifiers.
Keep any version or checksum suffix in those identifiers. Every dependency in
the array must also have its own record. Omit `dependsOn` when it would be empty.

## Maintenance commands

Use the current CLI maintenance commands from `cli-current-usage`:

```sh
devcontainer outdated
devcontainer upgrade
```

`outdated` reports lockfile Features with available updates. `upgrade` updates
them.

## Standalone CLI installation

The standalone installer supports Linux and macOS on x64 and arm64. It
downloads its own Node.js runtime, so Node.js does not need to be preinstalled.
Its default destination is `$HOME/.devcontainers/bin`.

```sh
curl -fsSL https://raw.githubusercontent.com/devcontainers/cli/main/scripts/install.sh | sh
export PATH="$HOME/.devcontainers/bin:$PATH"
```

Installer controls:

- `--version`
- `--prefix`
- `--update`
- `--uninstall`

The npm installation alternative requires Python and a C/C++ toolchain.

## Teardown limitation

The CLI currently has no `devcontainer stop` or `devcontainer down` command
(`cli-current-usage`). Scripts that need teardown must use the appropriate
container engine or Compose command instead of assuming those subcommands exist.
