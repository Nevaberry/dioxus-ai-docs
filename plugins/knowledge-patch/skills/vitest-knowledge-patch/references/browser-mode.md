# Browser Mode

Relevant versioned source batches: `3.0.0`, `3.2.0`, `4.0-guides`, `4.0.0`, and `4.1.0`.

## Contents

- [Scaffold and choose a provider](#scaffold-and-choose-a-provider)
- [Configure multiple instances](#configure-multiple-instances)
- [Select a configured browser from the CLI](#select-a-configured-browser-from-the-cli)
- [Find the Browser Mode server](#find-the-browser-mode-server)
- [Respect browser runtime requirements](#respect-browser-runtime-requirements)
- [Extend and compose locators](#extend-and-compose-locators)
- [Handle strict actions](#handle-strict-actions)
- [Assert viewport intersection](#assert-viewport-intersection)
- [Debug browser tests](#debug-browser-tests)
- [Spy on module exports under browser ESM](#spy-on-module-exports-under-browser-esm)
- [Record Playwright traces](#record-playwright-traces)
- [Create visual-regression baselines](#create-visual-regression-baselines)
- [Configure screenshot capture and comparison](#configure-screenshot-capture-and-comparison)
- [Place the Browser UI details panel](#place-the-browser-ui-details-panel)

## Scaffold and choose a provider

Scaffold Browser Mode with the initializer when starting from scratch:

```sh
npx vitest init browser
```

It installs the required dependencies and creates browser configuration. A manual setup must define a provider. `@vitest/browser-preview` is a local preview environment that simulates events; use Playwright or WebdriverIO for CI, headless execution, or real browser automation.

Provider configuration changed to provider-specific packages and factory calls. Context imports also moved from `@vitest/browser/context` to `vitest/browser`:

```ts
import { playwright } from '@vitest/browser-playwright'
import { page } from 'vitest/browser'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      provider: playwright({
        launchOptions: { slowMo: 100 },
      }),
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

The provider packages include `@vitest/browser`, so a separate direct dependency on it can be removed. Older configuration passed a provider name such as `provider: 'playwright'`; migrate it to the imported factory.

## Configure multiple instances

Use `test.browser.instances` for multiple browser setups instead of creating workspace projects for them. Each instance selects a browser and may override `launch`, `setupFiles`, `provide`, and other supported browser options:

```ts
export default defineConfig({
  test: {
    browser: {
      provider: playwright(),
      instances: [
        { browser: 'chromium', launch: { devtools: true } },
        { browser: 'firefox', setupFiles: ['./setup.firefox.ts'] },
      ],
    },
  },
})
```

Playwright also supports persistent browser contexts and accepts both `launchOptions` and `connectOptions` in provider configuration.

## Select a configured browser from the CLI

Passing `--browser` without a `browser` option in configuration fails instead of assuming the Node test configuration is browser-compatible. Select a configured instance and headless behavior explicitly:

```sh
npx vitest --browser=chromium --browser.headless
```

This configuration requirement applies since `3.2.0`.

## Find the Browser Mode server

The default Browser Mode port is `63315`; configure it through `browser.api`. Vitest does not automatically print the browser Vite server URL. In watch mode, press `b` to display it.

## Respect browser runtime requirements

Browser Mode inherits Vite's target requirements and requires `BroadcastChannel`, native ESM, dynamic imports, and `import.meta`. The documented minimum browser versions are:

- Chrome 87
- Firefox 78
- Safari 15.4
- Edge 88

## Extend and compose locators

Register project-specific locator methods with `locators.extend`. A method can return a Playwright locator string, which produces a chainable locator scoped to the parent, or declare `this: Locator` and compose locator operations and user actions.

```ts
import { locators, page } from 'vitest/browser'

locators.extend({
  getByCommentsCount: (count: number) =>
    `.comments :text("${count} comments")`,
})

await expect.element(page.getByCommentsCount(1)).toBeVisible()
```

With the Playwright provider, `page.frameLocator` returns a `FrameLocator` for queries and actions inside an iframe:

```ts
const frame = page.frameLocator(page.getByTestId('iframe'))
await frame.getByText('Hello World').click()
```

Browser locators also expose `length`, so they can be passed directly to `toHaveLength`:

```ts
await expect.element(page.getByText('Item')).toHaveLength(3)
```

## Handle strict actions

WebdriverIO and Preview locators are strict by default. An action throws if its locator matches more than one element. Opt an individual action into the previous first-match behavior only when that ambiguity is intentional:

```ts
await page.getByRole('button').click({ strict: false })
```

## Assert viewport intersection

Use `toBeInViewport`, backed by `IntersectionObserver`, to check that a browser element intersects the viewport. The optional `ratio` requires a proportion of the element to be visible:

```ts
await expect.element(page.getByText('Welcome')).toBeInViewport({ ratio: 0.5 })
```

## Debug browser tests

Start Playwright or WebdriverIO browser tests with `vitest --inspect`, then attach through DevTools. Inspect mode automatically disables `browser.trackUnhandledErrors`. The official VS Code extension also provides a Debug Test action for browser tests.

Browser Mode pre-mocks synchronous, thread-blocking dialogs such as `alert` and `confirm`. A native dialog can block communication with the test page and hang the run. Explicitly mock these APIs when their return behavior is part of the test.

## Spy on module exports under browser ESM

Native ESM module namespace objects in the browser are sealed, so `vi.spyOn` cannot patch an imported namespace. Mock the module with `{ spy: true }`; this wraps every export while preserving its implementation, after which `vi.mocked` can configure an exported function:

```ts
import { vi } from 'vitest'
import * as api from './api.js'

vi.mock('./api.js', { spy: true })
vi.mocked(api.method).mockImplementation(() => 'stubbed')
```

This does not make exported variables replaceable. When a test must change a live binding, expose a function from the module that changes it.

## Record Playwright traces

The Playwright provider can record every test or limit recording to retries and failures. `browser.trace` accepts a mode string or an object with a root-relative `tracesDir`:

```ts
import { playwright } from '@vitest/browser-playwright'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      provider: playwright(),
      trace: {
        mode: 'retain-on-failure',
        tracesDir: './playwright-traces',
      },
    },
  },
})
```

Supported selective modes include `on-first-retry` and `on-all-retries`. Use `trace: 'on'` or `--browser.trace=on` to record every test. Without `tracesDir`, archives are written to `__traces__` beside the test file. Trace archives are also exposed to reporters as test annotations.

Browser assertions and interactions are automatically grouped in traces at the test lines that triggered them. Ordinary Node-side assertions are not grouped. Add meaningful trace structure with:

- `page.mark(name)` or `locator.mark(name)` for a named point.
- `page.mark(name, callback)` or the locator equivalent to group a flow.
- `vi.defineHelper(callback)` around reusable helpers so trace entries point to the helper's call site instead of its implementation.

```ts
const signIn = vi.defineHelper(async () => {
  await page.mark('sign in', async () => {
    await page.getByRole('textbox', { name: 'Email' })
      .fill('me@example.com')
    await page.getByRole('button', { name: 'Sign in' }).click()
  })
})
```

## Create visual-regression baselines

`toMatchScreenshot` is an asynchronous assertion for a page or locator:

```ts
await expect(page.getByTestId('hero'))
  .toMatchScreenshot('hero-section')
```

If no reference exists, Vitest creates one under `__screenshots__` beside the test and deliberately fails that run. Review and commit the browser-and-platform-specific baseline. Regenerate intentional changes with `vitest --update`.

Vitest repeatedly captures the target until the image stabilizes or the test times out. Freeze or mask continuously changing content so stabilization can succeed.

## Configure screenshot capture and comparison

Set `browser.expect.toMatchScreenshot` globally or pass the same comparator settings to an assertion. In the `4.0-guides` configuration, screenshot capture options could mask dynamic regions alongside explicit Pixelmatch settings:

```ts
export default defineConfig({
  test: {
    browser: {
      expect: {
        toMatchScreenshot: {
          comparatorName: 'pixelmatch',
          comparatorOptions: {
            threshold: 0.2,
            allowedMismatchedPixelRatio: 0.01,
          },
        },
      },
    },
  },
})

await expect(page.getByTestId('profile')).toMatchScreenshot('profile', {
  screenshotOptions: {
    mask: [page.getByTestId('last-seen')],
  },
})
```

The `4.0-guides` Pixelmatch configuration supports a color `threshold` plus `allowedMismatchedPixelRatio` or `allowedMismatchedPixels`. There is no default mismatch allowance, and the stricter limit applies when both allowance forms are present. With Playwright, screenshot animations are disabled by default.

In `4.1.0`, browser screenshot comparison switched from Pixelmatch to BlazeDiff. This can change visual-diff results after an upgrade, so review explicit comparator configuration and regenerated baselines carefully. Failure screenshots now go through the artifacts API; their attachments can be processed by the HTML reporter.

## Place the Browser UI details panel

Set the details panel below or beside the test view. The Browser UI exposes the same choice through its layout toggle:

```ts
export default defineConfig({
  test: {
    browser: {
      detailsPanelPosition: 'bottom',
    },
  },
})
```

Valid positions are `bottom` and `right`.
