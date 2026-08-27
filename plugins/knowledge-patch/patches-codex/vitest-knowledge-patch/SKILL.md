---
name: vitest-knowledge-patch
description: Vitest
version: "4.1"
license: MIT
metadata:
  author: Nevaberry
---


# Vitest Knowledge Patch

Use this skill when configuring, migrating, extending, or debugging a modern Vitest suite. Start with the migration checks, then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser Mode](references/browser-mode.md) | Providers, instances, locators, debugging, traces, screenshots, UI, and runtime behavior |
| [Experimental features](references/experimental-features.md) | Native Node execution, module caching, telemetry, import timing, changed files, and leak detection |
| [Migration and configuration](references/migration-and-configuration.md) | Workspace migration, compatibility changes, source-line filtering, watch triggers, and concurrency |
| [Projects and coverage](references/projects-and-coverage.md) | Project discovery and inheritance, scheduling, coverage providers, reporters, and exclusions |
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

The separate `vitest.workspace` file and `test.workspace` option are deprecated. A root config is not automatically a project. File-based project configs inherit no root test options; inline projects can opt in with `extends: true`.

Apply these migration checks:

- Import browser-provider factories from their provider packages and call them. Import browser context APIs from `vitest/browser`.
- Configure `test.browser` before using `--browser`; the flag does not convert a Node setup into a browser setup.
- Replace the removed `basic` reporter with `['default', { summary: false }]`.
- Replace deprecated `toBe*` spy assertions with their `toHaveBeen*` equivalents or `toThrowError`.
- Remove any reliance on the undocumented `Suite` argument in suite hooks.
- Expect WebdriverIO and Preview actions to reject locators matching multiple elements unless the action sets `strict: false`.
- Review visual baselines because screenshot comparison changed.
- Keep project names unique and keep coverage, reporters, and snapshot-path resolution at the root.

See [Migration and configuration](references/migration-and-configuration.md) for the full checklist and [Projects and coverage](references/projects-and-coverage.md) for project resolution.

## Configure Browser Mode

Use a real automation provider for CI or headless execution:

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

`@vitest/browser-preview` is a local event-simulation environment, not a CI/headless provider. Scaffold with `vitest init browser`, or configure Playwright or WebdriverIO manually. Run a configured instance with:

```sh
npx vitest --browser=chromium --browser.headless
```

Use `page.frameLocator` for iframe content, `locators.extend` for domain-specific queries, and `toBeInViewport({ ratio })` for intersection visibility. Native browser module namespace objects are sealed; use `vi.mock('./module', { spy: true })` before configuring an exported function.

Open [Browser Mode](references/browser-mode.md) before adding traces, screenshot baselines, persistent contexts, custom locators, or debugger integration.

## Add traces and visual regression

Record Playwright traces on failure or retry without tracing every passing test:

```ts
browser: {
  provider: playwright(),
  trace: {
    mode: 'retain-on-failure',
    tracesDir: './playwright-traces',
  },
}
```

Other selective modes are `on-first-retry` and `on-all-retries`; `trace: 'on'` records every test. Add semantic entries with `page.mark`, `locator.mark`, and `vi.defineHelper`.

Visual baselines use an asynchronous browser assertion:

```ts
await expect(page.getByTestId('hero')).toMatchScreenshot('hero-section', {
  screenshotOptions: { mask: [page.getByTestId('last-seen')] },
})
```

A missing baseline is written and the run fails intentionally. Review and commit the browser-and-platform-specific image, control continuously changing content, and use `vitest --update` for deliberate changes.

## Define projects explicitly

`test.projects` accepts inline configs, direct config paths, directories, and glob patterns. Directory matches can become projects without config files; matched config files must use supported Vitest/Vite config names.

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

Use `defineProject` in file-based project configs so unsupported project properties fail type checking. Projects with the same `groupOrder` run together; lower groups run first.

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

Use `test.aroundEach` or `test.aroundAll` when a transaction, tracing span, or async context must surround the test or suite. The callback must invoke its supplied runner.

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

Precedence is `not`, `and`, then `or`; repeated filter flags combine with AND. Suite tags are inherited, and `@module-tag` applies file-wide. Open [Test APIs](references/test-apis.md) for conflict priority, TypeScript catalogs, UI/API filtering, and runtime checks.

## Attach annotations and metadata

`annotate` accepts a message plus a type or attachment object and forwards the result to reporters:

```ts
test('creates a report', async ({ annotate }) => {
  await annotate('starting export', 'notice')
  await annotate('created report', { body: createTestSpecificFile() })
})
```

Await annotations when later code depends on completion. Vitest waits for otherwise-unawaited annotation work before finishing the test. Use the independent `meta` test option for arbitrary machine-readable data.

## Prefer current assertion and mock APIs

- Augment `Matchers` once for custom instance, asymmetric, and implementation matcher typing.
- Use `expect.assert(condition)` when an assertion signature must narrow a TypeScript type.
- Use `expect.schemaMatching(schema)` with a Standard Schema v1 implementation inside equality assertions.
- Bind `vi.spyOn` or `vi.fn` with `using` for automatic restoration where Explicit Resource Management is available.
- Bind the disposable returned by `vi.doMock` with `using` to remove a dynamic mock at scope exit.
- Sinon-compatible Chai chains such as `expect(fn).to.have.callCount(1)` are available.
- Fake timers expose Sinon's `setTickMode` controls.
- Snapshot updating accepts `--update=new`, `--update=all`, and configuration `update: 'none'`.

The test context also has an `AbortSignal` that fires on timeout, interruption, or a bail-triggering failure; pass it into cancellable work.

## Choose coverage behavior deliberately

Use `--coverage.changed` to run the selected tests but report only modified files. This differs from `--changed`, which narrows the tests themselves.

Both built-in providers understand start/stop ignore regions. Preserve ignore comments through transforms with `-- @preserve`; V8 additionally supports branch, next-node, and whole-file directives.

Custom Istanbul-compatible reporters can be loaded by package or absolute path. A custom provider uses `provider: 'custom'` with `customProviderModule`. Open [Projects and coverage](references/projects-and-coverage.md) before implementing either interface.

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

This disables Vite transforms, plugins, aliases, `import.meta.env`, and Istanbul coverage. Native TypeScript and optional mock-supporting loader behavior have specific Node requirements. Consult [Experimental features](references/experimental-features.md) before enabling it; that reference also covers transformed-module caching, telemetry, import-duration budgets, and custom changed-file discovery.

## Select reporters and integrations

The reporter lifecycle no longer centers on `onTaskUpdate`; review custom implementations. Built-ins include `tree`, completion-oriented `verbose`, GitHub Actions summaries, and the failure-only `agent` reporter.

For tooling, prefer the current public APIs for static collection, specification creation and filtering, test-file runs, watcher control, dynamic coverage, and run completion. Open [Reporters and integrations](references/reporters-and-integrations.md) for exact method names and editor behavior.
