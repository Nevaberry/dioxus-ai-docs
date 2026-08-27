# Routing and Requests

## Inspect the matched route chain

Since 4.8.0, `hono/route` exports:

- `matchedRoutes(c)` for the matched handlers.
- `routePath(c)` for the current route pattern.
- `baseRoutePath(c)` for a mounted application's registered base pattern.
- `basePath(c)` for the request-resolved mounted base path.

`routePath(c, index)` and `baseRoutePath(c, index)` accept an
`Array.prototype.at()`-style index, including negative values. This makes it
possible to inspect any entry in the middleware and route chain rather than
only the last match.

```ts
app.all('/api/*', (_c, next) => next())
app.get('/api/users/:id', (c) => c.json({
  first: routePath(c, 0),
  last: routePath(c, -1),
}))
```

Inside a mounted sub-application, distinguish the local route pattern from the
mount pattern and its resolved path:

```ts
const subApp = new Hono()
subApp.get('/posts/:id', (c) => c.json({
  route: routePath(c),         // '/posts/:id'
  baseRoute: baseRoutePath(c), // '/:sub'
  base: basePath(c),           // '/api' for GET /api/posts/123
}))
app.route('/:sub', subApp)
```

## Parse requests defensively

### Query and body normalization

As of 4.8.0, invalid query parameters no longer make request query parsing
throw. `parseBody()` also normalizes returned field names instead of exposing
inconsistent key forms.

With `parseBody({ dot: true })`, use a patched 4.12 line: current behavior
ignores `__proto__` path segments to prevent prototype-oriented input from
becoming object structure.

### Recreate a consumed raw request

Since 4.10.0, `cloneRawRequest` from `hono/request` reconstructs a raw
`Request` after a validator, `c.req.json()`, or other middleware has consumed
the body.

```ts
import { cloneRawRequest } from 'hono/request'

app.post('/api', async (c) => {
  await c.req.json()
  const request = cloneRawRequest(c.req)
  await externalLibrary.process(request)
  return c.body(null, 204)
})
```

## Respect proxy header semantics

Proxy behavior follows RFC 9110 as of 4.10.0. Hop-by-hop headers are stripped
or processed rather than forwarded unchanged. Do not use those headers as an
application-level communication channel across a proxy boundary.

## Control trailing slashes and locale fallback

In 4.12.0, `trimTrailingSlash({ alwaysRedirect: true })` redirects before
handlers run, including for wildcard routes. Later 4.12 releases add `skip` so
selected requests can be exempted.

Language normalization performs RFC 4647-style progressive truncation. For
example, requested `ja-JP` can match supported `ja` before the configured
fallback is used.

## Address HTTP endpoints over Unix sockets

Since 4.8.0, Hono recognizes the `http+unix` URL scheme for HTTP endpoints
reached over Unix domain sockets. Use that scheme rather than treating the
socket path as a conventional TCP host.

## Apply router and address fixes

Version 4.13.3 corrects several boundary cases:

- `TrieRouter` matches suffix-wildcard routes.
- `PatternRouter` and `LinearRouter` no longer let wildcard routes overmatch
  path prefixes.
- `expandIPv6` preserves embedded IPv4 addresses while expanding IPv6 input.

These fixes matter when router selection differs by deployment or when client
IP parsing accepts IPv4-mapped or other mixed-form IPv6 addresses.
