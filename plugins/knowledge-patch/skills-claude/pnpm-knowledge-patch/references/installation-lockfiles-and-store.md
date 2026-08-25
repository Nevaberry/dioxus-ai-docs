# Installation, Lockfiles, and Stores

Use this reference for dependency installation, lockfile compatibility and
integrity, CI behavior, fetching, virtual stores, and alternate install
backends.

## Installation Semantics

### Production and repeat installs (batches `2025-01` and `11.0.0`)

In pnpm 10, `NODE_ENV=production` no longer causes dependency categories to be
omitted; use explicit install options to select dependency types.

pnpm 11 enables `optimisticRepeatInstall` by default. It also defaults
`verifyDepsBeforeRun` to `install` and `strictDepBuilds` to true. Dependency
build approval is covered in the migration and build-security reference.

### Verify dependencies before scripts (batch `2025-01`)

`verify-deps-before-run` controls what happens when `node_modules` is stale
before a package script:

- `install` refreshes it;
- `warn` reports it;
- `prompt` asks;
- `error` stops; and
- `false` disables the check.

Commands that should not update `node_modules`, including
`pnpm install --lockfile-only`, do not validate or purge it. The equivalent
workspace-file setting is `verifyDepsBeforeRun`.

This feature does not support the PnP linker (batch `2025-04`).

### Preview without writes (batch `11.6-11.9`)

`pnpm install --dry-run` performs full resolution, reports the planned
changes, and leaves manifests, the lockfile, and `node_modules` untouched. A
successful preview exits zero.

```sh
pnpm install --dry-run
```

### Target architecture (batch `2025-07`)

`pnpm install` and `pnpm add` accept command-local `--cpu`, `--libc`, and
`--os` overrides for `supportedArchitectures`.

### Warn on slow fetches (batch `2025-10`)

`fetchWarnTimeoutMs` sets the elapsed-time threshold for slow metadata and
tarball requests. `fetchMinSpeedKiBps` sets the minimum tarball transfer speed
before pnpm warns.

```yaml
fetchWarnTimeoutMs: 10000
fetchMinSpeedKiBps: 50
```

## CI and Frozen Installs

### Incompatible lockfiles are fatal (batch `2026-03`)

With frozen-lockfile mode in CI, a lockfile incompatible with the running pnpm
is an error. Non-frozen CI installs retain fallback behavior.

`pnpm ci` cleans every workspace `node_modules` and performs a frozen-lockfile
install (batch `11.0.0`).

### Regenerating a missing root lockfile (batch `11.4-11.5`)

If `pnpm-lock.yaml` is absent but `node_modules/.pnpm/lock.yaml` still matches
the manifest, a non-frozen install can reconstruct the root lockfile from that
installed snapshot without resolving again. A frozen install always refuses
to proceed without the root lockfile.

### Symlinked lockfiles (batch `11.10-11.17`)

pnpm can read `pnpm-lock.yaml` through a symlink and leaves it untouched if the
installation makes no lockfile changes. If the lockfile would change, pnpm
refuses to write through the symlink. This supports frozen staged-build
sandboxes without redirecting lockfile mutations.

## Lockfile Compatibility

### Upgrade a v6 lockfile through pnpm 9 (batch `2025-01`)

pnpm 10 cannot convert lockfile v6 directly to v9. Run a pnpm 9 install to
perform the conversion before switching the project to pnpm 10.

### Read pnpm 11 two-document files from pnpm 10 (batch `2026-03`)

pnpm 10.33 can consume pnpm 11's two-document YAML lockfile. It ignores the
first document, which carries pnpm-version integrities and config-dependency
resolutions.

### Package-manager and runtime records (batches `11.0.0` and `11.1-11.3`)

pnpm records a resolved `devEngines.packageManager` version and reuses it while
the declared range still accepts it. Lockfile-managed Node.js, Deno, and Bun
runtimes remain frozen-valid when `pnpm install --no-runtime` skips fetching
and linking them.

## Tarball and Resolution Integrity

### Changed checksums are not repaired implicitly (batch `10.34.0`)

A non-frozen install fails with `ERR_PNPM_TARBALL_INTEGRITY` when fetched
content disagrees with a locked checksum. `--force`, `pnpm update`, and
`--fix-lockfile` do not bypass this check.

Use `--update-checksums` only to explicitly accept and lock the content the
registry currently serves:

```sh
pnpm install --update-checksums
```

### Missing checksums are fatal (batch `11.4-11.5`)

A tarball lockfile entry without integrity fails during lockfile reading with
`ERR_PNPM_MISSING_TARBALL_INTEGRITY`, including frozen installs. Git-hosted
tarballs and local `file:` tarballs are exempt.

For an HTTP tarball, pnpm computes and stores integrity on its first fetch so a
later install detects changed content at the same URL (batch `2025-12`).

When a registry generates a tarball on demand and omits a checksum from
metadata, pnpm downloads it and records computed integrity. Therefore
`--lockfile-only` may still download such a tarball to create a verifiable
lockfile (batch `11.6-11.9`).

### Git resolutions (batch `11.4-11.5`)

The lockfile `commit` for a Git resolution must be a full 40-character
hexadecimal SHA. pnpm rejects other values before calling Git.

## Fetch and Virtual-Store-Only Workflows

### Local file dependencies (batch `2026-01-02`)

`pnpm fetch` skips local directory dependencies that use `file:`. This allows
a container prefetch layer to run before local sources are copied, but the
directories must exist for the later install.

### Virtual-store-only materialization (batch `11.0.0`)

`virtualStoreOnly` populates the virtual store without importer symlinks,
hoisting, binary links, or lifecycle scripts. `pnpm fetch` uses this mode
internally.

```yaml
virtualStoreOnly: true
```

## Global Virtual Store

### Shared graph-keyed storage (batch `2025-05-06`)

With `enableGlobalVirtualStore`, project `node_modules` entries link to
`<store-path>/links` rather than `node_modules/.pnpm`. Graph hashes key the
packages, allowing projects with the same dependency graph to share them.
pnpm disables this mode automatically in CI; the `ci` setting can override
environment detection.

```yaml
enableGlobalVirtualStore: true
```

It may also be enabled in global configuration:

```sh
pnpm config -g set enable-global-virtual-store true
```

`pnpm deploy` ignores this setting and creates a deployment-local store
(batch `2026-01-02`).

### Pruning shared links (batch `2025-12`)

Projects using the global virtual store register under
`{storeDir}/v10/projects/`. `pnpm store prune` follows registered project and
workspace `node_modules` trees, retains reachable content, and removes unused
entries from `links/`.

Unscoped packages now appear under an `@` directory in this store. Account for
that layout in tooling that inspects the store directly.

## pnpm 11 Store

The package index is a single SQLite database at `$STORE/index.db`. Packages
not present in this index are refetched on demand instead of being discovered
from the former per-package JSON indexes (batch `11.0.0`).

`pnpm cache path` prints the metadata cache. `pnpm store prune` preserves the
lockfile verification log, so an unchanged lockfile need not repeat
supply-chain checks after pruning (batch `2026-08`).

## Read-Only Store Operation

`frozenStore` or `--frozen-store` suppresses every store write and supports
installation from a fully populated, read-only store (batch `11.6-11.9`).
Combine it with offline and frozen-lockfile operation:

```sh
pnpm install --frozen-store --offline --frozen-lockfile
```

All required build outputs must already exist. The mode is incompatible with
`--force` and pnpr servers. It requires Node.js 22.15+ on the 22.x line,
23.11+ on the 23.x line, or 24+.

## Pacquet Backend

Installing `@pnpm/pacquet` as a config dependency delegates install
materialization while pnpm initially retains dependency resolution. In pnpm
11.2.2, flags for `install`/`i` are forwarded, while flags from `add`,
`update`, and `dedupe` are not (batch `11.1-11.3`).

With pacquet 0.11.7 or newer and the isolated linker, an ordinary non-frozen
install delegates both resolution and materialization. `add`, `update`, and
`remove` still resolve in pnpm; older pacquet versions retain the split
pipeline (batch `11.6-11.9`).

A pnpmfile custom fetcher can delegate a rewritten resolution back to pnpm's
built-in fetcher; see the configuration reference.

## Workspace Discovery and Pruning

`--prefix=<dir>` affects workspace-root discovery even when pnpm starts outside
the target. It loads that directory's `pnpm-workspace.yaml`
(batch `10.34.0`).

`pnpm prune` is recursive by default in a workspace. In particular,
`pnpm prune --prod` at the root preserves production links that other
workspace projects need (batch `2026-08`).

## Script-Safe Output

Reporter output from `pnpm store` and `pnpm config` subcommands goes to stderr,
allowing automation to capture stdout cleanly (batch `11.6-11.9`).
