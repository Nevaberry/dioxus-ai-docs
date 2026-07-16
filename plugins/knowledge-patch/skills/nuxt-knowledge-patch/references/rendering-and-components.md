# Rendering and components

Use this reference for server/client boundaries, server components and islands, delayed hydration, head state, runtime hooks, error handling, and built-in components.

## Contents

- [Server-only, client-only, and multi-app rendering](#server-only-client-only-and-multi-app-rendering)
- [Server components and islands](#server-components-and-islands)
- [Hydration control](#hydration-control)
- [Head and response APIs](#head-and-response-apis)
- [Built-in components and error handling](#built-in-components-and-error-handling)
- [Component authoring and render functions](#component-authoring-and-render-functions)

## Server-only, client-only, and multi-app rendering

### Use page suffixes for whole-page rendering modes (3.11.0)

A page ending in `.client.vue` skips SSR for the entire page. A page ending in `.server.vue` renders HTML on the server while still supporting client navigation and link prefetching.

### Enable deep selective client islands only when needed (3.11.0)

Set `componentIslands.selectiveClient` to `'deep'` to allow `nuxt-client` anywhere inside a server-component tree. Server components emit `@error` on load failure. Nuxt automatically enables server-only components when the project or a layer contains a server-only component or page; these APIs remain experimental.

```ts
export default defineNuxtConfig({
  experimental: {
    componentIslands: { selectiveClient: 'deep' },
  },
})
```

### Type the server-component fallback slot (3.12.0)

The `#fallback` slot exposed by server components has generated types; avoid replacing it with an untyped wrapper API.

### Evaluate multi-app support as experimental (3.12.0)

Use the unfinished `experimental.multiApp` support only for deliberate testing of multiple application instances running in parallel at runtime.

```ts
export default defineNuxtConfig({
  experimental: { multiApp: true },
})
```

## Server components and islands

### Add document head entries from server islands (3.13.0)

Server component islands can update the document head during rendering, including SEO metadata.

### Prerender compatible server components for static hosting (4.0-platform-guide)

Nuxt prerenders server components used by crawled pages by default. They work on fully static hosting when they are not first discovered only in the browser and their props do not change at runtime. With payload extraction enabled, their payloads can be prefetched for client navigation.

### Use server-island runtime context carefully (4.0-platform-guide)

Server components can read shared state and the current route, nest like ordinary components, and run all application plugins during rendering. At the platform guide's snapshot, a `<NuxtLink>` rendered inside a server component does not by itself provide interactive client routing; handle the click in a client parent with `navigateTo` when SPA navigation is required.

### Keep server-island props out of secrets (release-catalogs)

Props passed to server components and islands are serialized into the island request query string. Keep them URL-serializable, within practical URL size limits, and free of secrets.

## Hydration control

### Run browser work immediately before hydration (3.12.0)

Use `onPrehydrate` for browser code that must execute during the hydration cycle before Nuxt hydrates the page.

```ts
onPrehydrate(() => {
  // runs before hydration
})
```

### Delay auto-imported component hydration (3.16.0)

Lazy components support Vue's visibility, idle, interaction, media-query, and timed hydration strategies. Listen for `hydrated` when completion matters.

```vue
<LazyChart hydrate-on-visible @hydrated="onHydrated" />
<LazyMenu hydrate-on-interaction="mouseover" />
<LazyFooter :hydrate-after="2000" />
```

Use `hydrate-on-visible`, `hydrate-on-idle`, `hydrate-on-interaction`, `hydrate-on-media-query`, or `hydrate-after` according to the trigger.

### Apply lazy hydration to explicit imports (3.18.0)

Use `defineLazyHydrationComponent` when the component is imported explicitly rather than discovered as an auto-imported `Lazy` component.

```vue
<script setup lang="ts">
const LazyHydrationChart = defineLazyHydrationComponent(
  'visible',
  () => import('./components/Chart.vue'),
)
</script>

<template>
  <LazyHydrationChart :hydrate-on-visible="{ rootMargin: '100px' }" />
</template>
```

### Use lazy-hydration macros without auto-imports (3.19.0)

Macro transformation no longer depends on Nuxt auto-imports being enabled. Projects that disable or customize auto-imports can still use the lazy-hydration macros.

## Head and response APIs

### Import head composables through Nuxt (3.16.0)

Nuxt uses Unhead v2 with a Nuxt 3 compatibility build. Import head composables through Nuxt auto-imports or `#app/composables/head`; a direct `@unhead/vue` import can lose Nuxt async context.

```ts
import { useHead } from '#app/composables/head'
```

### Target a specific head instance (3.19.0)

`useHead` honors its `head` option:

```ts
useHead({ title: 'Preview' }, { head })
```

### Use response-header and runtime-hook composables (3.14.0)

Use `useResponseHeader` to work with an outgoing response header and `useRuntimeHook` to register a Nuxt runtime hook through composable APIs.

## Built-in components and error handling

### Format time without hydration mismatches (3.17.0)

`<NuxtTime>` formats dates consistently between server and client.

```vue
<NuxtTime :datetime="Date.now()" />
```

### Control relative-time formatting (4.2.0)

In relative mode, `<NuxtTime>` exposes `numeric` and `relativeStyle`.

```vue
<NuxtTime :datetime="date" relative numeric="auto" relative-style="short" />
```

### Reuse stronger built-in component types (3.18.0)

`<ClientOnly>` and `<DevOnly>` expose typed slots, and `<NuxtTime>` exports its prop types for wrapper components and extensions.

### Inspect and clear error boundaries through public state (3.17.0)

`<NuxtErrorBoundary>` exposes `error` and `clearError` on its instance and typed error slot. Templates and `useTemplateRef` can inspect and reset a captured error.

```vue
<NuxtErrorBoundary>
  <template #error="{ error, clearError }">
    <p>{{ error.message }}</p>
    <button @click="clearError">Try again</button>
  </template>
  <MyComponent />
</NuxtErrorBoundary>
```

## Component authoring and render functions

### Auto-import watcher cleanup (3.18.0)

Nuxt auto-imports Vue's `onWatcherCleanup`, allowing watcher-owned resources to be released without an explicit Vue import.

```ts
watch(source, () => {
  const timer = setInterval(runTask, 1000)
  onWatcherCleanup(() => clearInterval(timer))
})
```

### Use auto-imported components with `h()` (4.2.0)

Auto-imported components can be passed directly to Vue's `h()` function without manually resolving the component first.
