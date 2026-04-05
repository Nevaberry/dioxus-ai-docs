# Projects Configuration

## Workspace to Projects Migration

The `workspace` configuration (and separate `vitest.workspace.js` files) was deprecated in v3.2 and removed in v4. The replacement is `projects` in the root config.

### Before (workspace)

```ts
// vitest.workspace.js
import { defineWorkspace } from 'vitest/config'

export default defineWorkspace([
  './packages/*',
  { test: { name: 'unit' } },
])
```

### After (projects)

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      './packages/*',
      { test: { name: 'unit' } },
    ],
  },
})
```

Key differences:
- Cannot specify a separate file as project source — everything is inline or glob
- No `defineWorkspace` — use `defineConfig` with `test.projects`
- `workspace` name clashed with PNPM monorepo concepts; `projects` is clearer

## Inline Workspace (v3.0)

Vitest 3.0 added inline workspace definitions. No separate file needed:

```ts
export default defineConfig({
  test: {
    workspace: ['packages/*'], // v3.0-3.1
    // projects: ['packages/*'], // v3.2+
  },
})
```

## Project Configuration

Use `defineProject` (not `defineConfig`) in per-project config files for type safety:

```ts
// packages/a/vitest.config.ts
import { defineProject } from 'vitest/config'

export default defineProject({
  test: {
    environment: 'jsdom',
  },
})
```

Unsupported project-level options (must be in root config):
- `coverage` — done for the whole process
- `reporters` — only root-level reporters supported
- `resolveSnapshotPath` — only root-level resolver

### `extends: true`

Inline projects inherit nothing by default. Use `extends: true` to inherit root config:

```ts
export default defineConfig({
  plugins: [react()],
  test: {
    pool: 'threads',
    projects: [
      {
        extends: true, // inherits plugins and pool
        test: { name: 'unit', include: ['**/*.unit.test.ts'] },
      },
      {
        extends: false, // default — inherits nothing
        test: { name: 'integration', include: ['**/*.integration.test.ts'] },
      },
    ],
  },
})
```

### Custom Project Name Colors (v3.2)

```ts
test: {
  name: { label: 'browser', color: 'green' },
}
```

## `sequence.groupOrder` (v3.2)

Control execution order of projects. Projects with the same group number run together; groups run from lowest to highest:

```ts
export default defineConfig({
  test: {
    projects: [
      { test: { name: 'slow', sequence: { groupOrder: 0 } } },
      { test: { name: 'fast', sequence: { groupOrder: 0 } } },
      { test: { name: 'flaky', sequence: { groupOrder: 1 } } },
    ],
  },
})
// slow + fast run together, then flaky runs alone
```

Without `groupOrder`, all projects run in parallel.

## `watchTriggerPatterns` (v3.2)

Configure which tests to rerun when non-imported files change:

```ts
export default defineConfig({
  test: {
    watchTriggerPatterns: [
      {
        pattern: /^src\/templates\/(.*)\.(ts|html|txt)$/,
        testsToRun: (file, match) => {
          return `api/tests/mailers/${match[2]}.test.ts`
        },
      },
    ],
  },
})
```

Vitest's static analysis only respects `import` statements. Use this for files read via `fs`, spawned processes, or other non-import dependencies.

## Multi-Browser Configuration (v3.0)

Define multiple browser instances without workspace overhead:

```ts
export default defineConfig({
  test: {
    browser: {
      provider: 'playwright', // v3.x string syntax
      instances: [
        { browser: 'chromium', launch: { devtools: true } },
        {
          browser: 'firefox',
          setupFiles: ['./setup.firefox.ts'],
          provide: { secret: 'my-secret' },
        },
      ],
    },
  },
})
```

Advantage over workspace: single Vite server, files processed once regardless of browser count.

## Filtering by Location (v3.0)

Run tests by line number:

```sh
vitest basic/foo.js:10
vitest ./basic/foo.js:10
```
