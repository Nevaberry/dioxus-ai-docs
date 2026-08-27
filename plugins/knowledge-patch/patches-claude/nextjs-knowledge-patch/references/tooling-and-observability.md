# Tooling and Observability

## Client instrumentation (`15.3.0`)

Place `instrumentation-client.js` or `instrumentation-client.ts` at the project root. It runs monitoring and analytics setup before the application's frontend code starts.

```js
// instrumentation-client.js
performance.mark('app-init')

window.addEventListener('error', (event) => {
  reportError(event.error)
})
```

## Prerender diagnostics and server restart (`15.4.0`)

Use the dedicated build flag for a focused prerender failure investigation:

```sh
next build --debug-prerender
```

Restart the development server directly from either the error overlay or the development-indicator preferences.

## Compile and render timing (`16.0.0`)

Development request logs distinguish compile time, which covers routing and compilation, from render time, which covers application code and React rendering. Production builds report each build stage's duration.

## Bundle analysis (`16.1.0`)

`next experimental-analyze` opens an interactive production-bundle view for client and server code. It filters by route, shows complete import chains across Server-to-Client Component and dynamic-import boundaries, reports CSS and other asset sizes, and switches between client and server views.

```sh
next experimental-analyze
```

## Process-specific inspection (`16.1.0`, `16.2.0`)

`next dev --inspect` attaches Node.js debugging only to the process running application code. Unlike `NODE_OPTIONS=--inspect`, it does not attach an inspector to every process Next.js starts.

```sh
next dev --inspect
```

Use `next start --inspect` to attach the debugger to the production server for debugging plus CPU or memory profiling.

## Route enumeration (`16.1.0`)

The Next.js DevTools MCP server's `get_routes` tool returns the application's complete route list.

## Bundled documentation and managed rules (`16.2-guide`, `16.3.0`)

The `next` package ships its full Markdown documentation beneath `node_modules/next/dist/docs/`. `create-next-app` adds an `AGENTS.md` directive that points development tools there.

For an existing project, generate the managed section with:

```sh
npx @next/codemod@latest agents-md
```

Next.js-managed comment markers preserve content outside their block. In 16.3.0, `next dev` detects a coding-agent environment and maintains this pointer automatically; commit the generated block. Disable this behavior with top-level `agentRules: false`.

```ts
const nextConfig = { agentRules: false }
export default nextConfig
```

## Browser logs in the terminal (`15.4.0`, `16.2-guide`)

The 15.4 canary preview used `experimental.browserDebugInfoInTerminal`. The later stable configuration forwards browser errors during development by default through `logging.browserToTerminal`.

Accepted values are `'error'`, `'warn'`, `true` for all console output, and `false` to disable forwarding.

```ts
const nextConfig = { logging: { browserToTerminal: 'warn' } }
export default nextConfig
```

## Browser inspection CLI evolution (`16.2-guide`, `16.3.0`)

The experimental `next-browser` CLI exposed React trees, props, hooks, PPR shells, errors, logs, requests, and screenshots as structured output while preserving a browser session across calls. For PPR diagnosis, `next-browser ppr lock` showed only the static shell, `next-browser goto /path` navigated, and `next-browser ppr unlock` reported dynamic blockers and their owners.

In 16.3.0, `agent-browser` 0.27 or newer superseded `next-browser`.

```sh
npm install -g agent-browser@^0.27
agent-browser --enable react-devtools
```

With React DevTools enabled, use `react tree`, `react inspect <fiberId>`, `react renders start` and `react renders stop` for profiling, and `react suspense --only-dynamic --json` for dynamic-Suspense inspection.

## Development diagnostics (`16.2.0`)

Development output adds three focused signals:

- Every Server Function execution is logged with its function name, arguments, execution time, and defining file.
- Hydration diffs use `+ Client` and `- Server` labels to identify output from each renderer.
- The error overlay flattens `Error.cause` chains beneath the top-level error, up to five levels deep.

## First-party workflow Skills (`16.3.0`)

Earlier Next.js knowledge Skills are retired because the documentation is bundled; `npx skills update` removes them. Three workflow Skills replace them:

- `next-dev-loop` drives runtime inspection and requires `agent-browser` 0.27 or newer.
- `next-cache-components-adoption` supports incremental or direct Cache Components adoption.
- `next-cache-components-optimizer` expands a route's static shell in page-render or navigation mode.

```sh
npx skills add vercel/next.js --skill next-dev-loop
npx skills add vercel/next.js --skill next-cache-components-adoption
npx skills add vercel/next.js --skill next-cache-components-optimizer
```

## Instant-state testing (`16.3.0`)

`@next/playwright` exports `instant()`, which scopes assertions to UI available immediately after an action rather than content arriving after a network round trip.

```ts
import { instant } from '@next/playwright'

await instant(page, async () => {
  await page.click('a[href="/products/hats"]')
  await expect(page.getByText('Checking inventory...')).toBeVisible()
})
```

## DevTools MCP compilation tools (`16.3.0`)

The DevTools MCP server removes its knowledge-base, upgrade, and Cache Components helper tools. It adds `get_compilation_issues` for the whole project and `compile_route` for one route.

First-party Skills call `/_next/mcp` directly. A custom client can expose the tools by configuring `next-devtools-mcp` in `.mcp.json`.

## Markdown documentation endpoints (`16.3.0`)

Append `.md` to a `nextjs.org/docs` URL or send `Accept: text/markdown` to receive Markdown. `/docs/llms.txt` is an index, while `/docs/llms-full.txt` combines every documentation page.
