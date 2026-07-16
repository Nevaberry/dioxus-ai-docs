# Experimental Features

Relevant versioned source batch: `4.1.0`.

## Contents

- [Execute with native Node imports](#execute-with-native-node-imports)
- [Control the optional native Node loader](#control-the-optional-native-node-loader)
- [Persist transformed modules between reruns](#persist-transformed-modules-between-reruns)
- [Instrument runs with OpenTelemetry](#instrument-runs-with-opentelemetry)
- [Measure import durations](#measure-import-durations)
- [Replace Git changed-file discovery](#replace-git-changed-file-discovery)
- [Detect asynchronous resource leaks](#detect-asynchronous-resource-leaks)

Experimental options can change shape or carry substantial performance and compatibility tradeoffs. Enable them for a specific need, and document why the suite relies on them.

## Execute with native Node imports

Set `experimental.viteModuleRunner: false` to execute test files, source files, and setup files through native Node imports:

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

This mode disables the behavior supplied by Vite's module runner, including:

- Vite transforms and plugins
- Vite aliases
- `import.meta.env`
- Istanbul coverage

Native TypeScript execution requires Node 22.18 or newer, or Node 23.6 or newer. Supporting `vi.mock` and `vi.hoisted` in this mode relies on Node's module-loader API and requires Node 22.15 or newer.

## Control the optional native Node loader

When `experimental.viteModuleRunner` is `false`, `experimental.nodeLoader` defaults to `true`. The loader supplies transformations needed for:

- `import.meta.vitest`
- `vi.mock`
- `vi.hoisted`

Disable it only if the native-import suite uses none of those features and the loader work is unwanted:

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

## Persist transformed modules between reruns

`test.experimental.fsModuleCache` stores transformed modules on disk for reuse across reruns. It defaults to `false` and does not affect Browser Mode.

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    experimental: {
      fsModuleCache: true,
      fsModuleCachePath: 'node_modules/.experimental-vitest-cache',
    },
  },
})
```

`fsModuleCachePath` defaults to `node_modules/.experimental-vitest-cache`. It is independent of both `test.cache.dir` and Vite's `cacheDir`. Clear stored entries with:

```sh
vitest --clearCache
```

Transform plugins that depend on external state must participate in cache-key generation or stale transforms can be reused. Register `experimental_defineCacheKeyGenerator` from the plugin's `configureVitest` hook. A generator can return `false` to skip caching a module. A plugin that is irrelevant to transform cache keys can set `api.vitest.experimental.ignoreFsModuleCache`.

## Instrument runs with OpenTelemetry

`experimental.openTelemetry` loads a configured SDK in the main thread and before every test file:

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

The root-relative `sdkPath` must be directly executable by Node without Vitest transforms and must default-export an already-started SDK. `browserSdkPath` supplies the browser-side SDK.

Instrumentation is disabled by default and can add substantial overhead. It is intended primarily for local performance debugging rather than routine suite execution.

## Measure import durations

`experimental.importDurations` records two timings:

- Self time excludes time spent in static imports.
- Total time includes static-import time but excludes the current module's transform time.

Configure printing, budgets, and thresholds together:

```ts
export default defineConfig({
  test: {
    experimental: {
      importDurations: {
        print: 'on-warn',
        failOnDanger: true,
        limit: 20,
        thresholds: {
          warn: 150,
          danger: 750,
        },
      },
    },
  },
})
```

CLI output supports `print: true` and `print: 'on-warn'` with the `default`, `verbose`, and `tree` reporters. The UI can toggle the timing breakdown independently.

`failOnDanger` fails the run when an import exceeds the danger threshold and forces the breakdown to be shown. Defaults are:

- Warning threshold: 100 ms
- Danger threshold: 500 ms
- `limit`: `0` normally, or `10` when printing, failure enforcement, or the UI is enabled

## Replace Git changed-file discovery

`experimental.vcsProvider` replaces the default Git-based file discovery used by `--changed`. Supply an object directly or a module path whose default export implements `findChangedFiles`:

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

`findChangedFiles({ root, changedSince })` returns file paths. `changedSince` is an optional string or boolean.

This changes how `--changed` discovers files; it is separate from `--coverage.changed`, which limits coverage output to modified files while retaining the selected test set.

## Detect asynchronous resource leaks

Enable async leak detection temporarily to find leaked timers, handles, and unresolved asynchronous resources with source locations:

```sh
vitest --detect-async-leaks
```

The equivalent configuration is:

```ts
export default defineConfig({
  test: {
    detectAsyncLeaks: true,
  },
})
```

Leak detection uses `node:async_hooks` and adds runtime overhead, so it is best used as a focused diagnostic rather than left on for every run.
