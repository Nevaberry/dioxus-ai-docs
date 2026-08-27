# CLI, Scripts, and Runtimes

Use this reference for command invocation, script behavior, initialization,
runtime provisioning, global tools, and diagnostics.

## CLI Selection and Package-Manager Declarations

### Automatic version selection (batch `2025-01`)

`manage-package-manager-versions` is enabled by default in pnpm 10, so the root
`packageManager` declaration selects the pnpm CLI. Installing `pnpm` or
`@pnpm/exe` through `pnpm add --global` fails; use `pnpm self-update`.

The declaration must not prefix its version with `v` (batch `2025-02`):

```json
{ "packageManager": "pnpm@10.4.0" }
```

When pnpm switches CLI versions it disables `managePackageManagerVersions` to
avoid another automatic switch (batch `2025-10`).

### pnpm 11 package-manager policy (batches `migration-10-to-11` and `11.0.0`)

`pmOnFail` replaces `managePackageManagerVersions`, `packageManagerStrict`, and
`packageManagerStrictVersion`. Its values are `download`, `ignore`, `warn`,
and `error`.

With `init-package-manager` enabled, `pnpm init` writes
`devEngines.packageManager` instead of `packageManager`. It may contain a
range; pnpm records and reuses a compatible resolved CLI in the lockfile.
Use `pnpm with` for a one-off pnpm version that bypasses a project pin.

pnpm 11 can self-update or switch from a package-manager declaration to the
native pnpm 12 build published under `next-12`; the installed package is the
unscoped `pnpm` package even when the old executable came from `@pnpm/exe`
(batch `11.10-11.17`).

```sh
pnpm self-update next-12
```

## Package Initialization and Setup

### Manifest shape (batches `2025-05-06`, `2025-12`, and `11.0.0`)

`pnpm init --init-type=module` creates a manifest with `"type": "module"`.
New pnpm 11 manifests use ESM by default. `pnpm init --bare` emits only the
required fields.

```sh
pnpm init --init-type=module
pnpm init --bare
```

### Shell and global setup (batches `2025-05-06` and `11.0.0`)

`pnpm setup` supports Nushell. In pnpm 11, global binaries moved to
`PNPM_HOME/bin`, so rerun setup after upgrading.

Do not run `pnpm setup`, `pnpm self-update`, or global-mutating commands under
`sudo`: they operate in root's home and warn now; pnpm 12 will reject them
with `ERR_PNPM_SUDO_NOT_SUPPORTED`. Read-only commands such as
`pnpm bin --global` are unaffected (batch `2026-08`).

## Running Package Scripts

### Argument and environment behavior (batches `2025-01` and `2025-04`)

`pnpm test` passes every following argument to the script; no `--` separator
is needed. Installation runs a project's `preprepare` and `postprepare`.
Scripts receive `npm_package_json`.

Under pnpm 10, `NODE_ENV=production` no longer controls which dependency types
are installed. Script metadata is limited to the `npm_package_*` values for
`name`, `version`, `bin`, `engines`, and `config`.

### pnpm 11 script behavior (batches `migration-10-to-11` and `11.0.0`)

A script named `clean`, `setup`, `deploy`, or `rebuild` shadows the built-in
command. Use `pnpm pm <name>` for the built-in.

Scripts whose names start with `.` are hidden from `pnpm run` and may be
invoked only from other scripts. Command banners are written as
`$ command` to stderr, leaving stdout available to pipelines. Lifecycle scripts
no longer receive config-derived `npm_config_*` variables, though well-known
`npm_*` variables remain.

User-supplied `npm_config_*` variables again reach lifecycle scripts in later
pnpm 11 releases, but this does not restore variables synthesized from pnpm
configuration (batch `11.6-11.9`).

### Select and sequence scripts (batch `11.10-11.17`)

Pass a slash-delimited regular expression to `pnpm run` to run every matching
script. `--sequential` or `-s` sets `workspaceConcurrency` to one across and
within packages.

```sh
pnpm run --sequential "/^build:.*/"
```

A non-recursive `pnpm run --no-bail` continues all matching scripts but exits
nonzero if any failed (batch `11.6-11.9`).

## Runtime Provisioning

### Project runtimes (batch `2025-07`)

`devEngines.runtime` declares Node.js, Deno, or Bun for a workspace project.
Installation resolves its range, locks the exact version and checksum, and
runs project scripts with the local runtime. `onFail` initially supported only
`download`.

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

`nodeVersion`, when used, must be an exact semantic version rather than a range
or tag (batch `2025-09`).

### Dependency-owned runtimes (batch `2025-11`)

A dependency may declare `engines.runtime`. pnpm downloads that Node.js
runtime, binds the dependency's CLI to it, and uses it for the dependency's
`postinstall` regardless of the global Node.js version.

### Runtime migration and validation

The pnpm 11 codemod moves a root `useNodeVersion` setting to
`devEngines.runtime`. Manually replace each subpackage's
`pnpm.executionEnv.nodeVersion` with that subpackage's own runtime declaration
(batch `migration-10-to-11`).

Ranges in `devEngines.runtime` and `engines.runtime` are enforced for Node.js,
Deno, and Bun when `onFail` is `warn` or `error`. Invalid resolved versions
report `ERR_PNPM_BAD_RUNTIME_VERSION` (batch `11.4-11.5`).

`pnpm runtime set <name> <version>` writes `devEngines.runtime` by default.
Use `--save-prod` or `-P` for `engines.runtime` (batch `11.4-11.5`).

```sh
pnpm runtime set node 24.0.0
pnpm runtime set node 24.0.0 --save-prod
```

`pnpm install --no-runtime`, equivalent to `runtime: false`, skips fetching and
linking declared runtimes without removing their lockfile records; frozen
validation still succeeds (batch `11.1-11.3`).

`pnpm outdated` and interactive updates include dependencies declared with
`runtime:` specifiers (batch `11.1-11.3`).

Runtime download mirrors now belong in `nodeDownloadMirrors` in
`pnpm-workspace.yaml`, replacing `node-mirror:<channel>` in `.npmrc`
(batch `11.0.0`).

## Command-Line Targeting

### Architecture overrides (batch `2025-07`)

`pnpm install`, `add`, and `dlx` accept `--cpu`, `--libc`, and `--os` to
override configured supported architectures for that command.

### dlx parsing and catalogs (batches `2025-07` and `2026-01-02`)

`pnpm dlx` recognizes its options between `dlx` and the executable, including
before `--`. `pnpm dlx` and `pnpx` also accept catalog-backed versions:

```sh
pnpm dlx shx@catalog:
```

Packages invoked through `dlx` or `create` may run their own postinstall, while
their dependencies still require `--allow-build`; see the build-security
reference.

### Short flags (batch `11.0.0`)

`-F` aliases `--filter`. Within `pnpm add`, `-d`, `-p`, `-o`, and `-e` mean
`--save-dev`, `--save-prod`, `--save-optional`, and `--save-exact`.

## Inspecting Dependencies

### Finder functions (batch `2025-09`)

Top-level `finders` in a pnpmfile define predicates for `pnpm list` and
`pnpm why`. Select one with `--find-by=<name>`. Return `true` for a match or a
string to match and display that string as extra result information.

### Lockfile and reverse-tree views (batches `2025-11` and `2026-01-02`)

`pnpm list --lockfile-only` reads the expected graph without requiring
`node_modules`. `pnpm why` places the queried package at the root and walks
through dependents back to workspace roots.

Running `pnpm view` without a package name searches upward for the nearest
manifest and queries its package name (batch `11.6-11.9`).

## Global Package Groups

pnpm 11 stores each global installation group under
`{pnpmHomeDir}/global/v11/{hash}/` with its own manifest, lockfile, and
`node_modules`. Removing one member removes the group; updating produces a new
group. `pnpm link --global` and argument-free `pnpm link` are removed; use
`pnpm add -g .` for the former workflow (batch `11.0.0`).

Space-separated names create separate groups; comma-separated names share a
group and are removed together (batch `11.1-11.3`):

```sh
pnpm add -g foo bar
pnpm add -g foo,bar qar
```

Review build scripts for global package dependencies with
`pnpm approve-builds --global` (batch `2025-02`). Select installation groups
with `pnpm update --global --interactive` (batch `2026-08`).

## Maintenance and Diagnostics

pnpm 11 adds or changes these commands (batch `11.0.0`):

- `pnpm ci` cleans workspace `node_modules` and performs a frozen install.
- `pnpm clean --lockfile` also removes the root lockfile.
- `pnpm peers check` reports lockfile peer problems.
- `pnpm runtime set` replaces `pnpm env use`.
- `pnpm pack-app` builds Node.js single-executable applications.
- `pnpm sbom` produces CycloneDX 1.7 or SPDX 2.3 JSON.

`pnpm doctor` checks installation method, global-bin `PATH`, store/cache
writability, supported link strategies, registry connectivity, and an offline
`file:` install. Failures produce a nonzero status; `--offline` skips network
checks, `--json` emits structured output, and `--benchmark` times filesystem
and install checks (batch `11.10-11.17`).

`pnpm cache path` prints the metadata cache. Cache it with the lockfile
verification log; `pnpm store prune` preserves that log (batch `2026-08`).

Reporter output from `pnpm store` and `pnpm config` subcommands goes to stderr
so stdout is safe to capture (batch `11.6-11.9`).

`pnpm version -r --json` prints `[]` when no pending release changes exist,
keeping empty and non-empty output valid JSON (batch `2026-08`).
