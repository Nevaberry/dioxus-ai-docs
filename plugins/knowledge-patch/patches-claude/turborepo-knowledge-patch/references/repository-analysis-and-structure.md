# Repository analysis and structure

## Detect package-boundary violations (since 2.4.0)

The experimental `turbo boundaries` command detects imports that escape a
package's directory and imports of packages not declared in that package's
dependencies.

```bash
turbo boundaries
```

Package-boundary analysis gained package rules and implicit-dependency
handling, and boundary checks support TypeScript configuration path aliases
(since 2.5.0).

Boundary checks can also detect circular package dependencies, and import
analysis includes dynamic imports (since 2.10.0).

## Use actionable package-cycle diagnostics (since 2.4.0)

Cycle errors list sets of dependency edges where removing any one complete set
will break the Package Graph cycle, rather than listing only the packages
involved.

## Inspect live graphs (since 2.7.0)

`turbo devtools` provides visual Package Graph and Task Graph views that
hot-reload as the repository changes. The views expose direct and transitive
relationships that explain cache misses.

```bash
turbo devtools
```

## Query repositories (since 2.9.0)

`turbo query` is stable. Running it without a query opens GraphiQL. Queries can
be inline or passed with `--file`, and `--schema` exposes the GraphQL schema.

```bash
turbo query
turbo query --schema
turbo query '{ packages { items { name } } }'
turbo query --file=query.gql
```

The `affected` shorthand emits structured JSON for changed tasks or packages:

```bash
turbo query affected --tasks build
turbo query affected --packages
```

`ls` pretty-prints package details by default. It also supports JSON output,
affected-only results, and selectors.

```bash
turbo query ls web --output=json
turbo query ls --affected --filter='./apps/*'
```

`turbo-ignore` is deprecated in favor of `turbo query affected`.

## Validate cycles at the Task Graph (since 2.9.0)

Cycles in the Package Graph no longer make Turborepo exit automatically.
Turborepo validates the Task Graph instead, so tasks without cyclic task
dependencies can run in a cyclic package graph. A relationship such as
`^build` still errors when it creates a Task Graph cycle.

```json
{
  "tasks": {
    "simple-task": {},
    "build": { "dependsOn": ["^build"] }
  }
}
```

## Infer Cargo workspace tasks (since 2.10.0)

Turborepo supports repositories containing only a Cargo workspace and can infer
tasks for its workspace members.

## Run on Android (since 2.10.8)

The `turbo` CLI supports running on Android in a Termux environment.

## Use native Cargo and uv tasks (since 2.10.8)

The native Cargo integration provides a format task for Cargo workspaces.
Turborepo also discovers uv workspaces and runs their native tasks.
