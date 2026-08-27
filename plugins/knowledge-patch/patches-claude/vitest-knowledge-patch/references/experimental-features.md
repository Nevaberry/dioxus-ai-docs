# Experimental Features

Experimental options have sharper compatibility and performance tradeoffs than ordinary configuration. Enable them deliberately and keep project behavior and runtime versions authoritative.

## Run with native Node imports

Since 4.1.0, set `experimental.viteModuleRunner: false` to execute tests, source, and setup files with native Node imports:

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

This disables Vite transforms, plugins, aliases, `import.meta.env`, and Istanbul coverage. Native TypeScript requires Node 22.18+ or 23.6+. Support for `vi.mock` and `vi.hoisted` in this mode uses Node's module-loader API and requires Node 22.15+.

## Configure the optional Node loader

When `experimental.viteModuleRunner` is `false`, `experimental.nodeLoader` defaults to `true`. It transforms native Node execution to support `import.meta.vitest`, `vi.mock`, and `vi.hoisted`. Disable it only when none of those features are needed:

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

`test.experimental.fsModuleCache` persists transformed modules between reruns. It defaults to `false`, does not affect Browser Mode, and `vitest --clearCache` removes stored entries. `fsModuleCachePath` defaults to `node_modules/.experimental-vitest-cache`, independently of `test.cache.dir` and Vite's `cacheDir`.

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

Transform plugins that depend on external state must register `experimental_defineCacheKeyGenerator` from `configureVitest` to prevent stale output. Returning `false` skips a module. Set `api.vitest.experimental.ignoreFsModuleCache` when a plugin is irrelevant to cache keys.

## Instrument with OpenTelemetry

`experimental.openTelemetry` loads a configured SDK in the main thread and before every test file. The root-relative `sdkPath` must be directly executable by Node without Vitest transforms and must default-export a started SDK; `browserSdkPath` supplies the browser SDK.

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

## Diagnose import durations

`experimental.importDurations` collects module self time excluding static imports and total time including them but excluding the current module's transform. CLI printing supports `true` or `'on-warn'` with the `default`, `verbose`, and `tree` reporters; the UI can toggle the breakdown independently.

`failOnDanger` fails the run and forces the breakdown when an import exceeds the danger threshold. Warning and danger defaults are 100 ms and 500 ms. `limit` defaults to `0`, or to `10` when printing, failure enforcement, or the UI is enabled.

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

## Supply changed files from another VCS

`experimental.vcsProvider` replaces the default Git-based changed-file detection used by `--changed`. Supply an object or a module path whose default export implements `findChangedFiles({ root, changedSince })` and returns file paths. `changedSince` is an optional string or boolean.

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

## Detect asynchronous leaks

Since 4.1.0, `detectAsyncLeaks` reports leaked timers, handles, and unresolved async resources with source locations. It uses `node:async_hooks` and adds runtime overhead, so enable it temporarily:

```sh
vitest --detect-async-leaks
```

The equivalent configuration is `test: { detectAsyncLeaks: true }`.
