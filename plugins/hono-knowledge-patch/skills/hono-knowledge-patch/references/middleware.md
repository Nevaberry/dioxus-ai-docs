# Middleware

## MCP Middleware (`@hono/mcp`, 4.8+)

Create remote MCP servers over Streamable HTTP Transport:

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

## UA Blocker Middleware (`@hono/ua-blocker`, 4.8+)

Block requests by user agent, includes AI bot presets:

```ts
import { uaBlocker } from '@hono/ua-blocker'
import { aiBots } from '@hono/ua-blocker/ai-bots'
app.use('*', uaBlocker({ blocklist: aiBots }))
```

## JWT/JWK — `alg` Now Required (4.11.4, Security Fix)

Algorithm confusion vulnerability fixed. The `alg` option is now **required** for both JWT and JWK middleware:

```ts
import { jwt } from 'hono/jwt'
app.use('/auth/*', jwt({ secret: 'my-secret', alg: 'HS256' })) // alg required

import { jwk } from 'hono/jwk'
app.use('/auth/*', jwk({ jwks_uri: '...', alg: ['RS256'] })) // alg required (array)
```

## JWT `headerName` Option (4.8+)

Read tokens from custom headers instead of Authorization:

```ts
jwt({ secret: 's', alg: 'HS256', headerName: 'X-Auth-Token' })
```

## JWT `issuer` Validation (4.9+)

Validate the `iss` claim:

```ts
jwt({ secret: 's', alg: 'HS256', issuer: 'https://auth.example.com' })
```

## CORS Dynamic `allowMethods` (4.8+)

`allowMethods` accepts a function for per-origin method control:

```ts
cors({
  allowMethods: (origin) => origin.includes('admin') ? ['GET', 'POST', 'DELETE'] : ['GET']
})
```

## JWK Options (4.8+)

- `allow_anon: true` — lets unauthenticated requests through
- `keys`/`jwks_uri` accept functions receiving context for dynamic configuration

## Cache `cacheableStatusCodes` (4.8+)

Specify which status codes to cache:

```ts
cache({ cacheableStatusCodes: [200, 404] })
```

## Basic Auth `onAuthSuccess` (4.12+)

```ts
basicAuth({
  username: 'hono', password: 'secret',
  onAuthSuccess: (c, username) => { c.set('user', username) },
})
```

## `getConnInfo` for New Platforms (4.12+)

```ts
import { handle, getConnInfo } from 'hono/aws-lambda'      // API GW v1/v2, ALB
import { handle, getConnInfo } from 'hono/cloudflare-pages'
import { handle, getConnInfo } from 'hono/netlify'
```
