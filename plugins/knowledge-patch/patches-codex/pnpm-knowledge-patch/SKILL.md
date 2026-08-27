---
name: pnpm-knowledge-patch
description: pnpm
version: "11.17.0"
license: MIT
metadata:
  author: Nevaberry
---


# pnpm Knowledge Patch

Use this skill for pnpm configuration, installation, workspaces, dependency security, runtime management, publishing, and migration work. Match guidance to the project's pnpm version, especially for settings or commands that pnpm 11 removed or relocated.

## Reference index

| Reference | Topics |
| --- | --- |
| [build-scripts.md](references/build-scripts.md) | Dependency lifecycle-script blocking, review, approvals, and `allowBuilds` |
| [configuration-hooks.md](references/configuration-hooks.md) | Workspace configuration, config dependencies, patches, pnpmfiles, and hooks |
| [installs-lockfiles-store.md](references/installs-lockfiles-store.md) | Installs, integrity, lockfiles, linkers, hoisting, and stores |
| [migration-pnpm-11.md](references/migration-pnpm-11.md) | pnpm 10-to-11 codemod, removals, default changes, and migration checklist |
| [registries-auth-publishing.md](references/registries-auth-publishing.md) | Registries, credentials, authentication, packing, and publishing |
| [release-management.md](references/release-management.md) | Changes, recursive versioning, release lanes, epics, and update intents |
| [runtimes-scripts-cli.md](references/runtimes-scripts-cli.md) | JavaScript runtimes, script behavior, initialization, globals, and CLI changes |
| [security-audit-sbom.md](references/security-audit-sbom.md) | Release-age policy, trust, audit, signature checks, and SBOM output |
| [workspaces-catalogs-deploy.md](references/workspaces-catalogs-deploy.md) | Workspaces, catalogs, peer resolution, recursive tasks, and deployment |

## Breaking changes and migration

### Start a pnpm 11 migration

Run the codemod from the project root:

```sh
pnpx codemod run pnpm-v10-to-v11
```

Then review the changes that require manual work:

- Move all settings except authentication and registry settings to camelCase keys in `pnpm-workspace.yaml`.
- Replace `managePackageManagerVersions`, `packageManagerStrict`, and `packageManagerStrictVersion` with `pmOnFail`.
- Rename configuration environment variables from `npm_config_*` to `pnpm_config_*`.
- Replace CVE entries under `auditConfig.ignoreCves` with GHSA entries under `auditConfig.ignoreGhsas`; the codemod cannot translate the identifiers.
- Fix or remove failed dependency patches; `ignorePatchFailures` is removed.
- Convert root `useNodeVersion` and subpackage `pnpm.executionEnv.nodeVersion` declarations to `devEngines.runtime`.
- Replace legacy dependency-build settings with `allowBuilds`.

pnpm 11 requires Node.js 22 or newer. Its standalone executable also requires glibc 2.27 or newer.

### Account for changed defaults

pnpm 11 defaults include:

```yaml
minimumReleaseAge: 1440
minimumReleaseAgeStrict: false
blockExoticSubdeps: true
strictDepBuilds: true
optimisticRepeatInstall: true
verifyDepsBeforeRun: install
```

Set `minimumReleaseAge: 0` to opt out of the one-day release-age delay.

### Replace removed or changed commands

- Use a filesystem path with `pnpm link`, such as `pnpm link ./foo`.
- Use `pnpm add -g <pkg>` instead of argument-free `pnpm install -g`.
- Do not use `pnpm server`; it has no replacement.
- Use `pnpm pm clean`, `pnpm pm setup`, `pnpm pm deploy`, or `pnpm pm rebuild` when a package script shadows the built-in.
- Use `pnpm runtime set` instead of `pnpm env use`.
- Use `pnpm add -g .` instead of `pnpm link --global`.

Read [migration-pnpm-11.md](references/migration-pnpm-11.md) before changing a pnpm 10 project or automation to pnpm 11.

## Dependency build scripts

### Use `allowBuilds` on pnpm 11

pnpm 11 removes the legacy allowlists and denylists. Express both decisions in one map:

```yaml
allowBuilds:
  esbuild: true
  core-js: false
  nx@21.6.4 || 21.6.5: true
```

Approve or deny named packages without an interactive selector:

```sh
pnpm approve-builds esbuild '!core-js'
pnpm approve-builds --all
```

`--allow-build` permissions are persisted to `allowBuilds`. Git-hosted dependencies may be approved by repository URL without the resolved commit; a package-name-only entry does not approve a Git artifact.

### Review pnpm 10 build scripts

For pnpm 10 projects using legacy settings:

```sh
pnpm ignored-builds
pnpm approve-builds
pnpm approve-builds --global
```

Set `strict-dep-builds=true` to fail when a dependency has an unreviewed build script. Use `--allow-build=<name>` on `add`, `dlx`, or `create` for a scoped one-command allowance. Read [build-scripts.md](references/build-scripts.md) before translating these settings across major versions.

## Installation and lockfile safety

### Treat integrity failures as explicit decisions

A non-frozen pnpm 10.34 install fails with `ERR_PNPM_TARBALL_INTEGRITY` instead of replacing a locked checksum. If current registry content should be accepted, use the narrow opt-in:

```sh
pnpm install --update-checksums
```

`--force`, `pnpm update`, and `--fix-lockfile` do not bypass this check. A missing lockfile tarball integrity value is also fatal in pnpm 11, except for Git-hosted and local `file:` tarballs.

### Preview or constrain installation

```sh
pnpm install --dry-run
pnpm install --frozen-lockfile
pnpm install --frozen-store --offline --frozen-lockfile
```

The dry run resolves and reports without changing manifests, the lockfile, or `node_modules`. Frozen-store mode requires a populated read-only store and preexisting build outputs. Consult [installs-lockfiles-store.md](references/installs-lockfiles-store.md) for its runtime requirements and incompatibilities.

## Configuration and patches

pnpm 11 treats `pnpm-workspace.yaml` as the authoritative home for non-registry, non-authentication settings. Use camelCase keys. Project configuration updates preserve comments, string formatting, and whitespace.

Use structured paths and JSON values when editing nested configuration:

```sh
pnpm config get catalog.react
pnpm config set .ignoreScripts true
pnpm config get --json catalog
```

Patch keys may be name-only, ranges, or exact versions; exact versions override ranges, and ranges override name-only entries. pnpm 11 makes every patch failure fatal. Read [configuration-hooks.md](references/configuration-hooks.md) for config dependencies, pnpmfile loading, hooks, and path restrictions.

## Workspaces and catalogs

Catalog-aware commands include:

```sh
pnpm add --save-catalog lodash
pnpm add --save-catalog-name=testing vitest
pnpm dlx shx@catalog:
```

`catalogMode` may be `manual`, `prefer`, or `strict`. Under a non-manual mode, an explicit compatible version on `add` or `update` moves the catalog resolution; strict mode still rejects an out-of-range version.

For deployment, pnpm 10 requires `inject-workspace-packages=true`. Deployment creates a local virtual store even when the global virtual store is enabled, and newer pnpm 11 versions support catalog-managed workspace dependencies.

Read [workspaces-catalogs-deploy.md](references/workspaces-catalogs-deploy.md) for injected-package synchronization, recursive packing, catalog pruning, peer schemes, and convergence overrides.

## Runtimes and scripts

Declare project runtimes with `devEngines.runtime`; declare a runtime for a
published dependency CLI and its postinstall with `engines.runtime`.

```sh
pnpm runtime set node 24.0.0
pnpm runtime set node 24.0.0 --save-prod
pnpm install --no-runtime
```

The default `runtime set` target is `devEngines.runtime`; `--save-prod` writes
`engines.runtime`. `--no-runtime` skips fetching and linking project runtimes
without removing lockfile entries.

Script output and environment behavior changed in pnpm 11. Command lines and
reporter progress use stderr so stdout remains suitable for pipelines. Read
[runtimes-scripts-cli.md](references/runtimes-scripts-cli.md) when scripts rely
on `npm_config_*`, hidden script names, runtime ranges, or global installs.

## Audit, trust, and SBOMs

Release-age and trust controls include:

```yaml
minimumReleaseAge: 1440
trustPolicy: no-downgrade
trustLockfile: true
```

`trustLockfile` is for lockfiles whose changes already pass trusted review; it
skips rechecking release age and trust downgrade policy for locked entries.

Useful verification and inventory commands include:

```sh
pnpm audit signatures
pnpm audit --fix=update --interactive
pnpm sbom --out sbom.json
pnpm sbom --split
pnpm sbom --exclude-peers
pnpm sbom --lockfile-only
```

Read [security-audit-sbom.md](references/security-audit-sbom.md) for maturity
exceptions, trust evidence, signature behavior, audit identifiers, and SBOM
platform semantics.

## Publishing and releases

Registry credentials may be URL-scoped, scope-specific, or supplied in the
trusted structured `_auth` form. Read
[registries-auth-publishing.md](references/registries-auth-publishing.md)
before moving credentials between project, global, CLI, and environment
sources.

For workspace release plans:

```sh
pnpm change
pnpm change status
pnpm version -r --dry-run
pnpm version from-git
```

`pnpm change` creates intent files and `pnpm version -r` consumes them with
workspace propagation. Release lanes, epics, changesets generated from updates,
and GitHub Actions dependency updates are detailed in
[release-management.md](references/release-management.md).
