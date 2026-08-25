# Feature Authoring

Source batch: `feature-authoring`.

## Package and installer contract

A Feature directory must contain:

- `devcontainer-feature.json`
- Executable `install.sh`

Other package files are included alongside them. Only `id`, `version`, and
`name` are required in the manifest. The `id` must match the directory name and
should be lowercase. The installer is invoked directly as root during the image
build.

## Options and installer environment

Feature options support only `string` and `boolean`.

- `proposals` supplies suggested values but permits free-form input.
- `enum` restricts input to its declared values.

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
`install.sh`, including the default of an omitted option.

To derive the installer variable from an option ID:

1. Replace non-word characters with `_`.
2. Replace a leading run of digits or underscores with one `_`.
3. Uppercase the result.

For example, `tool-version` becomes `$TOOL_VERSION`.

## Manifest environment timing

The manifest's `containerEnv` values are emitted as Dockerfile `ENV`
instructions before that Feature's installer executes. They are available both
during installation and in the resulting container.

## Target users from a root installer

`install.sh` runs as root but receives:

- `_CONTAINER_USER`
- `_REMOTE_USER`
- `_CONTAINER_USER_HOME`
- `_REMOTE_USER_HOME`

When no `remoteUser` is configured, the remote-user variables identify the
container user. Use these values when files, ownership, or configuration belong
to the eventual development account.

## Lifecycle contributions

A Feature manifest can contribute:

- `onCreateCommand`
- `updateContentCommand`
- `postCreateCommand`
- `postStartCommand`
- `postAttachCommand`

At each lifecycle stage, Feature contributions run sequentially in Feature
installation order. All Feature contributions finish before the matching user
command from `devcontainer.json`.

## Stable per-container resources

`${devcontainerId}` can appear in `entrypoint`, `mounts`, and `customizations`.
It is unique for a container on one host and remains stable across rebuilds.

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

Do not use `${devcontainerId}` in image-build inputs. It is unavailable when an
image is prebuilt.

## Hard dependencies

`dependsOn` is an object with the same Feature-reference and options shape as
the `features` property in `devcontainer.json`. It:

- Recursively adds required Features.
- Accepts options.
- Honors version and digest pins.
- Resolves a local path relative to the directory containing the active
  `devcontainer.json`.
- Fails creation for an unresolvable or circular dependency.

```json
{
  "dependsOn": {
    "ghcr.io/example/features/runtime:1": {
      "extensions": true
    }
  }
}
```

## Soft ordering

`installsAfter` is a non-recursive array of unversioned Feature IDs. It only
reorders matching Features already queued by user configuration or `dependsOn`.
It does not install missing Features.

```json
{
  "installsAfter": [
    "ghcr.io/example/features/base"
  ]
}
```

Entries cannot contain options, tags, or digests.

## User order overrides

`overrideFeatureInstallOrder` in `devcontainer.json` gives earlier IDs priority
only after their hard and soft dependencies have been installed.

Its entries cannot contain options, tags, or digests. An order inconsistent
with the dependency graph must fail instead of pulling a Feature ahead of one
of its dependencies.

## Distinct instances and idempotency

Feature equality includes exact package contents and option values. The same
Feature requested with different options is installed as distinct instances.
Local Features are always treated as unique.

An installer must therefore be idempotent. Package installation, configuration
edits, and shared-state changes must compose safely when several instances run.

## Rename and release continuity

To rename a Feature within a namespace:

1. Rename its folder.
2. Change its `id` to match.
3. Add the former ID to `legacyIds`.
4. Bump the version.
5. Republish.

Continue the existing semantic-version series rather than restarting at
`1.0.0`. Release tooling does not overwrite an already published exact version,
and it republishes the corresponding major and minor aliases.
