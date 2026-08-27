# Pinia Colada Queries

## Install and configure query defaults

Install `@pinia/colada` with Pinia. Register Pinia first and Pinia Colada
second. Global policies live under `queryOptions` and `mutationOptions`, and
plugin factories execute in array order. Query defaults are a 5-second
`staleTime` and a 5-minute `gcTime`.

```ts
app.use(createPinia())
app.use(PiniaColada, {
  queryOptions: { staleTime: 5_000, gcTime: 300_000 },
  mutationOptions: {},
  plugins: [],
})
```

## Query state and execution

`useQuery()` requires a cache `key` and a `query` function. Data state and
request activity are independent:

| Field | Values | Meaning |
| --- | --- | --- |
| `status` | `pending`, `success`, `error` | State of the data |
| `asyncStatus` | `idle`, `loading` | Whether a request is active |

`refresh()` deduplicates and honors freshness; `refetch()` forces a request.
Both normally resolve to the resulting state. Pass `true` to rethrow failures.

```ts
const { state, asyncStatus, refresh, refetch } = useQuery({
  key: ['todos'],
  query: fetchTodos,
})

await refresh()
await refetch(true)
```

### Pause queries with `enabled`

The reactive `enabled` option pauses execution when required inputs are absent
and can suppress server-side requests. A long-lived query continues watching
its key, so disable it when its route inputs are unavailable.

```ts
useQuery({
  key: () => ['decks', route.params.deckId],
  query: () => fetchDeck(route.params.deckId),
  enabled: () => 'deckId' in route.params && !import.meta.env.SSR,
})
```

## Design serializable hierarchical keys

Keys are serializable arrays. Put every reactive input used by `query` in a
reactive key getter. Array order matters, object property order does not, and
object fields whose value is `undefined` are stripped. Cache filters partially
match hierarchical keys unless `exact: true` is set.

```ts
useQuery({
  key: () => ['products', id.value, { comments: withComments.value }],
  query: () => getProduct(id.value, withComments.value),
})

useQueryCache().invalidateQueries({ key: ['products', id.value] })
```

### Share typed option factories

`defineQueryOptions()` accepts a static object or a parameterized factory and
tags its key with the query result type. Use `as const` key factories to retain
one hierarchy across queries and cache operations.

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

## Operate on the cache

`useQueryCache()` is available in injectable contexts. It provides typed
`getQueryData()`, `setQueryData()`, `ensure()`, refresh, and invalidation
operations.

`invalidateQueries()` marks every match stale but refetches active entries by
default. Pass `'all'` as its second argument to refetch inactive matches too.
Use `ensure()` before seeding or refreshing when the entry must retain its
query options and freshness behavior.

```ts
const cache = useQueryCache()
const options = productById('24')

await cache.refresh(cache.ensure(options))
await cache.invalidateQueries({ key: PRODUCT_KEYS.root }, 'all')
```

## Handle callbacks, metadata, and errors

Queries intentionally have no local `onSuccess`, `onError`, or `onSettled`
options. Watch query state for component-local effects. For global fetch hooks,
install `PiniaColadaQueryHooksPlugin`.

Query `meta` is resolved once when an entry is created. Plugins and hooks can
read it, and it must be serializable for SSR.

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

A failed refetch preserves previous data alongside the new error. Native
`fetch()` treats non-2xx responses as resolved values, so the query function
must explicitly throw to enter the error state.

Errors default to `Error`. Change that default only globally through
`TypesConfig.defaultError`; the discriminated `state.status` union narrows it.
The same augmentation can define query metadata.

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

### Regular pages and placeholder data

Put a reactive page value in the key so every page receives an independent
cache entry. `placeholderData` can keep earlier content visible with a
successful data status while the next page reports `asyncStatus: 'loading'`.
Placeholder values neither modify the cache nor serialize during SSR.

### Infinite queries

`useInfiniteQuery()` stores all pages in one entry. Put filters in the key,
but put the page number or cursor in `pageParam`. The result exposes
`data.value.pages`, `data.value.pageParams`, `hasNextPage`, and page-loading
methods. A `null` next-page parameter means completion; `maxPages` can evict
old pages.

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

`@pinia/colada-plugin-retry` adds global or per-query retry behavior. `retry`
accepts `false`, a count, or a `(failureCount, error)` policy. A policy returns
`false` to stop, `true` to retry immediately, or a delay in milliseconds.
Retries stop when a query becomes inactive or disabled.

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

`@pinia/colada-plugin-auto-refetch` adds `autoRefetch`, whose value may be
`false`, `true`, a millisecond interval, or a state callback returning a
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

`@pinia/colada-plugin-delay` postpones transition to
`asyncStatus: 'loading'`, which avoids flicker for fast background refreshes.
Configure `delay` globally and override it with a number or `false` per query.

```ts
app.use(PiniaColada, {
  plugins: [PiniaColadaDelay({ delay: 200 })],
})
```
