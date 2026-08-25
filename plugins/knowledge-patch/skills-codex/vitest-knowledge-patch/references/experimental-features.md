# Experimental Features

Experimental options can change and may trade compatibility or runtime cost for diagnostics. Enable them narrowly and keep the constraints below with the configuration.

## Execute with native Node imports

Set `experimental.viteModuleRunner: false` to execute tests, source, and setup files through native Node imports (4.1.0):

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    experimental: {
      viteModuleRunner: false,
    },
  },
})
```

This disables Vite transforms, plugins, aliases, `import.meta.env`, and Istanbul coverage. Native TypeScript requires Node 22.18+ or 23.6+. Mock and hoist support uses Node's module-loader API and requires Node 22.15+.

When the Vite module runner is disabled, `experimental.nodeLoader` defaults to `true`. It transforms native execution to support `import.meta.vitest`, `vi.mock`, and `vi.hoisted`. Disable it only when none of those features are used:

```ts
export default defineConfig({
  test: {
    experimental: {
      viteModuleRunner: false,
      nodeLoader: false,
    },
  },
})
```

## Persist transformed modules

`test.experimental.fsModuleCache` persists transformed modules between reruns. It defaults to `false`, does not affect Browser Mode, and is cleared by `vitest --clearCache`.

```ts
export default defineConfig({
  test: {
    experimental: {
      fsModuleCache: true,
      fsModuleCachePath: 'node_modules/.experimental-vitest-cache',
    },
  },
})
```

`fsModuleCachePath` defaults to `node_modules/.experimental-vitest-cache` independently of `test.cache.dir` and Vite's `cacheDir`.

Transforms that depend on external state must register `experimental_defineCacheKeyGenerator` from `configureVitest` to prevent stale results. Returning `false` skips caching for a module. Set `api.vitest.experimental.ignoreFsModuleCache` on plugins whose configuration is irrelevant to cache keys.

## Instrument with OpenTelemetry

`experimental.openTelemetry` loads a configured SDK in the main thread and before each test file. The root-relative `sdkPath` must be directly executable by Node without Vitest transforms and must default-export a started SDK. `browserSdkPath` supplies the browser SDK.

```ts
export default defineConfig({
  test: {
    experimental: {
      openTelemetry: {
        enabled: true,
        sdkPath: './otel.js',
        browserSdkPath: './otel.browser.js',
      },
    },
  },
})
```

Instrumentation is disabled by default and can add substantial overhead. Use it primarily for local performance debugging.

## Measure import durations

`experimental.importDurations` records self time excluding static imports and total time including imports but excluding the current module's transform.

```ts
export default defineConfig({
  test: {
    experimental: {
      importDurations: {
        print: 'on-warn',
        failOnDanger: true,
        limit: 20,
        thresholds: { warn: 150, danger: 750 },
      },
    },
  },
})
```

CLI output supports `print: true` or `'on-warn'` with the `default`, `verbose`, and `tree` reporters. The UI toggles the breakdown independently. `failOnDanger` fails the run and forces the breakdown when an import crosses the danger threshold.

Default thresholds are 100 ms for warnings and 500 ms for danger. `limit` defaults to `0`, or to `10` when printing, failure enforcement, or the UI is enabled.

## Supply changed files from another VCS

`experimental.vcsProvider` replaces the default Git-based file discovery behind `--changed`. Supply an object or a module path whose default export implements `findChangedFiles({ root, changedSince })` and returns file paths. `changedSince` can be a string or boolean.

```ts
export default defineConfig({
  test: {
    experimental: {
      vcsProvider: {
        async findChangedFiles({ root, changedSince }) {
          return []
        },
      },
    },
  },
})
```

This changes test selection for `--changed`; it is separate from `--coverage.changed`, which limits the coverage report.

## Detect asynchronous leaks

Vitest 4.1.0 can report leaked timers, handles, and unresolved resources with source locations:

```sh
vitest --detect-async-leaks
```

The equivalent configuration is `test: { detectAsyncLeaks: true }`. Detection uses `node:async_hooks` and adds runtime overhead, so enable it temporarily while diagnosing leaks.
