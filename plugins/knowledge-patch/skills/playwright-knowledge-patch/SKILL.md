---
name: playwright-knowledge-patch
description: Playwright
license: MIT
version: 1.61.0
metadata:
  author: Nevaberry
---

# Playwright Knowledge Patch

Baseline: Playwright through 1.49. Covered range: 1.59.1 through 1.61.0, plus the current Playwright MCP server and built-in test-agent workflow.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser automation](references/browser-automation.md) | Screencasts and overlays, bound browser sessions, async disposal, passkeys, Web Storage, ARIA and locator tools, diagnostics, protocol metadata, artifact placement |
| [Test runner and debugging](references/test-runner-and-debugging.md) | Removed support, CLI debugging, trace inspection and retention, video modes, soft polling, runner and reporter data, WebSocket recordings, platform support |
| [MCP server](references/mcp-server.md) | Installation, snapshot-driven interaction, profiles, initialization, capability groups, configuration, guardrails, HTTP and embedded deployment |
| [Test agents](references/test-agents.md) | Agent initialization, planner/generator/healer roles, seed tests, plans, generated artifacts, regeneration requirements |

## Breaking removals and platform changes

- WebKit no longer supports macOS 14 (since 1.59.1).
- `@playwright/experimental-ct-svelte` has been removed (since 1.59.1).
- Ubuntu 26.04 is supported (since 1.61.0).
- The MCP Docker image supports headless Chromium only.

## Controlled page screencasts

Use `page.screencast` when a test or tool needs explicit recording control, JPEG frame streaming, or presentation overlays.

```ts
const recording = await page.screencast.start({
  path: 'video.webm',
  onFrame: ({ data, timestamp }) => consumeFrame(data, timestamp),
  size: { width: 800, height: 600 },
  quality: 90,
});

await using actions = await page.screencast.showActions();
await page.screencast.showChapter('Checkout');
await page.screencast.stop();
```

`size` is an aspect-ratio-preserving maximum. Without it, the viewport is scaled within 800×800. A screencast already started by tracing or video can override the requested size. `quality` ranges from 0 to 100. `start()`, `showActions()`, and `showOverlay()` return disposables.

The regular test `video` option can annotate recordings through `show.actions` and `show.test`. See [Browser automation](references/browser-automation.md) for all decoration and overlay controls.

## Shared browser sessions

Expose one launched browser to several Playwright clients, `playwright-cli`, or `@playwright/mcp` with `browser.bind()` (since 1.59.1):

```ts
const { endpoint } = await browser.bind('review-session', {
  workspaceDir: process.cwd(),
  host: 'localhost',
  port: 0,
});
const attached = await chromium.connect(endpoint);
// Later: stop accepting connections.
browser.unbind();
```

Providing `host` and `port` creates a WebSocket endpoint; otherwise the session uses a named pipe. `playwright-cli show` opens the dashboard for bound sessions, DevTools, and manual intervention. CLI-launched browsers bind automatically. Set `PLAYWRIGHT_DASHBOARD=1` to include `@playwright/test` browsers.

## Passkeys without hardware

Each browser context exposes a cross-browser `credentials` virtual authenticator (since 1.61.0). Seed a passkey, install the authenticator, and exercise the application's normal WebAuthn flow:

```ts
await context.credentials.create('example.com', {
  id: credentialId,
  userHandle,
  privateKey,
  publicKey,
});
await context.credentials.install();
await page.goto('https://example.com/login');
```

The authenticator answers `navigator.credentials.create()` and `navigator.credentials.get()` ceremonies. Use `credentials.get()` to retrieve app-registered credentials and reuse them in later tests.

## Direct storage access

Use `page.localStorage` and `page.sessionStorage` for the current origin (since 1.61.0):

```ts
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');
const sessionItems = await page.sessionStorage.items();
```

To replace a whole context's state without recreating it, call `browserContext.setStorageState()` (since 1.59.1). It clears current cookies, local-storage origins, and IndexedDB origins before applying the replacement.

## Async-disposable resources

JavaScript resources such as pages, routes, and init scripts support `await using` cleanup (since 1.59.1):

```ts
await using page = await context.newPage();
{
  await using route = await page.route('**/*', route => route.continue());
  await using script = await page.addInitScript('console.log("ready")');
  await page.goto('https://example.com');
}
```

Scope exit closes the page and removes the route or init script.

## Locator and ARIA utilities

- `page.ariaSnapshot()` snapshots the whole page, equivalent to a body locator snapshot.
- Locator ARIA snapshots accept `depth` and `mode`.
- `locator.normalize()` rewrites a locator toward recommended test-id and ARIA-role forms.
- `page.pickLocator()` lets a person hover and select an element; `page.cancelPickLocator()` cancels selection.

These APIs arrived in 1.59.1.

## CLI debugging and trace inspection

Run a test with a command-controlled debugger, attach to its bound session, and step it:

```bash
npx playwright test --debug=cli
playwright-cli attach
# In the attached session:
step-over
```

Inspect a saved trace without opening the GUI (since 1.59.1):

```bash
npx playwright trace open trace.zip
actions
action <id>
snapshot <id> --name before
snapshot <id> --name after
close
```

Use `tracing.start({ live: true })` for real-time trace updates. For flaky tests, `'retain-on-failure-and-retries'` records every attempt and retains all attempt traces if any attempt fails.

## Video retry policies and soft polls

Video mode adds three retry-aware choices in 1.61.0:

- `'on-all-retries'`
- `'retain-on-first-failure'`
- `'retain-on-failure-and-retries'`

```ts
export default defineConfig({
  use: { video: 'retain-on-failure-and-retries' },
});

await expect.soft.poll(async () => readStatus()).toBe('ready');
```

`expect.soft.poll()` collects a polling failure without immediately stopping the test.

## MCP essentials

`@playwright/mcp` runs on Node.js 18 or newer. It uses structured accessibility snapshots for actions: take a snapshot and pass its element `ref` to an interaction tool. Screenshots are for visual verification, not action targeting.

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--caps=network,storage,testing"]
    }
  }
}
```

The browser is headed by default. Use `--headless` or `--browser=chrome|firefox|webkit|msedge`. The default persistent profile keeps login state and is partitioned by browser channel and MCP workspace. Use `--isolated` for an in-memory session discarded at browser close.

Opt-in capabilities add specialized tools:

| Capability | Adds |
| --- | --- |
| `network` | Offline state, route mocking, route listing and removal |
| `storage` | Cookies, local/session storage, storage-state operations |
| `testing` | Locator generation and visibility/list/text/value assertions |
| `devtools` | Pause/resume, tracing, video, chapter markers |
| `vision` | Coordinate-based mouse operations |
| `pdf` | PDF output |
| `config` | Final merged configuration |

Read [MCP server](references/mcp-server.md) before configuring profiles, remote access, file access, origin rules, secrets, or embedded transport.

## Built-in test agents

Generate the three bundled test-agent definitions with the loop for the consuming client:

```bash
npx playwright init-agents --loop=vscode
```

Regenerate them after every Playwright upgrade so their instructions and MCP tools stay current.

- The planner explores the live application and writes a Markdown plan under `specs/`.
- The generator validates locators and assertions against the app and writes tests under `tests/`.
- The healer runs a failure, repairs locators, waits, or data, and reruns within guardrails. It can skip a test when product behavior is broken.

A seed test supplies application state, project fixtures, and the preferred generated-test style. See [Test agents](references/test-agents.md) for the full artifact flow and audit links.

## Runner and artifact notes

- `fullConfig.argv` captures runner `process.argv`, including custom values after `--`.
- `fullConfig.failOnFlakyTests` exposes the active flaky-test policy to reporters.
- `testInfo.errors` expands an `AggregateError` into separate entries.
- `-G` is shorthand for `--grep-invert`.
- HAR and trace recordings include WebSocket requests.
- `browserType.launch({ artifactsDir })` selects the launch artifact directory.
- `browserType.connectOverCDP(endpoint, { artifactsDir })` places artifacts from an attached browser.

See [Test runner and debugging](references/test-runner-and-debugging.md) and [Browser automation](references/browser-automation.md) for the complete runner, response, diagnostic, and protocol additions.
