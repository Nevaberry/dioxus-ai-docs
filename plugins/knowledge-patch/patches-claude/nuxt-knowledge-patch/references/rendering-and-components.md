# Rendering and components

## Server-only and client-only pages

Pages ending in `.client.vue` skip SSR for the entire page. Pages ending in `.server.vue` emit server-rendered HTML while still supporting client navigation and prefetch (3.11.0).

Experimental multi-app support can run multiple application instances in parallel behind `experimental.multiApp` (3.12.0). Treat it as unfinished compatibility-sensitive behavior.

## Lazy hydration

Auto-imported lazy components support visibility, idle, interaction, media-query, and delay strategies through `hydrate-on-visible`, `hydrate-on-idle`, `hydrate-on-interaction`, `hydrate-on-media-query`, and `hydrate-after`. The `hydrated` event signals completion (3.16.0).

```vue
<LazyChart hydrate-on-visible @hydrated="onHydrated" />
<LazyMenu hydrate-on-interaction="mouseover" />
<LazyFooter :hydrate-after="2000" />
```

Use `defineLazyHydrationComponent` for explicitly imported components (3.18.0):

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

Lazy-hydration macro transforms also work when Nuxt auto-imports are disabled or customized (3.19.0). Use `onPrehydrate` for browser work that must run during the hydration cycle immediately before Nuxt hydrates the page (3.12.0).

## Server islands and server components

With `componentIslands.selectiveClient: 'deep'`, `nuxt-client` can appear anywhere inside a server-component tree. Server components emit `@error` on loading failure, and Nuxt auto-enables server-only components when the project or a layer contains one; these APIs began as experimental (3.11.0). Their `#fallback` slot is typed (3.12.0).

Server islands can update document head state while rendering, including SEO metadata (3.13.0). They can access shared state and the current route, nest normally, and run application plugins (4.0-platform-guide).

Server components used by crawled pages are prerendered by default and can work on static hosting. This does not apply when a component first appears only after client navigation or requires runtime-changing props. Payload extraction allows eligible island payloads to be prefetched for navigation (4.0-platform-guide).

Island props are serialized into the island request query string. They must be non-secret, serializable, small, and object-shaped; Nitro rejects non-object props (release-catalogs, 4.5.2).

At the 4.0-platform-guide snapshot, links inside server components required a client wrapper for SPA navigation. Since 4.5.2, island links navigate client-side directly. That patch also preserves payload keys containing underscores and supports Options API island components rendered with `v-for`.

Page-island rendering runs Nuxt middleware rather than bypassing it (3.21.0).

## Head and runtime composables

Import head composables through Nuxt auto-imports or `#app/composables/head`; direct `@unhead/vue` imports can lose async context (3.16.0). `useHead` accepts a `head` option to target a specific head instance (3.19.0).

```ts
useHead({ title: 'Preview' }, { head })
```

`useResponseHeader` works with a response header from application code. `useRuntimeHook` registers a runtime hook through a composable API (3.14.0).

## Built-in components

`<NuxtTime>` formats dates without server/client hydration mismatches (3.17.0). Relative mode also accepts `numeric` and `relativeStyle` (4.2.0).

```vue
<NuxtTime :datetime="date" relative numeric="auto" relative-style="short" />
```

`<ClientOnly>` and `<DevOnly>` expose typed slots, and `<NuxtTime>` exports its prop types for wrappers (3.18.0). Auto-imported components can be passed directly to Vue's `h()` in render functions (4.2.0).

## Error boundaries and error pages

`<NuxtErrorBoundary>` exposes `error` and `clearError` through its component instance and typed error slot (3.17.0):

```vue
<NuxtErrorBoundary>
  <template #error="{ error, clearError }">
    <p>{{ error.message }}</p>
    <button @click="clearError">Try again</button>
  </template>
  <MyComponent />
</NuxtErrorBoundary>
```

In development, a custom application error page appears with a toggleable technical overlay, allowing the rendered result and stack trace to be inspected together (4.2.0). The overlay can be moved to a corner or minimized, and its state persists across reloads (4.3.0).

`NuxtError` extends the standard `Error` type. Prefer `status` and `statusText` over deprecated `statusCode` and `statusMessage` (3.21.0, 4.3.0).

## Cleanup and component naming

Vue's `onWatcherCleanup` is auto-imported, allowing timers and other watcher-owned resources to be released without an explicit Vue import (3.18.0).

Under compatibility version 4, nested component paths contribute to runtime names: `components/App/Header.vue` becomes `AppHeader`. Review name-based `<KeepAlive>` filters and diagnostics when enabling those defaults (3.14.0).
