# Search Parameters

## Handle validation failures deliberately

`validateSearch` receives the JSON-parsed but unvalidated search object. If it
throws, the route's `onError` runs with `error.routerCode ===
'VALIDATE_SEARCH'`, then the route renders `errorComponent`. Prefer tolerant
schema fallbacks when malformed shared URLs should still navigate.

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

Navigation is typed against the validator's input; reading validated search is
typed against its output. A default can make a field optional for links only
if both sides are inferred correctly.

- Zod v3 requires `@tanstack/zod-adapter`. Wrap the schema with
  `zodValidator`, and use the adapter's `fallback` instead of a type-erasing
  Zod v3 `.catch()`.
- Zod v4 schemas can be passed directly.
- Standard Schema implementations can be passed directly, including Valibot
  1, ArkType 2, and Effect's `standardSchemaV1`.

```tsx
import { fallback, zodValidator } from '@tanstack/zod-adapter'

const searchSchema = z.object({
  page: fallback(z.number(), 1).default(1),
})

export const Route = createFileRoute('/products')({
  validateSearch: zodValidator(searchSchema),
})

// The default makes search optional here.
const link = <Link to="/products" />
```

## Transform destinations with search middlewares

A route's `search.middlewares` transforms search for links to that route or
its descendants. The chain runs again on navigation after validation, and
middlewares compose through `next`.

`retainSearchParams` carries selected values from the current search into the
destination. `stripSearchParams` removes values equal to the supplied defaults.

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
