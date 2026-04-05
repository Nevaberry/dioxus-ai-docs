# JSX & SSG

## JSX Streaming Nonce (4.8+)

`StreamingContext` accepts `scriptNonce` for CSP compliance on Suspense/ErrorBoundary inline scripts:

```tsx
import { StreamingContext } from 'hono/jsx/streaming'
<StreamingContext value={{ scriptNonce: 'random-nonce' }}>
  <Suspense fallback={<div>Loading...</div>}><AsyncComponent /></Suspense>
</StreamingContext>
```

## JSX Renderer Function-Based Options (4.12.6+)

`jsxRenderer` options can now be a function receiving the context for dynamic configuration:

```ts
import { jsxRenderer } from 'hono/jsx-renderer'
app.use('*', jsxRenderer((c) => ({ title: c.req.path === '/' ? 'Home' : 'Page' })))
```

## SSG Plugin System (4.8+)

`toSSG` now accepts a `plugins` array. Plugins can hook into generation stages (e.g., `afterGenerateHook`):

```ts
import type { SSGPlugin } from 'hono/ssg'
const myPlugin: SSGPlugin = {
  afterGenerateHook: (result, fsModule, options) => { /* ... */ }
}
toSSG(app, fs, { plugins: [myPlugin] })
```
