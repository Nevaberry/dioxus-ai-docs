# Browser Automation

## Controlled screencasts and overlays

`page.screencast.start()` can save a WebM through `path`, deliver JPEG frames
through `onFrame`, or do both, with explicit `stop()` control (since 1.59.1).

```ts
await page.screencast.start({
  path: 'video.webm',
  onFrame: ({ data, timestamp }) => consumeFrame(data, timestamp),
  size: { width: 800, height: 600 },
  quality: 90,
});
await page.screencast.stop();
```

`size` supplies aspect-ratio-preserving maximum bounds. By default the
viewport is scaled within 800x800. A screencast already started by tracing or
video recording can override the requested size, and `quality` ranges from 0
through 100. Frame events include the browser presentation `timestamp` (since
1.61.0).

`showActions({ position, duration, fontSize, cursor })` annotates interactions
and returns a disposable; `cursor` controls the pointer decoration. The cursor
option was added in 1.61.0. `showChapter(title, { description, duration })`
adds a timed title card. `showOverlay(html, { duration })` returns a disposable
for arbitrary HTML, and an overlay can be hidden and restored without being
removed. The test `video` option can configure `show.actions` and `show.test`
annotations.

## Bound sessions and the dashboard

`browser.bind(name, { workspaceDir })` makes a launched browser available to
multiple Playwright, `playwright-cli`, or MCP clients (since 1.59.1). Pass its
returned `endpoint` to `chromium.connect()` or the corresponding browser type.

```ts
const { endpoint } = await browser.bind('my-session', {
  workspaceDir: process.cwd(),
  host: 'localhost',
  port: 0,
});
const attached = await chromium.connect(endpoint);
```

Adding `host` and `port` creates a WebSocket endpoint; otherwise the session
uses a named pipe. `browser.unbind()` stops accepting new connections.
`playwright-cli show` opens a dashboard for bound browsers with manual
intervention and DevTools. CLI-launched browsers bind automatically; set
`PLAYWRIGHT_DASHBOARD=1` to expose browsers launched by `@playwright/test`.

## AbortSignal and scroll control

Most operations and web-first assertions accept `signal` (since 1.62.0), so
actions, navigation, waits, and assertions can be cancelled independently of
their timeout. A supplied signal does not disable the default timeout; use
`timeout: 0` when only the signal should bound the operation.

```ts
const controller = new AbortController();
setTimeout(() => controller.abort(), 1_000);
await page.getByRole('button', { name: 'Submit' }).click({
  signal: controller.signal,
});
await expect(page.getByText('Done')).toBeVisible({
  signal: controller.signal,
});
```

Actions accept `scroll: 'auto' | 'none'` (since 1.62.0). Use `'none'` to
prevent Playwright from automatically scrolling the target into view.

## Virtual passkeys and storage state

`browserContext.credentials` provides a cross-browser virtual authenticator
(since 1.61.0). It can seed backend-provisioned passkeys and answer the page's
`navigator.credentials.create()` and `navigator.credentials.get()` ceremonies
without a hardware key.

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

Retrieve an app-created credential with `credentials.get()` and reuse it in a
later test. Storage state accepts `credentials` (since 1.62.0), allowing a
context's virtual WebAuthn credentials to be persisted and used to seed later
contexts.

## Direct and mutable Web Storage

`page.localStorage` and `page.sessionStorage` expose the current origin's
storage directly (since 1.61.0).

```ts
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');
const items = await page.sessionStorage.items();
```

`browserContext.setStorageState()` replaces a live context's state without
recreating it (since 1.59.1). It clears the current cookies, local-storage
origins, and IndexedDB origins before applying the replacement.

## WebP screenshots and snapshots

Page and locator screenshot assertions select WebP when the snapshot name ends
in `.webp` (since 1.62.0). Standalone page and locator screenshots accept
`type: 'webp'`; quality 100 is lossless and is the default, while lower values
enable lossy compression.

```ts
await expect(page).toHaveScreenshot('homepage.webp');
await page.screenshot({ path: 'homepage.webp', quality: 50 });
```

## ARIA snapshots and locator tools

The following APIs were added in 1.59.1:

- `page.ariaSnapshot()` snapshots the whole page, equivalent to
  `page.locator('body').ariaSnapshot()`.
- Locator ARIA snapshots accept `depth` and `mode`.
- `locator.normalize()` converts a locator toward recommended test-id and
  ARIA-role forms.
- `page.pickLocator()` highlights elements interactively and returns the
  selected element's locator; `page.cancelPickLocator()` cancels selection.

## Async-disposable resources

Pages, routes, init scripts, and other returned JavaScript resources support
`await using` (since 1.59.1). Scope exit closes the page or removes the route
or script.

```ts
await using page = await context.newPage();
{
  await using route = await page.route('**/*', route => route.continue());
  await using script = await page.addInitScript('console.log("ready")');
  await page.goto('https://example.com');
}
```

## Evaluation and init-script arguments

`page.evaluate()` and related evaluation methods accept functions as argument
values (since 1.62.0). `page.addInitScript()` and
`browserContext.addInitScript()` likewise accept functions as init-script
arguments.

## Retained page diagnostics

`page.consoleMessages()` and `page.pageErrors()` accept `filter` (since
1.59.1). Reset retained entries with `clearConsoleMessages()` and
`clearPageErrors()`. Retained console messages expose `timestamp()`.

## Debugger, response, protocol, and lifecycle APIs

The following additions date to 1.59.1:

- `browserContext.debugger` exposes programmatic debugger control.
- `browserContext.isClosed()` reports context lifecycle state.
- `request.existingResponse()` returns an already-available response without
  waiting.
- `response.httpVersion()` reports the negotiated HTTP version.
- CDP sessions emit `event` and `close`.

Responses from API requests add `apiResponse.securityDetails()` and
`apiResponse.serverAddr()` (since 1.61.0), matching the TLS and server-address
metadata available on browser responses.

## Artifact placement

`browserType.launch({ artifactsDir })` chooses the launch artifact directory
(since 1.59.1). `browserType.connectOverCDP(endpoint, { artifactsDir })`
controls where traces, downloads, and other artifacts from an attached browser
are stored (since 1.61.0).

```ts
const browser = await chromium.connectOverCDP(endpoint, {
  artifactsDir: 'artifacts',
});
```
