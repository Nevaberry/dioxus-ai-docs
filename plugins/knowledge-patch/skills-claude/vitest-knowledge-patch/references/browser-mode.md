# Browser Mode

## Scaffold and choose a provider

Run the browser initializer to install dependencies and create configuration:

```sh
npx vitest init browser
```

A manual setup must define a provider. `@vitest/browser-preview` simulates browser events for local preview; it is not a CI or headless provider. Use Playwright or WebdriverIO when real browser automation matters.

Since 4.0.0, providers live in separate packages and are factory functions. Browser context APIs such as `page` moved from `@vitest/browser/context` to `vitest/browser`. Provider packages already include `@vitest/browser`, so a separate direct dependency can be removed.

```ts
import { playwright } from '@vitest/browser-playwright'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      provider: playwright({ launchOptions: { slowMo: 100 } }),
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

## Configure multiple instances

Since 3.0.0, `test.browser.instances` can hold multiple browser setups instead of representing browsers as workspace projects. Each instance selects a browser and can override instance options such as `launch`, `setupFiles`, and `provide`.

```ts
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

The Playwright provider also supports persistent contexts and accepts `launchOptions` together with `connectOptions` (since 4.1.0).

## Start and discover the browser server

Since Vitest 3.2, `--browser` fails unless the config already has a `browser` option. It no longer assumes an arbitrary Node test config is browser-compatible. Select a configured instance explicitly:

```sh
npx vitest --browser=chromium --browser.headless
```

The browser server defaults to port `63315`; change it through `browser.api`. Its Vite server URL is not printed automatically. Press `b` in watch mode to display it.

Browser Mode inherits Vite's target requirements and additionally needs `BroadcastChannel`, native ESM, dynamic import, and `import.meta`. The documented browser floors are Chrome 87, Firefox 78, Safari 15.4, and Edge 88.

## Handle blocking dialogs

Browser Mode pre-mocks synchronous dialogs such as `alert` and `confirm`, because native dialogs block communication with the test page and can hang the run. Explicitly mock their return behavior when it matters to the test.

## Extend and use locators

Custom locators have been supported since 3.2.0. With current imports, call `locators.extend` from `vitest/browser`. A method may return a Playwright locator string, which becomes a parent-scoped chainable locator, or use a `this: Locator` context to compose locator operations and user actions.

```ts
import { locators, page } from 'vitest/browser'

locators.extend({
  getByCommentsCount: (count: number) => `.comments :text("${count} comments")`,
})

await expect.element(page.getByCommentsCount(1)).toBeVisible()
```

With the Playwright provider, `page.frameLocator` queries within an iframe. Locators expose `length`, so they work with `toHaveLength` (since 4.0.0).

```ts
const frame = page.frameLocator(page.getByTestId('iframe'))
await frame.getByText('Hello World').click()
await expect.element(page.getByText('Item')).toHaveLength(3)
```

WebdriverIO and Preview locators became strict by default in 4.1.0. An action throws if its locator matches multiple elements. Opt out for one action only when first-match behavior is intentional:

```ts
await page.getByRole('button').click({ strict: false })
```

## Assert viewport visibility

Since 4.0.0, locator assertions include `toBeInViewport`, backed by `IntersectionObserver`. Supply `ratio` to require a fraction of the element to be visible:

```ts
await expect.element(page.getByText('Welcome')).toBeInViewport({ ratio: 0.5 })
```

## Spy on native ESM exports

Browser module namespace objects are sealed, so `vi.spyOn` cannot patch an imported namespace. Mock with `{ spy: true }` to wrap every export without replacing its implementation, then configure the typed mock:

```ts
import { vi } from 'vitest'
import * as api from './api.js'

vi.mock('./api.js', { spy: true })
vi.mocked(api.method).mockImplementation(() => 'stubbed')
```

Exported variables cannot be mocked this way. Expose a function that changes the module's live binding when a test must alter one.

## Debug browser tests and arrange the UI

Since 4.0.0, Playwright and WebdriverIO tests can start with `vitest --inspect` and attach through DevTools. Inspect mode automatically disables `browser.trackUnhandledErrors`. The official editor extension exposes a Debug Test action for browser tests.

Since 4.1.0, set `browser.detailsPanelPosition` to `bottom` or `right`; the Browser UI offers the same layout toggle.

```ts
export default defineConfig({
  test: { browser: { detailsPanelPosition: 'bottom' } },
})
```

## Capture Playwright traces

The 4.0-guides behavior lets the Playwright provider record every test or retain traces around retries and failures. `browser.trace` accepts a mode or an object with a root-relative `tracesDir`. Trace archives are exposed to reporters as test annotations.

```ts
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

Selective modes are `on-first-retry` and `on-all-retries`. `trace: 'on'` or `--browser.trace=on` records every test. Without `tracesDir`, archives go in `__traces__` beside the test file.

Browser assertions and interactions are grouped in traces at their triggering test lines; ordinary Node-side assertions are not. Add named points with `page.mark()` or `locator.mark()`, group a flow with a callback, and wrap reusable helpers in `vi.defineHelper()` so entries point to the helper call site.

```ts
const signIn = vi.defineHelper(async () => {
  await page.mark('sign in', async () => {
    await page.getByRole('textbox', { name: 'Email' }).fill('me@example.com')
    await page.getByRole('button', { name: 'Sign in' }).click()
  })
})
```

## Maintain visual regression baselines

The 4.0-guides behavior adds asynchronous `toMatchScreenshot` assertions for pages and locators. A missing reference is created under `__screenshots__` beside the test and deliberately fails that run. Review and commit the browser-and-platform-specific baseline; regenerate intentional changes with `vitest --update`.

```ts
await expect(page.getByTestId('hero')).toMatchScreenshot('hero-section')
```

Vitest repeatedly captures until the image stabilizes or the test times out, so control continuously changing content. Assertion-level and `browser.expect.toMatchScreenshot` settings can configure comparison and screenshot capture. Under the original guide, Pixelmatch accepted `threshold`, `allowedMismatchedPixelRatio`, and `allowedMismatchedPixels`; there was no default mismatch allowance, and the stricter limit won if both allowance forms were set. Playwright disables screenshot animations by default and can mask dynamic regions:

```ts
await expect(page.getByTestId('profile')).toMatchScreenshot('profile', {
  screenshotOptions: { mask: [page.getByTestId('last-seen')] },
})
```

Vitest 4.1.0 changed screenshot comparison from Pixelmatch to BlazeDiff, so existing results can differ after upgrading. Failure screenshots now use the artifacts API, allowing the HTML reporter to process artifact attachments.
