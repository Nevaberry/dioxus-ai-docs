# Playwright MCP Server

## Server and action model

The `mcp-and-test-agents` package guidance describes `@playwright/mcp` as a
Node.js 18+ MCP server that drives Playwright through structured accessibility
snapshots.

Actions target the exact `ref` returned by a snapshot. Selectors are available
as a fallback. Screenshots are for visual verification rather than action
targeting. `browser_run_code` accepts either an async function of `page` or a
source filename.

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

The browser is headed by default; use `--headless` to change that. `--browser`
accepts `chrome`, `firefox`, `webkit`, or `msedge`.

## Profiles and initial browser state

The default persistent profile keeps login state in a platform cache directory
named for the browser channel and workspace hash. This gives separate profiles
to separate projects. `--user-data-dir` overrides the directory.

`--isolated` discards state when the browser closes and can seed cookies and
local storage with `--storage-state`. `--extension` attaches to existing Chrome
or Edge tabs through the Playwright MCP Bridge extension.

`--init-page` loads a TypeScript module for page-level setup. Repeatable
`--init-script` files instead run before page scripts in every page.

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

Core accessibility-based automation and tab management are directly
available. Additional `--caps` groups expose:

| Capability | Added tools |
| --- | --- |
| `config` | Resolved configuration |
| `network` | Request mocking and offline state |
| `storage` | Cookie and Web Storage management plus storage-state save and restore |
| `devtools` | Pause and resume, tracing, and video |
| `vision` | Coordinate input |
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

## Configuration

`--config` loads JSON that can cover:

- browser launch and context options;
- CDP or remote endpoints;
- server binding and capabilities;
- output and console filtering;
- network rules and test IDs;
- timeouts, image responses, snapshots, and code generation.

## File and origin guardrails

File access is restricted to client workspace roots, or to the current
directory if no roots are supplied. `file://` navigation is blocked unless
`allowUnrestrictedFileAccess` or its CLI flag is enabled.

Allowed- and blocked-origin rules filter browser requests, with the blocklist
winning. They do not cover redirects and are explicitly not a security
boundary.

The `secrets` setting redacts matching response text only as a convenience.
Deployment still needs client-level permissions and normal security controls.

## Standalone HTTP server

`--port` starts an HTTP server for workers or display-hosted environments.
Clients connect to `/mcp`. `sharedBrowserContext` can make all HTTP clients
reuse one context.

```sh
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

The package exports `createConnection()` for programmatic attachment of an
MCP SDK transport. Its supplied Docker image currently supports only headless
Chromium.

## Bundled package entry points

In `1.62.0`, Playwright bundles the MCP server and `playwright-cli`, so both
can be launched through the main package instead of separate package entry
points.

```sh
npx playwright mcp
npx playwright cli
```
