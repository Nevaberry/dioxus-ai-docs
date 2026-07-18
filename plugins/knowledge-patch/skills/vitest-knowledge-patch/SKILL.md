---
name: vitest-knowledge-patch
description: Vitest
license: MIT
version: "4.1"
metadata:
  author: Nevaberry
---

# Vitest Knowledge Patch

Use this skill when configuring, migrating, extending, or debugging a modern Vitest suite. Start with the migration notes, then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser Mode](references/browser-mode.md) | Provider setup, instances, locators, debugging, traces, screenshots, and browser UI |
| [Experimental features](references/experimental-features.md) | Native Node execution, file-system module cache, OpenTelemetry, import timings, changed-file providers, and leak detection |
| [Migration and configuration](references/migration-and-configuration.md) | Workspace migration, compatibility changes, source-line filtering, and watch triggers |
| [Projects and coverage](references/projects-and-coverage.md) | Project discovery and inheritance, scheduling, coverage providers/reporters, exclusions, and changed-file coverage |
| [Reporters and integrations](references/reporters-and-integrations.md) | Reporter migration, annotations, GitHub Actions, editor behavior, and programmatic APIs |
| [Test APIs](references/test-apis.md) | Fixtures, hooks, annotations, tags, matchers, mocks, timers, metadata, and snapshots |

## Migrate configuration first

Replace both workspace forms with root-level `test.projects`:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: ['packages/*'],
  },
})
```

The separate `vitest.workspace` file and `test.workspace` option are deprecated. A root config is not automatically a project. File-based project configs do not inherit root test options; inline projects can opt in with `extends: true`.

Keep these migration checks in view:

- Browser providers are factory functions from provider-specific packages, and browser context APIs come from `vitest/browser`.
- `--browser` requires browser configuration; it no longer turns an arbitrary Node configuration into a browser configuration.
- The `basic` reporter is gone. Use `['default', { summary: false }]` for the closest replacement.
- Old `toBe*` spy assertions are deprecated; use the corresponding `toHaveBeen*` assertion or `toThrowError`.
- File/worker contexts are available to suite hooks, but suite hooks no longer receive the undocumented `Suite` argument.
- WebdriverIO and Preview actions now reject locators matching multiple elements unless that action sets `strict: false`.
- Browser image comparison uses BlazeDiff, so existing visual results can change.
- Vitest supports Vite 8 and reuses the project's installed Vite when possible.

See [Migration and configuration](references/migration-and-configuration.md) for the complete checklist and [Projects and coverage](references/projects-and-coverage.md) for resolution rules.

## Configure Browser Mode

Use a production browser provider in CI or headless runs:

```ts
import { playwright } from '@vitest/browser-playwright'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      provider: playwright(),
      instances: [
        { browser: 'chromium' },
        { browser: 'firefox', setupFiles: ['./setup.firefox.ts'] },
      ],
    },
  },
})
```

`@vitest/browser-preview` is a local event simulation environment, not a CI/headless provider. Use Playwright or WebdriverIO when real browser automation matters. `vitest init browser` can scaffold the dependencies and configuration.

For a configured instance:

```sh
npx vitest --browser=chromium --browser.headless
```

Use `page.frameLocator` for iframe content, custom methods through `locators.extend`, and `toBeInViewport({ ratio })` for visibility by intersection. Native browser module namespace objects are sealed; use `vi.mock('./module', { spy: true })` before configuring an exported function.

Open [Browser Mode](references/browser-mode.md) before adding traces, screenshot baselines, persistent contexts, custom locators, or debugger integration.

## Add traces and visual regression

Playwright traces can be always-on or limited to retry/failure paths:

```ts
browser: {
  provider: playwright(),
  trace: {
    mode: 'retain-on-failure',
    tracesDir: './playwright-traces',
  },
}
```

The other selective modes are `on-first-retry` and `on-all-retries`; `trace: 'on'` records every test. Add semantic trace entries with `page.mark`, `locator.mark`, and `vi.defineHelper`.

Visual baselines use the asynchronous browser assertion:

```ts
await expect(page.getByTestId('hero')).toMatchScreenshot('hero-section', {
  screenshotOptions: { mask: [page.getByTestId('last-seen')] },
})
```

A missing baseline is written and the run fails intentionally. Review and commit the browser-and-platform-specific file, control animated content, and use `vitest --update` for deliberate changes.

## Define projects explicitly

`test.projects` accepts inline configs, config paths, directories, and glob patterns. Directory matches can become projects without config files; matched config files must follow Vitest/Vite config naming rules. Every project needs a unique resolved name.

```ts
export default defineConfig({
  test: {
    projects: [{
      extends: true,
      test: {
        name: { label: 'unit', color: 'red' },
        include: ['**/*.unit.test.ts'],
        sequence: { groupOrder: 0 },
      },
    }],
  },
})
```

`coverage`, `reporters`, and `resolveSnapshotPath` are root-only. Use `defineProject` in file-based project configs so unsupported project properties fail type checking.

## Use scoped and builder fixtures

Fixtures can be test-, file-, or worker-scoped. File fixtures behave like lazy top-level suite hooks; worker fixtures initialize once per worker. Default worker isolation still recreates state, so disable isolation only when shared worker state is intentional.

The builder form infers fixture types and registers teardown through `onCleanup`:

```ts
const test = baseTest
  .extend('config', { port: 3000 })
  .extend('server', async ({ config }, { onCleanup }) => {
    const server = await startServer(config.port)
    onCleanup(() => server.close())
    return server
  })
```

Use `test.aroundEach` or `test.aroundAll` when a transaction, tracing span, or async context must surround the test or suite. The callback must invoke the supplied runner.

## Catalog and filter tags

Declare tags before attaching them; there are no built-ins and undeclared tags throw unless `strictTags: false`.

```ts
export default defineConfig({
  test: {
    tags: [
      { name: 'db', timeout: 60_000 },
      { name: 'flaky', retry: 3, priority: 1 },
    ],
  },
})

test('query', { tags: ['db', 'flaky'] }, () => {})
```

Filter with boolean expressions:

```sh
vitest --tags-filter="db && !flaky"
vitest --list-tags
```

Precedence is `not`, `and`, then `or`; repeated filter flags combine with AND. Tags on suites are inherited, and `@module-tag` applies file-wide. Open [Test APIs](references/test-apis.md) for conflict priority, TypeScript catalogs, UI/API filtering, and runtime checks.

## Attach annotations and metadata

`annotate` accepts a message plus a type or attachment object and forwards the result to reporters:

```ts
test('creates a report', async ({ annotate }) => {
  await annotate('starting export', 'notice')
  await annotate('created report', { body: createTestSpecificFile() })
})
```

Await annotations when later code depends on completion. Vitest waits for otherwise-unawaited annotation work before finishing the test. Use the independent `meta` test option for arbitrary machine-readable data.

## Prefer the current assertion and mock APIs

- Use one `Matchers` augmentation for custom instance, asymmetric, and implementation matcher typing.
- Use `expect.assert(condition)` when an assertion signature must narrow a TypeScript type.
- Use `expect.schemaMatching(schema)` with a Standard Schema v1 implementation inside equality assertions.
- Bind `vi.spyOn` or `vi.fn` with `using` for automatic restoration where Explicit Resource Management is available.
- Bind the disposable returned by `vi.doMock` with `using` to remove a dynamic mock at scope exit.
- Sinon-compatible Chai chains such as `expect(fn).to.have.callCount(1)` are available.
- Fake timers expose Sinon's `setTickMode` controls.
- Snapshot updating accepts `--update=new`, `--update=all`, and configuration `update: 'none'`.

The test context also has an `AbortSignal` that fires on timeout, interruption, or a bail-triggering failure; pass it into cancellable work.

## Choose coverage behavior deliberately

Use `--coverage.changed` to run the selected tests but report only modified files. This is different from `--changed`, which narrows the tests themselves.

Both built-in providers understand start/stop ignore regions. Preserve ignore comments through transforms with `-- @preserve`; V8 additionally supports branch, next-node, and whole-file directives.

Custom Istanbul-compatible reporters can be loaded by package or absolute path. A custom provider uses `provider: 'custom'` with `customProviderModule`. See [Projects and coverage](references/projects-and-coverage.md) before implementing either interface.

## Diagnose execution and imports

Use `--detect-async-leaks` temporarily to locate leaked timers, handles, and unresolved resources; it uses async hooks and adds overhead.

Native Node execution is opt-in:

```ts
export default defineConfig({
  test: {
    experimental: {
      viteModuleRunner: false,
    },
  },
})
```

This disables Vite transforms, plugins, aliases, `import.meta.env`, and Istanbul coverage. Native TypeScript and the optional mock-supporting Node loader have specific Node version requirements. Consult [Experimental features](references/experimental-features.md) before enabling it.

That reference also covers persistent transformed-module caching, OpenTelemetry instrumentation, import-duration budgets, and custom changed-file discovery.

## Select reporters and programmatic APIs

The reporter lifecycle no longer centers on `onTaskUpdate`; review custom implementations. Useful built-ins include `tree`, completion-oriented `verbose`, GitHub Actions summaries, and the failure-only `agent` reporter.

For tooling, prefer the current public APIs for static collection, specification creation/filtering, test-file runs, watcher control, dynamic coverage, and run completion. Open [Reporters and integrations](references/reporters-and-integrations.md) for exact method names and editor behavior.
