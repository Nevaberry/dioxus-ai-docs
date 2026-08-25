# Browser Mode

## Providers, configuration, and instances

Browser instances moved into `test.browser.instances` in 3.0.0. Each instance selects a browser and can override options such as `launch`, `setupFiles`, and `provide`; do not model each browser as a project.

Provider configuration changed again in 4.0.0: install a provider-specific package, import its factory, call it, and import runtime context APIs from `vitest/browser` rather than `@vitest/browser/context`. The provider packages include `@vitest/browser`, so it need not remain a direct dependency solely for that purpose.

```ts
import { defineConfig } from 'vitest/config'
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      provider: playwright({ launchOptions: { slowMo: 100 } }),
      instances: [
        { browser: 'chromium' },
        { browser: 'firefox', setupFiles: ['./setup.firefox.ts'] },
      ],
    },
  },
})
```

`vitest init browser` installs the required dependencies and creates a browser configuration. A manual setup must define a provider. `@vitest/browser-preview` simulates local events; use Playwright or WebdriverIO for CI and headless automation.

Since 3.2.0, `--browser` fails when the config has no browser option. Select an existing instance explicitly:

```sh
npx vitest --browser=chromium --browser.headless
```

## Browser server and runtime

The browser server defaults to port `63315`; configure it through `browser.api`. The CLI does not print its Vite server URL automatically, so press `b` in watch mode to display it.

Browser Mode inherits Vite's target requirements and also requires `BroadcastChannel`, native ESM, dynamic import, and `import.meta`. The documented browser minimums are Chrome 87, Firefox 78, Safari 15.4, and Edge 88.

Synchronous dialogs such as `alert` and `confirm` are pre-mocked because native dialogs block communication with the test page and can hang a run. Mock them explicitly when a test depends on their return value.

## Locators and actions

Custom locators arrived in 3.2.0. Extend the vocabulary with `locators.extend`; a method can return a Playwright locator string that becomes chainable and parent-scoped, or use `this: Locator` to compose locator operations and actions. Use the current `vitest/browser` import path.

```ts
import { locators, page } from 'vitest/browser'

locators.extend({
  getByCommentsCount: (count: number) => `.comments :text("${count} comments")`,
})

await expect.element(page.getByCommentsCount(1)).toBeVisible()
```

With the Playwright provider, `page.frameLocator` returns a `FrameLocator` for querying inside an iframe. Locators expose `length` and work directly with `toHaveLength` (4.0.0).

```ts
const frame = page.frameLocator(page.getByTestId('iframe'))
await frame.getByText('Hello World').click()
await expect.element(page.getByText('Item')).toHaveLength(3)
```

`toBeInViewport` uses `IntersectionObserver`; pass `ratio` to require a proportion of the element to be visible (4.0.0).

```ts
await expect.element(page.getByText('Welcome')).toBeInViewport({ ratio: 0.5 })
```

WebdriverIO and Preview actions became strict in 4.1.0. An action throws when its locator matches multiple elements; opt into prior first-match behavior per action only when it is intentional:

```ts
await page.getByRole('button').click({ strict: false })
```

## Spying on native ESM exports

Browser module namespace objects are sealed, so `vi.spyOn` cannot patch an imported namespace. Mock the module with `{ spy: true }` to wrap each export without replacing its implementation, then configure the typed function.

```ts
import { vi } from 'vitest'
import * as api from './api.js'

vi.mock('./api.js', { spy: true })
vi.mocked(api.method).mockImplementation(() => 'stubbed')
```

Exported variables cannot be mocked this way. Expose a function that changes the live binding when a test must alter one.

## Debugging and UI

Playwright and WebdriverIO browser tests can start with `vitest --inspect` and attach through DevTools. Inspection automatically disables `browser.trackUnhandledErrors`. The official editor extension also provides a Debug Test action for browser tests (4.0.0).

Set the Browser UI details panel to the bottom or right, or use the UI layout toggle (4.1.0):

```ts
export default defineConfig({
  test: { browser: { detailsPanelPosition: 'bottom' } },
})
```

The Playwright provider also accepts `launchOptions` together with `connectOptions` and supports persistent contexts (4.1.0).

## Playwright traces

The 4.0-guides trace workflow records every test or retains trace data only around retries and failures. `browser.trace` accepts a mode directly or an object with a root-relative `tracesDir`; trace archives are exposed to reporters as annotations.

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

Selective modes are `on-first-retry` and `on-all-retries`. `trace: 'on'` or `--browser.trace=on` records every test. Without `tracesDir`, archives go to `__traces__` beside the test file.

Browser assertions and interactions are grouped at their triggering test lines in traces; ordinary Node-side assertions are not. Add named points with `page.mark()` or `locator.mark()`, group a flow with a callback, and wrap reusable helpers in `vi.defineHelper()` so trace entries point at each helper call site.

```ts
const signIn = vi.defineHelper(async () => {
  await page.mark('sign in', async () => {
    await page.getByRole('textbox', { name: 'Email' }).fill('me@example.com')
    await page.getByRole('button', { name: 'Sign in' }).click()
  })
})
```

## Screenshot baselines

The 4.0-guides visual-regression workflow uses asynchronous `toMatchScreenshot` assertions on pages or locators. A missing reference is created under `__screenshots__` beside the test and the run deliberately fails. Review and commit the browser-and-platform-specific baseline, then regenerate deliberate changes with `vitest --update`.

```ts
await expect(page.getByTestId('hero')).toMatchScreenshot('hero-section', {
  screenshotOptions: { mask: [page.getByTestId('last-seen')] },
})
```

Vitest captures repeatedly until the image stabilizes or the test times out, so control continuously changing content. The Playwright provider disables screenshot animations by default and can mask dynamic regions.

In the 4.0-guides comparator configuration, Pixelmatch accepted a color `threshold` and either `allowedMismatchedPixelRatio` or `allowedMismatchedPixels`; there was no default mismatch allowance, and the stricter limit applied when both were set. Put these settings globally under `browser.expect.toMatchScreenshot` or pass the same comparator settings to an individual assertion.

```ts
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
}
```

Vitest 4.1.0 changed screenshot comparison from Pixelmatch to BlazeDiff, so existing visual results can change after upgrading. Failure screenshots now go through the artifacts API, allowing the HTML reporter to process their attachments.
