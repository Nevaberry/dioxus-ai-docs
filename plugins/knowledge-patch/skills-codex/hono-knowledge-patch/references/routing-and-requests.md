# Routing and Requests

## Inspect matched routes and mounted paths

Since `4.8.0`, `hono/route` exports `matchedRoutes(c)`, `routePath(c)`,
`baseRoutePath(c)`, and `basePath(c)`. They expose the matched handler chain,
the current route pattern, the mounted base pattern, and the resolved base path.

`routePath(c, index)` and `baseRoutePath(c, index)` also accept an
`Array.prototype.at()`-style index, including negative indices, so middleware can
inspect a particular match rather than only the last one.

```ts
app.all('/api/*', (_c, next) => next())
app.get('/api/users/:id', (c) => c.json({
  first: routePath(c, 0),
  last: routePath(c, -1),
}))
```

Inside a mounted sub-application, `baseRoutePath(c)` returns the registered
mount pattern, while `basePath(c)` substitutes request parameters. `routePath(c)`
remains the sub-application-local pattern.

```ts
const subApp = new Hono()
subApp.get('/posts/:id', (c) => c.json({
  route: routePath(c),
  baseRoute: baseRoutePath(c),
  base: basePath(c),
}))
app.route('/:sub', subApp)
```

## Parse queries and bodies defensively

As of `4.8.0`, invalid query parameters no longer make request query parsing
throw. `parseBody()` also normalizes its returned field names instead of exposing
inconsistent key forms. Do not reintroduce error handling or key-shape
assumptions based on older behavior.

When `parseBody({ dot: true })` is used on a patched 4.12 release, `__proto__`
path segments are ignored. Keep the framework on the security floor described in
[Security and authentication](security-and-auth.md), and do not merge
user-controlled nested input into privileged objects without validation.

## Reconstruct a consumed request

Since `4.10.0`, import `cloneRawRequest` from `hono/request` when middleware or a
validator has consumed the request body but another integration still needs a
raw `Request`.

```ts
import { cloneRawRequest } from 'hono/request'

app.post('/api', async (c) => {
  await c.req.json()
  const request = cloneRawRequest(c.req)
  await externalLibrary.process(request)
})
```

## Respect proxy header semantics

Since `4.10.0`, proxy handling processes or strips hop-by-hop headers according
to RFC 9110. Do not depend on those headers being forwarded unchanged, and test
proxy behavior at the deployment boundary.

## Control trailing slashes and locale fallback

Since `4.12.0`, `trimTrailingSlash({ alwaysRedirect: true })` redirects before
route handlers run, including for wildcard routes. A later 4.12 patch adds
`skip` for requests that must be exempt.

Language normalization now uses RFC 4647-style progressive truncation. For
example, `ja-JP` can match supported locale `ja` before the configured fallback.

## Address HTTP services through Unix sockets

Since `4.8.0`, Hono recognizes the `http+unix` scheme for HTTP endpoints reached
through Unix domain sockets. Preserve that scheme when constructing adapter or
proxy URLs; do not treat the socket path as an ordinary HTTP host.

## Retest wildcard routing after router fixes

In `4.13.3`, `TrieRouter` correctly matches suffix-wildcard routes, while
`PatternRouter` and `LinearRouter` stop wildcard routes from overmatching path
prefixes. Add boundary cases for a path that should match, a neighboring prefix
that must not match, and mounted or fallback routes that might compete.

## Expand embedded IPv4 addresses in IPv6 input

The `4.13.3` `expandIPv6` fix preserves embedded IPv4 addresses instead of
truncating them during expansion. If access control, connection metadata, or
logging normalizes IPv4-mapped IPv6 input, test the complete address rather than
only pure-IPv6 forms.
