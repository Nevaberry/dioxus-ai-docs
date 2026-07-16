# Migration and Configuration

Relevant versioned source batches: `3.0.0`, `3.2.0`, `4.0.0`, and `4.1.0`.

## Contents

- [Replace workspaces with projects](#replace-workspaces-with-projects)
- [Migrate Browser Mode providers and imports](#migrate-browser-mode-providers-and-imports)
- [Update reporters and extensions](#update-reporters-and-extensions)
- [Update test and hook APIs](#update-test-and-hook-apis)
- [Use the installed Vite version](#use-the-installed-vite-version)
- [Filter a test by source line](#filter-a-test-by-source-line)
- [Rerun tests for non-import dependencies](#rerun-tests-for-non-import-dependencies)
- [Review programmatic integrations](#review-programmatic-integrations)
- [Check coverage migration separately](#check-coverage-migration-separately)

## Replace workspaces with projects

Inline workspace configuration was introduced through `test.workspace`, allowing projects to be declared in `vitest.config` without a separate workspace file:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    workspace: ['packages/*'],
  },
})
```

That transitional API is now deprecated. Both a separate `vitest.workspace` file and the `test.workspace` option warn; move declarations to root-level `test.projects` before workspace support is removed in a future major:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: ['packages/*'],
  },
})
```

Before migrating a nontrivial workspace, account for project resolution and inheritance:

- A root `vitest.config` is not itself a test project unless explicitly included.
- File-based project configs inherit none of the root test options.
- An inline project can opt into root-option merging with `extends: true`.
- `coverage`, `reporters`, and `resolveSnapshotPath` remain root-only.
- Every resolved project name must be unique.

See [Projects and coverage](projects-and-coverage.md) for glob, directory, config-name, identity, and scheduling rules.

## Migrate Browser Mode providers and imports

Browser providers are supplied by provider-specific packages and configured by invoking a factory. Browser context APIs come from `vitest/browser`, not `@vitest/browser/context`:

```ts
import { playwright } from '@vitest/browser-playwright'
import { page } from 'vitest/browser'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      provider: playwright(),
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

The provider package already includes `@vitest/browser`, so remove an unnecessary direct dependency. Replace old provider strings such as `provider: 'playwright'` with factory calls.

Passing `--browser` also requires a configured `browser` option. It no longer assumes a Node test configuration can run unchanged in a browser:

```sh
npx vitest --browser=chromium --browser.headless
```

Open [Browser Mode](browser-mode.md) for instance overrides, provider selection, locators, traces, screenshots, and runtime requirements.

## Update reporters and extensions

The public reporter lifecycle was redesigned; custom reporters centered on the previous `onTaskUpdate` callback need review.

The `basic` reporter was removed. Use the default reporter with its summary disabled for the closest replacement:

```ts
export default defineConfig({
  test: {
    reporters: [['default', { summary: false }]],
  },
})
```

Reporter output semantics also changed: `default` shows a test tree only for a single test file, `tree` always shows it, and `verbose` reports each test as it completes in every environment.

The VS Code extension removed `maximumConfigs` and no longer leaves Vitest running in the background unless continuous run is enabled manually or through `watchOnStartup`. See [Reporters and integrations](reporters-and-integrations.md) for the current reporter and extension surface.

## Update test and hook APIs

Review these test-facing compatibility changes:

- Old `toBe*` mock/spy assertions are deprecated. Use their `toHaveBeen*` forms or `toThrowError` as appropriate.
- `beforeAll`, `afterAll`, and `aroundAll` receive file/worker fixture contexts, but no longer receive the previously undocumented `Suite` argument.
- WebdriverIO and Preview locator actions are strict by default. Add `{ strict: false }` only to an action that intentionally uses the first of multiple matches.
- Browser screenshot comparison uses BlazeDiff instead of Pixelmatch, which can alter visual-diff results.
- The `--update` snapshot flag accepts explicit `new` and `all` modes; snapshot configuration accepts `update: 'none'`.

## Use the installed Vite version

Vitest supports Vite 8. When possible, it reuses the project's installed `vite` package instead of obtaining a separate copy. This avoids configuration type mismatches caused by two Vite versions.

## Filter a test by source line

Append a line number to a test-file path to run the test at that location. Both accepted relative forms are useful in scripts and editor integrations:

```sh
vitest basic/foo.js:10
vitest ./basic/foo.js:10
```

## Rerun tests for non-import dependencies

Static and dynamic imports let Vitest infer most watch dependencies. Use `test.watchTriggerPatterns` when changes outside that graph—templates, generated inputs, child-process resources, or similar files—must rerun related tests.

Each entry matches a changed path and computes the test path or paths to run:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    watchTriggerPatterns: [{
      pattern: /^src\/templates\/(.*)\.html$/,
      testsToRun: (_file, match) =>
        `api/tests/mailers/${match[1]}.test.ts`,
    }],
  },
})
```

## Review programmatic integrations

The Node API exported from `vitest/node` was redesigned. Do not carry assumptions from the earlier experimental shape into current integrations. Custom runners, editor adapters, and build tooling should use the current methods documented in [Reporters and integrations](reporters-and-integrations.md), including static collection and specification filtering.

## Check coverage migration separately

Coverage behavior has independent opt-ins and new extension interfaces. In particular, AST-aware V8 remapping began as an explicit option, ignore comments need transform-preserving forms, and changed-file coverage is different from changed-test selection. See [Projects and coverage](projects-and-coverage.md) before updating coverage configuration.
