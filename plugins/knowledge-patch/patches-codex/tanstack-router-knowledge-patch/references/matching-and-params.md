# Matching and Parameters

## Expect deterministic segment-priority matching

Matching traverses a segment trie rather than sorting and scanning a flat route
list. It explores ambiguous static, dynamic, optional, and wildcard branches
by priority. A fully static branch can win immediately, and wildcard branches
are considered last. Matching therefore does not depend on browser sorting
behavior.

## Break candidate ties with parameter priority

Set `params.priority` when otherwise competing route candidates need an
explicit tie-breaker. It complements the segment-priority matcher; it is not a
replacement for designing unambiguous paths.

## Reject candidates from parameter parsing

`params.parse` may experimentally return `false` to skip an incoming route
candidate. Throwing from the parser still surfaces a parse error on the route
that is selected. Outgoing typed route-template links continue to resolve the
exact route and then call `params.stringify`.

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

## Throw not-found results from components

A component may throw `notFound()` without an explicit `routeId`. The route's
`notFoundComponent` handles it, and framework error boundaries preserve the
not-found error.

## Preserve primitive `beforeLoad` failures

Primitive values thrown from `beforeLoad` remain intact as they pass through
router error handling. Code consuming route errors should not assume every
failure is an `Error` instance.
