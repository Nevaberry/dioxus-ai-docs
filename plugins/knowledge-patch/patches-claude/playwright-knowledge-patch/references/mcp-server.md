# Playwright MCP Server

This reference contains the server guidance from `mcp-and-test-agents`.

## Entry points and interaction model

The Playwright MCP server requires Node.js 18 or newer. It drives Playwright
through structured accessibility snapshots. Take a snapshot and pass the exact
element `ref` to an interaction tool; selectors are a fallback. Screenshots are
for visual verification rather than action targeting. `browser_run_code`
accepts either an async function of `page` or a source filename.

The server and `playwright-cli` are bundled with Playwright (since 1.62.0):

```bash
npx playwright mcp
npx playwright cli
```

The separate package entry point remains configurable:

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

The browser is headed by default. Use `--headless` to change that. `--browser`
accepts `chrome`, `firefox`, `webkit`, or `msedge`.

## Persistent, isolated, and extension sessions

The default persistent profile retains login state in a platform cache
directory named for the browser channel and workspace hash, giving projects
separate profiles. `--user-data-dir` overrides that directory.

Use `--isolated` for a session discarded when the browser closes. It can seed
cookies and local storage through `--storage-state`. Use `--extension` to
attach to existing Chrome or Edge tabs through the Playwright MCP Bridge
extension.

## Initial browser state

`--init-page` loads one TypeScript module for page-level setup. Repeatable
`--init-script` files run before page scripts in every page.

```ts
// init-page.ts
export default async ({ page }) => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({
    latitude: 37.7749,
    longitude: -122.4194,
  });
};
```

## Capability-gated tools

Core accessibility automation and tab management are always available. Add
specialized tool groups with `--caps`:

| Capability | Adds |
| --- | --- |
| `config` | Resolved configuration |
| `network` | Request mocking and offline state |
| `storage` | Cookies, Web Storage, and storage-state save/restore |
| `devtools` | Pause/resume, tracing, and video |
| `vision` | Coordinate-based input |
| `pdf` | PDF output |
| `testing` | Locator and assertion helpers |

```json
{
  "args": [
    "@playwright/mcp@latest",
    "--caps=network,storage,testing"
  ]
}
```

## Configuration surface

`--config` loads JSON that can cover browser launch and context options, CDP or
remote endpoints, server binding, capabilities, output, console filtering,
network rules, test IDs, timeouts, image responses, snapshots, and code
generation.

## File, origin, and secret guardrails

File access is limited to workspace roots supplied by the client, or to the
current directory when the client supplies none. `file://` navigation is
blocked unless `allowUnrestrictedFileAccess` or its CLI equivalent is enabled.

Allowed- and blocked-origin rules filter browser requests, with the blocklist
winning. They do not cover redirects and are not a security boundary. Likewise,
`secrets` only redacts matching response text as a convenience. Remote
deployments still need client-level permissions and ordinary security controls.

## HTTP and embedded deployment

`--port` starts an HTTP server for workers or display-hosted environments;
clients connect to `/mcp`. Set `sharedBrowserContext` when all HTTP clients
should reuse one browser context.

```bash
npx @playwright/mcp@latest --port 8931
```

```json
{
  "mcpServers": {
    "playwright": {
      "url": "http://localhost:8931/mcp"
    }
  }
}
```

The package exports `createConnection()` for attaching an MCP SDK transport
programmatically. Its supplied container image supports headless Chromium only.
