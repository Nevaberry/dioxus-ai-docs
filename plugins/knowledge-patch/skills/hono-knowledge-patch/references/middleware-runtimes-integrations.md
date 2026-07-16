# Middleware, Runtimes, and Integrations

## Contents

- [Cache, CORS, and compression](#cache-cors-and-compression)
- [Response formatting](#response-formatting)
- [Contexts and connection information](#contexts-and-connection-information)
- [Runtime adapter changes](#runtime-adapter-changes)
- [MCP, MIME types, and logging](#mcp-mime-types-and-logging)

## Cache, CORS, and compression

### Select cacheable responses

Set `cacheableStatusCodes` to control which response statuses cache middleware stores (since 4.8.0):

```ts
cache({ cacheName: 'app', cacheableStatusCodes: [200, 404] })
```

In 4.12, `onCacheNotAvailable` handles runtimes where the configured cache cannot be used. Configured `Vary` headers participate in cache keys. Responses declaring `Vary: Authorization` or `Vary: Cookie` are not cached, preventing cross-user reuse.

Use a current patch release: cache behavior also rejects responses marked `private` or `no-store`.

### Choose CORS methods by origin

`allowMethods` may be a function of the request origin (since 4.8.0):

```ts
cors({
  allowMethods: (origin) =>
    origin === trustedOrigin ? ['GET', 'POST'] : ['GET'],
})
```

### Filter compression by content type

Compression middleware accepts `contentTypeFilter` in 4.12. It re-exports `COMPRESSIBLE_CONTENT_TYPE_REGEX` as a starting point for custom eligibility logic. MessagePack is recognized as compressible.

## Response formatting

### Force pretty JSON

Set `force: true` to format every matching response without the usual request-side trigger (since 4.11.0):

```ts
import { prettyJSON } from 'hono/pretty-json'

app.use(prettyJSON({ force: true }))
```

## Contexts and connection information

### Access context storage optionally

`tryGetContext()` from `hono/context-storage` returns `undefined` instead of throwing when no request context is available (since 4.11.0):

```ts
import { tryGetContext } from 'hono/context-storage'

const context = tryGetContext<Env>()
```

### Use expanded context exports

- Hono's `ExecutionContext` type exposes its `props` property from 4.8.0.
- In 4.12, Cloudflare's `ExecutionContext` includes `exports`, which can be typed through module augmentation.
- A later 4.12 release makes the `Context` class a public runtime export.

```ts
declare module 'hono' {
  interface ExecutionContext {
    readonly exports: Cloudflare.Exports
  }
}
```

### Read hosted-adapter connection data

`getConnInfo(c)` is available from `hono/aws-lambda`, `hono/cloudflare-pages`, and `hono/netlify` in 4.12. The AWS Lambda implementation supports API Gateway v1, API Gateway v2, and ALB events.

```ts
import { getConnInfo } from 'hono/aws-lambda'

const remoteAddress = getConnInfo(c).remote.address
```

## Runtime adapter changes

### Start Service Workers with `fire`

Use the standalone startup helper introduced in 4.8.0:

```ts
import { fire } from 'hono/service-worker'

fire(app)
```

`app.fire()` is deprecated.

### Import Bun WebSocket helpers directly

The Bun adapter exports `upgradeWebSocket` and `websocket` directly from 4.9.0. Import them from the adapter when defining WebSocket routes and the Bun server; an indirect setup is no longer required.

### Declare binary AWS Lambda content types

The AWS Lambda adapter can be configured with response `Content-Type` values that should use Lambda binary handling (since 4.9.0). Declare binary formats so their bodies are not treated as text.

## MCP, MIME types, and logging

### Serve streamable HTTP MCP

`@hono/mcp` exports `StreamableHTTPTransport` from 4.8.0. Connect it to an MCP server and return `transport.handleRequest(c)` from an all-method route.

```ts
app.all('/mcp', (c) => transport.handleRequest(c))
```

The initial transport is intended for stateless servers without authentication; add another design for state or authentication requirements.

### Recognize manifests and suppress color

- Web app manifest files are recognized during MIME-type detection from 4.8.0.
- The logger honors the `NO_COLOR` environment setting on Cloudflare Workers from 4.8.0.
