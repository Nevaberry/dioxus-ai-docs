# Configuration and Workspaces

Use this reference for configuration placement, workspace mechanics, catalogs,
hooks, linking, deployment, hoisting, and package maps.

## Configuration Sources

### Workspace settings (batches `2025-02` and `2025-03`)

`pnpm-workspace.yaml` may exist without a `packages` field and may hold every
setting accepted by `.npmrc`. Write keys in camelCase. Environment-variable
substitution is supported in both keys and values.

`pnpm config get` and `pnpm config list` include workspace-file settings.
`pnpm config set --location=project` writes to `pnpm-workspace.yaml` when the
project has no `.npmrc`.

```yaml
verifyDepsBeforeRun: install
publicHoistPattern:
  - "*types*"
  - "!@types/react"
```

pnpm preserves comments, quoting, whitespace, and formatting when it updates
`pnpm-workspace.yaml` (batch `2026-03`).

### pnpm 11 authoritative locations (batch `migration-10-to-11`)

pnpm 11 ignores `package.json#pnpm`. Keep only authentication and registry
settings in `.npmrc`; put all other settings in `pnpm-workspace.yaml`.
The migration codemod places a subproject's old `.npmrc` settings under
`packageConfigs["<project-name>"]`.

pnpm 11 ignores `npm_config_*` for pnpm configuration; rename these variables
to `pnpm_config_*` in CI, shells, and container configuration. User-supplied
`npm_config_*` variables forwarded to lifecycle scripts are a separate
behavior described in the CLI reference.

### Structured config paths (batch `2025-08`)

`pnpm config get` and `set` accept dotted paths, leading-dot paths, and bracket
notation. Object reads use INI serialization by default. `--json` serializes a
read as JSON or parses a value being written as JSON.

```sh
pnpm config get catalog.react
pnpm config get 'packageExtensions["@babel/parser"].peerDependencies["@babel/types"]'
pnpm config set .ignoreScripts true
pnpm config get --json catalog
```

### Machine-level settings are not project settings (batch `2026-08`)

Workspace configuration cannot set `bin`, `configDir`, `dir`, `globalBinDir`,
`globalDir`, `npmrcAuthFile`, `pnpmHomeDir`, `stateDir`, `userconfig`, or
`workspaceDir`. pnpm ignores and warns on these keys.

Project-scoped `pnpm config set` rejects them with
`ERR_PNPM_CONFIG_SET_NOT_A_PROJECT_SETTING`, and `--config.*` aliases do not
bypass the boundary. Dedicated flags such as `--global-dir` still work, and
`pnpm config delete` can remove stale workspace keys. `cacheDir` and
`storeDir` remain valid project settings.

## Config Dependencies

### Definition and installation (batches `2025-01` and `2025-04`)

`pnpm.configDependencies` are installed before production, development, and
optional dependencies. Each entry requires an exact version plus an integrity
checksum. Config dependencies cannot have ordinary dependencies or lifecycle
scripts.

Use `pnpm add --config <package>` to create the checksummed entry:

```sh
pnpm add --config my-config@1.0.0
```

Config dependencies may have one level of `optionalDependencies` selected by
`os`, `cpu`, and `libc`. These optionals require exact versions, and the
environment lockfile records variants for every platform (batch `11.1-11.3`).

## pnpmfile Hooks and Plugins

### Configuration and local hooks (batch `2025-04`)

The experimental `hooks.updateConfig` hook in `.pnpmfile.cjs` can rewrite pnpm
settings. Local pnpmfiles may also export `preResolution`, `importPackage`,
and `fetchers` hooks.

```js
module.exports = {
  hooks: {
    updateConfig: (config) => ({ ...config, nodeLinker: "hoisted" }),
  },
}
```

### Multiple files and plugin discovery (batches `2025-07` and `2025-08`)

`pnpmfile` accepts a list. Config dependencies named `@pnpm/plugin-*`,
`pnpm-plugin-*`, or scoped `@scope/pnpm-plugin-*` packages have their
`pnpmfile.cjs` loaded automatically. Plugin files are loaded alphabetically;
list files explicitly when order matters.

```yaml
pnpmfile:
  - ./hooks/first.pnpmfile.cjs
  - ./hooks/second.pnpmfile.cjs
```

pnpm 11 also supports `.pnpmfile.mjs`. If both default module formats exist,
the ESM file takes precedence and only one of the two is loaded
(batch `11.0.0`).

### Delegating a custom fetch (batch `11.10-11.17`)

A custom fetcher may return `{ delegate: resolution }` to rewrite a resolution
and invoke pnpm's built-in fetcher. This is the portable pacquet form because
its hooks cannot receive `cafs` and `fetchers`.

## Catalogs

### Adding and saving dependencies (batches `2025-01` and `2025-05-06`)

`pnpm add` writes `catalog:` when the request matches the default workspace
catalog; omitting the requested range also selects the catalog. A nonmatching
request remains a direct specifier.

Use `--save-catalog` for the default catalog or
`--save-catalog-name=<name>` for a named catalog:

```sh
pnpm add --save-catalog lodash
pnpm add --save-catalog-name=testing vitest
```

The package manifest receives `catalog:` or `catalog:<name>` accordingly.

### Catalog update modes (batch `2025-05-06`)

`pnpm update` updates catalog-backed dependencies in `pnpm-workspace.yaml`.
`catalogMode` controls additions:

- `strict` rejects versions outside the catalog range.
- `prefer` uses a compatible catalog version and falls back to a direct
  dependency otherwise.
- `manual`, the default, does not select catalog entries automatically.

`cleanupUnusedCatalogs` removes unused entries during installation
(batch `2025-08`).

The newer name is `catalogPrune`; the old setting remains accepted, but the new
one wins if both appear (batch `2026-08`).

With a non-manual catalog mode, explicit `add` or `update` versions move a
compatible catalog entry's resolved version instead of silently discarding the
request. Strict mode accepts versions inside the range and rejects those
outside. Workspace projects omitted from the operation pick up the moved
resolution on their next install (batch `2026-08`).

### Catalog protocol variants

Bare `workspace:` is equivalent to `workspace:*` and becomes a concrete
version during publishing (batch `2026-01-02`).

`pnpm dlx` and `pnpx` accept `catalog:` versions (batch `2026-01-02`).
`pnpm deploy` supports catalog-managed workspace dependencies
(batch `11.10-11.17`).

## Linking and Injected Workspace Packages

### Link overrides (batches `2025-01`, `2025-04`, and `migration-10-to-11`)

Early pnpm 10 `pnpm link` wrote a root override to `package.json`, applying it
to every project in a workspace. Later pnpm 10 writes that override to
`pnpm-workspace.yaml`; `pnpm audit --fix` also updates overrides stored there.
For a pnpm 10 global link, run argument-free `pnpm link` from the package
directory rather than using `pnpm link -g`.

pnpm 11 requires `pnpm link` to receive a relative or absolute filesystem
path; it no longer resolves a package name from the global store.

```sh
pnpm link ./foo
```

### Injected packages and deployment (batches `2025-01` and `2025-02`)

`inject-workspace-packages=true` hard-links all local workspace dependencies
instead of symlinking and is required for pnpm 10 `deploy`. Deployment derives
a dedicated lockfile from the shared workspace lockfile, falling back to no
deployment lockfile if none exists or `force-legacy-deploy=true`.

`sync-injected-deps-after-scripts` names root-configured scripts after which
`pnpm run` resynchronizes an injected package into its consumers.

```ini
sync-injected-deps-after-scripts[]=compile
```

`pnpm deploy` always creates a deployment-local virtual store and ignores
`enableGlobalVirtualStore`, keeping the output self-contained
(batch `2026-01-02`).

## Peer Dependency Layout

### Root-guided automatic peers (batch `2025-08`)

When pnpm auto-installs a missing peer, it prefers a version already declared
as a direct dependency of the root workspace project. Upgrades can therefore
change peer selection even without a peer-range change; this selection rule
arrived in pnpm 10.15.

`workspace:` and `catalog:` specifiers may participate in wider
`peerDependencies` ranges rather than being restricted to exact workspace or
catalog matches (batch `2025-01`).

### Deduplicate recursive peers (batch `2026-03`)

`dedupePeers: true` uses version-only peer identifiers rather than full
dependency paths in peer suffixes. This prevents nested suffix chains and
reduces duplicate package instances in recursive peer graphs.

### Scheme-bearing peer specifiers (batch `11.10-11.17`)

Peer dependencies may use named-registry, `npm:` alias, `file:`, Git, or URL
specifiers. Matching uses the embedded range, such as `5.x.x` from
`work:5.x.x` or `^5` from `npm:bar@^5`; a scheme without a version uses `*`.
Bare `name@version` values remain invalid.

## Linkers, Hoisting, and Package Maps

The default public hoist pattern no longer makes names containing `eslint` or
`prettier` visible at the root; configure public hoisting explicitly when
tooling depends on it (batch `2025-01`).

`verifyDepsBeforeRun` is unsupported with `nodeLinker: pnp` and only warns;
PnP projects cannot rely on that stale-dependency check (batch `2025-04`).

With `nodeLinker: hoisted`, `hoistingLimits` accepts (batch `11.4-11.5`):

- `none`, the default, for maximum hoisting;
- `workspaces`, stopping at each workspace project; or
- `dependencies`, stopping at each project's direct dependencies.

Isolated and hoisted installations generate
`node_modules/.package-map.json`. Enable `nodeExperimentalPackageMap` to inject
it into pnpm-managed Node.js scripts; `nodePackageMapType: standard` exposes
declared dependencies only, while `loose` also exposes other reachable
installed packages (batch `11.6-11.9`).

## Workspace Execution

The default `workspaceConcurrency` is
`Math.min(os.availableParallelism(), 4)`, so recursive execution uses at most
four concurrent tasks unless configured otherwise (batch `2025-05-06`).

`pnpm -r pack` packs each workspace project (batch `2025-05-06`). For script
matching and sequential execution, see the CLI reference.

`pnpm prune` is recursive by default in a workspace. Root
`pnpm prune --prod` preserves production workspace links required by other
projects (batch `2026-08`).
