---
name: vitest-knowledge-patch
description: "Vitest changes since training cutoff (latest: 4.1) — projects config, test tags, stable browser mode, visual regression, test.extend builder, aroundEach hooks, expect.schemaMatching, agent reporter. Load before working with Vitest."
license: MIT
metadata:
  author: Nevaberry
  version: "4.1"
---

# Vitest Knowledge Patch (3.0 – 4.1)

Supplementary knowledge for Vitest features released after Claude's training cutoff. Covers versions 3.0 through 4.1 (January 2025 – March 2026).

## Reference Files

- **`references/projects-config.md`** — `workspace` replaced by `projects`, inline config, `sequence.groupOrder`, `watchTriggerPatterns`, `defineProject`
- **`references/browser-mode.md`** — Stable browser mode (v4), provider packages, locators, visual regression testing, Playwright traces, frame locators
- **`references/test-fixtures-hooks.md`** — Scoped fixtures, `test.extend` builder pattern, `aroundEach`/`aroundAll` hooks, type-aware hooks, `vi.defineHelper`, test `signal` API
- **`references/matchers-mocking.md`** — `expect.assert`, `expect.schemaMatching`, `Matchers` type, `mockThrow`, `using` with vi.spyOn/fn, v4 mocking changes
- **`references/test-organization.md`** — Test tags (v4.1), test annotations, `agent` reporter, GitHub Actions job summary, `--detect-async-leaks`
- **`references/migration-v4.md`** — Breaking changes, coverage overhaul, simplified `exclude`, `viteModuleRunner: false`, Node.js 20+ requirement

---

## Projects (replaces Workspace)

The `workspace` config and separate `vitest.workspace` files are deprecated (v3.2) and removed in v4. Use `projects` instead:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      'packages/*',
      {
        extends: true, // inherit root config
        test: {
          name: 'unit',
          include: ['**/*.unit.test.ts'],
        },
      },
      {
        test: {
          name: { label: 'browser', color: 'green' },
          browser: { enabled: true, /* ... */ },
        },
      },
    ],
  },
})
```

Use `defineProject` (not `defineConfig`) in per-project config files — it enforces project-level type safety.

## Browser Mode (Stable in v4)

Provider is now a function from a dedicated package, not a string. `@vitest/browser` is included automatically.

```ts
import { defineConfig } from 'vitest/config'
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      provider: playwright(),
      enabled: true,
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

Packages: `@vitest/browser-playwright`, `@vitest/browser-webdriverio`, `@vitest/browser-preview`. Import context from `vitest/browser` (not `@vitest/browser/context`).

## Test Tags (v4.1)

Define tags in config with optional test options. Filter with `--tags-filter`:

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    tags: [
      { name: 'db', timeout: 60_000 },
      { name: 'flaky', retry: process.env.CI ? 3 : 0, priority: 1 },
    ],
  },
})

// test file
test('flaky db test', { tags: ['flaky', 'db'] }, () => { /* ... */ })
```

```sh
vitest --tags-filter="frontend && !flaky"
vitest --tags-filter="(unit || e2e) && !slow"
```

Supports `and`/`&&`, `or`/`||`, `not`/`!`, `*` wildcards, `()` grouping.

## `test.extend` Builder Pattern (v4.1)

Return a value instead of calling `use()` — TypeScript infers fixture types automatically:

```ts
const test = baseTest
  .extend('config', { port: 3000, host: 'localhost' })
  .extend('server', async ({ config }) => {
    return `http://${config.host}:${config.port}`
  })
  .extend('tempFile', async ({}, { onCleanup }) => {
    const path = `/tmp/test-${Date.now()}.txt`
    await fs.writeFile(path, 'data')
    onCleanup(() => fs.unlink(path))
    return path
  })
```

## `aroundEach` / `aroundAll` Hooks (v4.1)

Wrap tests in a context (transactions, AsyncLocalStorage, tracing spans):

```ts
test.aroundEach(async (runTest, { db }) => {
  await db.transaction(runTest)
})

test('insert user', async ({ db }) => {
  await db.insert({ name: 'Alice' }) // runs inside transaction
})
```

## Key New APIs

| API | Version | Purpose |
|-----|---------|---------|
| `expect.schemaMatching(schema)` | 4.0 | Asymmetric matcher for Standard Schema v1 (Zod, Valibot, ArkType) |
| `expect.assert(condition)` | 4.0 | Type-narrowing assertion (like Chai assert on expect) |
| `vi.fn().mockThrow(error)` | 4.1 | Concise mock throwing (replaces `mockImplementation(() => { throw })`) |
| `vi.defineHelper(fn)` | 4.1 | Removes helper internals from stack traces |
| `using spy = vi.spyOn(...)` | 3.2 | Explicit Resource Management — auto-restores on block exit |
| `context.signal` | 3.2 | `AbortSignal` aborted on timeout, bail, or Ctrl+C |
| `context.annotate(msg)` | 3.2 | Attach messages/files to test results for reporters |
| `page.mark(name, fn?)` | 4.1 | Add named markers to Playwright trace timeline |
| `toMatchScreenshot(name)` | 4.0 | Visual regression testing in browser mode |
| `page.frameLocator(loc)` | 4.0 | Locate elements inside iframes (Playwright only) |
| `locator.length` | 4.0 | Use `toHaveLength` on locators |

## Visual Regression Testing (v4)

```ts
import { page } from 'vitest/browser'
await expect(page.getByTestId('hero')).toMatchScreenshot('hero-section')
```

Screenshots stored in `__screenshots__/` next to tests, named `{name}-{browser}-{platform}.png`. Update with `vitest --update`. See `references/browser-mode.md` for configuration.

## Coverage Changes (v4)

- `coverage.all` and `coverage.extensions` removed — define `coverage.include` explicitly
- V8 provider now uses AST-aware remapping (identical accuracy to Istanbul)
- `coverage.ignoreEmptyLines` removed
- New: `coverage.changed` — limit coverage to modified files only
- `/* v8 ignore start/stop */` and `/* istanbul ignore start/stop */` comments restored (v4.1)

## Agent Reporter (v4.1)

Auto-enabled when running inside AI coding agents. Only shows failed tests and errors, reducing token usage:

```sh
AI_AGENT=copilot vitest
```

## `experimental.viteModuleRunner: false` (v4.1)

Disable Vite's module runner to run tests with native Node.js `import`. Faster startup, closer to production. Requires Node.js 22.15+ for `vi.mock`/`vi.hoisted`. No `import.meta.env`, plugins, or aliases.

```ts
export default defineConfig({
  test: {
    experimental: { viteModuleRunner: false },
  },
})
```

## `--detect-async-leaks` (v4.1)

Detect leaked timers, handles, and unresolved async resources with source locations:

```sh
vitest --detect-async-leaks
```

## Reporter Changes (v4)

- `basic` reporter removed — use `['default', { summary: false }]`
- `verbose` now always prints tests one-by-one (not just CI)
- New `tree` reporter for always-on tree output
- `github-actions` reporter auto-generates Job Summary with flaky test details (v4.1)
