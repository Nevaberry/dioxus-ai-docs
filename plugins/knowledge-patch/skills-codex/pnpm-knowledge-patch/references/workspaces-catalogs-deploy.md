# Workspaces, Catalogs, Linking, and Deploy

## Injected packages for deployment (2025-01)

`inject-workspace-packages=true` hard-links all local workspace dependencies instead of symlinking them, and pnpm 10 requires it for `pnpm deploy`. Deploy derives a dedicated lockfile from the shared workspace lockfile, falling back to no deployment lockfile when none exists or `force-legacy-deploy=true`.

```ini
inject-workspace-packages=true
```

## Catalog-aware additions (2025-01)

`pnpm add` writes `catalog:` when the requested dependency and range match the default workspace catalog; omitting the range also selects the catalog entry. A nonmatching request retains a normal dependency specifier.

`workspace:` and `catalog:` specifiers may participate in wider `peerDependencies` ranges in pnpm 10.1.

## Resynchronize injected dependencies (2025-02)

At the workspace root, `sync-injected-deps-after-scripts` names scripts after which `pnpm run` synchronizes an injected package's files into consumers.

```ini
sync-injected-deps-after-scripts[]=compile
```

## Recursive packing and concurrency (2025-05-06)

`pnpm -r pack` packs every workspace project.

```sh
pnpm -r pack
```

The default `workspaceConcurrency` is `Math.min(os.availableParallelism(), 4)`, limiting recursive execution to four tasks unless configured otherwise.

## Update and save catalog dependencies (2025-05-06)

`pnpm update` updates `catalog:` dependencies and writes their specifiers to `pnpm-workspace.yaml`. `catalogMode` controls default-catalog additions: `strict` rejects versions outside the catalog range, `prefer` uses a compatible catalog version and otherwise falls back to a direct dependency, and `manual` (the default) does not add automatically.

```yaml
catalogMode: strict
```

`pnpm add --save-catalog` saves to the default catalog; `--save-catalog-name=<name>` targets a named catalog. The manifest receives `catalog:` or `catalog:<name>`.

```sh
pnpm add --save-catalog lodash
pnpm add --save-catalog-name=testing vitest
```

## Clean unused catalogs (2025-08)

Set `cleanupUnusedCatalogs: true` to remove unused catalog entries during installation.

## Use catalogs with ephemeral commands (2026-01-02)

`pnpm dlx` and `pnpx` accept `catalog:` specifiers.

```sh
pnpm dlx shx@catalog:
```

## Bare workspace protocol (2026-01-02)

A bare `workspace:` specifier is treated as `workspace:*` and replaced by the concrete version when publishing.

```json
{
  "dependencies": {
    "foo": "workspace:"
  }
}
```

## Deduplicate recursive peer graphs (2026-03)

`dedupePeers: true` uses version-only peer identifiers instead of full dependency paths in peer suffixes, reducing duplicate instances and avoiding nested suffix chains.

```yaml
dedupePeers: true
```

## Prefix-based workspace discovery (10.34.0)

When invoked outside the target, `--prefix=<dir>` affects workspace-root detection and loads `<dir>/pnpm-workspace.yaml`.

```sh
pnpm --prefix=./project install
```

## Convergence overrides (11.10-11.17)

An empty-range override selector such as `"pkg@"` changes only dependency edges whose declared range accepts the exact override value. The value must be exact, and pnpm warns when all ranges admit a newer convergence target.

```yaml
overrides:
  "form-data@": 4.0.6
```

## Scheme-bearing peer dependencies (11.10-11.17)

`peerDependencies` may use named-registry, `npm:` alias, `file:`, Git, or URL specifiers. Matching uses the embedded range, such as `5.x.x` from `work:5.x.x` or `^5` from `npm:bar@^5`, and `*` when no version is present. Bare `name@version` values remain invalid.

## Deploy catalog workspaces (11.10-11.17)

`pnpm deploy` supports workspaces whose dependencies are managed through catalogs.

## Catalog and release-age pruning (2026-08)

`catalogPrune` replaces `cleanupUnusedCatalogs`; the old name remains accepted, but `catalogPrune` wins when both exist.

`minimumReleaseAgeExcludePrune` makes `add`, `update`, and `remove` remove package/version exclusions absent from the newly written lockfile. It retains name patterns and skips cleanup when `sharedWorkspaceLockfile` is `false`.

```yaml
catalogPrune: true
minimumReleaseAgeExcludePrune: true
```

## Explicit versions move catalog resolutions (2026-08)

With non-manual `catalogMode`, `pnpm add <pkg>@<version>` and `pnpm update <pkg>@<version>` move a compatible catalog entry's resolved version rather than dropping the request. Strict mode accepts versions inside the catalog range and rejects versions outside it. Omitted workspace projects follow the moved resolution on their next install.

```sh
pnpm update react@19.2.3
```
