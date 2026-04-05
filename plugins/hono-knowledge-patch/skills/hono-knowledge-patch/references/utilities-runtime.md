# Utilities & Runtime

## Route Helper (`hono/route`, 4.8+)

New module for route introspection:

```ts
import { matchedRoutes, routePath, baseRoutePath, basePath } from 'hono/route'

app.get('/users/:id', (c) => {
  const matched = matchedRoutes(c) // Array of matched route handlers
  const current = routePath(c)     // Full resolved path including base
  const base = baseRoutePath(c)    // Base route path
  const appBase = basePath(c)      // App base path
})
```

## `cloneRawRequest` Utility (4.10+)

Clone a raw Request after its body has been consumed (e.g., by validators/middleware), so you can pass it to external libraries:

```ts
import { cloneRawRequest } from 'hono/request'

app.post('/api', async (c) => {
  const body = await c.req.json() // consumes body
  const clonedRequest = cloneRawRequest(c.req) // clone with body intact
  await externalLibrary.process(clonedRequest)
})
```

## `tryGetContext` Helper (4.11+)

Non-throwing variant of `getContext` — returns `undefined` when called outside middleware context:

```ts
import { tryGetContext } from 'hono/context-storage'
const ctx = tryGetContext<Env>() // undefined if no context
```

## Cookie String Generators (4.9+)

`generateCookie` and `generateSignedCookie` produce cookie header strings without setting them on the response:

```ts
import { generateCookie, generateSignedCookie } from 'hono/cookie'

const str = generateCookie('name', 'value', { path: '/', secure: true })
const signed = await generateSignedCookie(secret, 'name', 'value', { httpOnly: true })
```

## `getBunServer` Export (4.11.6+)

Access the underlying Bun server instance:

```ts
import { getBunServer } from 'hono/bun'
```

## Service Worker `fire()` (4.8+)

`app.fire()` is deprecated. Use the standalone `fire()` function:

```ts
import { fire } from 'hono/service-worker'
fire(app) // replaces deprecated app.fire()
```
