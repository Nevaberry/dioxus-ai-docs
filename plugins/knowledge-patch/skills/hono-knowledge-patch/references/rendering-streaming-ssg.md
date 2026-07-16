# Rendering, Streaming, and Static Generation

## Contents

- [Response streaming](#response-streaming)
- [Static generation entry points](#static-generation-entry-points)
- [Route-to-file generation](#route-to-file-generation)
- [SSG plugins](#ssg-plugins)
- [JSX rendering and CSS](#jsx-rendering-and-css)
- [Client JSX and view transitions](#client-jsx-and-view-transitions)

## Response streaming

### Run an abort-aware producer

`stream`, `streamText`, and `streamSSE` from `hono/streaming` run an async producer. Depending on the helper, their writers support byte or text writes, piping a readable stream, sleeping, and abort callbacks; the SSE writer also provides `writeSSE()`.

The response closes when the producer finishes. Stop a long-lived producer when `stream.aborted` becomes true.

```ts
return streamSSE(c, async (stream) => {
  while (!stream.aborted) {
    await stream.writeSSE({ data: 'tick', event: 'tick' })
    await stream.sleep(1000)
  }
})
```

### Handle errors after the response starts

Streaming helpers accept an optional third callback, `(err, stream)`, for producer failures. These errors do not reach the application's `onError` hook because the response has already started. The callback may write to or close the existing stream, but it cannot replace the response.

### Apply the Wrangler workaround when needed

If Cloudflare Workers streaming misbehaves under Wrangler, set the identity content encoding before returning the stream:

```ts
c.header('Content-Encoding', 'Identity')
```

### Add a CSP nonce to streamed JSX

Set `StreamingContext` to `value={{ scriptNonce: nonce }}` so inline scripts generated for streamed `Suspense` and `ErrorBoundary` receive a nonce (since 4.8.0). Allow that same nonce in the response CSP header.

## Static generation entry points

On Node.js, import `toSSG(app, fs, options)` from `hono/ssg` and pass a promise-based filesystem object. It defaults to `./static` with concurrency `2`. The result has `success`, generated `files`, and an optional `error`.

```ts
import fs from 'node:fs/promises'
import { toSSG } from 'hono/ssg'

const result = await toSSG(app, fs, { dir: './dist', concurrency: 4 })
```

The Deno and Bun adapters instead export `toSSG(app, options)` from `hono/deno` and `hono/bun`; do not pass a filesystem argument to those adapter entry points.

## Route-to-file generation

### Understand path mapping

SSG maps routes below the output directory as follows:

| Route | Generated path |
| --- | --- |
| `/` | `index.html` |
| `/path` | `path.html` |
| `/path/` | `path/index.html` |

Extensions derive from each response's `Content-Type`. Add MIME mappings with `extensionMap`, usually by extending `defaultExtensionMap`.

```ts
toSSG(app, fs, {
  extensionMap: { 'application/x-html': 'html', ...defaultExtensionMap },
})
```

### Enumerate parameterized routes

Attach `ssgParams()` before a parameterized handler to provide every parameter object that should be generated.

```ts
app.get(
  '/shops/:id',
  ssgParams(async () => [{ id: '1' }, { id: '2' }]),
  (c) => c.html(`<h1>${c.req.param('id')}</h1>`)
)
```

### Select generation modes

- `disableSSG()` excludes a route from generation.
- `onlySSG()` generates a route and then makes it return `c.notFound()` after `toSSG` finishes.
- `isSSGContext(c)` lets one handler return different content during static generation and normal serving.

## SSG plugins

### Use the plugin array

`toSSG()` accepts a `plugins` array of `SSGPlugin` objects from 4.8.0. Hooks such as `afterGenerateHook(result, fsModule, options)` can create artifacts after generation. `DEFAULT_OUTPUT_DIR` exposes the default destination.

Legacy SSG hook options are deprecated from 4.9.0; migrate the hooks into objects passed through `plugins`.

### Compose redirect and default behavior

Hono provides a default plugin with the recommended generation behavior from 4.10.0.

In 4.12, `redirectPlugin()` turns 301, 302, 303, 307, and 308 responses into HTML redirect pages. Put it before `defaultPlugin()` so redirects are handled before ordinary pages.

```ts
import { defaultPlugin, redirectPlugin, toSSG } from 'hono/ssg'

await toSSG(app, fs, {
  plugins: [redirectPlugin(), defaultPlugin()],
})
```

## JSX rendering and CSS

In 4.12, `jsxRenderer` accepts function-based options for request-dependent renderer settings. `createCssContext` accepts `classNameSlug` to customize generated class-name slugs.

## Client JSX and view transitions

### Configure the client runtime

Render browser components with `render()` from `hono/jsx/dom` and import hooks from `hono/jsx`. For the smaller client runtime, set `jsxImportSource` to `hono/jsx/dom`.

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "hono/jsx/dom"
  }
}
```

Its compatible or partially compatible surface includes transitions and deferred values, plus `use()`, `useSyncExternalStore()`, `useFormStatus()`, `useActionState()`, and `useOptimistic()`.

### Animate state changes

- `startViewTransition()` from `hono/jsx` wraps a state update in the browser View Transitions API.
- `viewTransition()` from `hono/jsx/dom/css` creates a class with a unique transition name and inserts it into `::view-transition-old()` and `::view-transition-new()` rules.
- `useViewTransition()` returns `[isUpdating, startViewTransition]` and reevaluates the component during the update and after the transition finishes.

```tsx
const [isUpdating, start] = useViewTransition()

<button onClick={() => start(() => setOpen((value) => !value))}>
  Toggle {isUpdating && '(updating)'}
</button>
```
