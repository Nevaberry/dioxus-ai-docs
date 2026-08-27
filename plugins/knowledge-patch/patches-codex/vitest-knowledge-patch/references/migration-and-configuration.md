# Migration and Configuration

## Replace workspace configuration with projects

Vitest 3.0.0 allowed projects to be declared inline through `test.workspace`, removing the need for a separate workspace file. Vitest 3.2.0 then deprecated both the separate `vitest.workspace` file and `test.workspace`. Move the declaration to root-level `test.projects`:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: ['packages/*'],
  },
})
```

Do this before the old forms are removed. Project resolution and inheritance have additional rules; see [Projects and coverage](projects-and-coverage.md).

## Browser migration checklist

The current Browser Mode configuration differs from the early 3.0.0 form:

- Import a provider factory from its provider-specific package and call it instead of assigning a provider string.
- Import `page`, `locators`, and other browser context APIs from `vitest/browser`, not `@vitest/browser/context`.
- Configure instances under `test.browser.instances`; each can override `launch`, `setupFiles`, and `provide`.
- Define `test.browser` before passing `--browser`; since 3.2.0 the flag does not assume a Node configuration is browser-compatible.
- Review screenshot baselines after moving to 4.1.0 because the comparison implementation changed.

## Reporter and assertion compatibility

When moving to 4.0.0:

- Replace the removed `basic` reporter with `['default', { summary: false }]`.
- Review custom reporters based on `onTaskUpdate`; the public lifecycle was redesigned in 3.0.0.

When moving to 4.1.0:

- Replace old `toBe*` spy assertions with corresponding `toHaveBeen*` forms or `toThrowError`.
- Remove use of the undocumented `Suite` argument from suite hooks. File and worker fixture contexts are available to `beforeAll`, `afterAll`, and `aroundAll` instead.
- Expect WebdriverIO and Preview actions to throw on multi-match locators unless a specific action opts out with `strict: false`.

## Run a test at a source line

Since 3.0.0, append a line number to a test-file path to run the test at that location. Both relative forms are valid:

```sh
vitest basic/foo.js:10
vitest ./basic/foo.js:10
```

## Watch non-imported dependencies

Use `test.watchTriggerPatterns` for templates, subprocess inputs, or other dependencies that Vitest cannot find through static or dynamic imports (3.2.0).

```ts
export default defineConfig({
  test: {
    watchTriggerPatterns: [{
      pattern: /^src\/templates\/(.*)\.html$/,
      testsToRun: (_file, match) => `api/tests/mailers/${match[1]}.test.ts`,
    }],
  },
})
```

## Vite compatibility

Vitest 4.1.0 supports Vite 8. When possible, it reuses the project's installed `vite` rather than obtaining a separate copy, which avoids configuration type mismatches between Vite versions.

## Lifecycle concurrency fix

Vitest 4.1.11 again enforces the global concurrency limit while running test lifecycles. Workloads affected by the regression should no longer exceed their configured global cap.

## Redirect mock filesystem boundary

In 4.1.11, redirect-based mocks respect the filesystem allowlist. A redirect target outside the permitted paths is rejected; place intentional redirect targets inside the allowed filesystem scope rather than widening access accidentally.
