# Search, Matching, Parameters, and Route Errors

## Recover from search validation failures

`validateSearch` receives the JSON-parsed but unvalidated search object. If it
throws, the route's `onError` runs with
`error.routerCode === 'VALIDATE_SEARCH'`, and the route renders its
`errorComponent`. Use tolerant schema fallbacks when malformed URL values
should not interrupt navigation.

```tsx
const searchSchema = z.object({
  page: z.number().catch(1),
  sort: z.enum(['newest', 'oldest']).catch('newest'),
})

export const Route = createFileRoute('/products')({
  validateSearch: searchSchema,
})
```

## Preserve validator input and output types

Navigation is typed from the validator's input, while route reads use its
output. Defaults make search optional only when inference preserves both sides.

Zod v3 requires `@tanstack/zod-adapter`. Use its `fallback` helper instead of a
type-erasing Zod v3 `.catch()`. Zod v4 schemas can be passed directly. Standard
Schema implementations including Valibot 1, ArkType 2, and Effect's
`standardSchemaV1` can also be passed directly.

```tsx
import { fallback, zodValidator } from '@tanstack/zod-adapter'

const searchSchema = z.object({
  page: fallback(z.number(), 1).default(1),
})

export const Route = createFileRoute('/products')({
  validateSearch: zodValidator(searchSchema),
})

const link = <Link to="/products" />
```

## Transform link search with middleware

A route's `search.middlewares` transforms search for links to that route or its
descendants. The middleware chain runs again on navigation after validation and
composes through `next`.

- `retainSearchParams` carries selected values from the current search.
- `stripSearchParams` removes values equal to the supplied defaults.

```tsx
import {
  createFileRoute,
  retainSearchParams,
  stripSearchParams,
} from '@tanstack/react-router'

export const Route = createFileRoute('/search')({
  validateSearch: searchSchema,
  search: {
    middlewares: [
      retainSearchParams(['campaign']),
      stripSearchParams({ page: 1, tags: [] }),
    ],
  },
})
```

## Understand deterministic matching priority

Route matching traverses a segment trie rather than sorting and scanning a flat
route list. Ambiguous branches are explored by segment priority: fully static
branches can win immediately, dynamic and optional branches follow, and
wildcards are considered last. Matching therefore does not depend on browser
sorting behavior.

## Break candidate ties with parameter priority

Set `params.priority` on a route when otherwise competing candidates need an
explicit tie-breaker.

## Reject a candidate during parameter parsing

`params.parse` may experimentally return `false` to skip an incoming route
candidate. A thrown parse error still surfaces on the selected match. Outgoing
typed route-template links continue to use exact route lookup and then call
`params.stringify`.

```tsx
const reportRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/reports/$id',
  params: {
    parse: (raw) =>
      /^\d+$/.test(raw.id) ? { id: Number(raw.id) } : false,
    stringify: ({ id }) => ({ id: String(id) }),
  },
})
```

## Throw not-found errors from components

A component can throw `notFound()` without an explicit `routeId`. The route's
`notFoundComponent` handles the error, and framework error boundaries preserve
it.

## Preserve primitive `beforeLoad` errors

Primitive values thrown by `beforeLoad` remain intact through router error
handling.
