---
name: playwright-knowledge-patch
description: Playwright
version: "1.61.0"
license: MIT
metadata:
  author: Nevaberry
---


# Playwright Knowledge Patch

Use this skill when implementing or reviewing Playwright browser automation,
component tests, runner configuration, debugging, MCP automation, or built-in
test-agent workflows that depend on the APIs and behavior described here.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser Automation](references/browser-automation.md) | Screencasts, overlays, browser sharing, storage, passkeys, locators, cancellation, screenshots, protocol data, and artifacts |
| [Playwright MCP Server](references/mcp-server.md) | Server startup, profiles, capabilities, configuration, guardrails, HTTP use, and package entry points |
| [Built-in Test Agents](references/test-agents.md) | Planner, generator, healer, loop initialization, seed tests, and generated artifacts |
| [Test Runner and Debugging](references/test-runner-and-debugging.md) | Debug attachment, trace inspection and retention, video, runner data, reporters, retries, component stories, and platform support |

Read only the reference that matches the task. The quick reference below keeps
breaking changes and commonly used additions close at hand.

## Removed support

- WebKit no longer supports macOS 14.
- The JavaScript package `@playwright/experimental-ct-svelte` has been removed.

## Cancellation and action scrolling

Most operations and web-first assertions accept an `AbortSignal` through
`signal`. Supplying a signal does not disable the default timeout; set
`timeout: 0` when the signal alone should bound the operation.

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

Actions also accept `scroll: 'auto' | 'none'`. Pass `'none'` to prevent
automatic scrolling of the target into view.

```ts
await page.getByRole('button', { name: 'Submit' }).click({ scroll: 'none' });
```

## Component stories

Component testing uses stories as concrete scenarios and a served gallery to
render them on demand. `mount` opens a story by id and returns a locator scoped
to the story root. That locator supports `update(props)` and `unmount()`. A
story type can be supplied as a type argument to check props.

```ts
test('click should expand', async ({ mount }) => {
  const component = await mount('components/Expandable/Stateful');
  await component.getByRole('button').click();
  await expect(component.getByTestId('expanded')).toHaveValue('true');
});
```

## Passkeys and storage

`browserContext.credentials` is a virtual authenticator. It can seed
backend-provisioned passkeys and answer the page's
`navigator.credentials.create()` and `navigator.credentials.get()`
ceremonies without a hardware key. Retrieve an app-created credential with
`credentials.get()` to reuse it in a later test.

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

The storage-state `credentials` option persists a context's virtual WebAuthn
credentials so they can seed later contexts. For direct access to the current
origin, use `page.localStorage` and `page.sessionStorage`.

```ts
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');
const items = await page.sessionStorage.items();
```

`browserContext.setStorageState()` first clears the current cookies, local
storage, and IndexedDB origins, then applies replacement state without
recreating the context.

## WebP screenshots

Page and locator screenshot assertions select WebP when the snapshot name ends
in `.webp`. Standalone page and locator screenshots accept `type: 'webp'`.
Quality `100` is the lossless default; lower values enable lossy compression.

```ts
await expect(page).toHaveScreenshot('homepage.webp');
await page.screenshot({ path: 'homepage.webp', quality: 50 });
```

## Recording and retry artifacts

Trace mode `'retain-on-failure-and-retries'` records every attempt and retains
all traces when an attempt fails. This makes passing and failing attempts of a
flaky test available for comparison.

```ts
export default defineConfig({
  use: { trace: 'retain-on-failure-and-retries' },
});
```

The `video` option accepts `'on-all-retries'`,
`'retain-on-first-failure'`, and `'retain-on-failure-and-retries'`.

```ts
export default defineConfig({
  use: { video: 'retain-on-failure-and-retries' },
});
```

## CLI debugging and trace inspection

Run `npx playwright test --debug=cli` to pause a test for attachment with
`playwright-cli attach`. Attached session commands such as `step-over` can
then control the test.

Inspect a trace without the GUI by running
`npx playwright trace open <trace.zip>`, followed by `actions`, `action <id>`,
`snapshot <id> --name before|after`, and `close`.

## MCP automation essentials

The Playwright MCP server drives the browser through structured accessibility
snapshots. Target the exact `ref` returned by a snapshot; selectors are a
fallback. Use screenshots for visual verification, not action targeting.

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

The server is headed by default. Pass `--headless` to change that. The
`--browser` choices are `chrome`, `firefox`, `webkit`, and `msedge`.

Playwright also bundles MCP and CLI entry points in its main package:

```sh
npx playwright mcp
npx playwright cli
```

## MCP access boundaries

MCP file access is limited to client workspace roots, or the current directory
when the client supplies none. `file://` navigation stays blocked unless
`allowUnrestrictedFileAccess` or the corresponding CLI flag is enabled.

Allowed- and blocked-origin rules filter browser requests, with the blocklist
winning. They do not cover redirects and are not a security boundary.
Configured `secrets` only provide convenient response-text redaction;
deployment still requires client-level permissions and normal security
controls.

## Shared browsers and cleanup

`browser.bind(name, { workspaceDir })` shares a launched browser with multiple
Playwright, `playwright-cli`, or MCP clients. Connect to the returned `endpoint`
with `chromium.connect()`. Supplying `host` and `port` creates a WebSocket
endpoint instead of a named pipe; `browser.unbind()` stops new connections.

Pages, routes, init scripts, and other returned resources support
`await using`. Scope exit closes the page or removes the route or init script.

```ts
await using page = await context.newPage();
{
  await using route = await page.route('**/*', route => route.continue());
  await using script = await page.addInitScript('console.log("ready")');
  await page.goto('https://example.com');
}
```

## Runner scheduling and preprocessing

`testConfig.retryStrategy` defaults to `'immediate'`, which schedules a retry
as soon as a worker becomes available. `'isolated'` defers retries until the
end and runs them serially in one worker to reduce interference with the main
suite.

A reporter's `preprocess()` runs after configuration resolution and before
`onBegin()`. Its `TestRun` can mark individual tests skipped, excluded, fixed,
or failing before execution begins.

## Soft polling

`expect.soft.poll()` performs a polling assertion whose final failure is
reported softly.

```ts
await expect.soft.poll(async () => readStatus()).toBe('ready');
```
