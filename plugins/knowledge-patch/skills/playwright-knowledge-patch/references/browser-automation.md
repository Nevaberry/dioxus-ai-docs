# Browser Automation

## Page screencasts and presentation overlays

`page.screencast` provides explicit start/stop control for WebM recording and can stream JPEG frames through `onFrame` at the same time (since 1.59.1).

```ts
await page.screencast.start({
  path: 'video.webm',
  onFrame: ({ data }) => consumeJpeg(data),
  size: { width: 800, height: 600 },
  quality: 90,
});
await page.screencast.stop();
```

The options behave as follows:

- `path` writes a WebM when recording stops.
- `onFrame` receives JPEG data. Since 1.61.0, each frame also includes its browser presentation `timestamp`.
- `size` is an aspect-ratio-preserving maximum, not a forced output shape. Its default scales the viewport within 800×800.
- `quality` ranges from 0 to 100.
- A screencast already started for tracing or video can override the requested size.

Decorate the recording with:

- `showActions({ position, duration, fontSize, cursor })` for action decorations; `cursor` was added in 1.61.0.
- `showChapter(title, { description, duration })` for timed title cards.
- `showOverlay(html, { duration })` for arbitrary HTML.
- `hideOverlays()` and `showOverlays()` to temporarily toggle overlays.
- `hideActions()` to remove action decorations.

`start()`, `showActions()`, and `showOverlay()` return disposables. The test runner's `video` option can also set `show.actions` and `show.test` annotation settings.

## Bound browsers and dashboard

`browser.bind(name, { workspaceDir })` exposes one launched browser to multiple Playwright clients, `playwright-cli`, or `@playwright/mcp` (since 1.59.1). The result contains an `endpoint` suitable for the normal connect API.

```ts
const { endpoint } = await browser.bind('my-session', {
  workspaceDir: process.cwd(),
  host: 'localhost',
  port: 0,
});
const attached = await chromium.connect(endpoint);
```

Supplying `host` and `port` exposes a WebSocket endpoint rather than a named pipe. Call `browser.unbind()` to prevent new connections. `playwright-cli show` opens a dashboard for bound browsers, manual intervention, and DevTools. CLI browsers bind automatically; set `PLAYWRIGHT_DASHBOARD=1` to include browsers launched by `@playwright/test`.

## Async disposal

Pages, routes, and init scripts support JavaScript async disposal (since 1.59.1):

```ts
await using page = await context.newPage();
{
  await using route = await page.route('**/*', route => route.continue());
  await using script = await page.addInitScript('console.log("ready")');
  await page.goto('https://example.com');
}
```

Leaving scope closes the page and removes the route or script.

## Virtual passkeys

Every browser context exposes a cross-browser `credentials` virtual authenticator (since 1.61.0). It can seed passkeys and answer the page's `navigator.credentials.create()` and `navigator.credentials.get()` ceremonies without physical hardware.

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

Credentials registered by the application can be fetched with `credentials.get()` and reused in later tests.

## Web Storage and context state

`page.localStorage` and `page.sessionStorage` expose `WebStorage` for the current page origin (since 1.61.0):

```ts
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');
const items = await page.sessionStorage.items();
```

`browserContext.setStorageState()` replaces state in an existing context (since 1.59.1). It first clears all cookies and all local-storage and IndexedDB origins, then applies the supplied replacement state. Recreating the context is not required.

## ARIA snapshots and locator tools

The following interactive and accessibility tools were added in 1.59.1:

- `page.ariaSnapshot()` snapshots the whole page in the same way as `page.locator('body').ariaSnapshot()`.
- Locator snapshots accept `depth` and `mode`.
- `locator.normalize()` rewrites a locator toward recommended test-id and ARIA-role forms.
- `page.pickLocator()` enters interactive selection: a person hovers and clicks an element, and the call returns its locator.
- `page.cancelPickLocator()` cancels active selection.

## Retained diagnostics

`page.consoleMessages()` and `page.pageErrors()` accept `filter` (since 1.59.1). Clear their retained entries with `clearConsoleMessages()` and `clearPageErrors()`. Console-message entries expose `timestamp()`.

## Browser and protocol inspection

The 1.59.1 APIs add several lower-level inspection hooks:

- `browserContext.debugger` provides programmatic debugger control.
- `browserContext.isClosed()` reports context lifecycle state.
- `request.existingResponse()` returns an already available response without waiting.
- `response.httpVersion()` reports the HTTP protocol version.
- CDP sessions emit generic `event` and `close` events.
- `tracing.start({ live: true })` enables real-time trace updates.
- `browserType.launch({ artifactsDir })` controls where launch artifacts are written.

API-request responses gained browser-response metadata in 1.61.0:

- `apiResponse.securityDetails()` returns connection security details.
- `apiResponse.serverAddr()` returns the responding server address.

Use `browserType.connectOverCDP(endpoint, { artifactsDir })` to choose where traces, downloads, and other artifacts from an attached browser are stored (since 1.61.0).
