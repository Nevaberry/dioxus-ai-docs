# Test Organization

## Test Tags (v4.1)

Tags label tests for filtering and option overrides. Must be defined in config — undefined tags cause errors (disable with `strictTags: false`).

### Define Tags

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    tags: [
      { name: 'frontend', description: 'Frontend tests.' },
      { name: 'backend', description: 'Backend tests.' },
      { name: 'db', description: 'Database tests.', timeout: 60_000 },
      {
        name: 'flaky',
        description: 'Flaky CI tests.',
        retry: process.env.CI ? 3 : 0,
        timeout: 30_000,
        priority: 1,
      },
    ],
  },
})
```

When multiple tags define the same option, resolved by priority (lower = higher priority). Tags without priority are merged first. Test's own options always take highest priority.

### Use Tags

```ts
test('renders homepage', { tags: ['frontend'] }, () => { /* ... */ })

describe('API endpoints', { tags: ['backend'] }, () => {
  test('returns user', () => {}) // inherits 'backend' tag
  test('validates input', { tags: ['validation'] }, () => {})
})
```

File-level tags via JSDoc (applies to ALL tests in the file):

```ts
/**
 * @module-tag acceptance
 * @module-tag admin/pages/dashboard
 */
```

### Filter by Tags

```sh
vitest --tags-filter="unit"
vitest --tags-filter="frontend and fast"
vitest --tags-filter="frontend && !flaky"
vitest --tags-filter="(unit || e2e) && !slow"
vitest --tags-filter="api/*" # wildcard
vitest --tags-filter="db && (postgres || mysql) && !slow"
```

Multiple `--tags-filter` flags combine with AND logic.

Operators: `and`/`&&`, `or`/`||`, `not`/`!`, `*` wildcards, `()` grouping. Standard operator precedence: `not` > `and` > `or`.

Reserved names: `and`, `or`, `not`. Tags cannot contain `(`, `)`, `&`, `|`, `!`, `*`, or spaces.

### TypeScript Tag Enforcement

```ts
import 'vitest'
declare module 'vitest' {
  interface TestTags {
    tags: 'frontend' | 'backend' | 'db' | 'flaky'
  }
}
```

### Runtime Tag Checking

```ts
import { beforeAll, TestRunner } from 'vitest'

beforeAll(async () => {
  if (TestRunner.matchesTags(['db'])) {
    await seedDatabase()
  }
})
```

### List Tags

```sh
vitest --list-tags      # human readable
vitest --list-tags=json # JSON output
```

In Vitest UI, prefix filter with `tag:` to filter by tags.

## Test Annotations (v3.2)

Annotate tests with messages and attachments via `context.annotate`:

```ts
test('hello world', async ({ annotate }) => {
  await annotate('this is my test')
  await annotate('warning message', 'warning')
  await annotate('file attachment', { body: fileContent })
})
```

`annotate` returns a Promise (auto-awaited before test finishes if not explicitly awaited).

### Reporter Support

| Reporter | Behavior |
|----------|----------|
| `default` | Shows annotations only on failure |
| `verbose` | Always shows annotations |
| `html` | Shows inline at source location |
| `junit` | Lists in `<properties>` tag |
| `github-actions` | Prints as notice/warning/error message |
| `tap` | Diagnostic lines starting with `#` |

## Agent Reporter (v4.1)

Minimal output for AI coding agents — only shows failed tests and errors:

```sh
AI_AGENT=copilot vitest  # or any agent name
```

Auto-detected via `std-env` for popular agent environments. If using custom reporters, add `'agent'` manually.

## GitHub Actions Job Summary (v4.1)

The `github-actions` reporter auto-generates a Job Summary with test statistics and flaky test details (with source permalinks). Enabled by default in GitHub Actions.

```ts
// Customize or disable:
export default defineConfig({
  test: {
    reporters: [
      ['github-actions', {
        jobSummary: {
          enabled: false, // or set outputPath
        },
      }],
    ],
  },
})
```

## `--detect-async-leaks` (v4.1)

Reports leaked timers, handles, and unresolved async resources with source locations:

```sh
vitest --detect-async-leaks
```

Or in config:

```ts
export default defineConfig({
  test: { detectAsyncLeaks: true },
})
```

Uses `node:async_hooks` — adds runtime overhead, best for debugging.

## Reporter Changes (v4)

- `basic` reporter removed — use `['default', { summary: false }]`
- `verbose` reporter always prints tests one-by-one (was CI-only behavior)
- New `tree` reporter — always prints tests in tree format
- `default` reporter only shows tree when a single test file runs

Conditional verbose for CI only:

```ts
export default defineConfig({
  test: {
    reporter: process.env.CI ? 'verbose' : 'default',
  },
})
```
