# Routing and Requests

## Contents

- [Route matching and introspection](#route-matching-and-introspection)
- [Trailing slashes and proxy behavior](#trailing-slashes-and-proxy-behavior)
- [Request bodies, queries, and cloning](#request-bodies-queries-and-cloning)
- [URLs and language matching](#urls-and-language-matching)

## Route matching and introspection

### HEAD follows GET routing

Hono converts every `HEAD` request to `GET` before route matching and strips the response body afterward. Define a `GET` route for the shared status and headers. Dedicated `app.head()` and `app.on('HEAD', ...)` handlers do not run.

Put HEAD-only behavior in middleware that checks the original `c.req.method`:

```ts
app.use('/api/users', async (c, next) => {
  await next()
  if (c.req.method === 'HEAD') {
    c.header('X-HEAD-Processed', 'true')
    c.res = new Response(null, c.res)
  }
})

app.get('/api/users', (c) => {
  c.header('X-Total-Count', '1')
  return c.json(['Ada'])
})
```

### Inspect matched routes

The `hono/route` module provides these helpers (since 4.8.0):

- `matchedRoutes(c)`
- `routePath(c)`
- `baseRoutePath(c)`
- `basePath(c)`

Use them to inspect the handlers that matched and the route paths involved in mounted applications.

`routePath(c, index)` and `baseRoutePath(c, index)` select a match using `Array.prototype.at()` semantics. Negative indices count from the end. The positions include matching middleware as well as the endpoint route.

```ts
import { routePath } from 'hono/route'

app.all('/api/*', (c, next) => next())
app.get('/api/users/:id', (c) => {
  const middlewarePath = routePath(c, 0) // '/api/*'
  const endpointPath = routePath(c, -1) // '/api/users/:id'
  return c.json({ middlewarePath, endpointPath })
})
```

## Trailing slashes and proxy behavior

### Redirect before wildcard handlers

Trailing-slash middleware accepts `alwaysRedirect: true` so its redirect happens before wildcard handlers run (since 4.12.0).

```ts
import { trimTrailingSlash } from 'hono/trailing-slash'

app.use(trimTrailingSlash({ alwaysRedirect: true }))
```

Later 4.12 releases add `skip` for selectively exempting requests.

### Expect RFC-compliant hop-by-hop handling

Proxy handling follows RFC 9110 from 4.10.0. Connection-specific, hop-by-hop headers must not be expected to traverse a proxy unchanged.

## Request bodies, queries, and cloning

### Read raw bytes

Use `c.req.bytes()` to read a request body as bytes (since 4.12.0):

```ts
const bytes = await c.req.bytes()
```

### Clone after body consumption

Use `cloneRawRequest` from `hono/request` when a validator, middleware, or handler has already consumed the body but another API still needs a raw `Request` (since 4.10.0):

```ts
import { cloneRawRequest } from 'hono/request'

await c.req.json()
const request = cloneRawRequest(c.req)
```

### Account for parsing fixes

- Invalid query parameters no longer make the request helper throw (since 4.8.0).
- `parseBody()` normalizes parsed field names (since 4.8.0).

Do not reintroduce exception handling or field-name assumptions based on the older behavior.

## URLs and language matching

### Use HTTP over Unix sockets

Hono recognizes the `http+unix` URL scheme (since 4.8.0).

### Use progressive locale fallback

Language normalization performs RFC 4647 Lookup-style progressive truncation (since 4.12.0). A requested locale such as `ja-JP` can match supported `ja` before the configured fallback language is used.
