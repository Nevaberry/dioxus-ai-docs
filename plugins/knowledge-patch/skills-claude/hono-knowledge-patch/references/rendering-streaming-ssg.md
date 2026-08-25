# Rendering, Streaming, and Static Generation

## Manage the streaming lifecycle

Long-lived `stream`, `streamText`, and `streamSSE` producers should stop when
`stream.aborted` becomes true. Register `stream.onAbort()` when resources also
need cleanup.

Producer failures after streaming begins cannot reach `app.onError()` because
the response has already started. Pass the helper's optional third callback to
log the error and finish or close the existing stream; it cannot replace the
response.

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

When streaming misbehaves under Wrangler, set
`Content-Encoding: Identity` before returning the streaming response.

Control characters in SSE fields are rejected by patched 4.12 behavior. Do
not bypass that check when constructing event data.

## Nonce streamed JSX scripts

Since 4.8.0, `StreamingContext` accepts `scriptNonce` for inline scripts emitted
by streamed `Suspense` or `ErrorBoundary` content. Allow the identical nonce in
the response CSP. See the security reference for the associated SSR hardening.

## Select the runtime-specific SSG entry point

On Node.js, import `toSSG` from `hono/ssg` and pass a promise-based filesystem
object. Bun and Deno export filesystem-bound `toSSG(app, options)` functions
from `hono/bun` and `hono/deno` instead; do not pass a filesystem argument to
those adapter forms.

Generation defaults to `./static` with concurrency `2` and returns
`{ success, files, error? }`.

```ts
import fs from 'node:fs/promises'
import { toSSG } from 'hono/ssg'

const result = await toSSG(app, fs, { dir: './dist', concurrency: 4 })
```

## Map routes to generated files

SSG maps `/` to `index.html`, `/path` to `path.html`, and `/path/` to
`path/index.html`. The extension comes from the response `Content-Type`.
Extend `defaultExtensionMap` through `extensionMap` for custom media types;
trailing-slash routes always become `index.<ext>`.

```ts
await toSSG(app, fs, {
  extensionMap: {
    'application/x-html': 'html',
    ...defaultExtensionMap,
  },
})
```

## Select static routes

- `ssgParams()` enumerates parameter sets for a dynamic route.
- `disableSSG()` excludes a route from generation.
- `onlySSG()` generates a route and makes it return `c.notFound()` afterward.
- `isSSGContext(c)` lets shared handlers vary output while generation runs.

```ts
app.get(
  '/shops/:id',
  ssgParams(async () => [{ id: '1' }, { id: '2' }]),
  (c) => c.html(`<h1>${c.req.param('id')}</h1>`)
)
app.get('/api', disableSSG(), (c) => c.text('dynamic'))
app.get('/build-only', onlySSG(), (c) => c.html('static'))
```

## Compose SSG plugins

`toSSG()` accepts `SSGPlugin` implementations through the `plugins` option
since 4.8.0. Hooks such as `afterGenerateHook` can emit additional files.
Legacy standalone hook options are deprecated as of 4.9.0.

The default SSG plugin introduced with 4.10.0 defines recommended generation
behavior and skips non-200 responses. It is implicit only when no `plugins`
option is supplied. Once custom plugins are present, add `defaultPlugin()`
explicitly if its filtering is wanted. `beforeRequestHook` and
`afterResponseHook` may return a changed value or `false` to skip a route or
file.

```ts
const getOnly: SSGPlugin = {
  beforeRequestHook: (request) =>
    request.method === 'GET' ? request : false,
}

await toSSG(app, fs, {
  plugins: [getOnly, defaultPlugin()],
})
```

In 4.12.0, `redirectPlugin()` emits HTML for 301, 302, 303, 307, and 308
responses. Place it before `defaultPlugin()` so redirects are claimed before
ordinary output filtering.

```ts
await toSSG(app, fs, {
  plugins: [redirectPlugin(), defaultPlugin()],
})
```

## Configure JSX and CSS per request

In 4.12.0, `jsxRenderer()` accepts function-based options so renderer
configuration can be derived per request. `createCssContext()` accepts
`classNameSlug` for project-specific generated CSS class slugs.

## Use the client JSX runtime

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

## Add view transitions

`startViewTransition()` from `hono/jsx` wraps a state update in the browser View
Transitions API. `viewTransition()` from `hono/jsx/dom/css` creates a class
with a unique transition name for `::view-transition-old()` and
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
