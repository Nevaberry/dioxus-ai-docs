# Projects and Coverage

Relevant versioned source batches: `3.2.0`, `4.0.0`, and `4.1.0`.

## Contents

- [Resolve project entries](#resolve-project-entries)
- [Understand the root config boundary](#understand-the-root-config-boundary)
- [Give every project a unique identity](#give-every-project-a-unique-identity)
- [Order groups of projects](#order-groups-of-projects)
- [Opt into AST-aware V8 remapping](#opt-into-ast-aware-v8-remapping)
- [Load a custom coverage reporter](#load-a-custom-coverage-reporter)
- [Load a custom coverage provider](#load-a-custom-coverage-provider)
- [Ignore coverage regions with both providers](#ignore-coverage-regions-with-both-providers)
- [Exclude precise V8 constructs](#exclude-precise-v8-constructs)
- [Distinguish changed tests from changed coverage](#distinguish-changed-tests-from-changed-coverage)
- [Integrate custom coverage HTML](#integrate-custom-coverage-html)
- [Toggle coverage through the public API](#toggle-coverage-through-the-public-api)

## Resolve project entries

`test.projects` accepts a mixture of:

- Inline project configurations
- Direct paths to project configuration files
- Directories
- Glob patterns, including negated patterns

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

A matched directory becomes a project even if it has no config file. A matched file must use one of these naming families:

- `vitest.config.*`
- `vite.config.*`
- `vitest.<name>.config.*`
- `vite.<name>.config.*`

The `<name>` segment can contain only letters, numbers, `_`, and `-`.

## Understand the root config boundary

The root `vitest.config` coordinates a multi-project run but is not automatically a test project. Include it explicitly if it should also discover tests.

Separate project config files inherit none of the root test options. Merge shared configuration explicitly for file-based projects. Use `defineProject` in a project config so the type checker rejects properties that are not supported at project scope.

An inline project can merge root options with `extends: true`:

```ts
export default defineConfig({
  test: {
    projects: [{
      extends: true,
      test: {
        name: 'unit',
        include: ['**/*.unit.test.ts'],
      },
    }],
  },
})
```

Root plugins still run configuration and server hooks. They are also used by global setup and custom coverage providers even though root test options are not automatically inherited.

The following are root-only rather than per-project options:

- `coverage`
- `reporters`
- `resolveSnapshotPath`

## Give every project a unique identity

Every resolved project name must be unique; Vitest throws on duplicates.

- Unnamed inline projects receive numeric names.
- Glob-discovered projects use the nearest `package.json` name when available.
- Without a package name, a glob-discovered project uses its folder name.

Set `test.name` to a string or to an object with a reporter label and color:

```ts
export default defineProject({
  test: {
    name: {
      label: 'unit',
      color: 'red',
    },
  },
})
```

The object form gives projects distinct labels in reporter output.

## Order groups of projects

Set `sequence.groupOrder` in a project's test config to schedule project groups from the lowest number to the highest:

```ts
export default defineProject({
  test: {
    sequence: {
      groupOrder: 0,
    },
  },
})
```

Projects with the same value still run together. Without `groupOrder`, all projects run in parallel.

## Opt into AST-aware V8 remapping

`coverage.experimentalAstAwareRemapping: true` aligns V8 coverage remapping more closely with Istanbul:

```ts
export default defineConfig({
  test: {
    coverage: {
      experimentalAstAwareRemapping: true,
    },
  },
})
```

This was opt-in in `3.2.0` and was intended to replace the older V8 remapper in the following major. Treat the option as migration-sensitive when maintaining configuration that spans releases.

## Load a custom coverage reporter

`coverage.reporter` accepts an npm package name or an absolute path to a local module. Either can be paired with reporter options:

```ts
export default defineConfig({
  test: {
    coverage: {
      reporter: [
        [
          '@acme/coverage-reporter',
          { file: 'coverage/custom.txt' },
        ],
        '/absolute/path/to/local-reporter.cjs',
      ],
    },
  },
})
```

The module must implement Istanbul's reporter interface. A typical implementation extends `ReportBase` from `istanbul-lib-report`.

## Load a custom coverage provider

Select `provider: 'custom'` and name the module through `customProviderModule`:

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

The module, loaded by package name or path, must default-export a `CoverageProviderModule`. Its `getProvider()` method returns a `CoverageProvider` instance. The provider's `initialize` method receives the Vitest context.

Root plugins remain active for a custom provider, which is one reason plugin setup belongs in the root configuration.

## Ignore coverage regions with both providers

Both V8 and Istanbul recognize start/stop regions. Add `-- @preserve` so transforms retain the directives:

```ts
/* v8 ignore start -- @preserve */
unreachablePlatformCode()
/* v8 ignore stop -- @preserve */
```

For Istanbul, use the corresponding `istanbul ignore start` and `istanbul ignore stop` directives with the same preservation suffix.

## Exclude precise V8 constructs

V8 coverage supports more granular directives:

- `v8 ignore if` excludes the `if` branch.
- `v8 ignore else` excludes the `else` branch.
- `v8 ignore next` can exclude the next statement, function, class, conditional, try/catch, or switch case.
- `v8 ignore file` excludes an entire file.

```js
/* v8 ignore if */
if (platformOnly) runNativePath()
else runPortablePath()

/* v8 ignore next */
export class UnsupportedRuntime {}
```

Placing `/* v8 ignore next */` between `catch (error)` and the catch body excludes the whole catch. That exact placement requires Rolldown Vite; esbuild does not support it.

## Distinguish changed tests from changed coverage

`coverage.changed` and `--coverage.changed` run the complete selected test set but restrict coverage reporting to modified files:

```sh
vitest --coverage.changed
```

This differs from `--changed`, which narrows the tests that run.

## Integrate custom coverage HTML

Custom coverage reporters can set `coverage.htmlDir`. Vitest then integrates their HTML output with the UI and HTML reporter, including applications deployed under a subpath.

## Toggle coverage through the public API

Programmatic integrations can enable and disable coverage dynamically with `enableCoverage` and `disableCoverage`. These are part of the redesigned public Vitest API; see [Reporters and integrations](reporters-and-integrations.md) for the surrounding lifecycle and run-control methods.
