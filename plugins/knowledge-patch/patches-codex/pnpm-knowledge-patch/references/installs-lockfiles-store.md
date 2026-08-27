# Installs, Lockfiles, Linkers, and Stores

## Linking behavior (2025-01, 2025-04)

In early pnpm 10, `pnpm link` adds an override to the root `package.json`; in a workspace, the link applies to every project. Run `pnpm link` from the package directory to create a global link instead of using `pnpm link -g`.

From the 2025-04 batch, `pnpm link` writes its root override to `pnpm-workspace.yaml` rather than `package.json`. `pnpm audit --fix` likewise updates overrides stored in the workspace file.

## Hoisting and production installs (2025-01)

`public-hoist-pattern` no longer implicitly hoists packages whose names contain `eslint` or `prettier`; configure hoisting explicitly if those packages must be visible at the root of `node_modules`.

`NODE_ENV=production` no longer causes pnpm to omit dependency types: all dependencies are installed.

## Verify dependencies before scripts (2025-01, 2025-04)

`verify-deps-before-run` controls stale-`node_modules` handling before a script with `install`, `warn`, `prompt`, `error`, or `false`. Commands that should not change `node_modules`, such as `pnpm install --lockfile-only`, do not validate or purge it.

```ini
verify-deps-before-run=install
```

`verifyDepsBeforeRun` is unsupported with `nodeLinker: pnp`; using them together emits a warning.

## Lockfile v6 migration (2025-01)

pnpm 10 cannot directly convert lockfile v6 to v9. Convert a v6 lockfile with the pnpm 9 CLI before upgrading.

## Root-guided automatic peer installation (2025-08)

When pnpm automatically installs a missing peer, it prefers a version already present in the root workspace package's direct dependencies. This can change the selected peer version after upgrading to pnpm 10.15.

## Global virtual store (2025-05-06, 2025-12)

With `enableGlobalVirtualStore`, project `node_modules` entries link to `<store-path>/links` instead of `node_modules/.pnpm`. Packages are keyed by dependency-graph hashes for cross-project sharing. pnpm automatically disables the mode in CI; the separate `ci` setting can explicitly control CI detection.

```yaml
enableGlobalVirtualStore: true
```

It may also be enabled globally:

```sh
pnpm config -g set enable-global-virtual-store true
```

Global-virtual-store projects are registered under `{storeDir}/v10/projects/`. `pnpm store prune` marks packages reachable from project and workspace `node_modules` trees and removes unused entries from `links/`. Unscoped packages now live below an `@` directory in the virtual global store.

## Slow-network warnings (2025-10)

`fetchWarnTimeoutMs` sets the elapsed-time threshold for slow metadata or tarball requests, and `fetchMinSpeedKiBps` sets the minimum transfer speed.

```yaml
fetchWarnTimeoutMs: 10000
fetchMinSpeedKiBps: 50
```

## Inspect the lockfile without installing (2025-11)

`pnpm list --lockfile-only` reads package information from the lockfile rather than `node_modules`.

```sh
pnpm list --lockfile-only
```

## HTTP tarball integrity (2025-12)

pnpm computes and records an integrity hash the first time it fetches an HTTP tarball dependency, so later installs can detect changed content at the same URL.

## Fetch and deployment stores (2026-01-02)

`pnpm deploy` ignores `enableGlobalVirtualStore` and creates a virtual store inside the deployment directory.

`pnpm fetch` skips local `file:` dependencies. This permits a Docker prefetch layer before local directories are copied, but the directories must exist for the later install.

## Frozen CI lockfiles and pnpm 11 format (2026-03)

In CI, an incompatible lockfile is fatal when frozen-lockfile mode is enabled. Non-frozen CI installs retain their fallback behavior.

```sh
pnpm install --frozen-lockfile
```

pnpm 10.33 ignores the first document in a two-document `pnpm-lock.yaml`, allowing it to consume pnpm 11's format for pnpm-version integrities and config-dependency resolutions.

## Store and virtual-store changes (11.0.0)

The store index is a single SQLite database at `$STORE/index.db`. Packages absent from the new index are fetched again on demand rather than found through the old per-package JSON index.

`virtualStoreOnly` fills the virtual store without importer symlinks, hoisting, binaries, or lifecycle scripts. `pnpm fetch` uses this mode internally.

```yaml
virtualStoreOnly: true
```

## Tarball checksum enforcement (10.34.0, 11.4-11.5)

A non-frozen `pnpm install` exits with `ERR_PNPM_TARBALL_INTEGRITY` instead of re-resolving a package and overwriting its locked checksum. Use only `--update-checksums` to accept and lock current registry content; `--force`, `pnpm update`, and `--fix-lockfile` do not bypass the check.

```sh
pnpm install --update-checksums
```

A lockfile tarball entry without integrity fails at read time with `ERR_PNPM_MISSING_TARBALL_INTEGRITY`, including during frozen installs. Git-hosted tarballs and local `file:` tarballs are exempt.

## Hoisting limits (11.4-11.5)

With `nodeLinker: hoisted`, `hoistingLimits` may be `none` (the default, hoist as far as possible), `workspaces` (stop at each workspace package), or `dependencies` (stop at each workspace package's direct dependencies).

```yaml
nodeLinker: hoisted
hoistingLimits: workspaces
```

## Regenerate a missing lockfile (11.4-11.5)

If `pnpm-lock.yaml` is absent but `node_modules/.pnpm/lock.yaml` satisfies the manifest, `pnpm install` reuses that snapshot to regenerate the root lockfile without resolving again. A frozen install still refuses to proceed without `pnpm-lock.yaml`.

## Read-only package stores (11.6-11.9)

`frozenStore` (`--frozen-store`) installs from a fully populated read-only store and suppresses all store writes. Use it with offline, frozen-lockfile installs. Required build outputs must exist; it is incompatible with `--force` and pnpr servers, and requires Node.js 22.15+ on 22.x, 23.11+ on 23.x, or 24+.

```sh
pnpm install --frozen-store --offline --frozen-lockfile
```

## Preview an install (11.6-11.9)

`pnpm install --dry-run` performs full resolution and reports changes without modifying manifests, the lockfile, or `node_modules`; a successful preview exits 0.

```sh
pnpm install --dry-run
```

## Node.js package maps (11.6-11.9)

Isolated and hoisted installs generate `node_modules/.package-map.json`. Enable `nodeExperimentalPackageMap` to inject it into pnpm-managed Node.js scripts. Set `nodePackageMapType` to `standard` for declared dependencies only or `loose` for other reachable installed packages.

```yaml
nodeExperimentalPackageMap: true
nodePackageMapType: standard
```

## Registry-generated tarball integrity (11.6-11.9)

When a registry generates tarballs on demand and omits metadata checksums, pnpm downloads the tarball, computes integrity, and records it. `--lockfile-only` may therefore download such a tarball.

## Symlinked lockfiles (11.10-11.17)

pnpm may read `pnpm-lock.yaml` through a symlink. An install that leaves it unchanged does not rewrite it; an install that would change it refuses to write through the symlink.

## Recursive workspace pruning (2026-08)

`pnpm prune` is recursive by default in a workspace, matching `pnpm install`. At the root, `pnpm prune --prod` preserves production workspace links required by other projects.

```sh
pnpm prune --prod
```
