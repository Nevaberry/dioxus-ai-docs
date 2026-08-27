# Pinia Colada Queries

## Installation and global policy

Install `@pinia/colada` alongside Pinia. Register Pinia first and Pinia Colada
second. Global defaults live below `queryOptions` and `mutationOptions`, and
plugin factories run in array order. Query defaults include a 5-second
`staleTime` and 5-minute `gcTime`.

```ts
app.use(createPinia())
app.use(PiniaColada, {
  queryOptions: { staleTime: 5_000, gcTime: 300_000 },
  mutationOptions: {},
  plugins: [],
})
```

## Query state and execution

`useQuery()` requires a cache `key` and a `query`. `status` describes data as
`'pending'`, `'success'`, or `'error'`; `asyncStatus` independently describes
request activity as `'idle'` or `'loading'`.

```ts
const { state, asyncStatus, refresh, refetch } = useQuery({
  key: ['todos'],
  query: fetchTodos,
})

await refresh()
await refetch(true)
```

`refresh()` deduplicates concurrent work and respects freshness. `refetch()`
forces a request. Both normally resolve to the resulting state; pass `true` to
rethrow an error.

### Gate execution with `enabled`

The reactive `enabled` option pauses queries when required inputs are absent
and can suppress server-side fetching. Long-lived queries continue watching
their keys, so disable them outside the route that supplies valid inputs.

```ts
useQuery({
  key: () => ['decks', route.params.deckId],
  query: () => fetchDeck(route.params.deckId),
  enabled: () => 'deckId' in route.params && !import.meta.env.SSR,
})
```

## Query keys

Keys are serializable arrays. Put every reactive query input in a reactive key
getter. Array order matters, object-property order does not, and `undefined`
object fields are removed. Cache filters partially match hierarchical keys
unless `exact: true` is supplied.

```ts
useQuery({
  key: () => ['products', id.value, { comments: withComments.value }],
  query: () => getProduct(id.value, withComments.value),
})

useQueryCache().invalidateQueries({ key: ['products', id.value] })
```

### Define reusable typed options

`defineQueryOptions()` accepts a static options object or parameterized factory
and tags the key with its result type, making cache reads and writes type-safe.
Use `as const` in key factories to preserve a hierarchy across queries and
cache operations.

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

`useQueryCache()` is available in injectable contexts. It exposes typed
`getQueryData()`, `setQueryData()`, `ensure()`, and refresh and invalidation
operations. `invalidateQueries()` marks every match stale but refetches only
active entries by default; pass `'all'` as the second argument to include
inactive matches. Use `ensure()` before seeding or refreshing when the entry
must preserve its query options and freshness behavior.

```ts
const cache = useQueryCache()
const options = productById('24')

await cache.refresh(cache.ensure(options))
await cache.invalidateQueries({ key: PRODUCT_KEYS.root }, 'all')
```

## Errors, callbacks, and metadata

A failed refetch retains previous data alongside the new error. The browser
`fetch()` API treats non-2xx responses as successful promises, so a query
function must explicitly throw for those responses to enter error state.

Errors default to `Error`. Change the type only globally through
`TypesConfig.defaultError`; error values then narrow through the discriminated
`state.status` union.

```ts
import '@pinia/colada'

declare module '@pinia/colada' {
  interface TypesConfig {
    defaultError: unknown
    queryMeta: { errorMessage?: string }
  }
}
```

Queries deliberately omit local `onSuccess`, `onError`, and `onSettled`
options. Watch state for component-local effects, or install
`PiniaColadaQueryHooksPlugin` for fetch-level global hooks. `meta` is resolved
once when the cache entry is created, is exposed to hooks and plugins, and must
be serializable for SSR.

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

## Pagination

### Keep regular pages in separate entries

For regular pagination, put the reactive page in the key so every page receives
its own cache entry. `placeholderData` can preserve previous content with a
successful data status while the next page has `asyncStatus: 'loading'`.
Placeholder values neither change the cache nor serialize during SSR.

### Keep infinite-query pages in one entry

`useInfiniteQuery()` stores every page in one entry. Put the cursor or page in
`pageParam`, not the key; keep filters in the key. The result exposes
`data.value.pages`, `data.value.pageParams`, `hasNextPage`, and page-loading
methods. A `null` next-page parameter means completion, and `maxPages` can evict
older pages.

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

## Query plugins

### Retry failed queries

`@pinia/colada-plugin-retry` configures retries globally or per query. `retry`
accepts `false`, a count, or a `(failureCount, error)` policy whose result is
`false`, immediate `true`, or a delay in milliseconds. Retries stop when the
query becomes inactive or disabled.

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

### Refetch on an interval

`@pinia/colada-plugin-auto-refetch` adds `autoRefetch`, whose value can be
`false`, `true`, a millisecond interval, or a function of state returning a
boolean or interval. `true` schedules from `staleTime`, so it requires a
nonzero stale time. Timers are client-only and are not scheduled during SSR.

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

### Delay the loading indicator

`@pinia/colada-plugin-delay` postpones a query's transition to
`asyncStatus: 'loading'`, avoiding flicker from quick background refreshes.
Set `delay` globally, then override it per query with a number or `false`.

```ts
app.use(PiniaColada, {
  plugins: [PiniaColadaDelay({ delay: 200 })],
})
```
