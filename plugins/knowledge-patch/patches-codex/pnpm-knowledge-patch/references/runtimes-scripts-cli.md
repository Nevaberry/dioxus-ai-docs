# Runtimes, Scripts, Initialization, and CLI Behavior

## Package-manager version selection (2025-01, 2025-02, 2025-10)

`manage-package-manager-versions` is enabled by default in pnpm 10, so pnpm selects its own version from the root `packageManager` field. Global installation of `pnpm` or `@pnpm/exe` with `pnpm add --global` fails; use `pnpm self-update`.

```json
{
  "packageManager": "pnpm@10.1.0"
}
```

The version must not have a `v` prefix: use `pnpm@10.4.0`, not `pnpm@v10.4.0`.

When pnpm switches to another CLI version, it sets `managePackageManagerVersions` to `false` to prevent subsequent automatic switches.

## Script arguments and lifecycle environment (2025-01, 2025-04)

`pnpm test` passes all arguments after `test` directly to the script, matching `pnpm run test`; no separator is required.

```sh
pnpm test --watch
```

`pnpm install` executes a project's `preprepare` and `postprepare` scripts. Scripts receive only the `npm_package_*` values for `name`, `version`, `bin`, `engines`, and `config`, and executed scripts also receive `npm_package_json`.

## Initialization and shell setup (2025-05-06)

`pnpm init --init-type=module` creates a manifest with `"type": "module"`; `init-type=module` is also accepted as a setting. `pnpm setup` can configure pnpm for Nushell.

```sh
pnpm init --init-type=module
```

## Lockfile-pinned project runtimes (2025-07)

`devEngines.runtime` provisions Node.js, Deno, or Bun per workspace project. `pnpm install` resolves the range, records an exact version and checksum in the lockfile, and runs scripts with the local runtime. `onFail` supports only `download` in this batch.

```json
{
  "devEngines": {
    "runtime": {
      "name": "node",
      "version": "^24.4.0",
      "onFail": "download"
    }
  }
}
```

## Per-command architecture and `dlx` parsing (2025-07)

`pnpm install`, `pnpm add`, and `pnpm dlx` accept `--cpu`, `--libc`, and `--os` to override `supportedArchitectures`. `pnpm dlx` parses flags between `dlx` and the executed command, including before `--`.

## Finder functions (2025-09)

Top-level `.pnpmfile.cjs` `finders` define predicates for `pnpm list` and `pnpm why`; select one with `--find-by=<name>`. A finder returns `true`, or returns a string to match and print as extra result information.

```js
module.exports = {
  finders: {
    react17: (ctx) =>
      ctx.readManifest().peerDependencies?.react === "^17.0.0",
  },
};
```

```sh
pnpm why --find-by=react17
```

## Exact `nodeVersion` (2025-09)

`nodeVersion` must be an exact semantic version; ranges and tags cause an error.

```yaml
nodeVersion: 22.20.0
```

## Dependency-declared runtimes (2025-11)

A dependency may declare `engines.runtime`. pnpm installs the requested Node.js version, binds the dependency's CLI to it, and uses it for the dependency's `postinstall`, regardless of the global Node.js version.

```json
{
  "engines": {
    "runtime": {
      "name": "node",
      "version": "^24.11.0",
      "onFail": "download"
    }
  }
}
```

## Bare initialization (2025-12)

`pnpm init --bare` creates a `package.json` with only required fields.

```sh
pnpm init --bare
```

## Reverse dependency output (2026-01-02)

`pnpm why` places the searched package at the root and walks through dependents back to workspace roots, replacing the former forward dependency-tree output.

## pnpm 11 runtime declaration migration (migration-10-to-11)

The codemod converts root `useNodeVersion` to `devEngines.runtime`. In each workspace subpackage, manually replace `package.json#pnpm.executionEnv.nodeVersion` with that package's `devEngines.runtime`.

## pnpm 11 global installs and commands (migration-10-to-11, 11.0.0)

Argument-free `pnpm install -g` is unsupported; use `pnpm add -g <pkg>`. `pnpm server` is removed without replacement.

Package scripts named `clean`, `setup`, `deploy`, or `rebuild` shadow built-ins. Use `pnpm pm <name>` for the built-in.

Each global install group has a separate manifest, lockfile, and `node_modules` at `{pnpmHomeDir}/global/v11/{hash}/`. Removing one package removes its group; updating creates a new group. Global binaries are in `PNPM_HOME/bin`, so run `pnpm setup` after upgrading. `pnpm link --global` and argument-free `pnpm link` are removed; use `pnpm add -g .` for the former.

## Script output and environments (11.0.0, 11.6-11.9)

Command scripts print `$ command` to stderr, keeping stdout pipe-friendly, and show project identity only when running in another directory. Lifecycle scripts do not receive config-derived `npm_config_*` values, though well-known `npm_*` values remain.

User-supplied `npm_config_*` values such as `npm_config_platform_arch` again reach lifecycle scripts in 11.6-11.9. This does not restore config-derived variables.

Reporter output from `pnpm store` and `pnpm config` subcommands also goes to stderr so scripts can capture stdout without progress text.

## Package-manager declarations and initialization (11.0.0)

With `init-package-manager`, `pnpm init` writes `devEngines.packageManager` instead of `packageManager`; new packages default to `"type": "module"`. `devEngines.packageManager` accepts ranges, stores the resolved version in `pnpm-lock.yaml`, and reuses it while compatible.

## Hidden scripts and short flags (11.0.0)

Scripts beginning with `.` can only be called by other scripts and are omitted from `pnpm run`. `-F` aliases `--filter`. For `pnpm add`, `-d`, `-p`, `-o`, and `-e` mean `--save-dev`, `--save-prod`, `--save-optional`, and `--save-exact`.

## Runtime download mirrors (11.0.0)

Use `nodeDownloadMirrors` in `pnpm-workspace.yaml`; it replaces `.npmrc`'s `node-mirror:<channel>`.

```yaml
nodeDownloadMirrors:
  release: https://my-mirror.example.com/download/release/
```

## Skip lockfile-managed runtimes (11.1-11.3)

`pnpm install --no-runtime` (`runtime: false`) skips fetching and linking `devEngines.runtime` runtimes without removing lockfile entries, so frozen-lockfile validation still succeeds.

## Global installation groups (11.1-11.3)

Space-separated `pnpm add -g` arguments create independent groups. Comma-separated names share one group and are removed together.

```sh
pnpm add -g foo bar
pnpm add -g foo,bar qar
```

## Runtime-aware update reports (11.1-11.3)

`pnpm outdated` and `pnpm update --interactive` include Node.js, Deno, and Bun project dependencies declared with `runtime:` specifiers.

## Save development or production runtimes (11.4-11.5)

`pnpm runtime set <name> <version>` writes `devEngines.runtime` by default. Use `--save-prod` or `-P` for `engines.runtime`.

```sh
pnpm runtime set node 24.0.0
pnpm runtime set node 24.0.0 --save-prod
```

Ranges in `devEngines.runtime` and `engines.runtime` are enforced for Node.js, Deno, and Bun when `onFail` is `error` or `warn`; invalid versions report `ERR_PNPM_BAD_RUNTIME_VERSION`.

## Aggregate script failure (11.6-11.9)

Non-recursive `pnpm run --no-bail` continues through all matched scripts but exits nonzero if any fail.

## Upgrade to the native pnpm 12 build (11.10-11.17)

pnpm 11's self-updater and `packageManager` switching can install the Rust pnpm 12 build from `next-12`. The installed package is unscoped `pnpm`, including upgrades from `@pnpm/exe`.

```sh
pnpm self-update next-12
```

## Diagnose pnpm (11.10-11.17)

`pnpm doctor` checks installation method, global-bin `PATH`, store and cache writability, filesystem link strategies, registry connectivity, and an offline `file:` install. It exits nonzero on failures. `--offline`, `--json`, and `--benchmark` skip network checks, produce machine-readable output, or time filesystem and install checks.

```sh
pnpm doctor --json
```

## Select scripts by regular expression (11.10-11.17)

`pnpm run` accepts a slash-delimited regular expression. `--sequential` (`-s`) forces `workspaceConcurrency` to one for matched scripts across and within packages.

```sh
pnpm run --sequential "/^build:.*/"
```

## Global updates and `sudo` (2026-08)

`pnpm update --global --interactive` selects global installation groups interactively.

```sh
pnpm update --global --interactive
```

Running `pnpm setup`, `pnpm self-update`, or a global-mutating command through `sudo` warns because it operates in root's home. pnpm 12 will reject this with `ERR_PNPM_SUDO_NOT_SUPPORTED`. Read-only global commands such as `pnpm bin --global` are unaffected.
