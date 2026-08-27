---
name: pnpm-knowledge-patch
description: pnpm
version: "11.17.0"
license: MIT
metadata:
  author: Nevaberry
---


# pnpm Knowledge Patch

Use this skill for pnpm installation, workspace configuration, dependency
policy, runtime management, publishing, registry authentication, release
management, and migration work.

## Start Here

Before changing a project:

1. Read the root manifest and identify `packageManager` or
   `devEngines.packageManager`.
2. Read `pnpm-workspace.yaml`, the lockfile, and only the registry/authentication
   portions of `.npmrc`.
3. Check whether the project is migrating between pnpm major versions.
4. Preserve the project's existing linker, store, catalog, build-permission,
   release-age, and trust policies unless the task explicitly changes them.
5. Use the reference index below for the exact command or setting behavior.

Treat the manifest, lockfile, repository configuration, and observed command
behavior as the source of truth when they differ from generic assumptions.

## Reference Index

| Reference | Read when working on |
| --- | --- |
| [CLI, scripts, and runtimes](references/cli-scripts-and-runtimes.md) | Commands, script execution, package initialization, runtime provisioning, diagnostics, and global tools |
| [Configuration and workspaces](references/configuration-and-workspaces.md) | `pnpm-workspace.yaml`, catalogs, hooks, workspace linking, deployment, hoisting, and package maps |
| [Installation, lockfiles, and stores](references/installation-lockfiles-and-store.md) | Install/fetch behavior, lockfile compatibility, integrity, virtual stores, pacquet, pruning, and CI |
| [Migration and dependency-build security](references/migration-and-build-security.md) | pnpm 10-to-11 migration, dependency lifecycle approvals, patch safety, and exotic dependencies |
| [Registries, publishing, and supply chain](references/registries-publishing-and-supply-chain.md) | Authentication, named registries, audit, trust, packing, publishing, staging, provenance, and SBOMs |
| [Releases and updates](references/releases-and-updates.md) | Release-age policy, dependency updates, changesets, lanes, epics, global groups, and update automation |

## Breaking Changes First

### Migrate configuration deliberately

pnpm 11 does not read the `pnpm` object in `package.json`. Keep registry and
authentication settings in `.npmrc` and move other settings to camelCase keys
in `pnpm-workspace.yaml`. Use:

```sh
pnpx codemod run pnpm-v10-to-v11
```

Review the result manually:

- Replace the three package-manager selection settings with `pmOnFail`.
- Convert audit exclusions from CVEs to GHSA identifiers.
- Move per-project Node runtime declarations to `devEngines.runtime`.
- Rename configuration environment variables from `npm_config_*` to
  `pnpm_config_*` where they configure pnpm itself.
- Supply a filesystem path to `pnpm link`.
- Replace argument-free global install and removed server workflows.

Read
[Migration and dependency-build security](references/migration-and-build-security.md)
before committing a migration.

### Account for runtime and CLI requirements

pnpm 11 requires Node.js 22 or newer and is pure ESM. The standalone binary
also requires glibc 2.27 or newer. After upgrading, run `pnpm setup` because
global binaries live under `PNPM_HOME/bin`.

Package scripts named `clean`, `setup`, `deploy`, or `rebuild` shadow pnpm's
built-ins. Invoke a built-in explicitly with `pnpm pm <name>`.

### Replace legacy build controls

Use `allowBuilds` as the unified dependency-build permission map:

```yaml
allowBuilds:
  esbuild: true
  core-js: false
```

pnpm 11 rejects the older allow/deny settings. Use `pnpm ignored-builds` to
inspect skipped scripts and `pnpm approve-builds` to record decisions. Keep
`strictDepBuilds` enabled unless the project deliberately accepts unreviewed
build scripts.

### Expect stricter installation defaults

The current defaults include:

- a one-day `minimumReleaseAge`;
- blocked exotic transitive sources;
- failure on unreviewed dependency builds;
- optimistic repeat installs; and
- dependency verification before scripts.

Set `minimumReleaseAge: 0` only as an explicit opt-out. Do not weaken integrity,
patch-path, Git-SHA, alias-traversal, or build-script checks merely to make an
install pass.

## High-Value Workflows

### Preview or reproduce an installation

Use `pnpm install --dry-run` to resolve and report changes without writing the
manifest, lockfile, or `node_modules`.

Use `pnpm ci` for a clean workspace install with a frozen lockfile. A frozen CI
install fails on an incompatible or absent root lockfile; fix or regenerate it
outside the frozen operation.

For an intentionally read-only, prepopulated store, combine
`--frozen-store --offline --frozen-lockfile` and satisfy the documented Node.js
minor-version requirements.

### Manage project runtimes

Declare Node.js, Deno, or Bun under `devEngines.runtime`. Installation resolves
the requested range, locks the exact runtime and checksum, and uses that runtime
for project scripts.

Use `pnpm runtime set <name> <version>` for development runtimes, or
`--save-prod` for `engines.runtime`. Use `pnpm install --no-runtime` to skip
fetching a lockfile-managed runtime without deleting its lockfile entry.

### Configure workspaces in one place

Use camelCase settings in `pnpm-workspace.yaml`. The file may contain settings
without a `packages` key. Project-level `pnpm config set` writes there when no
project `.npmrc` exists.

Use catalogs when projects must share dependency ranges:

- `catalogMode: strict` rejects requested versions outside the catalog range.
- `catalogMode: prefer` uses a compatible catalog entry and otherwise falls
  back to a direct specifier.
- `catalogMode: manual` leaves catalog selection explicit.
- `catalogPrune` removes unused catalog entries during installation.

### Keep dependency builds explicit

For one command, use `--allow-build=<package>`. Current releases persist that
decision in `allowBuilds`. Use `pnpm approve-builds --all` only when blanket
approval is intended and has been reviewed.

Git dependencies require repository-aware approval for prepare/build scripts.
An ordinary package-name rule does not approve a Git-hosted artifact.

### Diagnose dependency and environment state

- `pnpm list --lockfile-only` inspects the expected graph without installing.
- `pnpm why <package>` shows reverse paths from the package to workspace roots.
- `pnpm peers check` finds lockfile peer issues.
- `pnpm audit signatures` verifies installed registry signatures.
- `pnpm doctor --json` checks installation, paths, store/cache access, link
  strategies, registry access, and an offline local-package install.
- `pnpm cache path` prints the metadata-cache directory for CI caching.

### Publish with the intended trust boundary

Use `pnpm pack --dry-run` to inspect package contents. A `beforePacking` hook
may alter only the published manifest, while `--skip-manifest-obfuscation`
retains package-manager metadata and publish lifecycle scripts.

Use atomic batch publishing only when the registry implements pnpm's batch
endpoint. Use staged publishing when a version must remain hidden until an
approval step.

Generate an SBOM with `pnpm sbom` and choose CycloneDX or SPDX deliberately.
Use `--lockfile-only` for the complete platform-independent graph,
`--exclude-peers` to omit peer-only trees, and `--split` for one file per
workspace package.

### Manage releases and dependency updates

Use `pnpm change` to write release intents and `pnpm version -r` to consume
them. Check fixed groups, dependent propagation, release lanes, epic
major-version bands, changelog storage, and the consumption ledger before
automating publication.

When updating dependencies:

- release-age and trust policy can constrain candidates;
- explicit versions may move compatible catalog resolutions;
- `resolutionMode` still controls lowest/time-based selection;
- `--changeset` can generate release intents for affected workspaces; and
- GitHub Actions updates require the explicit non-interactive opt-in.

## Safety Checks

Before accepting a lockfile or supply-chain change:

- Investigate checksum changes; `--update-checksums` is a narrow, explicit
  acceptance mechanism, not a routine recovery flag.
- Require 40-character Git commit SHAs in lockfile resolutions.
- Keep patch paths inside the patched package directory.
- Reject dependency aliases with path traversal.
- Keep authentication destination-bound and out of project configuration when
  the setting is global-only.
- Treat `trustLockfile: true` as a reviewed-lockfile policy decision.
- Do not assume an optional dependency softens trust-policy failures.

## Output and Automation Notes

pnpm sends command-script banners and reporter output from `store` and `config`
commands to stderr so stdout remains pipe-friendly. A non-recursive
`pnpm run --no-bail` continues matching scripts but exits nonzero if any fail.
Recursive empty version plans print `[]` with `--json`.

Use `pnpm run "/pattern/"` to select scripts by regular expression and
`--sequential` when execution order or resource limits require concurrency one.

## When Guidance Conflicts with a Repository

Prefer pinned project behavior and reproduce it locally. Check the exact pnpm
binary selected by the project, because `packageManager` switching,
`devEngines.packageManager`, `pnpm with`, and `pmOnFail` can select different
CLIs. Apply only settings supported by that selected major version.
