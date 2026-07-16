# Playwright MCP Server

## Installation and interaction pattern

`@playwright/mcp` exposes Playwright browser automation to MCP clients and requires Node.js 18 or newer.

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

The server operates primarily on structured accessibility snapshots. Take a snapshot, then use the element `ref` it returns for an action. Screenshots are intended for visual verification rather than as action inputs.

The browser is headed by default. Use `--headless` for headless operation or `--browser=chrome|firefox|webkit|msedge` to select a browser or channel.

Core tools cover snapshot-based navigation and interaction, tabs, dialogs, file uploads, console and network inspection, screenshots, and arbitrary Playwright code. `browser_run_code` accepts an `async (page) => { ... }` function or loads that function from `filename`. Snapshot, console, network, evaluation, and screenshot results can be written to files instead of returned inline.

## Profiles and existing browsers

The default persistent profile retains login state. Profiles are partitioned by browser channel and MCP workspace.

- `--isolated` uses an in-memory profile that is discarded when the browser closes.
- Combine `--isolated` with `--storage-state=path/to/storage.json` to seed cookies and local storage.
- `--extension` connects through the MCP Bridge extension to existing Chrome or Edge tabs.

## Initial page and script setup

Use `--init-page` one or more times to load TypeScript modules whose default export receives `{ page }`:

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

Use `--init-script` to inject JavaScript before page scripts on every page. Initial-page modules run against a page, whereas init scripts run early in each document.

## Capability-gated tools

Enable additional tool groups with `--caps`:

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

| Capability | Additional operations |
| --- | --- |
| `network` | Online/offline control; route, list, and unroute network mocks |
| `storage` | Cookies, local/session storage, and storage-state operations |
| `testing` | Locator generation and visibility, list, text, and value assertions |
| `devtools` | Pause/resume, tracing, video, and chapter markers |
| `vision` | Coordinate-based mouse operations |
| `pdf` | PDF output |
| `config` | Access to the final merged server configuration |

`browser_snapshot` accepts `selector` and `depth` to limit the returned accessibility tree.

Network inspection can include response bodies or headers, filter request URLs with a regular expression, and omit successful static resources by default. `browser_route` fulfills a glob pattern with a selected status, body, content type, and headers; the mock remains active until removed with `browser_unroute`.

## Configuration

Pass `--config path/to/config.json` to use the typed configuration surface. It covers:

- Browser launch and context options or remote browser endpoints.
- Server binding and enabled capabilities.
- Output paths and session saving.
- Console reporting level and network rules.
- Test-id attribute and action, navigation, and assertion timeouts.
- Image responses, snapshot mode, and code generation.

Most command-line settings also have a corresponding `PLAYWRIGHT_MCP_*` environment variable.

## File, network, and secret guardrails

File access is restricted to workspace roots supplied by the client, or to the current directory if the client supplies none. `file://` navigation is blocked unless `--allow-unrestricted-file-access` is set.

`allowedHosts` protects against DNS rebinding. Allowed- and blocked-origin rules do not cover redirects and must not be treated as a security boundary. Similarly, `--secrets` masks matching dotenv values in tool responses as a convenience but is not a security boundary.

## HTTP transport and shared contexts

Start standalone HTTP transport on port 8931:

```bash
npx @playwright/mcp@latest --port 8931
```

Configure clients with `url: "http://localhost:8931/mcp"`. Add `--shared-browser-context` when connected HTTP clients should reuse one browser context.

The published Docker image currently supports headless Chromium only.

## Embedded server

Applications can import `createConnection` from `@playwright/mcp`, create a connection with Playwright-style browser configuration, and attach an MCP SDK transport programmatically.
