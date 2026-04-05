---
name: hono-knowledge-patch
description: >
  Hono 4.8–4.12 features: RPC client improvements ($path, parseResponse,
  ApplyGlobalResponse, typed URLs), MCP middleware, JWT/JWK alg requirement,
  route introspection, cookie generators, SSG plugins, JSX streaming nonce.
  Load before writing Hono 4.8+ code.
license: MIT
metadata:
  author: Nevaberry
  version: "4.12"
---

# Hono 4.8+ Knowledge Patch

Claude's baseline knowledge covers Hono through 4.7. This skill provides features from 4.8 (June 2025) onwards.

## Reference Index

- [RPC Client & Types](references/rpc-client-types.md) — `parseResponse`, `$path`, typed URLs, `ApplyGlobalResponse`, `PickResponseByStatusCode`, custom `NotFoundResponse`, `buildSearchParams`
- [Middleware](references/middleware.md) — MCP middleware, UA blocker, JWT/JWK `alg` required, JWT `iss`/`headerName`, CORS dynamic methods, JWK `allow_anon`, Cache `cacheableStatusCodes`, Basic Auth `onAuthSuccess`
- [Utilities & Runtime](references/utilities-runtime.md) — Route helper (`hono/route`), `cloneRawRequest`, `tryGetContext`, cookie string generators, `getBunServer`, service worker `fire()`, `getConnInfo` for new platforms
- [JSX & SSG](references/jsx-ssg.md) — Streaming nonce for CSP, `jsxRenderer` function-based options, SSG plugin system

## Quick Reference

### RPC Client Essentials

| Feature | Import | Since |
|---------|--------|-------|
| `$path()` — get path string (not URL) | `hono/client` | 4.12 |
| `parseResponse()` — auto content-type handling | `hono/client` | 4.9 |
| `ApplyGlobalResponse` — add error types to all routes | `hono/client` | 4.12 |
| `PickResponseByStatusCode` — extract status type | `hono/client` | 4.12 |
| Typed URL via second type param on `hc` | `hono/client` | 4.11 |
| `buildSearchParams` option on `hc` | `hono/client` | 4.11 |

```ts
// $path — returns path string, not full URL
const client = hc<typeof app>('http://localhost:8787')
client.api.posts.$path()                                // '/api/posts'
client.api.posts[':id'].$path({ param: { id: '123' } }) // '/api/posts/123'

// parseResponse — structured error handling
import { parseResponse, DetailedError } from 'hono/client'
const result = await parseResponse(client.hello.$get()).catch((e: DetailedError) => {
  console.error(e.status, e.message)
})

// ApplyGlobalResponse — type app.onError() responses into client
import { hc, ApplyGlobalResponse } from 'hono/client'
type AppWithErrors = ApplyGlobalResponse<typeof app, {
  401: { json: { error: string } }
  500: { json: { error: string } }
}>
const client = hc<AppWithErrors>('http://api.example.com')
```

### JWT/JWK — `alg` Now Required (4.11.4, Security Fix)

Algorithm confusion vulnerability fixed. **Always specify `alg`**:

```ts
import { jwt } from 'hono/jwt'
app.use('/auth/*', jwt({ secret: 'my-secret', alg: 'HS256' }))

import { jwk } from 'hono/jwk'
app.use('/auth/*', jwk({ jwks_uri: '...', alg: ['RS256'] }))
```

### MCP Middleware (`@hono/mcp`, 4.8+)

```ts
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StreamableHTTPTransport } from '@hono/mcp'

const mcpServer = new McpServer({ name: 'my-server', version: '1.0.0' })
app.all('/mcp', async (c) => {
  const transport = new StreamableHTTPTransport()
  await mcpServer.connect(transport)
  return transport.handleRequest(c)
})
```

### Route Introspection (`hono/route`, 4.8+)

```ts
import { matchedRoutes, routePath, baseRoutePath, basePath } from 'hono/route'
app.get('/users/:id', (c) => {
  const matched = matchedRoutes(c) // Array of matched route handlers
  const current = routePath(c)     // Full resolved path
})
```

### Utility Helpers

```ts
// cloneRawRequest — clone after body consumed (4.10+)
import { cloneRawRequest } from 'hono/request'
const cloned = cloneRawRequest(c.req) // body intact

// tryGetContext — non-throwing getContext (4.11+)
import { tryGetContext } from 'hono/context-storage'
const ctx = tryGetContext<Env>() // undefined if no context

// Cookie string generators (4.9+)
import { generateCookie, generateSignedCookie } from 'hono/cookie'
const str = generateCookie('name', 'value', { path: '/', secure: true })
```

### UA Blocker (`@hono/ua-blocker`, 4.8+)

```ts
import { uaBlocker } from '@hono/ua-blocker'
import { aiBots } from '@hono/ua-blocker/ai-bots'
app.use('*', uaBlocker({ blocklist: aiBots }))
```

### Typed URL & NotFoundResponse (4.11+)

```ts
// Typed URL — second type param gives full URL type (useful for SWR cache keys)
const client = hc<typeof app, 'http://localhost:8787'>('http://localhost:8787/')
const url = client.api.posts.$url() // TypedURL with protocol + host + path

// Custom NotFoundResponse — type c.notFound() for RPC client
declare module 'hono' {
  interface NotFoundResponse extends Response,
    TypedResponse<{ error: string }, 404, 'json'> {}
}
```

### SSG Plugin System (4.8+)

```ts
import type { SSGPlugin } from 'hono/ssg'
const myPlugin: SSGPlugin = {
  afterGenerateHook: (result, fsModule, options) => { /* ... */ }
}
toSSG(app, fs, { plugins: [myPlugin] })
```

### JSX Streaming Nonce (4.8+)

```tsx
import { StreamingContext } from 'hono/jsx/streaming'
<StreamingContext value={{ scriptNonce: 'random-nonce' }}>
  <Suspense fallback={<div>Loading...</div>}><AsyncComponent /></Suspense>
</StreamingContext>
```

### New Middleware Options

| Middleware | Option | Since |
|-----------|--------|-------|
| JWT | `headerName` — read from custom header | 4.8 |
| JWT | `issuer` — validate `iss` claim | 4.9 |
| JWT/JWK | `alg` — **required** | 4.11.4 |
| CORS | `allowMethods` as `(origin) => string[]` | 4.8 |
| JWK | `allow_anon: true` — pass unauthenticated | 4.8 |
| Cache | `cacheableStatusCodes` array | 4.8 |
| Basic Auth | `onAuthSuccess` callback | 4.12 |

### Platform `getConnInfo` (4.12+)

```ts
import { handle, getConnInfo } from 'hono/aws-lambda'
import { handle, getConnInfo } from 'hono/cloudflare-pages'
import { handle, getConnInfo } from 'hono/netlify'
```

### Breaking/Notable Changes

| Change | Since |
|--------|-------|
| `app.fire()` deprecated → use `fire()` from `hono/service-worker` | 4.8 |
| JWT/JWK `alg` option now **required** (security fix) | 4.11.4 |
| `getBunServer` export from `hono/bun` | 4.11.6 |
