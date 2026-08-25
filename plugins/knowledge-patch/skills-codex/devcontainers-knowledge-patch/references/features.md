# Feature Authoring

## Package and installer contract

A Feature directory must contain:

- `devcontainer-feature.json`
- An executable `install.sh`

Package any other files in the directory alongside those two. The manifest
requires only `id`, `version`, and `name`. Make `id` match the directory name
and prefer lowercase. The image build invokes `install.sh` directly as root.

## Options and installer variables

Options support only `string` and `boolean`.

- Use `proposals` to suggest values while still accepting free-form input.
- Use `enum` to enforce a closed set of values.

```json
{
  "options": {
    "tool-version": {
      "type": "string",
      "proposals": ["latest", "1"],
      "default": "latest"
    }
  }
}
```

Every option is written to `devcontainer-features.env` and sourced for
`install.sh`. This includes the default for an omitted option.

To derive the installer variable name from the option ID:

1. Replace every non-word character with `_`.
2. Replace a leading run of digits or underscores with one `_`.
3. Uppercase the result.

For example, read the `tool-version` option from `$TOOL_VERSION`.

## Environment and user identity during installation

A Feature manifest's `containerEnv` entries become Dockerfile `ENV`
instructions before that Feature's installer runs. They are therefore
available during installation and remain in the built container.

Although `install.sh` runs as root, use these variables to target configured
accounts and home directories:

- `_CONTAINER_USER`
- `_REMOTE_USER`
- `_CONTAINER_USER_HOME`
- `_REMOTE_USER_HOME`

If `remoteUser` is absent, the remote-user variables identify the container
user.

## Lifecycle contributions

A Feature may contribute:

- `onCreateCommand`
- `updateContentCommand`
- `postCreateCommand`
- `postStartCommand`
- `postAttachCommand`

At each stage, execute Feature contributions sequentially in Feature
installation order. Finish all Feature contributions before running the
corresponding command from `devcontainer.json`.

## Stable per-container resources

Use `${devcontainerId}` in `entrypoint`, `mounts`, and `customizations` to
create resource names that are unique on a container host and stable across
rebuilds:

```json
{
  "mounts": [
    {
      "source": "tool-cache-${devcontainerId}",
      "target": "/var/cache/tool",
      "type": "volume"
    }
  ]
}
```

Do not use `${devcontainerId}` in image-build inputs. It is unavailable when
an image is prebuilt.

## Hard dependencies

`dependsOn` is an object with the same Feature-reference and options shape as
the `features` object in `devcontainer.json`.

```json
{
  "dependsOn": {
    "ghcr.io/example/features/runtime:1": {
      "extensions": true
    }
  }
}
```

It recursively installs required Features and honors version or digest pins.
Resolve a local dependency path relative to the directory containing the
active `devcontainer.json`. Fail creation for an unresolved or circular hard
dependency.

## Soft ordering

`installsAfter` is a non-recursive array of unversioned Feature IDs:

```json
{
  "installsAfter": [
    "ghcr.io/example/features/base"
  ]
}
```

It reorders only matching Features already queued by user configuration or
`dependsOn`. It does not install a missing Feature and does not accept options,
tags, or digests.

## User order overrides

`overrideFeatureInstallOrder` in `devcontainer.json` gives earlier IDs higher
priority only after their hard and soft dependencies have been installed. Its
entries cannot contain options, tags, or digests.

Reject an override that conflicts with the dependency graph. Do not move a
Feature ahead of one of its dependencies.

## Repeated and distinct instances

Feature identity includes exact package contents and option values. Requests
for the same Feature with different options install distinct instances. Local
Features are always considered unique.

Make installation and shared-state changes idempotent so multiple instances
compose safely.

## Renaming and release continuity

To rename a Feature within a namespace:

1. Rename its directory and manifest `id`.
2. Add the former ID to `legacyIds`.
3. Bump the version.
4. Republish it.

Continue the existing semantic-version sequence instead of restarting at
`1.0.0`. Release tooling does not overwrite an exact version that was already
published and republishes the matching major and minor aliases.
