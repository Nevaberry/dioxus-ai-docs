# Pinia Colada Queries

## Query state and execution

`useQuery()` requires a serializable array `key` and a `query` function.
Its data status and request activity are separate:

- `status` is `'pending'`, `'success'`, or `'error'`.
- `asyncStatus` is `'idle'` or `'loading'`.

`refresh()` deduplicates requests and respects freshness; `refetch()` forces a
request. Both normally resolve to the resulting state. Pass `true` to either
method to rethrow errors:

```ts
const { state, asyncStatus, refresh, refetch } = useQuery({
  key: ['todos'],
  query: fetchTodos,
})

await refresh()
await refetch(true)
```

### Conditional execution

The reactive `enabled` option pauses a query when inputs are unavailable and
can suppress server-side fetching:

```ts
useQuery({
  key: () => ['decks', route.params.deckId],
  query: () => fetchDeck(route.params.deckId),
  enabled: () => 'deckId' in route.params && !import.meta.env.SSR,
})
```

Long-lived queries continue watching their keys. Disable them outside the
relevant route to avoid requests with stale or missing parameters.

## Keys and reusable options

Every reactive input read by `query` must also occur in a reactive key getter:

```ts
useQuery({
  key: () => ['products', id.value, { comments: withComments.value }],
  query: () => getProduct(id.value, withComments.value),
})
```

Keys have deterministic matching rules:

- Array order matters.
- Object-property order does not matter.
- Object fields whose value is `undefined` are stripped.
- Cache filters partially match hierarchical keys unless `exact: true` is set.

For example, this targets all matching entries below a product prefix:

```ts
useQueryCache().invalidateQueries({ key: ['products', id.value] })
```

`defineQueryOptions()` accepts a static options object or a parameterized
factory. It tags the key with the query result type so cache reads and writes
remain type-safe. Key factories declared `as const` preserve a reusable
hierarchy:

```ts
const PRODUCT_KEYS = {
  root: ['products'] as const,
  byId: (id: string) => [...PRODUCT_KEYS.root, id] as const,
}

const productById = defineQueryOptions((id: string) => ({
  key: PRODUCT_KEYS.byId(id),
  query: () => getProduct(id),
}))

const cached = useQueryCache().getQueryData(productById('24').key)
```

## Cache operations

`useQueryCache()` is available in injectable contexts. It provides typed
`getQueryData()`, `setQueryData()`, `ensure()`, refresh, invalidation, and other
cache operations.

`invalidateQueries()` marks every matching entry stale but refetches active
entries only by default. Pass `'all'` as the second argument to refetch inactive
matches as well. Prefer `ensure()` before seeding data when the entry must keep
its query options and freshness behavior:

```ts
const cache = useQueryCache()
const options = productById('24')

await cache.refresh(cache.ensure(options))
await cache.invalidateQueries({ key: PRODUCT_KEYS.root }, 'all')
```

## Callbacks, metadata, and errors

Queries intentionally do not accept local `onSuccess`, `onError`, or
`onSettled` options. Watch query state for component-local side effects. For
fetch-level global hooks, install the built-in
`PiniaColadaQueryHooksPlugin`:

```ts
app.use(PiniaColada, {
  plugins: [
    PiniaColadaQueryHooksPlugin({
      onError(_error, entry) {
        if (entry.meta?.errorMessage) toast.error(entry.meta.errorMessage)
      },
    }),
  ],
})

useQuery({
  key: ['todos'],
  query: fetchTodos,
  meta: { errorMessage: 'Failed to load todos' },
})
```

Query `meta` is resolved once for each cache entry, is visible to hooks and
plugins, and must be serializable for SSR.

A failed refetch preserves previous data alongside the new error. Also,
`fetch()` does not throw for non-2xx responses, so such a response counts as a
query success unless the query function checks it and throws explicitly.

Errors default to `Error`. Change the default only globally through
`TypesConfig.defaultError`; the discriminated `state.status` union then narrows
the configured error type. Query metadata can be typed in the same module
augmentation:

```ts
import '@pinia/colada'

declare module '@pinia/colada' {
  interface TypesConfig {
    defaultError: unknown
    queryMeta: { errorMessage?: string }
  }
}
```

## Pagination

### Independent page entries

For ordinary pagination, put the reactive page in the key so every page gets a
separate cache entry. `placeholderData` can keep previous content visible while
the next page loads. During that interval the data status is successful while
`asyncStatus` is `'loading'`. Placeholder values neither change the cache nor
serialize during SSR.

### Infinite queries

`useInfiniteQuery()` keeps all pages in one cache entry. Put the page or cursor
in `pageParam`, not in the key; filters still belong in the key:

```ts
const feed = useInfiniteQuery({
  key: ['feed'],
  initialPageParam: 1,
  query: ({ pageParam }) => fetchFeed(pageParam),
  getNextPageParam: (lastPage) => lastPage.nextPage ?? null,
  maxPages: 10,
})

feed.loadNextPage()
```

Infinite queries expose `data.value.pages`, `data.value.pageParams`,
`hasNextPage`, and page-loading methods. A `null` next-page parameter means
there are no more pages. Set `maxPages` to evict older pages.

## Query behavior plugins

Plugin factories run in the array order configured on `PiniaColada`.

### Retry

`@pinia/colada-plugin-retry` adds query retries globally or per query. `retry`
accepts `false`, a count, or a `(failureCount, error)` policy. A policy returns
`false` to stop, `true` for an immediate retry, or a millisecond delay. Retries
stop when a query becomes inactive or disabled.

```ts
app.use(PiniaColada, {
  plugins: [PiniaColadaRetry({ retry: 3 })],
})

useQuery({
  key: ['todos'],
  query: fetchTodos,
  retry: (count, error) => count < 2 && shouldRetry(error),
})
```

### Automatic refetching

`@pinia/colada-plugin-auto-refetch` accepts
`autoRefetch: false | true | number | (state => boolean | number)`. The `true`
form schedules from `staleTime`, so it requires a nonzero stale time. Timers are
client-only and are not scheduled during SSR.

```ts
app.use(PiniaColada, {
  plugins: [PiniaColadaAutoRefetch({ autoRefetch: true })],
})

useQuery({
  key: ['todos'],
  query: fetchTodos,
  staleTime: 10_000,
  autoRefetch: true,
})
```

### Delayed loading state

`@pinia/colada-plugin-delay` postpones a query's transition to
`asyncStatus: 'loading'`, which avoids flicker when a background refresh
finishes quickly. Configure `delay` globally, then override it with a number or
`false` on individual queries:

```ts
app.use(PiniaColada, {
  plugins: [PiniaColadaDelay({ delay: 200 })],
})
```
