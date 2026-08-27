# Caching, environment, and package managers

## Prune with Git ignore rules (since 2.4.0)

`turbo prune` can opt into respecting `.gitignore` with `--use-gitignore`.

```bash
turbo prune <target> --use-gitignore
```

## Apply environment and cache settings (since 2.4.0)

`DISPLAY` is passed through by default. `passThroughEnv` negation can exclude
built-ins and variables inherited from `globalPassThroughEnv`. Force mode
overrides other cache settings instead of being overridden by
`remoteCache.enable`.

## Prune Bun repositories (since 2.5.0)

`turbo prune` supports repositories using Bun 1.2 or newer and its text-based
lockfile.

```bash
turbo prune web
```

## Invalidate Bun dependencies granularly (since 2.6.0)

Stable Bun package-manager support parses the text `bun.lock` v1 format
granularly. Changing one application's dependencies invalidates cache only for
packages affected by that dependency change, rather than every package in the
repository.

## Use Yarn catalogs (since 2.7.0)

The lockfile parser understands catalogs from Yarn 4.10.0 and newer. Changing
a catalog invalidates only affected packages and tasks rather than the entire
repository.

```yaml
catalog:
  react: ^19.2.3
```

## Share cache across Git worktrees automatically (since 2.8.0)

Turborepo detects linked Git worktrees and shares their local cache
automatically. A task cached in one worktree can hit the cache in another; no
configuration is required.

```bash
turbo run build
git worktree add -B my-branch ../my-branch
cd ../my-branch
turbo run build
```

## Include global files in pruning (since 2.9.0)

The `pruneIncludesGlobalFiles` Future Flag copies files matched by
`globalDependencies` into `turbo prune` output. Enabling it affects the global
hash.

## Use current cache option replacements (since 2.9.0)

- Replace `--no-cache` with `--cache=local:r,remote:r`.
- Replace `TURBO_REMOTE_ONLY` and `--remote-only` with `--cache=remote:rw`.
- Replace `TURBO_REMOTE_CACHE_READ_ONLY` and `--remote-cache-read-only` with
  `--cache=local:rw,remote:r`.
- The `longerSignatureKey` Future Flag requires
  `TURBO_REMOTE_CACHE_SIGNATURE_KEY` to be at least 32 bytes.

## Evict the local cache automatically (since 2.10.0)

Top-level `cacheMaxAge` and `cacheMaxSize` opt into age- and size-based local
cache eviction. At the start of each `turbo run`, eviction removes expired
artifacts and then the oldest artifacts needed to meet the size cap in a
background thread.

```jsonc
{
  "cacheMaxAge": "7d",
  "cacheMaxSize": "10GB"
}
```

## Migrate package-manager catalogs (since 2.10.0)

The migration codemod handles package-manager catalogs when upgrading a
repository.

```bash
npx @turbo/codemod migrate
```

## Use Vercel Remote Cache OIDC policies (since 2.10.8)

Vercel Remote Cache authentication guidance includes OIDC policies as a
supported authentication path.

## Run Cargo formatting (since 2.10.8)

The native Cargo integration provides a format task, allowing Cargo workspaces
to run formatting through Turborepo's task graph.

## Work with uv workspaces (since 2.10.8)

Turborepo discovers uv workspaces and runs their native tasks. It hashes uv
lockfile dependency closures, watches uv workspace changes, and supports
pruning uv workspaces. Cache invalidation and pruned outputs remain
dependency-aware for Python monorepos.
