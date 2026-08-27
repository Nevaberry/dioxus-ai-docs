# Middleware, Runtimes, and Integrations

## Cache selected responses safely

Since 4.8.0, `cacheableStatusCodes` selects which response statuses cache
middleware may store.

```ts
app.use('*', cache({
  cacheName: 'pages',
  cacheControl: 'max-age=3600',
  cacheableStatusCodes: [200, 404],
}))
```

In 4.12.0, `onCacheNotAvailable` handles runtimes without an available Cache
API, and configured `Vary` headers become part of cache keys. Patched 4.12
releases refuse responses with `Vary: Authorization` or `Vary: Cookie` as well
as responses marked `private` or `no-store`.

## Configure CORS per origin

`cors({ allowMethods })` accepts an origin callback as of 4.8.0, allowing the
permitted methods to depend on the request origin.

```ts
app.use('*', cors({
  allowMethods: (origin) =>
    origin === trustedOrigin ? ['GET', 'POST'] : ['GET'],
}))
```

Version 4.13.3 appends `Origin` to `Vary` on `OPTIONS` preflight responses so a
shared cache distinguishes preflight results by origin. It also exempts
preflights from CSRF validation; do not undo the `Vary` header when adding
response middleware.

## Filter compression by content type

In 4.12.0, compression middleware accepts `contentTypeFilter` and exports
`COMPRESSIBLE_CONTENT_TYPE_REGEX` as a starting point for custom filters.
MessagePack is recognized as compressible.

## Start Service Workers explicitly

Since 4.8.0, import `fire` from `hono/service-worker` and call it with the
application. The older `app.fire()` method is deprecated.

```ts
import { fire } from 'hono/service-worker'

fire(app)
```

## Use adapter capabilities directly

### Bun WebSockets

Since 4.9.0, the Bun adapter exports `upgradeWebSocket` and `websocket`
directly. Do not obtain them indirectly through the former factory API.

### AWS Lambda binary bodies

The AWS Lambda adapter can designate response content types as binary from
4.9.0. Configure the binary list when returning images, archives, or other
non-text bodies so Lambda does not treat their bytes as ordinary text.

### Connection information

As of 4.12.0, `getConnInfo(c)` is exported by `hono/aws-lambda`,
`hono/cloudflare-pages`, and `hono/netlify`. The Lambda implementation supports
API Gateway v1, API Gateway v2, and ALB request shapes.

### Cloudflare execution context

`ExecutionContext` includes runtime-provided `props` from 4.8.0 and `exports`
from 4.12.0. A Cloudflare application can module-augment the latter to use
Wrangler-generated export types:

```ts
declare module 'hono' {
  interface ExecutionContext {
    readonly exports: Cloudflare.Exports
  }
}
```

### Public Context class

The runtime `Context` class is publicly exported from `hono` as of 4.12.0 for
integrations that need the class itself rather than only its structural type.

## Expose an MCP server over Streamable HTTP

Since 4.8.0, `@hono/mcp` provides `StreamableHTTPTransport`.

```ts
app.all('/mcp', async (c) => {
  const transport = new StreamableHTTPTransport()
  await mcpServer.connect(transport)
  return transport.handleRequest(c)
})
```

Create and connect a transport for the request, then return
`transport.handleRequest(c)` from the Hono handler.

## Format JSON deliberately

From 4.11.0, Pretty JSON accepts `force: true` to enable formatting explicitly.

```ts
app.use(prettyJSON({ force: true }))
```

Version 4.13.3 also recognizes structured JSON media types ending in `+json`,
including `application/problem+json`, and pretty-prints them.

## Preserve ETag stream and 304 behavior

Version 4.13.3 makes ETag handling copy pending stream bytes and retain the
appropriate headers while filtering a `304` response. Avoid application-level
workarounds that discard buffered bytes or all headers when adopting this fix.

## Use current MIME and logging behavior

Since 4.8.0, MIME utilities recognize web app manifest files. The logger also
honors `NO_COLOR` on Cloudflare Workers, so deployment output can disable ANSI
color without replacing the logger.
