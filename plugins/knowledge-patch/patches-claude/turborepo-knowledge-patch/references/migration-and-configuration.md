# Migration and configuration

## Use the installed schema (since 2.4.0)

The installed `turbo` package includes `schema.json`, so editor completion and
validation can track the repository's installed version instead of the hosted
schema.

```json
{
  "$schema": "./node_modules/turbo/schema.json"
}
```

Package-level `turbo.json` files may need a relative path such as
`../../node_modules/turbo/schema.json`.

## Configure ESLint Flat Config (since 2.4.0)

`eslint-config-turbo` and `eslint-plugin-turbo` support ESLint Flat Config and
remain compatible with ESLint 8. Spread a shareable config into the exported
array:

```js
export default [
  ...turboConfig,
];
```

When using the plugin directly, register `turbo` in the flat-config `plugins`
object:

```js
export default [
  {
    plugins: { turbo },
    rules: {
      "turbo/no-undeclared-env-vars": "error",
    },
  },
];
```

## Choose JSONC or trailing commas

Configuration can use the `turbo.jsonc` filename and JSON-with-comments syntax
(since 2.5.0):

```jsonc
{
  "tasks": {
    "test": {
      // Build dependencies before testing.
      "dependsOn": ["^build"]
    }
  }
}
```

`turbo.json` itself accepts trailing commas without requiring the separate
`turbo.jsonc` filename (since 2.6.0).

```jsonc
{
  "tasks": {
    "build": {},
  },
}
```

## Extend workspace configuration (since 2.7.0)

A package-level `turbo.json` can inherit from another workspace package by
putting that package's name in `extends`. `//` still refers to the root
configuration.

```json
{
  "extends": ["//", "web"]
}
```

Put `$TURBO_EXTENDS$` in an array to keep inherited values while adding local
ones. Without this keyword, the local array replaces the inherited array.

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", ".next/**"]
    }
  }
}
```

## Enable Biome environment-variable linting (since 2.7.0)

Biome 2.3.10 and newer automatically detect Turborepo projects from repository
dependencies. The `noUndeclaredEnvVars` rule is currently in the nursery group
and must be enabled explicitly. It catches environment-variable use that could
produce incorrect cache hits.

```json
{
  "linter": {
    "rules": {
      "nursery": {
        "noUndeclaredEnvVars": "error"
      }
    }
  }
}
```

## Add informational task descriptions (since 2.8.0)

Task definitions accept a `description` field for human and tool context. The
description does not affect task execution.

```json
{
  "tasks": {
    "build": {
      "description": "Compiles TypeScript and bundles the application",
      "outputs": ["dist/**"]
    }
  }
}
```

## Opt into individual Future Flags (since 2.9.0)

Future Flags are enabled independently under `futureFlags`. Enabling any one
affects the global hash.

- `globalConfiguration` moves formerly top-level global settings under
  `global`.
- `affectedUsingTaskInputs` makes `--affected` select individual tasks by
  their `inputs` rather than every task in a changed package.
- `watchUsingTaskInputs` makes `turbo watch` rerun only tasks whose `inputs`
  match changed files.
- `filterUsingTasks` resolves filters at task level, using `inputs` for Git
  ranges and the Task Graph for `...` traversal.
- `pruneIncludesGlobalFiles` copies files matched by `globalDependencies` into
  `turbo prune` output.
- `errorsOnlyShowHash` includes task hashes with `outputLogs: "errors-only"`.
- `longerSignatureKey` requires `TURBO_REMOTE_CACHE_SIGNATURE_KEY` to contain
  at least 32 bytes.
- `experimentalObservability` gates the OpenTelemetry configuration.

## Remove daemon settings (since 2.9.0)

`turbo run` and `turbo watch` no longer use the daemon. `TURBO_DAEMON`, the
`--daemon` and `--no-daemon` flags, and the `daemon` configuration key are
deprecated because they no longer have a role.

## Migrate interfaces that warn in 2.9.0

These interfaces still work in 2.9 but warn and should be migrated before the
next major release:

- `turbo scan` is obsolete and has no replacement.
- Replace `--parallel` with task-level `persistent` and `with`.
- Replace `--no-cache` with `--cache=local:r,remote:r`.
- Replace `TURBO_REMOTE_ONLY` and `--remote-only` with `--cache=remote:rw`.
- Replace `TURBO_REMOTE_CACHE_READ_ONLY` and `--remote-cache-read-only` with
  `--cache=local:rw,remote:r`.
- Replace `.png`, `.jpg`, or `.pdf` `--graph` output with `.svg`, `.html`,
  `.mermaid`, or `.dot`.
- Replace `.json` graph output with `turbo query`.
- Replace `turbo prune --scope web` with `turbo prune web`.
- Replace deprecated `turbo-ignore` with `turbo query affected`.

## Run catalog-aware migrations (since 2.10.0)

The migration codemod handles package-manager catalogs when upgrading a
repository.

```bash
npx @turbo/codemod migrate
```

## Resolve remote base refs in GitHub Actions (since 2.10.8)

Turborepo can resolve GitHub Actions remote base refs when the corresponding
Future Flag is enabled. This allows Git-based comparisons to use a base ref
that is not already available locally.
