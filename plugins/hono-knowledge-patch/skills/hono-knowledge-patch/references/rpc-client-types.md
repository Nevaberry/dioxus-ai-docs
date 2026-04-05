# RPC Client & Types

## `$path` — Path String from Client (4.12+)

Returns the path string (not a full URL) from the RPC client — useful for cache keys, routers, or path-based logic:

```ts
const client = hc<typeof app>('http://localhost:8787')
client.api.posts.$path()                                // '/api/posts'
client.api.posts[':id'].$path({ param: { id: '123' } }) // '/api/posts/123'
client.api.posts.$path({ query: { filter: 'test' } })   // '/api/posts?filter=test'
```

## `parseResponse` — Structured Response Parsing (4.9+)

Parses `hc` responses with automatic content-type handling and structured errors:

```ts
import { parseResponse, DetailedError } from 'hono/client'

const result = await parseResponse(client.hello.$get()).catch((e: DetailedError) => {
  console.error(e.status, e.message)
})
```

## `ApplyGlobalResponse` Type Helper (4.12+)

Add global error response types (from `app.onError()` etc.) to all RPC client routes:

```ts
import { hc, ApplyGlobalResponse } from 'hono/client'

type AppWithErrors = ApplyGlobalResponse<typeof app, {
  401: { json: { error: string } }
  500: { json: { error: string } }
}>
const client = hc<AppWithErrors>('http://api.example.com')
```

## `PickResponseByStatusCode` Type (4.12.9+)

Extract a specific status code's response type from an RPC client endpoint:

```ts
import type { PickResponseByStatusCode } from 'hono/client'
type Ok = PickResponseByStatusCode<typeof client.api.users.$get, 200>
```

## Typed URL for Hono Client (4.11+)

Pass a base URL as the second type parameter to `hc` for precise URL types (useful as type-safe cache keys for SWR, etc.):

```ts
const client = hc<typeof app, 'http://localhost:8787'>('http://localhost:8787/')
const url = client.api.posts.$url() // TypedURL with protocol + host + path
```

## Custom NotFoundResponse Type (4.11+)

Use module augmentation to type `c.notFound()` so the RPC client infers 404 response types:

```ts
declare module 'hono' {
  interface NotFoundResponse extends Response,
    TypedResponse<{ error: string }, 404, 'json'> {}
}
```

## Custom Query Serializer for `hc` (4.11+)

`buildSearchParams` option on `hc` to control query string serialization (e.g., array bracket notation):

```ts
const client = hc<AppType>('http://localhost', {
  buildSearchParams: (query) => {
    const sp = new URLSearchParams()
    for (const [k, v] of Object.entries(query)) {
      if (Array.isArray(v)) v.forEach((item) => sp.append(`${k}[]`, item))
      else if (v !== undefined) sp.set(k, v)
    }
    return sp
  },
})
```
