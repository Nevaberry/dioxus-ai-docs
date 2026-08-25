# Projects and Coverage

## Resolve project entries

`test.projects` can mix inline configurations, direct config paths, directories, and glob patterns. A matched directory becomes a project even without its own config. A matched file must use a `vitest.config*` or `vite.config*` name, or the `vitest.<name>.config.*` or `vite.<name>.config.*` form; `<name>` may contain only letters, numbers, `_`, or `-`.

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      'packages/*',
      '!packages/legacy',
      'apps/*/vitest.config.{unit,e2e}.ts',
    ],
  },
})
```

The root `vitest.config` is not itself a test project unless explicitly included.

## Control inheritance and root-only settings

File-based project configs inherit none of the root config's options. Merge a shared config explicitly when they need common settings. Inline projects can opt into a merge with `extends: true`:

```ts
export default defineConfig({
  test: {
    projects: [{
      extends: true,
      test: { name: 'unit', include: ['**/*.unit.test.ts'] },
    }],
  },
})
```

Root plugins still run their configuration and server hooks and are used by global setup and custom coverage providers. `coverage`, `reporters`, and `resolveSnapshotPath` are root-only, not per-project. Use `defineProject` in file-based project configs so the type checker rejects unsupported properties.

## Give every project a unique identity

Every resolved project name must be unique or Vitest throws. Unnamed inline projects receive numeric names. Projects discovered through globs use the nearest `package.json` name, falling back to the folder name.

Since 3.2.0, `test.name` may be an object such as `{ label: 'unit', color: 'red' }` to give a project a distinct reporter label.

## Order project groups

Since 3.2.0, `sequence: { groupOrder: 0 }` schedules project groups from the lowest number to the highest. Projects with equal values run together; without this option, all projects run in parallel.

```ts
export default defineConfig({
  test: {
    projects: [{
      test: {
        name: { label: 'unit', color: 'red' },
        sequence: { groupOrder: 0 },
      },
    }],
  },
})
```

## Understand V8 remapping history

Vitest 3.2.0 offered `coverage.experimentalAstAwareRemapping: true` to align V8 coverage remapping more closely with Istanbul. It was opt-in and intended to replace the old V8 remapper in the next major. Treat this as upgrade context when removing a legacy setting or comparing coverage output across that boundary.

## Load a custom coverage reporter

`coverage.reporter` accepts an npm package name or an absolute local path, optionally paired with reporter options. The loaded module must implement Istanbul's reporter interface, for example by extending `ReportBase` from `istanbul-lib-report`.

```ts
export default defineConfig({
  test: {
    coverage: {
      reporter: [
        ['@acme/coverage-reporter', { file: 'coverage/custom.txt' }],
        '/absolute/path/to/local-reporter.cjs',
      ],
    },
  },
})
```

Custom reporters can set `coverage.htmlDir` so their HTML output integrates with the Vitest UI and HTML reporter, including deployments under a subpath (since 4.1.0).

## Load a custom coverage provider

Select `provider: 'custom'` with `customProviderModule` to load a provider by package name or path. The module must default-export a `CoverageProviderModule`; its `getProvider()` returns a `CoverageProvider`, whose `initialize` method receives the Vitest context.

```ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'custom',
      customProviderModule: './coverage-provider.ts',
    },
  },
})
```

## Exclude code with coverage directives

Since 4.1.0, both V8 and Istanbul providers recognize start/stop ignore regions. Preserve comments through transforms with `-- @preserve`:

```ts
/* v8 ignore start -- @preserve */
unreachablePlatformCode()
/* v8 ignore stop -- @preserve */
```

Use `istanbul ignore start` and `istanbul ignore stop` for the corresponding Istanbul directives.

V8 also supports fine-grained exclusions:

- `v8 ignore if` and `v8 ignore else` exclude one branch.
- `v8 ignore next` excludes the following statement, function, class, conditional, try/catch, or switch case.
- `v8 ignore file` excludes a whole file.

```js
/* v8 ignore if */
if (platformOnly) runNativePath()
else runPortablePath()

/* v8 ignore next */
export class UnsupportedRuntime {}
```

Placing `/* v8 ignore next */` between a `catch (error)` clause and its body excludes the whole catch, but that placement requires Rolldown Vite because esbuild does not support it.

## Distinguish changed coverage from changed tests

Since 4.1.0, `coverage.changed` or `--coverage.changed` runs the full selected test set but limits the coverage report to modified files:

```sh
vitest --coverage.changed
```

This differs from `--changed`, which narrows the tests themselves.
