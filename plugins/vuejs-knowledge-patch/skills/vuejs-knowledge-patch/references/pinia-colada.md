# Pinia Colada (`@pinia/colada`)

## Overview

Official data-fetching layer for Vue, comparable to TanStack Query but designed specifically for Vue/Pinia. Provides queries, mutations, infinite queries, caching, and cache invalidation.

## Installation

```bash
npm i @pinia/colada
```

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { PiniaColada } from '@pinia/colada'

const app = createApp(App)
app.use(createPinia())
app.use(PiniaColada, {
  // global options (optional)
  plugins: [],
})
```

## Queries (`useQuery`)

```ts
import { useQuery } from '@pinia/colada'

const {
  data,         // Ref<T | undefined> — the resolved data
  isLoading,    // boolean — first load (no data yet)
  status,       // 'pending' | 'error' | 'success'
  asyncStatus,  // 'idle' | 'loading' — tracks background refetches too
  error,        // Ref<Error | null>
  refresh,      // () => Promise — refetch if stale
  refetch,      // () => Promise — always refetch
} = useQuery({
  key: ['todos'],
  query: () => fetch('/api/todos').then(r => r.json()),
  staleTime: 5_000,    // ms before data is considered stale (default: 0)
  gcTime: 300_000,     // ms before unused cache entry is garbage collected (default: 300_000)
})
```

### Query Keys

Array-based hierarchical keys. Queries with a key that starts with another key's prefix are considered related for invalidation:

```ts
// These are related — invalidating ['todos'] also invalidates ['todos', 1]
useQuery({ key: ['todos'], ... })
useQuery({ key: ['todos', 1], ... })

// Reactive keys
const todoId = ref(1)
useQuery({
  key: () => ['todos', todoId.value],
  query: () => fetchTodo(todoId.value),
})
```

### Reusable Query Definitions

```ts
import { defineQueryOptions } from '@pinia/colada'

const todosQueryOptions = defineQueryOptions({
  key: ['todos'],
  query: () => fetchTodos(),
})

// In components:
const { data } = useQuery(todosQueryOptions)

// Outside components (e.g., in loaders or actions):
queryCache.fetch(todosQueryOptions)
```

## Mutations (`useMutation`)

```ts
import { useMutation, useQueryCache } from '@pinia/colada'

const queryCache = useQueryCache()

const { mutate, isLoading, error, data, reset } = useMutation({
  mutation: (newTodo: Todo) =>
    fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify(newTodo),
    }).then(r => r.json()),

  onSuccess: () => {
    queryCache.invalidateQueries({ key: ['todos'] })
  },
})

// Usage
mutate({ title: 'Buy milk', done: false })
```

### Optimistic Updates

```ts
const { mutate } = useMutation({
  mutation: updateTodo,

  onMutate: async (updatedTodo) => {
    // Cancel outgoing refetches
    await queryCache.cancelQueries({ key: ['todos'] })

    // Snapshot previous value
    const previousTodos = queryCache.getQueryData(['todos'])

    // Optimistically update
    queryCache.setQueryData(['todos'], (old) =>
      old?.map(t => t.id === updatedTodo.id ? updatedTodo : t)
    )

    return { previousTodos }
  },

  onError: ({ context }) => {
    // Rollback on error
    queryCache.setQueryData(['todos'], context.previousTodos)
  },

  onSettled: () => {
    // Always refetch after mutation settles
    queryCache.invalidateQueries({ key: ['todos'] })
  },
})
```

## Infinite Queries (`useInfiniteQuery`)

Loads and merges multiple pages into a single cache entry:

```ts
import { useInfiniteQuery } from '@pinia/colada'

const {
  data,       // merged array of all pages
  fetchNext,  // load next page
  fetchPrev,  // load previous page
  hasNext,
  hasPrev,
  isLoading,
} = useInfiniteQuery({
  key: ['todos-list'],
  query: ({ pageParam }) =>
    fetch(`/api/todos?page=${pageParam}`).then(r => r.json()),
  initialPageParam: 1,
  getNextPageParam: (lastPage) => lastPage.nextPage ?? undefined,
})
```

## Cache Management

```ts
import { useQueryCache } from '@pinia/colada'

const queryCache = useQueryCache()

// Invalidate (triggers refetch for active queries)
queryCache.invalidateQueries({ key: ['todos'] })
queryCache.invalidateQueries({ key: ['todos'], exact: true })

// Set data directly
queryCache.setQueryData(['todos'], newTodos)

// Read cached data
const cached = queryCache.getQueryData(['todos'])

// Cancel outgoing queries
await queryCache.cancelQueries({ key: ['todos'] })

// Fetch (use outside of components)
const data = await queryCache.fetch({ key: ['todos'], query: fetchTodos })
```

## Official Plugins

### Auto Refetch

```bash
npm i @pinia/colada-plugin-auto-refetch
```

```ts
import { PiniaColadaAutoRefetch } from '@pinia/colada-plugin-auto-refetch'

app.use(PiniaColada, {
  plugins: [
    PiniaColadaAutoRefetch({ autoRefetch: true }),
  ],
})
```

Per-query: `autoRefetch: true` (uses `staleTime`), `autoRefetch: 5000` (fixed ms), or `autoRefetch: (state) => boolean | number`.

### Retry

```bash
npm i @pinia/colada-plugin-retry
```

```ts
import { PiniaColadaRetry } from '@pinia/colada-plugin-retry'

app.use(PiniaColada, {
  plugins: [
    PiniaColadaRetry({ retry: 3, delay: 1000 }),
  ],
})
```

### Cache Persister

```bash
npm i @pinia/colada-plugin-cache-persister
```

Persists query cache to storage (localStorage, sessionStorage, etc.) so users don't start with empty state on reload. Increase `gcTime` to keep data longer.

### Delay

```bash
npm i @pinia/colada-plugin-delay
```

Delays `isLoading` becoming `true` to avoid flash-of-loading-state for fast queries.

### Query Hooks Plugin (Built-in)

```ts
import { PiniaColadaQueryHooksPlugin } from '@pinia/colada'

app.use(PiniaColada, {
  plugins: [
    PiniaColadaQueryHooksPlugin({
      onSuccess: ({ data }) => { /* global success handler */ },
      onError: ({ error }) => { /* global error handler */ },
    }),
  ],
})
```

## Nuxt Integration

Dedicated Nuxt module available for seamless SSR with automatic payload serialization and revival.

## Differences from TanStack Vue Query

- Query functions receive **no context object** — use closures for dependencies
- Keys are always arrays (no string keys)
- Cache operations use `queryCache` from `useQueryCache()` (not `queryClient`)
- `isLoading` means first load (no data); `asyncStatus === 'loading'` tracks background refetches
- Migration codemods are available
