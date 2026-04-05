# Migration to Vitest 4

## Prerequisites

- **Vite >= 6.0.0**
- **Node.js >= 20.0.0**

## V8 Coverage Overhaul

V8 provider now uses AST-based remapping (identical accuracy to Istanbul). Previously used `v8-to-istanbul` which had many false positives.

### Removed Options

- `coverage.all` — removed. By default, only covered files are included. Define `coverage.include` explicitly to include uncovered files
- `coverage.extensions` — removed
- `coverage.ignoreEmptyLines` — removed (lines without runtime code no longer included)
- `coverage.experimentalAstAwareRemapping` — removed (now always on)

### Recommended Coverage Setup

```ts
export default defineConfig({
  test: {
    coverage: {
      include: ['packages/**/src/**.{js,jsx,ts,tsx}'],
      exclude: ['**/some-pattern/**'],
    },
  },
})
```

Without `coverage.include`, only files loaded during tests appear in reports.

### New Coverage Features

- `coverage.ignoreClassMethods` now supported by V8 provider
- `coverage.changed` (v4.1) — limit coverage to modified files only (runs all tests, but reports only changed files)
- `coverage.htmlDir` (v4.1) — custom directory for coverage HTML output
- `/* v8 ignore start/stop */` and `/* istanbul ignore start/stop */` comments restored (v4.1, both providers)

```ts
/* v8 ignore start -- @preserve */
if (parameter) { console.log('Ignored') }
/* v8 ignore stop -- @preserve */
console.log('Included')
```

## Simplified `exclude`

Vitest 4 only excludes `node_modules` and `.git` by default. No longer excludes `dist`, `cypress`, `.idea`, `.cache`, config files, etc.

Use `test.dir` to limit test file directory (more performant than excludes):

```ts
export default defineConfig({
  test: { dir: './frontend/tests' },
})
```

Or restore old excludes:

```ts
import { configDefaults, defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    exclude: [
      ...configDefaults.exclude,
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build,eslint,prettier}.config.*',
    ],
  },
})
```

## `workspace` Replaced with `projects`

The `workspace` config is fully removed. Migrate:

```ts
// Before:
test: { workspace: './vitest.workspace.js' }
// After:
test: { projects: ['./packages/*', { test: { name: 'unit' } }] }
```

`defineWorkspace` is removed — use `defineConfig` with `test.projects`.

## Browser Provider Rework

Provider is now a function from a dedicated package:

```ts
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      provider: playwright(), // not 'playwright' string
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

Install `@vitest/browser-playwright`, `@vitest/browser-webdriverio`, or `@vitest/browser-preview`. Remove `@vitest/browser` from dependencies.

## Mocking Changes

See `references/matchers-mocking.md` for full details. Key breaking changes:

- `vi.fn().getMockName()` returns `vi.fn()` (was `spy`) — affects snapshots
- `vi.restoreAllMocks` only restores manual `vi.spyOn` spies
- `vi.fn().mock.invocationCallOrder` starts at `1` (was `0`)
- Arrow functions in `mockImplementation` throw when mock is called with `new`
- Automocked getters return `undefined` (no longer call original)

## `vite-node` Replaced with Module Runner

Vitest uses Vite's built-in Module Runner instead of `vite-node`:

- `VITE_NODE_DEPS_MODULE_DIRECTORIES` → `VITEST_MODULE_DIRECTORIES`
- `vitest/execute` entry point removed
- Custom environments: `transformMode` → `viteEnvironment`
- `deps.optimizer.web` → `deps.optimizer.client`
- `vite-node` no longer a dependency

## `experimental.viteModuleRunner: false` (v4.1)

Disable Vite's module runner for native Node.js `import`:

```ts
export default defineConfig({
  test: {
    experimental: { viteModuleRunner: false },
  },
})
```

Benefits: faster startup, production-like behavior. Requires Node.js 22.15+ for `vi.mock`/`vi.hoisted`. Not available: `import.meta.env`, Vite plugins, aliases, `istanbul` provider.

TypeScript works natively on Node.js 22.18+/23.6+. For 22.6-22.18: `NODE_OPTIONS="--experimental-strip-types" vitest`.

### Mocking Differences

```ts
// vi.spyOn on ESM doesn't work:
vi.spyOn(fs, 'readFileSync') // ❌

// Use vi.mock with spy: true:
vi.mock('node:fs', { spy: true })
fs.readFileSync.mockImplementation(() => '42') // ✅
```

## Standalone Mode Change

`vitest --standalone math.test.ts` now runs matched files immediately (previously ignored the filter).

## Other Experimental Features (v4.0.11+)

### `experimental.fsModuleCache`

Persistent file system cache for faster reruns. Clear with `vitest --clearCache`.

```ts
experimental: { fsModuleCache: true }
```

### `experimental.openTelemetry`

OpenTelemetry support for debugging slow tests:

```ts
experimental: {
  openTelemetry: {
    enabled: true,
    sdkPath: './otel.js',
  },
}
```

### `experimental.importDurations` (v4.1)

Track and display module import times:

```ts
experimental: {
  importDurations: {
    print: true,        // or 'on-warn'
    failOnDanger: true, // fail if any import > 500ms
    thresholds: { warn: 100, danger: 500 },
  },
}
```
