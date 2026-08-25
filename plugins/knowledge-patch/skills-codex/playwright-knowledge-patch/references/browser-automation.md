# Browser Automation

## Screencasts, annotations, and overlays

In `1.59.1`, `page.screencast.start()` can save a WebM with `path`, deliver
JPEG frames through `onFrame`, or do both. Recording continues until an
explicit `page.screencast.stop()`.

```ts
await page.screencast.start({
  path: 'video.webm',
  onFrame: ({ data }) => consumeJpeg(data),
  size: { width: 800, height: 600 },
});
await page.screencast.stop();
```

`size` gives aspect-ratio-preserving maximum bounds. Its default is the
viewport scaled within 800×800. `quality` ranges from 0 through 100. An
existing screencast from tracing or video recording can override the requested
size.

`showActions({ position, duration, fontSize })` annotates interactions and
returns a disposable. `showChapter(title, { description, duration })` adds a
timed title card. `showOverlay(html, { duration })` returns a disposable for
arbitrary HTML; an overlay can be hidden and restored without removing it.
The test `video` option can configure `show.actions` and `show.test`
annotations.

Since `1.61.0`, `screencast.showActions()` also accepts `cursor` to control
the pointer decoration, and every `screencast.start()` `onFrame` event includes
the browser presentation timestamp.

```ts
await page.screencast.start({
  onFrame: ({ data, timestamp }) => consumeFrame(data, timestamp),
});
```

## Shared browser sessions and dashboard

In `1.59.1`, `browser.bind(name, { workspaceDir })` makes a launched browser
available to multiple Playwright, `playwright-cli`, or MCP clients. Its
returned `endpoint` is accepted by `chromium.connect()`.

```ts
const { endpoint } = await browser.bind('my-session', {
  host: 'localhost',
  port: 0,
});
const attached = await chromium.connect(endpoint);
```

Adding `host` and `port` creates a WebSocket endpoint rather than a named pipe.
`browser.unbind()` stops accepting new connections.

`playwright-cli show` opens a dashboard for bound browsers with manual
intervention and DevTools. CLI browsers bind automatically.
`PLAYWRIGHT_DASHBOARD=1` also exposes browsers launched by `@playwright/test`.

## Async-disposable resources

In `1.59.1`, pages, routes, init scripts, and other returned resources support
`await using`. Scope exit closes the page or removes the route or script.

```ts
await using page = await context.newPage();
{
  await using route = await page.route('**/*', route => route.continue());
  await using script = await page.addInitScript('console.log("ready")');
  await page.goto('https://example.com');
}
```

## ARIA snapshots and locator selection

In `1.59.1`, `page.ariaSnapshot()` snapshots the whole page and is equivalent
to `page.locator('body').ariaSnapshot()`. Locator snapshots accept `depth` and
`mode`.

`locator.normalize()` converts a locator toward recommended test-id and
ARIA-role forms. `page.pickLocator()` highlights elements interactively and
returns the clicked element's locator. `page.cancelPickLocator()` cancels the
interactive selection.

## Mutable storage state and retained diagnostics

In `1.59.1`, `browserContext.setStorageState()` clears the context's current
cookies, local storage, and IndexedDB origins and applies replacement state
without recreating the context.

`page.consoleMessages()` and `page.pageErrors()` accept `filter`. Reset their
retained entries with `clearConsoleMessages()` and `clearPageErrors()`.
Console messages expose `timestamp()`.

## Debugger, protocol, tracing, and artifact controls

The following controls are available in `1.59.1`:

- `browserContext.debugger` exposes programmatic debugger control.
- `browserContext.isClosed()` reports the context lifecycle state.
- `request.existingResponse()` returns an already-available response without
  waiting.
- `response.httpVersion()` reports the negotiated HTTP version.
- CDP sessions emit `event` and `close`.
- `tracing.start({ live: true })` enables live trace updates.
- `browserType.launch({ artifactsDir })` selects the artifact directory.

## Cross-browser passkeys

Since `1.61.0`, `browserContext.credentials` provides a virtual authenticator
that can seed backend-provisioned passkeys and answer the page's
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

An app-created credential can be retrieved with `credentials.get()` and
reused in later tests.

In `1.62.0`, the storage-state `credentials` option includes a context's
virtual WebAuthn credentials, allowing passkeys to be persisted and used to
seed later contexts.

## Direct Web Storage access

Since `1.61.0`, `page.localStorage` and `page.sessionStorage` directly expose
the current origin's storage.

```ts
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');
const items = await page.sessionStorage.items();
```

## Response connection metadata

Since `1.61.0`, API-request responses expose
`apiResponse.securityDetails()` and `apiResponse.serverAddr()`. These mirror
the TLS and server-address metadata available on browser responses.

## Artifact placement for attached browsers

Since `1.61.0`, `browserType.connectOverCDP()` accepts `artifactsDir` to
control where traces, downloads, and other artifacts from an attached browser
are stored.

```ts
const browser = await chromium.connectOverCDP(endpoint, {
  artifactsDir: 'artifacts',
});
```

## AbortSignal cancellation

In `1.62.0`, most operations and web-first assertions accept `signal`, so
actions, navigation, waits, and assertions can be cancelled independently of
their timeout. A supplied signal leaves the default timeout active. Pass
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

## WebP screenshots and visual snapshots

In `1.62.0`, page and locator screenshot assertions select WebP when the
snapshot name ends in `.webp`. Standalone page and locator screenshots also
accept `type: 'webp'`. Quality `100` is the lossless default; lower values
enable lossy compression.

```ts
await expect(page).toHaveScreenshot('homepage.webp');
await page.screenshot({ path: 'homepage.webp', quality: 50 });
```

## Per-action scroll control

In `1.62.0`, actions accept `scroll: 'auto' | 'none'`. Use `'none'` to prevent
Playwright from automatically scrolling the target into view.

```ts
await page.getByRole('button', { name: 'Submit' }).click({ scroll: 'none' });
```

## Function-valued arguments

In `1.62.0`, `page.evaluate()` and related evaluation methods accept functions
as argument values. `page.addInitScript()` and
`browserContext.addInitScript()` likewise accept functions as init-script
arguments.
