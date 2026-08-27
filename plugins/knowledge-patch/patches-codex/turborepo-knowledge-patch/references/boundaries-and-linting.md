# Package Boundaries and Environment Linting

## Run Boundary Analysis

The experimental `turbo boundaries` command detects imports that escape a
package directory and imports of packages missing from that package's declared
dependencies (since 2.4.0):

```bash
turbo boundaries
```

Package rules, implicit-dependency handling, and TypeScript configuration path
aliases are included in boundary analysis (since 2.5.0). Boundary checks also
detect circular package dependencies and analyze dynamic imports (since
2.10.0).

## Interpret Cycles at the Right Graph Level

Circular-dependency diagnostics report sets of dependency edges where removing
all edges in any one complete set breaks the Package Graph cycle (since 2.4.0).
This is more actionable than a package-only list; choose one reported set and
remove or redirect every edge in it.

Package Graph cycles no longer cause an unconditional exit (since 2.9.0).
Turborepo validates the Task Graph instead. A task without cyclic task
dependencies can run even when its packages form a cycle, while a recursive
relationship such as `^build` can still form a Task Graph cycle:

```json
{
  "tasks": {
    "simple-task": {},
    "build": { "dependsOn": ["^build"] }
  }
}
```

Do not treat a successful simple task as proof that every task is safe; inspect
the selected task relationships.

## Configure ESLint Flat Config

`eslint-config-turbo` and `eslint-plugin-turbo` support ESLint Flat Config and
remain compatible with ESLint 8 (since 2.4.0).

Spread the shareable configuration into the exported array:

```js
export default [
  ...turboConfig,
];
```

For direct plugin use, register the plugin in the Flat Config `plugins` object
and then enable its rule:

```js
export default [
  {
    plugins: { turbo },
    rules: {
      "turbo/no-undeclared-env-vars": "error",
    },
  },
];
```

## Configure Biome Environment Checks

Biome 2.3.10 and newer automatically detects a Turborepo project from its
repository dependencies (since Turborepo 2.7.0). The
`noUndeclaredEnvVars` rule remains in Biome's nursery group and is not enabled
by detection alone. Enable it explicitly:

```json
{
  "linter": {
    "rules": {
      "nursery": {
        "noUndeclaredEnvVars": "error"
      }
    }
  }
}
```

The rule catches environment-variable reads that are absent from Turborepo's
declared environment configuration and could otherwise produce incorrect cache
hits.
