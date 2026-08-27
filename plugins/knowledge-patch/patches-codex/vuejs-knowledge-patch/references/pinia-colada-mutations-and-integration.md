# Pinia Colada Mutations and Integration

## Mutations

`useMutation()` accepts an optional key, a one-argument `mutation`, and
`onMutate`, `onSuccess`, `onError`, and `onSettled` hooks. The same hooks can be
set globally under `mutationOptions`. Awaited hook promises keep the mutation
in its loading state.

`mutate()` catches failures and returns nothing. `mutateAsync()` returns a
promise that rejects. `reset()` clears mutation state. The value returned by
`onMutate` is passed to later hooks as context. Give the mutation a key when
other components need to locate its entry through `useMutationCache()`.

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

1. Snapshot the cached value and replace it in `onMutate`.
2. Call `cancelQueries()` so outdated results are discarded without refetching.
3. Return both the old and optimistic values as rollback context.
4. On failure, roll back only if the cache still contains this mutation's optimistic value; this avoids overwriting newer work.
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

## Shared definitions

`defineQuery()` creates a once-instantiated, globally shared composable that
can combine a query with extra reactive state. Use `defineQueryOptions()` when
parameters should not be global, and use `defineMutation()` for reusable
mutations. Extra state returned by `defineQuery()` is not serialized for SSR.
A query placed in a long-lived Pinia store is effectively immortal.

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

`@pinia/colada-plugin-cache-persister` writes successful query results to
synchronous or asynchronous storage. Its default key is
`pinia-colada-cache`, and its default debounce is one second. Key or predicate
filters restrict what is stored. Persisted entries are still eligible for
garbage collection.

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

When storage is asynchronous, wait for `isCacheReady()` before mounting so the
application does not race cache restoration.

## SSR and Nuxt

The `@pinia/colada-nuxt` module runs queries through `onServerPrefetch`,
serializes the cache, and hydrates it. SSR queries therefore need no explicit
`await`. Pinia's Nuxt module is also required, and plugin options belong in the
root-level `colada.options.ts` file.

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/colada-nuxt'],
})

// colada.options.ts
import type { PiniaColadaOptions } from '@pinia/colada'

export default {} satisfies PiniaColadaOptions
```

In a Nuxt `defineQuery()`, import `useRoute` from `vue-router` to avoid extra
triggers. Custom SSR integrations should identify, serialize, and revive cache
state with `isQueryCache()`, `serializeQueryCache()`, and
`hydrateQueryCache()`.

## Component tests

Use a real `createPinia()` in component tests. `createTestingPinia()` stubs
internal cache actions that Pinia Colada requires. Mount with both plugins,
mock network access when possible, and flush promises after query or mutation
work.

```ts
mount(Component, {
  global: { plugins: [createPinia(), PiniaColada] },
})
await flushPromises()
```

## TanStack Vue Query migration

Map `queryKey` to `key`, `queryFn` to `query`, `mutationFn` to `mutation`, and
`fetchStatus` to `asyncStatus`. Pinia Colada's `asyncStatus` values are
`'idle'` and `'loading'`, and its default stale time is five seconds.

Use `refresh()` for a non-canceling refetch and `refetch(true)` when errors
should throw. Replace `select` with a Vue computed value. Interval refetching
and retry support come from separate plugins rather than query-core options.

## Breaking-change codemods

The package ships ast-grep migration rules:

- The 0.13-to-0.14 rule nests global query defaults under `queryOptions` and requires `app.use(PiniaColada, {})` when options are otherwise empty.
- The 0.21-to-1.0 rule replaces the removed two-argument `useQuery` and `useQueryState` forms with the one-object API.

Commit existing work first, then run the matching rule from the installed
package against the source directory:

```sh
pnpm --package=@ast-grep/cli dlx ast-grep scan \
  -r node_modules/@pinia/colada/codemods/rules/migration-0-21-to-1-0.yaml \
  -i src
```

## Plugin extension API

A custom `PiniaColadaPlugin` receives `queryCache`, `pinia`, and an effect
`scope`. Observe cache lifecycle operations with Pinia `$onAction()`. Mutation
support is opt-in through `useMutationCache(pinia)`.

Add reactive `entry.ext` fields only during the one-time `extend` action, and
create their effects inside `scope.run()`. Use `setEntryState` to observe every
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
