# Tooling and Observability

## Application instrumentation

### Client startup hook (`15.3.0`)

Place `instrumentation-client.js` or `instrumentation-client.ts` at the project
root to initialize monitoring and analytics before frontend application code.

```js
performance.mark('app-init')

window.addEventListener('error', (event) => {
  reportError(event.error)
})
```

## Logging and error diagnosis

### Prerender debugging (`15.4.0`)

Use the dedicated build mode for focused prerender diagnostics:

```sh
next build --debug-prerender
```

### Browser output in the terminal (`16.2-guide`)

Browser errors are forwarded to the terminal by default during development.
`logging.browserToTerminal` accepts `'error'`, `'warn'`, `true` for all console
output, or `false` to disable forwarding.

```ts
const nextConfig = { logging: { browserToTerminal: 'warn' } }
export default nextConfig
```

### Server Function and overlay detail (`16.2.0`)

Development logs each Server Function execution with its name, arguments,
duration, and defining file. Hydration mismatch diffs label output as
`+ Client` and `- Server`. The error overlay flattens `Error.cause` chains
beneath the top-level error, up to five levels deep.

## Inspectors and analyzers

### Application-only development inspection (`16.1.0`)

`next dev --inspect` debugs only the process running application code. Unlike
`NODE_OPTIONS=--inspect`, it does not attach an inspector to every spawned
process.

### Production inspection (`16.2.0`)

`next start --inspect` attaches the Node.js debugger to the production server
for debugging and CPU or memory profiling.

### Turbopack bundle analyzer (`16.1.0`)

`next experimental-analyze` launches an interactive production-bundle UI for
client and server output. Filter by route, follow full import chains across
Server-to-Client Component and dynamic-import boundaries, inspect CSS and other
asset sizes, and switch between client and server views.

```sh
next experimental-analyze
```

### Browser inspection transition (`16.2-guide`, `16.3.0`)

The experimental `next-browser` CLI originally exposed React trees, props,
hooks, PPR shells, errors, logs, requests, and screenshots while retaining a
browser session across calls. Its PPR workflow used `ppr lock`, `goto`, and
`ppr unlock` to distinguish the static shell from dynamic blockers.

It was superseded by `agent-browser` 0.27+. Start the replacement with
`--enable react-devtools`; it supports `react tree`,
`react inspect <fiberId>`, render profiling with `react renders start` and
`stop`, and dynamic-Suspense inspection with
`react suspense --only-dynamic --json`.

```sh
npm install -g agent-browser@^0.27
```

## DevTools MCP

### Route enumeration (`16.1.0`)

The DevTools MCP server exposes `get_routes`, which returns the application's
complete route list.

### Compilation tools (`16.3.0`)

The server removed its knowledge-base, upgrade, and Cache Components helper
tools. It added `get_compilation_issues` for the project and `compile_route`
for an individual route. First-party workflow Skills call `/_next/mcp`
directly; custom clients can expose these tools by configuring
`next-devtools-mcp` in `.mcp.json`.

## Documentation and project guidance

### Bundled documentation (`16.2-guide`)

The `next` package ships version-matched Markdown documentation under
`node_modules/next/dist/docs/`. `create-next-app` adds an `AGENTS.md` directive
pointing there. In existing projects, the managed block preserves surrounding
content. Generate the setup on earlier projects with:

```sh
npx @next/codemod@latest agents-md
```

### Managed rules (`16.3.0`)

When `next dev` detects a coding-agent environment, it maintains the
documentation pointer inside managed `AGENTS.md` markers. Commit the generated
block; content outside the markers remains untouched. Opt out at the top level:

```ts
const nextConfig = { agentRules: false }
export default nextConfig
```

### Workflow Skills (`16.3.0`)

Earlier Next.js knowledge Skills were retired once documentation became
bundled; `npx skills update` removes them. The replacement workflow Skills are:

- `next-dev-loop`, for runtime inspection; it requires `agent-browser` 0.27+.
- `next-cache-components-adoption`, for incremental or direct adoption.
- `next-cache-components-optimizer`, for growing a route's static shell in
  page-render or navigation mode.

```sh
npx skills add vercel/next.js --skill next-dev-loop
npx skills add vercel/next.js --skill next-cache-components-adoption
npx skills add vercel/next.js --skill next-cache-components-optimizer
```

### Markdown endpoints (`16.3.0`)

Append `.md` to any `nextjs.org/docs` URL or send
`Accept: text/markdown` to receive Markdown. `/docs/llms.txt` is an index;
`/docs/llms-full.txt` combines all documentation pages.
