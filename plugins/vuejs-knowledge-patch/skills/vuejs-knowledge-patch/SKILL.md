---
name: vuejs-knowledge-patch
description: "Vue.js ecosystem changes since training cutoff — Vue 3.6 Vapor Mode, Pinia 3, Pinia Colada, Vue Router 5, Data Loaders. Load before working with Vue.js."
license: MIT
metadata:
  author: Nevaberry
  version: "3.6.0-beta"
---

# Vue.js Knowledge Patch (3.6 Beta + Ecosystem)

Supplementary knowledge for Vue.js ecosystem features released after Claude's training cutoff. Covers Vue 3.6 (beta), Pinia 3, Pinia Colada, Vue Router 5, and Data Loaders.

## Vue 3.6: Vapor Mode (Beta)

A new opt-in compilation mode that bypasses the virtual DOM entirely, generating direct DOM manipulation code. Delivers Solid.js/Svelte 5-level performance.

**Opt in** by adding the `vapor` attribute to the script setup tag:

```html
<script setup vapor>
import { ref } from 'vue'
const count = ref(0)
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

**Two app creation modes:**

```js
// 1. Pure Vapor app (no VDOM runtime, smallest bundle)
import { createVaporApp } from 'vue'
createVaporApp(App).mount('#app')

// 2. Mixed VDOM + Vapor (incremental adoption)
import { createApp, vaporInteropPlugin } from 'vue'
createApp(App)
  .use(vaporInteropPlugin)
  .mount('#app')
```

**Not supported in Vapor Mode:** Options API, `app.config.globalProperties`, `getCurrentInstance()` (returns `null`), `@vue:xxx` per-element lifecycle events.

**Custom directives** have a different interface in Vapor — `value` is a reactive getter, return a cleanup function:

```ts
const vHighlight: VaporDirective = (el, color) => {
  watchEffect(() => {
    ;(el as HTMLElement).style.backgroundColor = color?.() ?? 'yellow'
  })
  return () => { /* cleanup */ }
}
```

For full Vapor directive API, VDOM interop details, and feature matrix, see **`references/vapor-mode.md`**.

## Vue 3.6: Reactivity Refactor

Vue 3.6 refactors `@vue/reactivity` based on [alien-signals](https://github.com/stackblitz/alien-signals). Same API surface, significantly improved performance and memory usage. No code changes required.

## Vue Router 5

**Transition release** — merges `unplugin-vue-router` (file-based routing) into core. **No breaking changes** for Vue Router 4 users without `unplugin-vue-router`.

```bash
pnpm update vue-router@5
```

### Import Migration (from unplugin-vue-router)

| Old import | New import |
|---|---|
| `unplugin-vue-router/vite` | `vue-router/vite` |
| `unplugin-vue-router/data-loaders/basic` | `vue-router/experimental` |
| `unplugin-vue-router/data-loaders/pinia-colada` | `vue-router/experimental/pinia-colada` |
| `unplugin-vue-router` (utilities) | `vue-router/unplugin` |
| `unplugin-vue-router/volar/*` | `vue-router/volar/*` |

### New Exports Reference

| Export | Purpose |
|---|---|
| `vue-router` | Main API (unchanged) |
| `vue-router/vite` | Vite plugin for file-based routing |
| `vue-router/auto-routes` | Generated routes |
| `vue-router/unplugin` | Webpack/Rollup/esbuild + utilities |
| `vue-router/experimental` | Data loaders (`defineBasicLoader`, `DataLoaderPlugin`) |
| `vue-router/experimental/pinia-colada` | Pinia Colada loader (`defineColadaLoader`) |

**`next()` callback deprecated** in navigation guards — prepare for removal in Vue Router 6:

```ts
// Deprecated
router.beforeEach((to, from, next) => {
  if (isAuthenticated) next()
  else next('/login')
})

// Recommended (works since v4)
router.beforeEach((to) => {
  if (!isAuthenticated) return '/login'
})
```

New in v5.0.3: `reroute()` replaces `NavigationResult`, `_parent` folders for non-matchable layout routes.

For full migration checklist, see **`references/vue-router-5.md`**.

## Data Loaders (Vue Router Experimental)

Extract async data fetching **outside** the component setup, running it in a navigation guard. Data is ready before the component renders.

```ts
// Setup
import { DataLoaderPlugin } from 'vue-router/experimental'
app.use(DataLoaderPlugin, { router })
app.use(router)
```

```vue
<script lang="ts">
import { defineBasicLoader } from 'vue-router/experimental'
import { getUserById } from '../api'

export const useUserData = defineBasicLoader('/users/[id]', async (route) => {
  return getUserById(route.params.id)
})
</script>

<script setup lang="ts">
const { data: user, isLoading, error, reload } = useUserData()
</script>
```

Two loader implementations: `defineBasicLoader` (always re-runs) and `defineColadaLoader` (uses `@pinia/colada` for caching). For details, see **`references/data-loaders.md`**.

## Pinia 3

A "boring" major with **no new features** — drops deprecated APIs. For most users, no code changes required.

| Change | Migration |
|---|---|
| Vue 2 support dropped | Vue 3 only |
| TypeScript 5+ required | Update TS |
| `PiniaStorePlugin` removed | Use `PiniaPlugin` |
| `defineStore({ id: 'name' })` removed | Use `defineStore('name', { ... })` |
| Published as `type: module` | CJS dist files still provided |
| Devtools API upgraded to v7 | IIFE build no longer includes devtools |

## Pinia Colada (`@pinia/colada`)

Official data-fetching layer for Vue — comparable to TanStack Query but Vue/Pinia-native.

```ts
import { PiniaColada } from '@pinia/colada'
app.use(PiniaColada)
```

```ts
import { useQuery } from '@pinia/colada'

const { data, isLoading, error, status, refresh, refetch } = useQuery({
  key: ['todos'],
  query: () => fetch('/api/todos').then(r => r.json()),
  staleTime: 5_000,
  gcTime: 300_000,
})
```

```ts
import { useMutation } from '@pinia/colada'

const { mutate, isLoading } = useMutation({
  mutation: (todo) => fetch('/api/todos', {
    method: 'POST',
    body: JSON.stringify(todo),
  }),
  onSuccess: ({ queryCache }) => {
    queryCache.invalidateQueries({ key: ['todos'] })
  },
})
```

### Query Keys & Cache

Array-based hierarchical keys. Invalidating a prefix invalidates all descendants:

```ts
// These are related — invalidating ['todos'] also invalidates ['todos', 1]
useQuery({ key: ['todos'], ... })
useQuery({ key: ['todos', 1], ... })

// Reactive keys
const id = ref(1)
useQuery({ key: () => ['todos', id.value], query: () => fetchTodo(id.value) })
```

```ts
import { useQueryCache } from '@pinia/colada'
const queryCache = useQueryCache()

queryCache.invalidateQueries({ key: ['todos'] })        // prefix match
queryCache.invalidateQueries({ key: ['todos'], exact: true }) // exact match
queryCache.setQueryData(['todos'], newData)               // set directly
```

### Reusable Query Definitions

```ts
import { defineQueryOptions } from '@pinia/colada'

const todosQuery = defineQueryOptions({
  key: ['todos'],
  query: () => fetchTodos(),
})

// In components:
const { data } = useQuery(todosQuery)
// Outside components:
queryCache.fetch(todosQuery)
```

### Plugins

| Plugin | Package | Purpose |
|---|---|---|
| Auto Refetch | `@pinia/colada-plugin-auto-refetch` | Refetch on interval/stale time |
| Retry | `@pinia/colada-plugin-retry` | Retry failed queries |
| Cache Persister | `@pinia/colada-plugin-cache-persister` | Persist cache to storage |
| Delay | `@pinia/colada-plugin-delay` | Delay loading state (avoid flash) |
| Query Hooks | Built-in (`PiniaColadaQueryHooksPlugin`) | Global lifecycle hooks |

For `useInfiniteQuery`, optimistic updates, plugin configuration, and full API reference, see **`references/pinia-colada.md`**.

## Reference Files

- **`references/vapor-mode.md`** — Custom directives, VDOM interop, feature restrictions, supported APIs
- **`references/vue-router-5.md`** — Full migration checklist, `_parent` routes, `reroute()`, deprecations
- **`references/data-loaders.md`** — `defineBasicLoader`, `defineColadaLoader`, parallel loading, SSR
- **`references/pinia-colada.md`** — Full API: queries, mutations, infinite queries, cache management, plugins, optimistic updates
