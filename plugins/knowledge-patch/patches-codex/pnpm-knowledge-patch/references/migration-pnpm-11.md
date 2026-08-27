# Migrating from pnpm 10 to pnpm 11

## Run the codemod (migration-10-to-11)

From the project root, run the v10-to-v11 codemod to relocate supported settings and update the root `packageManager` declaration.

```sh
pnpx codemod run pnpm-v10-to-v11
```

Review the result against the topic guides because some changes require manual work.

## Configuration checklist (migration-10-to-11)

- Move non-authentication and non-registry settings to camelCase keys in `pnpm-workspace.yaml`; pnpm 11 does not read `package.json#pnpm`, and `.npmrc` is limited to authentication and registries. See [configuration-hooks.md](configuration-hooks.md).
- Replace `managePackageManagerVersions`, `packageManagerStrict`, and `packageManagerStrictVersion` with `pmOnFail`.
- Rename configuration environment variables from `npm_config_*` to `pnpm_config_*`.
- Replace each `auditConfig.ignoreCves` entry manually with the matching GHSA from the **More info** column of `pnpm audit`; the codemod renames the key to `auditConfig.ignoreGhsas` but cannot translate values. See [security-audit-sbom.md](security-audit-sbom.md).
- Fix or remove dependencies whose patches fail; `ignorePatchFailures` is gone and all failures throw.
- The codemod converts root `useNodeVersion` to `devEngines.runtime`. In subpackages, manually replace `package.json#pnpm.executionEnv.nodeVersion` with that package's `devEngines.runtime`. See [runtimes-scripts-cli.md](runtimes-scripts-cli.md).

## Command changes (migration-10-to-11)

`pnpm link <pkg-name>` no longer resolves through the global store. Pass a relative or absolute filesystem path.

```sh
pnpm link ./foo
```

Argument-free `pnpm install -g` is unsupported; use `pnpm add -g <pkg>` for a named package. `pnpm server` is removed without a replacement.

If a package defines `clean`, `setup`, `deploy`, or `rebuild`, `pnpm <name>` runs the package script. Use `pnpm pm <name>` to force the built-in command.

```sh
pnpm pm deploy
```

## Runtime and executable requirements (11.0.0)

pnpm 11 requires Node.js 22 or newer and is pure ESM. Its standalone executable additionally requires glibc 2.27 or newer.

## Default policy changes (11.0.0)

The defaults are:

```yaml
minimumReleaseAge: 1440
minimumReleaseAgeStrict: false
blockExoticSubdeps: true
strictDepBuilds: true
optimisticRepeatInstall: true
verifyDepsBeforeRun: install
```

Set `minimumReleaseAge: 0` to opt out of the one-day publication delay.

## Removed legacy build settings (11.0.0)

`onlyBuiltDependencies`, `onlyBuiltDependenciesFile`, `neverBuiltDependencies`, `ignoredBuiltDependencies`, and `ignoreDepScripts` are unsupported. Replace them with `allowBuilds`; see [build-scripts.md](build-scripts.md).

## Registry command implementation changes (11.0.0)

`publish`, `view`, `login`, `logout`, `deprecate`, `unpublish`, `dist-tag`, `version`, `search`, `star`, and `whoami` are native rather than npm CLI passthroughs. `access`, `bugs`, `edit`, `issues`, `owner`, `prefix`, `profile`, `pkg`, `repo`, `set-script`, `team`, `token`, and `xmas` throw “not implemented” in this batch. Publishing reads OTPs from `PNPM_CONFIG_OTP`, prompts when required, and supports QR-code and URL web authentication.

## Global installation migration (11.0.0)

Each `pnpm add -g` installation group has its own manifest, lockfile, and `node_modules` under `{pnpmHomeDir}/global/v11/{hash}/`. Removing one package removes its group, and updating creates a new group. Global binaries moved to `PNPM_HOME/bin`, so run `pnpm setup` after upgrading. `pnpm link --global` and argument-free `pnpm link` are removed; use `pnpm add -g .` in place of the former.

## New command replacements and utilities (11.0.0)

- `pnpm ci` cleans workspace `node_modules` and performs a frozen-lockfile install.
- `pnpm clean --lockfile` also removes `pnpm-lock.yaml`.
- `pnpm sbom` emits CycloneDX 1.7 or SPDX 2.3 JSON.
- `pnpm peers check` inspects lockfile peer issues.
- `pnpm runtime set` replaces `pnpm env use`.
- `pnpm with` runs a one-off pnpm version and bypasses `packageManager` pins.
- `pnpm pack-app` creates Node.js SEA executables.

## Initialization and package-manager declarations (11.0.0)

With `init-package-manager` enabled, `pnpm init` writes `devEngines.packageManager` rather than `packageManager`. New packages default to `"type": "module"`. `devEngines.packageManager` accepts ranges; the resolved version is stored in `pnpm-lock.yaml` and reused while compatible.

## Script and environment review (11.0.0)

Command scripts print `$ command` to stderr so stdout remains pipe-friendly and show project identity only when running elsewhere. Lifecycle scripts no longer receive config-derived `npm_config_*` values, although well-known `npm_*` variables remain. See [runtimes-scripts-cli.md](runtimes-scripts-cli.md) for script invocation changes.
