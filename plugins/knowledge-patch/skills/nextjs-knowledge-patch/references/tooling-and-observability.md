# Tooling and Observability

Batch attributions used here: `15.3.0`, `15.4.0`, `15.5.0`, `16.0.0`, `16.1.0`, `16.2-guide`, `16.2.0`, and `16.3.0`.

## Client instrumentation

Put `instrumentation-client.js` or `instrumentation-client.ts` at the project root to initialize monitoring and analytics before application frontend code starts (`15.3.0`).

```js
// instrumentation-client.js
performance.mark('app-init')

window.addEventListener('error', (event) => {
  reportError(event.error)
})
```

This is an early client hook; keep server-only secrets and packages out of it.

## Prerender diagnostics and development restarts

Use the focused build mode when a prerender failure needs dedicated diagnostics (`15.4.0`):

```sh
next build --debug-prerender
```

The development server can also be restarted directly from either the error overlay or the development-indicator preferences (`15.4.0`). A restart is useful after changing state that HMR cannot safely reconcile.

## Stage timing and command isolation

Development request logs separate compilation time—routing and compilation—from render time, which covers application code and React rendering (`16.0.0`). Production builds likewise report the duration of each build stage. Use the split to distinguish a compiler bottleneck from slow application work.

`next dev` and `next build` write to separate output directories, so they can run concurrently. Project locking prevents conflicting command instances from running together.

## Bundle analysis

`next experimental-analyze` opens an interactive production bundle interface for both client and server code (`16.1.0`). It can:

- Filter by route.
- Switch between client and server views.
- Show complete import chains across Server-to-Client Component and dynamic-import boundaries.
- Display JavaScript, CSS, and other asset sizes.

```sh
next experimental-analyze
```

## Process inspection

Use the scoped development inspector when only application code should attach to Node.js debugging (`16.1.0`):

```sh
next dev --inspect
```

Unlike `NODE_OPTIONS=--inspect`, this does not attach an inspector to every process spawned by Next.js.

Inspect the production server for debugging or CPU and memory profiling with (`16.2.0`):

```sh
next start --inspect
```

## Browser-to-terminal logging

Browser errors are forwarded to the development terminal by default in `16.2-guide`. Configure the level with `logging.browserToTerminal`:

```ts
const nextConfig = {
  logging: { browserToTerminal: 'warn' },
}

export default nextConfig
```

Accepted values are:

- `'error'` for errors only.
- `'warn'` for warnings and errors.
- `true` for all browser console output.
- `false` to disable forwarding.

The earlier `experimental.browserDebugInfoInTerminal` flag was a `15.4.0` preview of this capability.

## Development error and function diagnostics

Development output gained more precise labels in `16.2.0`:

- Every Server Function execution is logged with its function name, arguments, execution time, and defining file.
- Hydration diffs label browser output as `+ Client` and server output as `- Server`.
- The error overlay flattens an `Error.cause` chain below the top-level exception, up to five levels deep.

Use these labels before adding ad hoc logging: they identify the executing function, the side responsible for mismatched markup, and nested causes directly.

## Bundled documentation and managed `AGENTS.md`

The installed `next` package includes its Markdown documentation under `node_modules/next/dist/docs/` (`16.2-guide`). `create-next-app` adds an `AGENTS.md` directive pointing coding tools at that version-matched documentation. In an existing project, the updater preserves all content outside the managed comment markers.

Projects using an earlier setup can generate the directive with:

```sh
npx @next/codemod@latest agents-md
```

In `16.3.0`, `next dev` detects a coding-agent environment and writes or maintains the documentation pointer inside those managed markers. Commit the generated block so other environments receive the same rule. Opt out at the top level only when the project deliberately manages this itself:

```ts
const nextConfig = { agentRules: false }
export default nextConfig
```

Do not edit inside generated markers unless the tool's workflow explicitly permits it; surrounding project instructions remain yours.

## Documentation over HTTP

Next.js documentation has Markdown endpoints as of `16.3.0`:

- Append `.md` to a `nextjs.org/docs` URL.
- Or send `Accept: text/markdown` to the normal documentation URL.
- Use `/docs/llms.txt` as a documentation index.
- Use `/docs/llms-full.txt` for the combined documentation set.

Prefer the installed documentation when it must match the package in the application; use the HTTP forms for tooling that consumes current site content.

## DevTools MCP route and compilation tools

The DevTools MCP server exposed `get_routes` in `16.1.0`; it returns the application's full route list.

In `16.3.0`, the server removes its knowledge-base, upgrade, and Cache Components helper tools and adds:

- `get_compilation_issues` for project-wide compilation problems.
- `compile_route` for compiling one selected route.

First-party workflow Skills call `/_next/mcp` directly. A custom agent client can expose the same tools by configuring `next-devtools-mcp` in `.mcp.json`.

## Browser inspection tools

### Earlier `next-browser` workflow

The experimental `next-browser` CLI in `16.2-guide` maintained one browser session across commands and returned structured data for React trees, props, hooks, PPR shells, errors, logs, requests, and screenshots.

For PPR diagnosis, the sequence was:

```sh
next-browser ppr lock
next-browser goto /path
next-browser ppr unlock
```

`ppr lock` displayed only the static shell. `ppr unlock` then reported dynamic blockers and their owners.

### `agent-browser` replacement

`agent-browser` 0.27 or newer supersedes `next-browser` in `16.3.0`.

```sh
npm install -g agent-browser@^0.27
agent-browser --enable react-devtools
```

With React DevTools enabled, relevant commands include:

- `react tree`.
- `react inspect <fiberId>`.
- `react renders start` and `react renders stop` for profiling.
- `react suspense --only-dynamic --json` for dynamic-Suspense inspection.

## First-party workflow Skills

Earlier Next.js knowledge Skills are retired in `16.3.0`; `npx skills update` removes them. Three workflow Skills replace them:

- `next-dev-loop` drives runtime inspection and requires `agent-browser` 0.27 or newer.
- `next-cache-components-adoption` performs incremental or direct Cache Components adoption.
- `next-cache-components-optimizer` expands a route's static shell in page-render or navigation mode.

```sh
npx skills add vercel/next.js --skill next-dev-loop
npx skills add vercel/next.js --skill next-cache-components-adoption
npx skills add vercel/next.js --skill next-cache-components-optimizer
```

## Instant-state Playwright assertions

`@next/playwright` exports `instant()`, which scopes assertions to UI available immediately after an action rather than content arriving after a network round trip (`16.3.0`).

```ts
import { instant } from '@next/playwright'

await instant(page, async () => {
  await page.click('a[href="/products/hats"]')
  await expect(page.getByText('Checking inventory...')).toBeVisible()
})
```

Use this to verify the loading shell or other instant navigation state separately from eventual server content.

## Linter command migration

`next lint` was deprecated in `15.5.0` and removed in Next.js 16. Use the direct linter migration:

```sh
npx @next/codemod@latest next-lint-to-eslint-cli .
```

Run ESLint, Biome, or another selected linter as its own CI step; `next build` no longer performs linting.
