# Browser Mode

## Stable Browser Mode (v4)

Browser mode is no longer experimental as of Vitest 4. The provider API changed — install a dedicated package and pass a function instead of a string:

### Provider Packages

| Package | Provider |
|---------|----------|
| `@vitest/browser-playwright` | `playwright()` |
| `@vitest/browser-webdriverio` | `webdriverio()` |
| `@vitest/browser-preview` | `preview()` |

`@vitest/browser` is included automatically in each provider package — remove it from your dependencies.

### Configuration

```ts
import { defineConfig } from 'vitest/config'
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      provider: playwright({
        launchOptions: { slowMo: 100 },
      }),
      enabled: true,
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

### Context Import Change

```ts
// Old (still works until next major)
import { page } from '@vitest/browser/context'

// New (v4+)
import { page, userEvent } from 'vitest/browser'
```

### Component Rendering Packages

- `vitest-browser-vue` — Vue
- `vitest-browser-svelte` — Svelte
- `vitest-browser-react` — React
- `vitest-browser-angular` — Angular

Example:

```tsx
import { render } from 'vitest-browser-react'

test('loads greeting', async () => {
  const screen = render(<Fetch url="/greeting" />)
  await screen.getByText('Load Greeting').click()
  await expect.element(screen.getByRole('heading')).toHaveTextContent('hello there')
})
```

### Spying on Module Exports

Browser ESM is sealed — `vi.spyOn` on imports throws. Use `vi.mock` with `spy: true`:

```ts
import * as module from './module.js'
vi.mock('./module.js', { spy: true })
vi.mocked(module.method).mockImplementation(() => { /* ... */ })
```

## Visual Regression Testing (v4)

Captures and compares screenshots against baseline images.

### Basic Usage

```ts
import { page } from 'vitest/browser'

test('hero looks correct', async () => {
  await expect(page.getByTestId('hero')).toMatchScreenshot('hero-section')
  // Full page:
  await expect(page).toMatchScreenshot()
})
```

### How It Works

1. First run creates a reference screenshot and fails — review it, then re-run
2. Screenshots stored in `__screenshots__/` next to tests, named `{name}-{browser}-{platform}.png`
3. Vitest auto-detects stability (retakes until page settles or timeout)
4. Update baselines with `vitest --update`

### Configuration

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
```

Per-test overrides:

```ts
await expect(element).toMatchScreenshot('button-hover', {
  comparatorOptions: { allowedMismatchedPixelRatio: 0.1 },
})
```

### Best Practices

- Test specific elements, not full pages, to reduce false positives
- Mask dynamic content (Playwright): `screenshotOptions: { mask: [page.getByTestId('timestamp')] }`
- Disable animations or use Playwright provider (auto-disables animations)
- Set explicit viewport: `await page.viewport(1280, 720)` or in instance config
- Use Git LFS for large screenshot suites
- Run in consistent environments (Docker, CI) — screenshots differ across OS/GPU

### `toBeInViewport` Matcher (v4)

```ts
await expect.element(page.getByText('Welcome')).toBeInViewport()
await expect.element(page.getByText('To')).toBeInViewport({ ratio: 0.5 })
```

## Playwright Traces (v4)

Generate Playwright trace files for browser tests.

### Enable

```ts
export default defineConfig({
  test: {
    browser: {
      provider: playwright(),
      trace: 'on', // or 'on-first-retry', 'on-all-retries', 'retain-on-failure'
    },
  },
})
```

CLI: `vitest --browser.trace=on`

Traces saved in `__traces__/` next to tests. Named: `{project}-{test}-{repeat}-{retry}.trace.zip`.

Custom output directory:

```ts
trace: { mode: 'on', tracesDir: './playwright-traces' }
```

### Trace Markers (v4.1)

```ts
import { page } from 'vitest/browser'

await page.mark('before sign in')
await page.getByRole('button', { name: 'Sign in' }).click()

// Group operations under one marker:
await page.mark('sign in flow', async () => {
  await page.getByRole('textbox', { name: 'Email' }).fill('john@example.com')
  await page.getByRole('button', { name: 'Sign in' }).click()
})
```

Both `page.mark()` and `locator.mark()` are available. Automatic grouping for `expect.element`, `click`, `fill`, etc.

### View Traces

```sh
npx playwright show-trace "path-to-trace-file"
```

Or upload at https://trace.playwright.dev

## Locator Improvements (v4)

### Frame Locator (Playwright only)

```ts
const frame = page.frameLocator(page.getByTestId('iframe'))
await frame.getByText('Hello World').click()
```

### `locator.length`

```ts
await expect.element(page.getByText('Item')).toHaveLength(3)
```

### Strict Mode (v4.1)

`webdriverio` and `preview` providers now default to strict mode (matching Playwright). Multiple matches throw instead of picking the first:

```ts
await button.click() // throws if multiple buttons match
await button.click({ strict: false }) // opt out
```

## Custom Locators (v3.2)

Extend the locator API with custom methods:

```ts
import { locators } from '@vitest/browser/context'
import type { Locator } from '@vitest/browser/context'

locators.extend({
  getByCommentsCount(count: number) {
    return `.comments :text("${count} comments")`
  },
  // With context access:
  getByBoth(this: Locator, count: number) {
    return this.getByRole('comment').and(this.getByText(`${count} comments`))
  },
  // Custom actions:
  async clickAndFill(this: Locator, text: string) {
    await this.click()
    await this.fill(text)
  },
})

await page.getByCommentsCount(1).getByText('comments') // chainable
await page.getByRole('textbox').clickAndFill('Hello World')
```

## Debugging (v4)

- VS Code extension supports "Debug Test" button for browser tests
- `--inspect` flag available with Playwright/WebdriverIO for manual DevTools connection
- `trackUnhandledErrors` option auto-disabled during debug

## Configure UI Panel Position (v4.1)

```ts
browser: {
  detailsPanelPosition: 'bottom', // or 'right'
}
```
