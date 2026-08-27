---
name: playwright-knowledge-patch
description: Playwright
version: "1.61.0"
license: MIT
metadata:
  author: Nevaberry
---


# Playwright Knowledge Patch

Use this skill for Playwright browser automation, component tests, the test runner, MCP, or test-agent workflows.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser automation](references/browser-automation.md) | Screencasts, bound sessions, cancellation, storage and passkeys, screenshots, locators, diagnostics, protocol metadata, and resource disposal |
| [Component testing](references/component-testing.md) | Story gallery, mounting by story id, typed props, update, and unmount |
| [Test runner and debugging](references/test-runner-and-debugging.md) | Removed support, CLI debugging, traces, retry scheduling, video, reporters, runner data, recordings, artifacts, and platforms |
| [MCP server](references/mcp-server.md) | Entry points, snapshot interaction, profiles, initialization, capabilities, configuration, guardrails, HTTP, and embedding |
| [Test agents](references/test-agents.md) | Initialization, planner/generator/healer roles, seed tests, plans, generated artifacts, and regeneration |

## Breaking removals and compatibility changes

- WebKit no longer supports macOS 14.
- `@playwright/experimental-ct-svelte` has been removed.
- Ubuntu 26.04 is supported.
- The supplied MCP container image supports headless Chromium only.
- Regenerate bundled test-agent definitions after every Playwright upgrade so
  their instructions and tools remain synchronized with the installed version.

## Cancel operations independently

Most operations and web-first assertions accept an `AbortSignal`. The normal
timeout remains active when a signal is supplied; set `timeout: 0` when the
signal alone should bound the operation.

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

Actions also accept `scroll: 'auto' | 'none'`. Use `'none'` when Playwright
must not scroll the target into view.

## Use story-based component tests

Define concrete component scenarios as stories and let the served gallery
render them on demand. `mount(storyId)` returns a locator scoped to the story's
root; use that locator for assertions and interactions, and call its
`update(props)` or `unmount()` methods for lifecycle tests.

```ts
test('click should expand', async ({ mount }) => {
  const component = await mount('components/Expandable/Stateful');
  await component.getByRole('button').click();
  await expect(component.getByTestId('expanded')).toHaveValue('true');
});
```

Supply the story type as a type argument when props should be checked. See
[Component testing](references/component-testing.md) for the workflow.

## Persist and exercise passkeys

Each browser context exposes a cross-browser `credentials` virtual
authenticator. Seed a backend-provisioned credential, install the authenticator,
then exercise the page's normal WebAuthn ceremony without a hardware key.

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

Use `credentials.get()` to retrieve an app-created credential for reuse. Add
`credentials` to storage state when passkeys must seed later contexts.

## Work with storage directly

`page.localStorage` and `page.sessionStorage` expose the current origin's Web
Storage without evaluating page code.

```ts
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');
const sessionItems = await page.sessionStorage.items();
```

Use `browserContext.setStorageState()` to replace a live context's state. It
first clears cookies, local-storage origins, and IndexedDB origins, then applies
the replacement state.

## Record and annotate screencasts

Use `page.screencast` for explicit recording control, JPEG frame delivery, or
presentation overlays.

```ts
await page.screencast.start({
  path: 'video.webm',
  onFrame: ({ data, timestamp }) => consumeFrame(data, timestamp),
  size: { width: 800, height: 600 },
  quality: 90,
});

await using actions = await page.screencast.showActions({ cursor });
await page.screencast.showChapter('Checkout');
await page.screencast.stop();
```

`size` is an aspect-ratio-preserving maximum; without it, the viewport is
scaled within 800x800. A screencast already started by tracing or video can
override that size. Quality ranges from 0 through 100. See
[Browser automation](references/browser-automation.md) for overlays and the
regular test `video.show` annotations.

## Share a launched browser

Bind a launched browser when multiple Playwright, CLI, or MCP clients must use
one session.

```ts
const { endpoint } = await browser.bind('review-session', {
  workspaceDir: process.cwd(),
  host: 'localhost',
  port: 0,
});
const attached = await chromium.connect(endpoint);
browser.unbind();
```

Without `host` and `port`, binding uses a named pipe; with them, it exposes a
WebSocket endpoint. `browser.unbind()` stops accepting new clients.

## Generate WebP visual artifacts

End a visual snapshot name in `.webp` to select WebP. Standalone page and
locator screenshots accept `type: 'webp'`; quality 100 is lossless and is the
default, while lower values enable lossy compression.

```ts
await expect(page).toHaveScreenshot('homepage.webp');
await page.screenshot({ path: 'homepage.webp', quality: 50 });
```

## Inspect locators and page accessibility

- `page.ariaSnapshot()` snapshots the whole page, like a body locator.
- Locator ARIA snapshots accept `depth` and `mode`.
- `locator.normalize()` rewrites a locator toward recommended test-id and
  ARIA-role forms.
- `page.pickLocator()` lets a person select an element interactively;
  `page.cancelPickLocator()` cancels the picker.

## Use disposable resources

JavaScript resources such as pages, routes, and init scripts support
`await using`; scope exit closes the page or removes the installed resource.

```ts
await using page = await context.newPage();
{
  await using route = await page.route('**/*', route => route.continue());
  await using script = await page.addInitScript('console.log("ready")');
  await page.goto('https://example.com');
}
```

Evaluation methods accept functions as argument values. Page and context
`addInitScript()` methods also accept functions as init-script arguments.

## Debug from the command line

Start a test with the command-controlled debugger, attach to the bound session,
then issue debugger commands:

```bash
npx playwright test --debug=cli
playwright-cli attach
step-over
```

Inspect a saved trace without the GUI:

```bash
npx playwright trace open trace.zip
actions
action <id>
snapshot <id> --name before
snapshot <id> --name after
close
```

Use `tracing.start({ live: true })` for real-time trace updates. For flaky
tests, retain every attempt's trace when any attempt fails with
`'retain-on-failure-and-retries'`.

## Configure retries, videos, and soft polls

Set `testConfig.retryStrategy` to `'isolated'` to defer retries until the end
and run them serially in one worker. The default `'immediate'` schedules each
retry when a worker becomes available.

Video mode accepts `'on-all-retries'`, `'retain-on-first-failure'`, and
`'retain-on-failure-and-retries'`. Use `expect.soft.poll()` when a polling
failure should be collected without immediately stopping the test.

## Launch the MCP server

The MCP server requires Node.js 18 or newer. It is bundled with Playwright and
can be launched from the main package:

```bash
npx playwright mcp
npx playwright cli
```

For automation, take a structured accessibility snapshot and pass an element's
exact `ref` to the interaction tool. Use screenshots for visual verification,
not action targeting. Read [MCP server](references/mcp-server.md) before
enabling remote access, file access, origin rules, or secrets.

## Generate built-in test agents

Generate definitions for the consuming client loop:

```bash
npx playwright init-agents --loop=vscode
```

The planner explores the application and writes a plan under `specs/`; the
generator validates selectors and assertions and writes tests under `tests/`;
the healer replays failures, repairs tests within guardrails, and reruns them.
Use a seed test to provide ready application state, fixtures, setup, project
dependencies, and the preferred generated-test style. See
[Test agents](references/test-agents.md) for the artifact and audit-link flow.
