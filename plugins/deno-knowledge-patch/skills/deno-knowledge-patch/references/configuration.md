# Configuration

## Local npm Package Linking

Use `"links"` in `deno.json` for local npm packages during development. Requires `"nodeModulesDir": "auto"` or `"manual"`.

```jsonc
{
  "nodeModulesDir": "auto",
  "links": ["../path/to/local_npm_package"]
}
```

Note: This was initially called `"patch"` in 2.3, renamed to `"links"` in 2.4 (deprecation warning if using `patch`).

## `minimumDependencyAge` (2.6+)

Prevent installing newly published packages. Accepts minutes, ISO-8601 duration, or RFC3339 timestamp.

```jsonc
{ "minimumDependencyAge": "P2D" }  // only deps at least 2 days old
```

## `"publish": false` (2.6+)

Prevent accidental `deno publish` of private/internal packages:

```jsonc
{ "publish": false }
```

## `jsr:` Scheme in package.json (2.7+)

Use `jsr:` specifiers directly in `package.json` dependencies without needing `deno.json`.

## `DENO_COMPAT=1` (2.4+)

Shorthand env var enabling `--unstable-detect-cjs`, `--unstable-node-globals`, `--unstable-bare-node-builtins`, and `--unstable-sloppy-imports` for package.json-first projects.

## `package.json` Overrides (2.7+)

Deno now supports the `overrides` field in `package.json` to pin transitive dependency versions.

## Workspace-scoped compilerOptions (2.2+)

Workspace members can override `compilerOptions` (e.g., different `lib` for frontend vs backend).
