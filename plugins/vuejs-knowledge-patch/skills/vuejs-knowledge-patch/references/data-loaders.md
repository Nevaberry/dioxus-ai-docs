# Data Loaders (Vue Router Experimental)

## Overview

Data loaders streamline async data fetching with Vue Router by extracting loading logic **outside** the component setup. They run in a navigation guard, ensuring data is ready before the component renders.

**Features:** Parallel data fetching, deduplication, automatic loading state, error handling, SSR support, prefetching.

## Installation

Install `DataLoaderPlugin` **before** the router:

```ts
import { createApp } from 'vue'
import { routes } from 'vue-router/auto-routes'
import { createRouter, createWebHistory } from 'vue-router'
import { DataLoaderPlugin } from 'vue-router/experimental'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp({})
app.use(DataLoaderPlugin, { router })
app.use(router)
app.mount('#app')
```

## Basic Loader

`defineBasicLoader` always re-runs data fetching on navigation. Define and **export** the loader from a page component:

```vue
<!-- src/pages/users/[id].vue -->
<script lang="ts">
import { defineBasicLoader } from 'vue-router/experimental'
import { getUserById } from '../api'

export const useUserData = defineBasicLoader('/users/[id]', async (route) => {
  return getUserById(route.params.id)
})
</script>

<script setup lang="ts">
const {
  data: user,    // the data returned by the loader
  isLoading,     // boolean — is the loader fetching?
  error,         // Error | null
  reload,        // re-fetch without navigating
} = useUserData()
</script>

<template>
  <main>
    <p v-if="isLoading">Loading...</p>
    <template v-else-if="error">
      <p>{{ error.message }}</p>
      <button @click="reload()">Retry</button>
    </template>
    <template v-else>
      <p>{{ user }}</p>
    </template>
  </main>
</template>
```

The returned composable (`useUserData`) can be reused in **any** component — it shares the same data fetching instance.

## Colada Loader

`defineColadaLoader` uses `@pinia/colada` under the hood for caching, stale-while-revalidate, and deduplication:

```vue
<script lang="ts">
import { defineColadaLoader } from 'vue-router/experimental/pinia-colada'
import { getUserById } from '../api'

export const useUserData = defineColadaLoader('/users/[id]', {
  key: (route) => ['users', route.params.id],
  query: (route) => getUserById(route.params.id),
  staleTime: 5_000,
})
</script>

<script setup lang="ts">
const { data: user, isLoading, error, reload } = useUserData()
</script>
```

Requires `@pinia/colada` to be installed and configured.

## Parallel Data Fetching

Multiple loaders in the same page component run in parallel by default:

```vue
<script lang="ts">
import { defineBasicLoader } from 'vue-router/experimental'

export const useUserData = defineBasicLoader('/users/[id]', async (route) => {
  return fetchUser(route.params.id)
})

export const useUserPosts = defineBasicLoader('/users/[id]', async (route) => {
  return fetchUserPosts(route.params.id)
})
</script>

<script setup lang="ts">
const { data: user } = useUserData()
const { data: posts } = useUserPosts()
</script>
```

## Organizing Loaders

Loaders can be defined in separate files as long as they are **re-exported** from a page component:

```ts
// src/loaders/user.ts
import { defineBasicLoader } from 'vue-router/experimental'
import { getUserById } from '../api'

export const useUserData = defineBasicLoader('/users/[id]', async (route) => {
  return getUserById(route.params.id)
})
```

```vue
<!-- src/pages/users/[id].vue -->
<script lang="ts">
// Re-export so the router can discover it
export { useUserData } from '../../loaders/user'
</script>

<script setup lang="ts">
import { useUserData } from '../../loaders/user'
const { data: user } = useUserData()
</script>
```

## Key Concepts

- Loaders are automatically collected from page component exports during navigation
- Navigation is delayed until all loaders resolve (like `beforeRouteEnter`)
- Loaders deduplicate — calling the same loader composable in multiple components shares one fetch
- Loaders re-run when the route changes (even same path with different params)
- The `reload()` function re-fetches without triggering a navigation
