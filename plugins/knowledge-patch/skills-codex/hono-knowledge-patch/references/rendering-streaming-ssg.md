# Rendering, Streaming, and Static Generation

## Stop long-lived producers on abort

Long-lived `stream`, `streamText`, and `streamSSE` producers should stop when
`stream.aborted` becomes true. Register `stream.onAbort()` for cleanup.

```ts
return streamText(
  c,
  async (stream) => {
    stream.onAbort(() => cleanup())
    while (!stream.aborted) {
      await stream.writeln(await nextMessage())
      await stream.sleep(1000)
    }
  },
  (err, stream) => {
    console.error(err)
    stream.writeln('Stream failed')
  }
)
```

A producer error after the response starts goes to the streaming helper's
optional third callback rather than `app.onError()`. The callback may finish or
close the existing stream, but it cannot replace the response.

If streaming misbehaves under Wrangler, set `Content-Encoding: Identity` before
returning the streaming response.

## Nonce streamed JSX scripts

Since `4.8.0`, `StreamingContext` accepts `scriptNonce`. Wrap streamed `Suspense`
or `ErrorBoundary` output with that value and allow the same nonce in the
response CSP, because those features may emit inline scripts.

```tsx
<StreamingContext value={{ scriptNonce: nonce }}>
  <Suspense fallback={<p>Loading…</p>}>
    <Page />
  </Suspense>
</StreamingContext>
```

## Start Service Worker applications with the helper

Since `4.8.0`, import `fire` from `hono/service-worker` and call `fire(app)`.
The older `app.fire()` method is deprecated.

```ts
import { fire } from 'hono/service-worker'

fire(app)
```

## Use the SSG plugin pipeline

Since `4.8.0`, `toSSG()` accepts `SSGPlugin` implementations through the
`plugins` option. Plugins may use hooks such as `afterGenerateHook` to emit
additional files. The legacy SSG hook options are deprecated as of `4.9.0`;
move custom hooks into plugin objects.

The default plugin introduced in `4.10.0` defines the recommended generation
behavior. With no `plugins` option, it skips non-200 responses. Supplying custom
plugins disables that implicit default, so include `defaultPlugin()` explicitly
when its filtering is still wanted.

`beforeRequestHook` and `afterResponseHook` may return a changed value or `false`
to skip a route or generated file.

```ts
const getOnly: SSGPlugin = {
  beforeRequestHook: (request) =>
    request.method === 'GET' ? request : false,
}

await toSSG(app, fs, {
  plugins: [getOnly, defaultPlugin()],
})
```

## Generate redirect pages before normal pages

Since `4.12.0`, `redirectPlugin()` emits HTML pages for 301, 302, 303, 307, and
308 responses. Put it before `defaultPlugin()` so redirects are handled before
normal generation.

```ts
await toSSG(app, fs, {
  plugins: [redirectPlugin(), defaultPlugin()],
})
```

## Select runtime-specific SSG entry points

On Node.js, import `toSSG` from `hono/ssg` and pass a promise-based filesystem
object. Bun and Deno export filesystem-bound `toSSG(app, options)` functions
from `hono/bun` and `hono/deno`. Generation defaults to `./static` with
concurrency `2` and returns `{ success, files, error? }`.

```ts
import fs from 'node:fs/promises'
import { toSSG } from 'hono/ssg'

const result = await toSSG(app, fs, { dir: './dist', concurrency: 4 })
```

## Map routes to generated files

SSG maps `/` to `index.html`, `/path` to `path.html`, and `/path/` to
`path/index.html`. File extensions come from each response's `Content-Type`.
Extend `defaultExtensionMap` through `extensionMap` for custom types. A
trailing-slash route always becomes `index.<ext>`.

```ts
await toSSG(app, fs, {
  extensionMap: {
    'application/x-html': 'html',
    ...defaultExtensionMap,
  },
})
```

## Select routes for static generation

Use `ssgParams()` to enumerate parameter sets for a dynamic route,
`disableSSG()` to omit a route, and `onlySSG()` for a route that is generated but
becomes `c.notFound()` afterward. `isSSGContext(c)` lets shared handlers vary
their output while `toSSG` runs.

```ts
app.get(
  '/shops/:id',
  ssgParams(async () => [{ id: '1' }, { id: '2' }]),
  (c) => c.html(`<h1>${c.req.param('id')}</h1>`)
)
app.get('/api', disableSSG(), (c) => c.text('dynamic'))
app.get('/build-only', onlySSG(), (c) => c.html('static'))
```

## Derive renderer and CSS options

Since `4.12.0`, `jsxRenderer()` accepts function-based options so renderer
configuration can depend on each request. `createCssContext()` accepts
`classNameSlug` for project-specific generated class-name slugs.

Keep request-derived rendering state isolated; current patched behavior isolates
JSX context per request and validates JSX tag and attribute names.

## Use the browser JSX runtime

Browser components render with `render()` from `hono/jsx/dom`. React-compatible
or partially compatible hooks such as `use()`, `useSyncExternalStore()`,
`useFormStatus()`, `useActionState()`, and `useOptimistic()` come from
`hono/jsx`. Set `jsxImportSource` to `hono/jsx/dom` for the smaller client
runtime.

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "hono/jsx/dom"
  }
}
```

## Apply JSX view transitions

`startViewTransition()` from `hono/jsx` wraps a state update in the browser View
Transitions API. `viewTransition()` from `hono/jsx/dom/css` creates a class with
a unique transition name for `::view-transition-old()` and
`::view-transition-new()` rules.

`useViewTransition()` returns `[isUpdating, startViewTransition]` and
reevaluates the component during the update and again when the transition
finishes.

```tsx
const [isUpdating, start] = useViewTransition()

<button onClick={() => start(() => setOpen((value) => !value))}>
  Toggle {isUpdating && '(updating)'}
</button>
```
