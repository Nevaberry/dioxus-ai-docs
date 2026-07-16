# Pinia Colada Mutations and Integration

## Installation and global policy

Install `@pinia/colada` alongside Pinia. Register Pinia first and Pinia Colada
second. Global query and mutation policies live under `queryOptions` and
`mutationOptions`, and plugin factories execute in array order:

```ts
app.use(createPinia())
app.use(PiniaColada, {
  queryOptions: { staleTime: 5_000, gcTime: 300_000 },
  mutationOptions: {},
  plugins: [],
})
```

The query defaults are a 5-second `staleTime` and a 5-minute `gcTime`.

## Mutations and hooks

`useMutation()` accepts an optional key, a one-argument `mutation` function,
and `onMutate`, `onSuccess`, `onError`, and `onSettled` hooks. The same hooks
can be configured globally under `mutationOptions`. Awaited hook promises keep
the mutation in its loading state.

`mutate()` catches failures and returns nothing. `mutateAsync()` returns a
promise that rejects on failure. `reset()` clears mutation state. The value
returned from `onMutate` becomes the context argument for subsequent hooks.
Give a mutation a key when other components must locate its entry through
`useMutationCache()`.

```ts
const mutation = useMutation({
  mutation: patchTodo,
  onSettled: () => cache.invalidateQueries({ key: ['todos'] }),
})

mutation.mutate(todo)
await mutation.mutateAsync(todo)
```

## Optimistic cache updates

For cache-level optimistic updates:

1. Snapshot the existing data and write the optimistic replacement in
   `onMutate`.
2. Call `cancelQueries()` so outdated results are discarded, without starting
   another refetch.
3. Return rollback context from `onMutate`.
4. Before rolling back, confirm the cache still contains this mutation's
   optimistic value; otherwise a rollback could overwrite newer work.
5. Invalidate the affected queries after settlement.

```ts
useMutation({
  mutation: createTodo,
  onMutate(text) {
    const old = cache.getQueryData(['todos'])
    const optimistic = [
      ...(old ?? []),
      { id: crypto.randomUUID(), text },
    ]
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

## Shared definitions

`defineQuery()` builds a once-instantiated, globally shared composable that can
combine a query with additional reactive state. Use `defineQueryOptions()`
instead when callers need parameters that should not be global. Use
`defineMutation()` for reusable mutations.

Additional state returned by `defineQuery()` is not serialized during SSR. A
query placed in a long-lived Pinia store is effectively immortal, because that
store keeps the query active.

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

## Cache persistence

`@pinia/colada-plugin-cache-persister` stores successful query results in
synchronous or asynchronous storage. It uses the storage key
`pinia-colada-cache` and a 1-second debounce by default. Key or predicate
filters restrict which entries are persisted:

```ts
app.use(PiniaColada, {
  plugins: [
    PiniaColadaCachePersister({
      filter: { key: ['users'] },
    }),
  ],
})
```

Persistence does not exempt entries from garbage collection; persisted entries
still disappear when their cache lifetime ends. With asynchronous storage,
wait for restoration before mounting:

```ts
await isCacheReady()
app.mount('#app')
```

## Nuxt and custom SSR

`@pinia/colada-nuxt` runs queries through `onServerPrefetch`, serializes the
query cache, and hydrates it on the client. Queries do not need an explicit
`await` for SSR. The Pinia Nuxt module is also required.

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/colada-nuxt'],
})
```

Put plugin options in the root-level `colada.options.ts` file:

```ts
import type { PiniaColadaOptions } from '@pinia/colada'

export default {} satisfies PiniaColadaOptions
```

Custom SSR integrations should identify, serialize, and hydrate cache state
with `isQueryCache()`, `serializeQueryCache()`, and `hydrateQueryCache()`.
Inside a Nuxt `defineQuery()`, import `useRoute` from `vue-router` rather than a
Nuxt auto-import to avoid extra reactive triggers.

## Component testing

Use a real `createPinia()` in component tests. `createTestingPinia()` stubs the
internal cache actions on which Pinia Colada depends. Mount with both plugins,
mock the network where possible, and flush promises after query or mutation
work:

```ts
mount(Component, {
  global: { plugins: [createPinia(), PiniaColada] },
})
await flushPromises()
```

## Migration from TanStack Vue Query

Use these conceptual mappings:

| TanStack Vue Query | Pinia Colada |
| --- | --- |
| `queryKey` | `key` |
| `queryFn` | `query` |
| `mutationFn` | `mutation` |
| `fetchStatus` | `asyncStatus` (`'idle'` or `'loading'`) |

Pinia Colada's default stale time is 5 seconds. `refresh()` corresponds to a
non-canceling refetch; use `refetch(true)` when errors should throw. Replace
`select` with a Vue computed value. Interval refetching and retries are separate
plugins rather than core query options.

## Bundled migration codemods

The package ships ast-grep rules for breaking migrations:

- The 0.13-to-0.14 rule nests global query defaults under `queryOptions` and
  changes an empty registration to `app.use(PiniaColada, {})`.
- The 0.21-to-1.0 rule replaces the removed two-argument `useQuery` and
  `useQueryState` forms.

Commit current work, then run the matching rule from the installed package
against the source directory. For example:

```sh
pnpm --package=@ast-grep/cli dlx ast-grep scan \
  -r node_modules/@pinia/colada/codemods/rules/migration-0-21-to-1-0.yaml \
  -i src
```

## Plugin extension API

A custom `PiniaColadaPlugin` receives `queryCache`, `pinia`, and an effect
`scope`. Observe cache lifecycles through Pinia's `$onAction()`. Mutation
support is opt-in through `useMutationCache(pinia)`.

Only add reactive `entry.ext` fields during the one-time `extend` action, and
create their effects within `scope.run()`. `setEntryState` is the hook for every
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
