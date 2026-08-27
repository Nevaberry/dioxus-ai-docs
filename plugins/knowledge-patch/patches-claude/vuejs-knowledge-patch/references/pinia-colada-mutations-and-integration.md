# Pinia Colada Mutations and Integration

## Mutation semantics

`useMutation()` accepts an optional key, a one-argument `mutation`, and
`onMutate`, `onSuccess`, `onError`, and `onSettled` hooks. The same hooks may
be configured globally under `mutationOptions`. Awaited hook promises keep the
mutation in its loading state.

`mutate()` catches failures and returns nothing. `mutateAsync()` returns a
promise that rejects. `reset()` clears mutation state. The value returned by
`onMutate` becomes the context passed to later hooks. Add a mutation key when
other components need to locate the entry through `useMutationCache()`.

```ts
const mutation = useMutation({
  mutation: patchTodo,
  onSettled: () => cache.invalidateQueries({ key: ['todos'] }),
})

mutation.mutate(todo)
await mutation.mutateAsync(todo)
```

## Optimistic updates

For a cache-level optimistic update:

1. Snapshot and replace cached data in `onMutate`.
2. Call `cancelQueries()` so an obsolete response is discarded without a refetch.
3. Return both old and optimistic values as rollback context.
4. Before rollback, verify that the cache still holds this mutation's value.
5. Invalidate the affected query in `onSettled`.

```ts
useMutation({
  mutation: createTodo,
  onMutate(text) {
    const old = cache.getQueryData(['todos'])
    const optimistic = [...(old ?? []), { id: crypto.randomUUID(), text }]
    cache.setQueryData(['todos'], optimistic)
    cache.cancelQueries({ key: ['todos'] })
    return { old, optimistic }
  },
  onError(_error, _text, { old, optimistic }) {
    if (cache.getQueryData(['todos']) === optimistic) {
      cache.setQueryData(['todos'], old)
    }
  },
  onSettled: () => cache.invalidateQueries({ key: ['todos'] }),
})
```

The identity check prevents an older failing mutation from overwriting newer
work.

## Shared definitions and query lifetime

`defineQuery()` creates a once-instantiated globally shared composable and can
combine a query with extra reactive state. Use `defineQueryOptions()` instead
when parameters must not become global. Use `defineMutation()` for reusable
mutations.

Extra state returned by `defineQuery()` is not serialized for SSR. A query
placed in a long-lived Pinia store is effectively immortal.

```ts
export const useFilteredTodos = defineQuery(() => {
  const search = ref('')
  return {
    search,
    ...useQuery({
      key: () => ['todos', { search: search.value }],
      query: () => fetchTodos(search.value),
    }),
  }
})
```

## Persist the query cache

`@pinia/colada-plugin-cache-persister` stores successful query results in
synchronous or asynchronous storage. Its default storage key is
`pinia-colada-cache`, and its default write debounce is one second. Limit
stored entries with key or predicate filters.

Persisted entries can still be removed by garbage collection. With async
storage, wait for `isCacheReady()` before mounting the application.

```ts
app.use(PiniaColada, {
  plugins: [
    PiniaColadaCachePersister({
      filter: { key: ['users'] },
    }),
  ],
})

await isCacheReady()
app.mount('#app')
```

## SSR and Nuxt

The `@pinia/colada-nuxt` module runs queries with `onServerPrefetch`, serializes
the cache, and hydrates it. SSR queries need no explicit `await`. Pinia's Nuxt
module is also required, and plugin options belong in root-level
`colada.options.ts`.

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/colada-nuxt'],
})

// colada.options.ts
import type { PiniaColadaOptions } from '@pinia/colada'

export default {} satisfies PiniaColadaOptions
```

Within a Nuxt `defineQuery()`, import `useRoute` from `vue-router` to avoid
extra triggers.

For custom SSR, detect, serialize, and hydrate the cache with
`isQueryCache()`, `serializeQueryCache()`, and `hydrateQueryCache()`.

## Component testing

Use a real `createPinia()` in component tests. `createTestingPinia()` stubs
internal cache actions required by Pinia Colada. Mount both plugins, mock the
network where possible, and flush promises after query or mutation work.

```ts
mount(Component, {
  global: { plugins: [createPinia(), PiniaColada] },
})
await flushPromises()
```

## Migrations

### Move from TanStack Vue Query

The main mappings are:

| TanStack Vue Query | Pinia Colada |
| --- | --- |
| `queryKey` | `key` |
| `queryFn` | `query` |
| `mutationFn` | `mutation` |
| `fetchStatus` | `asyncStatus` (`idle` or `loading`) |

Pinia Colada's default stale time is 5 seconds. `refresh()` corresponds to a
non-canceling refetch, while `refetch(true)` enables throwing. Replace `select`
with a Vue computed value. Interval refetching and retry behavior are separate
plugins.

### Run bundled breaking-change codemods

The package supplies ast-grep migration rules. The 0.13-to-0.14 rule nests
global query defaults under `queryOptions` and requires
`app.use(PiniaColada, {})` when options are empty. The 0.21-to-1.0 rule replaces
removed two-argument `useQuery` and `useQueryState` forms.

Commit current work first, then run the appropriate installed rule against the
source directory:

```sh
pnpm --package=@ast-grep/cli dlx ast-grep scan \
  -r node_modules/@pinia/colada/codemods/rules/migration-0-21-to-1-0.yaml \
  -i src
```

## Custom plugin extension API

A `PiniaColadaPlugin` receives `queryCache`, `pinia`, and an effect `scope`.
Observe cache lifecycles through Pinia `$onAction()`. Mutation support is
opt-in through `useMutationCache(pinia)`.

Add reactive `entry.ext` fields only during the one-time `extend` action, and
create their effects within `scope.run()`. Use `setEntryState` to observe every
cache-state change.

```ts
import type { PiniaColadaPlugin } from '@pinia/colada'
import { shallowRef, type ShallowRef } from 'vue'

export const FeaturePlugin: PiniaColadaPlugin = ({ queryCache, scope }) => {
  queryCache.$onAction(({ name, args }) => {
    if (name === 'extend') {
      const [entry] = args
      scope.run(() => {
        entry.ext.updatedAt = shallowRef(0)
      })
    }
  })
}

declare module '@pinia/colada' {
  interface UseQueryEntryExtensions<TData, TError> {
    updatedAt: ShallowRef<number>
  }
}
```
