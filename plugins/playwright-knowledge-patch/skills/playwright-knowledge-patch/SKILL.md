---
name: playwright-knowledge-patch
description: "Playwright 1.50-1.59 changes since training cutoff — Screencast API, browser.bind(), test agents, ARIA snapshot improvements, async disposables, storage state enhancements. Load before working with Playwright."
version: "1.59"
license: MIT
metadata:
  author: Nevaberry
---

# Playwright Knowledge Patch

Covers Playwright 1.50–1.59 (Jan 2025 – Mar 2026). Claude knows Playwright through 1.49 (page/locator/frame API, codegen, trace viewer, test runner, fixtures, projects, sharding, Clock API, TLS client certificates, `--only-changed`, ARIA snapshots). It is **unaware** of the Screencast API, browser binding, test agents, and any of the changes below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Test runner & config | [references/test-runner.md](references/test-runner.md) | test.step timeout/skip, TestStepInfo, failOnFlakyTests, per-project workers, testConfig.tag, captureGitInfo, webServer.wait, test agents |
| Assertions & locators | [references/assertions-locators.md](references/assertions-locators.md) | toHaveAccessibleErrorMessage, toContainClass, toHaveURL predicate, locator.filter({visible}), locator.describe/normalize, ARIA /children /url |
| Page & context APIs | [references/page-context-apis.md](references/page-context-apis.md) | Screencast API, storageState with indexedDB, setStorageState, cookie partitionKey, consoleMessages/pageErrors/requests, async disposables |
| Browser, CLI & tracing | [references/browser-cli.md](references/browser-cli.md) | browser.bind/unbind, dashboard, CLI debug/trace, connectOverCDP isLocal, Chrome for Testing, live tracing |
| Breaking changes | [references/breaking-changes.md](references/breaking-changes.md) | Removed selectors, narrowed assertions, glob pattern changes, dropped platforms |

---

## Version Timeline

| Version | Date | Highlights |
|---|---|---|
| 1.50 | 2025-01 | test.step timeout/skip, toHaveAccessibleErrorMessage, ARIA YAML files |
| 1.51 | 2025-03 | storageState indexedDB, locator.filter({visible}), TestStepInfo, toHaveURL predicate |
| 1.52 | 2025-04 | toContainClass, ARIA /children /url, per-project workers, failOnFlakyTests |
| 1.53 | 2025-05 | locator.describe() |
| 1.54 | 2025-07 | Cookie partitionKey, --user-data-dir for CLI |
| 1.55 | 2025-08 | Chromium extension MV2 dropped |
| 1.56 | 2025-10 | Test agents (planner/generator/healer), consoleMessages/pageErrors/requests |
| 1.57 | 2025-12 | webServer.wait, Chrome for Testing, testConfig.tag, service worker routing |
| 1.58 | 2026-01 | Removed legacy selectors (_react, _vue, :light), connectOverCDP isLocal |
| 1.59 | 2026-03 | Screencast API, browser.bind/unbind, dashboard, async disposables, locator.normalize |

---

## Screencast API (1.59)

```js
await page.screencast.start({ path: 'video.webm' });
await page.screencast.showActions({ position: 'top-right' });
await page.screencast.showChapter('Checkout flow', {
  description: 'Testing coupon application',
  duration: 1000,
});
await page.screencast.showOverlay('<div style="color: red">Recording</div>');
await page.screencast.stop();

// Real-time frame streaming
await page.screencast.start({
  onFrame: ({ data }) => sendToVisionModel(data),
  size: { width: 800, height: 600 },
});
```

Video config in `playwright.config.ts`:
```js
use: {
  video: {
    mode: 'on',
    show: {
      actions: { position: 'top-left' },
      test: { position: 'top-right' },
    },
  },
}
```

---

## Browser Binding (1.59)

Share a launched browser with CLI, MCP, or other clients:
```js
const { endpoint } = await browser.bind('my-session', {
  workspaceDir: '/my/project',
});
// CLI: playwright-cli attach my-session
// MCP: @playwright/mcp --endpoint=my-session
// API: await chromium.connect(endpoint);

// WebSocket binding:
const { endpoint } = await browser.bind('my-session', {
  host: 'localhost', port: 0,
});
await browser.unbind(); // stop accepting connections
```

`playwright-cli show` opens a dashboard listing bound browsers. Set `PLAYWRIGHT_DASHBOARD=1` to see `@playwright/test` browsers.

---

## Test Agents (1.56)

Three agent definitions for LLM-driven test creation:
- **planner** — explores app, produces Markdown test plan
- **generator** — transforms plan into Playwright Test files
- **healer** — runs tests, automatically repairs failures

```bash
npx playwright init-agents --loop=claude    # or --loop=vscode, --loop=opencode
```

Regenerate agents after each Playwright upgrade.

---

## Async Disposables (1.59)

Automatic cleanup for pages, routes, and init scripts:
```js
await using page = await context.newPage();
{
  await using route = await page.route('**/*', r => r.continue());
  await using script = await page.addInitScript('console.log("hi")');
  await page.goto('https://example.com');
}
// route and script automatically removed here
```

---

## Key Assertion & Locator Additions

| API | Version | Example |
|---|---|---|
| `toHaveAccessibleErrorMessage` | 1.50 | `expect(locator).toHaveAccessibleErrorMessage('Required')` |
| `toContainClass` | 1.52 | `expect(locator).toContainClass('done')` |
| `toHaveURL` predicate | 1.51 | `expect(page).toHaveURL(url => url.searchParams.has('token'))` |
| `locator.filter({ visible })` | 1.51 | `page.getByTestId('item').filter({ visible: true })` |
| `locator.describe()` | 1.53 | `page.getByTestId('btn').describe('Subscribe button')` |
| `locator.normalize()` | 1.59 | Converts locator to best-practice form |

---

## Storage State Enhancements

```js
// Save with IndexedDB (1.51) — useful for Firebase Auth tokens
await page.context().storageState({ path: authFile, indexedDB: true });

// Replace storage state without new context (1.59)
await context.setStorageState({ path: 'new-state.json' });

// Cookie partitionKey for CHIPS (1.54)
// browserContext.cookies() and addCookies() support partitionKey
```

---

## Critical Breaking Changes

| Version | Change |
|---|---|
| 1.50 | `toBeEditable()` throws on non-editable element types |
| 1.50 | `page.route()` globs no longer support `?` and `[]` — use regex |
| 1.52 | `route.continue()` ignores `Cookie` header — use `addCookies()` |
| 1.55 | Chromium extension manifest v2 dropped |
| 1.57 | `page.accessibility` removed — use Axe |
| 1.58 | `_react`, `_vue`, `:light` selectors removed |
| 1.58 | `devtools` launch option removed — use `args: ['--auto-open-devtools-for-tabs']` |
