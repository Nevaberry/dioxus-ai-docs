# Configuration, Patches, and Hooks

## Config dependencies (2025-01)

`pnpm.configDependencies` are installed before ordinary, development, and optional dependencies. Each entry uses an exact version plus an integrity checksum. At this stage, config dependencies cannot have dependencies or lifecycle scripts of their own.

```json
{
  "pnpm": {
    "configDependencies": {
      "my-configs": "1.0.0+sha512-30iZtAPgz+LTIYoeivqYo853f02jBYSd5uGnGpkFV0M3xOt9aN73erkgYAmZU43x4VfqcnLxW9Kpg3R5LC4YYw=="
    }
  }
}
```

## Workspace settings without package globs (2025-02)

Settings formerly under `pnpm` in `package.json` may instead be top-level keys in `pnpm-workspace.yaml`. The workspace file no longer requires `packages`, so it may exist only to hold settings such as build approvals.

```yaml
onlyBuiltDependencies:
  - esbuild
  - fuse-native
```

## Full workspace configuration (2025-03)

`pnpm-workspace.yaml` accepts every `.npmrc` setting as a camelCase key. Environment variables may appear in setting names and values. `pnpm config get` and `pnpm config list` include these workspace settings; `pnpm config set --location=project` writes to `pnpm-workspace.yaml` when the directory has no `.npmrc`.

```yaml
verifyDepsBeforeRun: install
optimisticRepeatInstall: true
publicHoistPattern:
  - "*types*"
  - "!@types/react"
```

## Version-selected patches (2025-03)

`patchedDependencies` accepts name-only, range, and exact-version keys. Exact versions override ranges, and ranges override name-only entries. Ranges should not overlap. `foo@*` matches like a name-only key except that application failures are not ignored.

```yaml
patchedDependencies:
  foo: patches/foo-1.patch
  foo@^2.0.0: patches/foo-2.patch
  foo@2.1.0: patches/foo-3.patch
```

`pnpm.allowNonAppliedPatches` was renamed to `pnpm.allowUnusedPatches`; the old name remains supported with a deprecation warning.

`ignorePatchFailures` is tri-state in this version line. Unset means exact-version or range patch failures are errors and name-only failures are ignored. `false` makes every failure an error; `true` makes every failure a warning.

```yaml
ignorePatchFailures: false
```

## Configuration and local pnpmfile hooks (2025-04)

The experimental `hooks.updateConfig` hook in `.pnpmfile.cjs` can rewrite pnpm settings. Local pnpmfiles may also define `preResolution`, `importPackage`, and `fetchers` hooks.

```js
module.exports = {
  hooks: {
    updateConfig: (config) => ({
      ...config,
      nodeLinker: "hoisted",
    }),
  },
};
```

Use `pnpm add --config` to install a configurational dependency without manually constructing its exact-version, checksummed entry.

```sh
pnpm add --config my-config@1.0.0
```

## Multiple and plugin-provided pnpmfiles (2025-07, 2025-08)

The `pnpmfile` setting accepts a list of hook files. Config dependencies named `@pnpm/plugin-*` or `pnpm-plugin-*` load their `pnpmfile.cjs` automatically in alphabetical order; list files explicitly when order matters. A config dependency named `@scope/pnpm-plugin-*` is also discovered automatically.

```yaml
pnpmfile:
  - ./hooks/first.pnpmfile.cjs
  - ./hooks/second.pnpmfile.cjs
```

## Structured config paths and JSON values (2025-08)

`pnpm config get` and `pnpm config set` accept property paths, including leading-dot and bracket notation. Object retrieval defaults to INI strings. Use `--json` to serialize retrieved values as JSON or parse values being set as JSON.

```sh
pnpm config get catalog.react
pnpm config get 'packageExtensions["@babel/parser"].peerDependencies["@babel/types"]'
pnpm config set .ignoreScripts true
pnpm config get --json catalog
```

## Customize manifests before packing (2026-01-02)

The `.pnpmfile.cjs` `beforePacking` hook runs immediately before `pnpm pack` or `pnpm publish` creates a tarball. It returns the manifest to publish without modifying the local `package.json`.

```js
module.exports = {
  hooks: {
    beforePacking(pkg) {
      delete pkg.devDependencies
      return pkg
    }
  }
}
```

## Preserve workspace-file formatting (2026-03)

When pnpm updates `pnpm-workspace.yaml`, it preserves comments, string formatting, and whitespace.

## Authoritative pnpm 11 configuration (migration-10-to-11)

pnpm 11 no longer reads the `pnpm` field in `package.json`, and `.npmrc` is limited to authentication and registry settings. Put other settings in `pnpm-workspace.yaml` as camelCase keys. The codemod places settings from a subproject's `.npmrc` under `packageConfigs["<project-name>"]`.

`managePackageManagerVersions`, `packageManagerStrict`, and `packageManagerStrictVersion` are replaced by `pmOnFail`, whose values are `download`, `ignore`, `warn`, and `error`.

```yaml
pmOnFail: download
```

pnpm 11 removes `ignorePatchFailures`; every failed dependency patch throws. Fix the patch or remove the affected dependency.

pnpm 11 ignores `npm_config_*` configuration environment variables. Rename them to `pnpm_config_*` in CI, shell profiles, containers, and other configuration sources.

## ESM pnpmfiles (11.0.0)

Hooks may be defined in `.pnpmfile.mjs`. If both formats exist, `.mjs` takes precedence over `.pnpmfile.cjs`, and only one file is loaded.

## Pacquet config dependency (11.1-11.3, 11.6-11.9)

Installing `@pnpm/pacquet` as a config dependency delegates install materialization to pacquet while pnpm retains dependency resolution. As of 11.2.2, `install`/`i` flags are forwarded, but flags from `add`, `update`, and `dedupe` are not.

```sh
pnpm add @pnpm/pacquet --config
```

Config dependencies may install one level of `optionalDependencies`, filtered by `os`, `cpu`, and `libc`. These optional dependencies require exact versions, and the environment lockfile records every platform variant.

With pacquet 0.11.7 or newer, a plain non-frozen install using the isolated linker delegates resolution and materialization to pacquet. `add`, `update`, and `remove` still resolve through pnpm; older pacquet versions retain the resolve-then-materialize split.

## Delegate custom fetches (11.10-11.17)

A custom fetcher exported from a pnpmfile may return `{ delegate: <resolution> }`, causing pnpm to rewrite the resolution and invoke its built-in fetcher. This is the portable delegation form for pacquet, where hook code cannot receive `cafs` and `fetchers`.

```js
return { delegate: resolution }
```

## Update and audit sections (11.10-11.17)

Top-level `update` and `audit` sections replace `updateConfig`, `auditConfig`, and `auditLevel`. Deprecated keys work until the next major, but new values win when both forms are present. Use `update.ignoreDeps`, `audit.level`, and `audit.ignore`.

```yaml
update:
  ignoreDeps:
    - webpack
    - "@babel/*"
audit:
  level: high
  ignore:
    - GHSA-xxxx-yyyy-zzzz
```

## Machine-level paths are not project settings (2026-08)

`pnpm-workspace.yaml` cannot set `bin`, `configDir`, `dir`, `globalBinDir`, `globalDir`, `npmrcAuthFile`, `pnpmHomeDir`, `stateDir`, `userconfig`, or `workspaceDir`; pnpm ignores them with a warning. `cacheDir` and `storeDir` remain valid there. Project-targeted `pnpm config set` rejects those writes with `ERR_PNPM_CONFIG_SET_NOT_A_PROJECT_SETTING`; `--config.*` aliases cannot bypass the boundary. Dedicated flags such as `--global-dir` still work, and `pnpm config delete` can remove stale keys.
