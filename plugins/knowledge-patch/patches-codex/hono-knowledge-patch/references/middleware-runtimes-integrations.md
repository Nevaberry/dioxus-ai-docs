# Middleware, Runtimes, and Integrations

## Configure origin-dependent CORS

Since `4.8.0`, `cors()` can derive `allowMethods` from the request origin.

```ts
app.use('*', cors({
  allowMethods: (origin) =>
    origin === trustedOrigin ? ['GET', 'POST'] : ['GET'],
}))
```

In `4.13.3`, CORS middleware appends `Origin` to `Vary` on `OPTIONS` preflight
responses. Shared caches can then distinguish preflight results by origin. Do
not remove that variation when a proxy or CDN rewrites response headers.

## Select cacheable responses and failure behavior

Since `4.8.0`, `cacheableStatusCodes` selects which response statuses cache
middleware may store.

```ts
app.use('*', cache({
  cacheName: 'pages',
  cacheControl: 'max-age=3600',
  cacheableStatusCodes: [200, 404],
}))
```

Since `4.12.0`, `onCacheNotAvailable` handles runtimes without a usable Cache
API, and configured `Vary` headers contribute to cache keys. Patched 4.12
releases refuse responses with `Vary: Authorization` or `Vary: Cookie` and also
avoid responses marked `private` or `no-store`. Keep these checks intact when
wrapping or replacing cache middleware.

## Filter compression by content type

Since `4.12.0`, compression middleware accepts `contentTypeFilter` and exports
`COMPRESSIBLE_CONTENT_TYPE_REGEX` as a starting point for custom predicates.
MessagePack is included among compressible content types. Extend the exported
baseline instead of rebuilding its known-type list unless replacement is
intentional.

## Format JSON responses

Since `4.11.0`, Pretty JSON accepts `force: true` to enable formatting without
its normal request-dependent trigger.

```ts
app.use(prettyJSON({ force: true }))
```

In `4.13.3`, Pretty JSON recognizes structured JSON media types ending in
`+json`, including `application/problem+json`. Preserve the original media type
while formatting the body.

## Preserve stream and conditional-response correctness

The `4.13.3` ETag fix copies pending stream bytes and preserves headers while
filtering a `304` response. When combining ETag middleware with streamed or
conditional responses, test both the initial body-bearing response and a later
`If-None-Match` request.

## Use direct adapter exports

Since `4.9.0`, the Bun adapter directly exports `upgradeWebSocket` and
`websocket`; do not obtain them through the adapter's older factory API.

Also since `4.9.0`, the AWS Lambda adapter can designate response content types
as binary. Configure the relevant types when returning images, archives, or
other binary bodies so Lambda does not treat them as text.

Since `4.12.0`, `getConnInfo(c)` is exported by `hono/aws-lambda`,
`hono/cloudflare-pages`, and `hono/netlify`. The Lambda implementation handles
API Gateway v1, API Gateway v2, and ALB requests.

## Type execution context and public context

Since `4.8.0`, Hono's `ExecutionContext` type contains the runtime-provided
`props` property.

Since `4.12.0`, it also contains `exports`. A Cloudflare application can
module-augment this as `readonly exports: Cloudflare.Exports` to consume
Wrangler-generated export types.

The runtime `Context` class is publicly exported from `hono` from `4.12.0`.
Integrations that construct, recognize, or extend the actual class can import it
directly instead of relying only on its structural type.

## Expose MCP over Streamable HTTP

Since `4.8.0`, `@hono/mcp` provides `StreamableHTTPTransport` for exposing an MCP
server over Streamable HTTP.

```ts
app.all('/mcp', async (c) => {
  const transport = new StreamableHTTPTransport()
  await mcpServer.connect(transport)
  return transport.handleRequest(c)
})
```

Create and connect the transport according to the MCP server's lifecycle, then
return `transport.handleRequest(c)` from the Hono route.

## Use updated MIME and logger behavior

Since `4.8.0`, MIME utilities recognize web app manifest files. Use the inferred
manifest MIME type rather than overriding it with a generic JSON or text type.

Also since `4.8.0`, the logger honors `NO_COLOR` on Cloudflare Workers. Set that
environment value for plain logs rather than stripping escape codes downstream.
