# Execution and Caching

## Start Sidecar Tasks With Persistent Work

A persistent task can use `with` to start other long-running tasks whenever it
runs (since 2.5.0). This expresses runtime coexistence; `dependsOn` expresses
completion ordering.

```json
{
  "tasks": {
    "dev": {
      "with": ["api#start"],
      "persistent": true,
      "cache": false
    }
  }
}
```

Dry-run and summary output includes these `with` relationships (since 2.6.0),
which makes the sidecar topology inspectable without starting tasks.

## Continue Only Through Successful Dependencies

`--continue=dependencies-successful` continues past task failures but runs a
dependent task only if all its dependencies succeeded (since 2.5.0):

```bash
turbo run test --continue=dependencies-successful
```

Use it when independent work should continue but failed prerequisites must
still block downstream tasks.

## Cache Watch Mode Explicitly

Watch Mode can write results to the cache only when explicitly enabled (since
2.4.0). The watched task argument is required:

```bash
turbo watch dev --experimental-write-cache
```

## Prune With Repository Semantics

Ask `turbo prune` to respect `.gitignore` with `--use-gitignore` (since 2.4.0):

```bash
turbo prune web --use-gitignore
```

The positional target form is preferred over the deprecated `--scope` form.
When the `pruneIncludesGlobalFiles` Future Flag is active, files matched by
`globalDependencies` are also copied to pruned output (since 2.9.0).

## Handle Environment and Force-Mode Cache Rules

`DISPLAY` passes through by default (since 2.4.0). Negated `passThroughEnv`
patterns can exclude built-in variables and variables inherited from
`globalPassThroughEnv`.

Force mode takes precedence over other cache settings, including
`remoteCache.enable`; do not assume disabling or narrowing remote cache settings
overrides an explicitly forced run.

## Share Cache Across Git Worktrees

Linked Git worktrees share their local Turborepo cache automatically (since
2.8.0). No setting is needed. A task cached in one linked worktree can be a
cache hit in another:

```bash
turbo run build
git worktree add -B my-branch ../my-branch
cd ../my-branch
turbo run build
```

## Remove Daemon Configuration

`turbo run` and `turbo watch` no longer use the daemon (since 2.9.0). The
following interfaces are deprecated because they no longer have a role:

- `TURBO_DAEMON`;
- `--daemon` and `--no-daemon`; and
- the `daemon` configuration key.

## Migrate Deprecated Execution and Cache Interfaces

These interfaces still work in 2.9.0 but warn in preparation for the next
major release:

- Remove `turbo scan`; it is obsolete and has no replacement.
- Replace `--parallel` with task-level `persistent` and `with`.
- Replace `--no-cache` with `--cache=local:r,remote:r`.
- Replace `TURBO_REMOTE_ONLY` or `--remote-only` with
  `--cache=remote:rw`.
- Replace `TURBO_REMOTE_CACHE_READ_ONLY` or
  `--remote-cache-read-only` with `--cache=local:rw,remote:r`.
- Replace `.png`, `.jpg`, or `.pdf` graph output with `.svg`, `.html`,
  `.mermaid`, or `.dot`.
- Replace `.json` graph output with `turbo query`.
- Replace `turbo prune --scope web` with `turbo prune web`.

## Intersect Affected and Filtered Scopes

`--affected` and `--filter` can be combined (since 2.10.0). The selected tasks
or packages must satisfy both constraints. A negative filter removes packages
from the affected set:

```bash
turbo run build --affected --filter=web
turbo run build --affected --filter=!docs
turbo query ls --affected --filter=my-app
```

## Evict Old Local Cache Artifacts

Top-level `cacheMaxAge` and `cacheMaxSize` opt into age- and size-based local
cache eviction (since 2.10.0):

```jsonc
{
  "cacheMaxAge": "7d",
  "cacheMaxSize": "10GB"
}
```

At the start of each `turbo run`, a background thread removes expired
artifacts, then removes the oldest remaining artifacts until the size cap is
met.

## Shut Tasks Down Gracefully

On `SIGINT` or `SIGTERM`, Turborepo forwards the signal to its tasks and waits
for their cleanup handlers (since 2.10.0). Press `Ctrl+C` a second time to force
an immediate exit. No configuration is required.

## Resolve Remote Base References in CI

With the corresponding Future Flag enabled, Turborepo can resolve remote base
refs in GitHub Actions (since 2.10.8). This allows Git comparisons to use a
base ref that is not already present locally.

## Authenticate Remote Cache With OIDC Policies

Remote Cache authentication guidance supports OIDC policies (since 2.10.8).
