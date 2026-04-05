# Browser, CLI & Tracing

## browser.bind() / unbind() (1.59)

Share a launched browser with playwright-cli, @playwright/mcp, or other clients:
```js
const { endpoint } = await browser.bind('my-session', {
  workspaceDir: '/my/project',
});
// Connect from CLI: playwright-cli attach my-session
// Connect from MCP: @playwright/mcp --endpoint=my-session
// Connect from API: await chromium.connect(endpoint);

// WebSocket binding:
const { endpoint } = await browser.bind('my-session', {
  host: 'localhost', port: 0,
});

await browser.unbind(); // stop accepting connections
```

## Dashboard (1.59)

`playwright-cli show` opens a dashboard listing bound browsers. Set `PLAYWRIGHT_DASHBOARD=1` to see `@playwright/test` browsers.

## CLI Debugging for Agents (1.59)

```bash
npx playwright test --debug=cli
# Then: playwright-cli attach <session-id>
# Commands: step-over, snapshot, etc.
```

## CLI Trace Analysis (1.59)

```bash
npx playwright trace open trace.zip
npx playwright trace actions --grep="expect"
npx playwright trace action 9
npx playwright trace snapshot 9 --name after
```

## connectOverCDP isLocal (1.58)

```js
await chromium.connectOverCDP(url, { isLocal: true }); // enables file system optimizations
```

## Chrome for Testing (1.57)

Playwright now runs Chrome for Testing builds instead of Chromium. Headed uses `chrome`, headless uses `chrome-headless-shell`. No functional changes expected. Arm64 Linux still uses Chromium.

## Service Worker Network Routing (1.57, Chromium only)

Service Worker network requests are now reported and routable via `BrowserContext`. Opt out with `PLAYWRIGHT_DISABLE_SERVICE_WORKER_NETWORK` env var.

## Tracing Enhancements (1.59)

- `tracing.start({ live: true })` — real-time trace updates
- `artifactsDir` option in `browserType.launch()`
- Trace mode `'retain-on-failure-and-retries'` — keeps traces from all retries of flaky tests

## Command-Line Changes (1.54)

- `--user-data-dir` for `codegen`, `open`, etc. to reuse browsing state
- `npx playwright open` no longer opens test recorder (use `codegen`)
- Node.js 16 removed, Node.js 18 deprecated
