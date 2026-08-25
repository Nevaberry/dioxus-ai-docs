---
name: turborepo-knowledge-patch
description: Turborepo
version: 2.10.0
license: MIT
metadata:
  author: Nevaberry
---


# Turborepo Knowledge Patch

Load this skill when configuring, migrating, debugging, or operating a
Turborepo repository. Check the repository's installed `turbo` version before
applying version-sensitive guidance, and prefer its manifest, lockfile,
configuration, and observed behavior when they disagree with general advice.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Package Boundaries and Environment Linting](references/boundaries-and-linting.md) | Boundary analysis, cycles, ESLint Flat Config, and Biome environment checks |
| [Configuration and Task Inputs](references/configuration-and-inputs.md) | Schemas, JSONC, inheritance, root globs, Future Flags, and deferred hashes |
| [Ecosystem, Documentation, and Migrations](references/ecosystem-and-migrations.md) | Package managers, documentation, migration tooling, Cargo, Termux, and uv |
| [Execution and Caching](references/execution-and-caching.md) | Sidecars, failure handling, watch mode, pruning, affected scopes, cache policy, and shutdown |
| [Queries, Observability, and Terminal UI](references/queries-observability-and-ui.md) | Repository queries, devtools, structured logs, metrics, profiles, and terminal controls |

## Start With Breaking Changes and Deprecations

### Replace Deprecated Invocation Forms

When preparing for the next major release, migrate these interfaces:

| Deprecated | Replacement |
| --- | --- |
| `turbo-ignore` | `turbo query affected` |
| `--parallel` | Task-level `persistent` and `with` |
| `--no-cache` | `--cache=local:r,remote:r` |
| `TURBO_REMOTE_ONLY` or `--remote-only` | `--cache=remote:rw` |
| `TURBO_REMOTE_CACHE_READ_ONLY` or `--remote-cache-read-only` | `--cache=local:rw,remote:r` |
| Raster/PDF `--graph` output | `.svg`, `.html`, `.mermaid`, or `.dot` |
| JSON `--graph` output | `turbo query` |
| `turbo prune --scope web` | `turbo prune web` |
| `turbo scan` | Remove it; there is no replacement |

The daemon no longer participates in `turbo run` or `turbo watch`. Remove
`TURBO_DAEMON`, `--daemon`, `--no-daemon`, and the `daemon` configuration key.

### Treat Package and Task Cycles Separately

A cycle in the Package Graph does not automatically stop execution. Turborepo
validates the Task Graph, so a cyclic package relationship is usable when the
selected tasks do not create cyclic task dependencies. A recursive dependency
such as `build.dependsOn: ["^build"]` can still fail.

Use `turbo boundaries` to detect circular package dependencies and invalid
imports. When a cycle error reports alternative edge-removal sets, removing
every edge in any one complete set breaks that cycle.

## Configure Repositories Safely

### Use the Installed Schema

Point root configuration at the package's local schema so editor validation
matches the installed CLI:

```json
{
  "$schema": "./node_modules/turbo/schema.json"
}
```

Adjust the relative path in package-level configuration. Both `turbo.jsonc`
and comments are supported, and `turbo.json` itself accepts trailing commas.

### Preserve Inherited Arrays Deliberately

Package configuration can extend the root with `"//"` and another workspace
package by name. Local arrays replace inherited arrays unless they contain
`$TURBO_EXTENDS$`:

```json
{
  "extends": ["//", "web"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", ".next/**"]
    }
  }
}
```

### Anchor Inputs at the Workspace Root

Use `$TURBO_ROOT$` instead of package-depth-dependent parent traversal:

```json
{
  "tasks": {
    "build": {
      "inputs": ["$TURBO_ROOT$/important-file.txt"]
    }
  }
}
```

For generated files, structured `inputs` can postpone hashing until task
dependencies complete. Choose `mode: "jit"` for files created upstream, or
`mode: "dependencyOutputs"` to hash selected outputs from dependency tasks.
See [Configuration and Task Inputs](references/configuration-and-inputs.md) for
complete forms and cache implications.

## Run Long-Running Work Correctly

Use `with` when a persistent task must coexist with another long-running task;
do not express coexistence as completion ordering:

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

To continue after failures without running dependents of failed work, use:

```bash
turbo run test --continue=dependencies-successful
```

Turborepo forwards `SIGINT` and `SIGTERM` to tasks and waits for cleanup. A
second `Ctrl+C` forces immediate termination.

## Control Cache Scope and Invalidation

### Share and Bound the Local Cache

Linked Git worktrees share their local Turborepo cache automatically. To cap
disk use, configure age and size eviction:

```json
{
  "cacheMaxAge": "7d",
  "cacheMaxSize": "10GB"
}
```

Eviction runs at the start of `turbo run`, removing expired artifacts before
the oldest artifacts needed to meet the size cap.

### Refine Affected Work

Combine `--affected` and `--filter` to take their intersection, including
negative filters:

```bash
turbo run build --affected --filter=web
turbo run build --affected --filter=!docs
```

Future Flags can make affected selection, watch reruns, filters, and pruning
respect task inputs or global dependencies more precisely. Because each flag
changes behavior and contributes to the global hash, enable them independently
and review the full flag list before migration.

## Query Before Guessing

`turbo query` exposes stable repository data. With no query it opens GraphiQL;
it accepts inline GraphQL, `--file`, and `--schema`. Use the `affected`
shorthand for machine-readable changed tasks or packages and `ls` for package
details:

```bash
turbo query affected --tasks build
turbo query affected --packages
turbo query ls web --output=json
turbo query ls --affected --filter='./apps/*'
```

Use `turbo devtools` for hot-reloading Package Graph and Task Graph views. JSON
from `turbo ls` contains dependents, while dry-run and summary data expose
`with` relationships.

## Observe Runs Without Losing Terminal Output

`--json` emits NDJSON log objects. `--log-file` keeps normal terminal output
and writes structured logs, either to the default timestamped path or a custom
one:

```bash
turbo run lint --json --log-file=logs.json
```

OpenTelemetry metrics require the `experimentalObservability` Future Flag and
an OTLP endpoint. Profiling flags no longer require a filename and produce a
Markdown companion next to the trace:

```bash
turbo run build --profile
```

## Validate Environment Declarations

For ESLint Flat Config, spread the shareable `eslint-config-turbo` array, or
register `eslint-plugin-turbo` under `plugins.turbo` and enable
`turbo/no-undeclared-env-vars`. Biome can detect Turborepo repositories, but
its `noUndeclaredEnvVars` rule must be explicitly enabled in the nursery group.

Remember that `DISPLAY` passes through by default. Negated `passThroughEnv`
entries can exclude built-ins and values inherited from
`globalPassThroughEnv`; force mode takes precedence over other cache settings.

## Check Ecosystem-Specific Behavior

Lockfile parsing is dependency-aware for Bun and Yarn catalogs. Native
workspace integration also covers Cargo and uv repositories, but support
details differ across task inference, formatting, watching, hashing, and
pruning. Consult [Ecosystem, Documentation, and Migrations](references/ecosystem-and-migrations.md)
before assuming JavaScript-only behavior.
