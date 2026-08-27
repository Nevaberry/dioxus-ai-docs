# Projects and Coverage

## Resolve project entries

Use root-level `test.projects`; the previous workspace forms were deprecated in 3.2.0. Entries can mix inline configurations, direct config paths, directories, and glob patterns. A matched directory becomes a project even when it has no config file.

A matched file must use a supported naming form: `vitest.config*`, `vite.config*`, `vitest.<name>.config.*`, or `vite.<name>.config.*`. The embedded name may contain only letters, numbers, `_`, or `-`.

```ts
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

## Understand root configuration and inheritance

The root `vitest.config` is not itself a test project unless explicitly included. Separate project config files inherit none of its test options. Inline projects can merge root configuration with `extends: true`:

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

Root plugins still run their configuration and server hooks and are used by global setup and custom coverage providers. `coverage`, `reporters`, and `resolveSnapshotPath` are root-only. Use `defineProject` in file-based project configs so unsupported properties fail type checking, and merge shared configuration explicitly when those projects need common settings.

## Name and schedule projects

Every resolved project name must be unique or Vitest throws. Unnamed inline projects receive numeric names. Glob-discovered projects use the nearest `package.json` name, falling back to the folder name.

Since 3.2.0, a project name can supply a reporter label and color:

```ts
test: {
  name: { label: 'unit', color: 'red' },
}
```

Also since 3.2.0, `sequence: { groupOrder: number }` schedules lower-numbered groups first. Projects with the same number run together; without the option, all projects run in parallel.

```ts
test: {
  name: 'unit',
  sequence: { groupOrder: 0 },
}
```

## Use custom coverage reporters

`coverage.reporter` accepts an npm package name or an absolute local path, optionally paired with reporter options. The module must implement Istanbul's reporter interface, for example by extending `ReportBase` from `istanbul-lib-report`.

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

Custom reporters can set `coverage.htmlDir` so HTML output integrates with the Vitest UI and HTML reporter, including subpath deployments (4.1.0).

## Implement a custom coverage provider

Select `provider: 'custom'` and set `customProviderModule` to a package name or path. The module must default-export a `CoverageProviderModule`; `getProvider()` returns the `CoverageProvider`, and its `initialize` method receives the Vitest context.

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

## Distinguish changed tests from changed coverage

`coverage.changed` or `--coverage.changed` runs the selected test set but limits the report to modified files (4.1.0). `--changed` instead narrows which tests run.

```sh
vitest --coverage.changed
```

## Preserve coverage ignore regions

Both V8 and Istanbul recognize start/stop regions as of 4.1.0. Preserve ignore comments through transforms with `-- @preserve`:

```ts
/* v8 ignore start -- @preserve */
unreachablePlatformCode()
/* v8 ignore stop -- @preserve */
```

Use the corresponding `istanbul ignore start` and `istanbul ignore stop` directives for Istanbul.

V8 also supports finer exclusions:

- `v8 ignore if` and `v8 ignore else` exclude one branch.
- `v8 ignore next` can exclude the following statement, function, class, conditional, try/catch, or switch case.
- `v8 ignore file` excludes a whole file.

```js
/* v8 ignore if */
if (platformOnly) runNativePath()
else runPortablePath()

/* v8 ignore next */
export class UnsupportedRuntime {}
```

Placing `/* v8 ignore next */` between a `catch (error)` clause and its body excludes the whole catch only with Rolldown Vite; esbuild does not support that placement.

## Account for V8 remapping history

Vitest 3.2.0 offered `coverage.experimentalAstAwareRemapping: true` to align V8 coverage remapping more closely with Istanbul. It was opt-in and intended to replace the older remapper in the next major, so remove assumptions that all 3.2-era runs used the same remapping behavior.
