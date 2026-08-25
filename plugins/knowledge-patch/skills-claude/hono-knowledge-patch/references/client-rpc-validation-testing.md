# Client, RPC, Validation, and Testing

## Generate client URLs and paths

### Preserve an exact URL type

Since 4.11.0, a literal second `hc` type parameter makes `$url()` preserve the
protocol, host, and path in its `TypedURL` type.

```ts
const client = hc<typeof app, 'http://localhost:8787'>(
  'http://localhost:8787/'
)
const url = client.api.posts.$url()
```

### Return only a client path

Endpoints expose `$path()` from 4.12.0. It applies path and query parameters but
returns a path string rather than a `URL`, which is useful for router inputs and
cache keys.

```ts
const path = client.posts[':id'].$path({
  param: { id: '42' },
  query: { view: 'full' },
})
```

### Keep path and query values in wire format

Both `param` and `query` values passed to Hono Client must be strings even when
server validation coerces them to numbers, booleans, or other types. `hc` does
not URL-encode path parameters. Encode ordinary values explicitly, and pass a
raw slash only when the server route intentionally accepts it through a regexp
parameter such as `/:id{.+}`.

```ts
await client.posts[':id'].$get({
  param: { id: encodeURIComponent('123/456') },
  query: { page: '1' },
})
```

Version 4.13.3 fixes `replaceUrlParam` so replacement values containing `$`
replacement-token text remain literal instead of corrupting the client URL.

### Customize query serialization

Set `buildSearchParams` in the `hc` options when an API uses conventions such
as bracketed array keys.

```ts
const client = hc<AppType>('http://localhost', {
  buildSearchParams(query) {
    const params = new URLSearchParams()
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined) continue
      if (Array.isArray(value)) {
        value.forEach((item) => params.append(`${key}[]`, item))
      } else {
        params.set(key, value)
      }
    }
    return params
  },
})
```

### Override fetch initialization per call

Pass `RequestInit` as `{ init }` in the method call's second argument. Its
values have final precedence and can override the method, body, or headers that
`hc` generated.

```ts
await client.posts.$post(
  { json: post },
  { init: { signal: abortController.signal } }
)
```

## Parse and type RPC responses

### Parse by response content type

Since 4.9.0, `parseResponse()` from `hono/client` accepts an `hc` response
promise, selects its parser from `Content-Type`, and throws a structured
`DetailedError` when the response is unsuccessful.

```ts
import { parseResponse } from 'hono/client'

const result = await parseResponse(client.hello.$get())
```

### Include middleware and earlier-handler responses

From 4.10.0, multi-handler route inference carries responses from middleware
and earlier handlers into the `hc` response union. Status checks for each
possible branch therefore narrow to the corresponding body type.

### Type custom not-found output

Augment `NotFoundResponse` when the application returns a typed custom 404, so
`c.notFound()` and the generated client retain that payload type.

```ts
import type { TypedResponse } from 'hono'

declare module 'hono' {
  interface NotFoundResponse
    extends Response,
      TypedResponse<{ error: string }, 404, 'json'> {}
}
```

### Add global and status-specific responses

`ApplyGlobalResponse`, exported from `hono/client` from v4.12.1, adds shared
responses from global middleware or `onError()` to every route schema.
`PickResponseByStatusCode` selects one status variant from an inferred union.

```ts
type AppWithErrors = ApplyGlobalResponse<
  typeof app,
  { 401: { json: { error: string } }; 500: { json: { error: string } } }
>
```

## Validate request inputs

### Honor parser preconditions

`validator('json', ...)` and `validator('form', ...)` receive `{}` when the
request lacks the matching `Content-Type`. The rule also applies to requests
created in tests. Header-validator input uses lowercase keys, so access
`value['idempotency-key']`, not a display-cased spelling.

```ts
const res = await app.request('/posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: 'Hello' }),
})
```

### Use Standard Schema or Zod 4

`@hono/standard-validator` exports `sValidator()` for any Standard
Schema-compatible library, including Zod, Valibot, and ArkType. Read validated
data through `c.req.valid()` as usual. `@hono/zod-validator` supports Zod v4
since 4.8.0-era integration updates.

```ts
import { sValidator } from '@hono/standard-validator'
import * as z from 'zod'

const schema = z.object({ name: z.string(), age: z.number() })
app.post('/author', sValidator('json', schema), (c) =>
  c.json(c.req.valid('json'))
)
```

## Test applications and clients

`testClient` accepts Hono Client options as of 4.8.0, allowing tests to
configure the generated client in the same way as production client creation.

Pass mocked `c.env` bindings as the third argument to
`app.request(path, init, env)`:

```ts
const res = await app.request('/posts', {}, {
  API_HOST: 'example.com',
})
```

Remember to supply the matching `Content-Type` in `app.request()` tests when a
JSON or form validator should parse the body.
