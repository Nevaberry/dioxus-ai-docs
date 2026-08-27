# Rendering and components

Work with hydration, islands, head state, errors, transitions, and built-in components.

## Built-ins, rendering, and transitions

### Auto-imported components in render functions (since 4.2.0)

Auto-imported components can now be passed directly as arguments to Vue's `h()` function.

### Experimental multi-app support (since 3.12.0)

Nuxt can run multiple app instances in parallel at runtime, with the unfinished support gated behind `experimental.multiApp`.

```ts
export default defineNuxtConfig({
  experimental: { multiApp: true },
})
```

### Loading and view-transition controls (since 3.11.0)

The loading indicator supports custom hide timings and a forced `finish()`. With experimental view transitions enabled, the new `page:view-transition:start` hook runs when a View Transition begins.

### Loading-indicator component delays (since 3.17.0)

`<NuxtLoadingIndicator>` now accepts `hideDelay` and `resetDelay` directly as props, controlling when the bar disappears and when its state resets.

```vue
<NuxtLoadingIndicator :hide-delay="500" :reset-delay="300" />
```

### Normalized page component names (since 4.4.0)

The experimental `normalizeComponentNames` option makes page component names match their route names for consistent debugging and DevTools output.

```ts
export default defineNuxtConfig({ experimental: { normalizeComponentNames: true } })
```

### Path-prefixed component names under v4 compatibility (since 3.14.0)

With `compatibilityVersion: 4`, a component such as `components/App/Header.vue` now has the runtime name `<AppHeader>` instead of `<Header>`. This can affect name-based `<KeepAlive>` configuration.

### Per-page view transitions (since 3.10.0)

After enabling experimental view transitions, `definePageMeta` can opt individual pages in or out. Transitions are skipped for `prefers-reduced-motion: reduce` by default; `viewTransition: 'always'` overrides that safeguard.

```ts
export default defineNuxtConfig({
  experimental: { viewTransition: true },
})

definePageMeta({ viewTransition: false })
```

### Relative-time formatting controls (since 4.2.0)

In relative mode, `<NuxtTime>` now exposes `numeric` and `relativeStyle` controls.

```vue
<NuxtTime :datetime="date" relative numeric="auto" relative-style="short" />
```

### SSR-safe time display (since 3.17.0)

The new built-in `<NuxtTime>` component formats dates without producing server/client hydration mismatches.

```vue
<NuxtTime :datetime="Date.now()" />
```

### Stronger built-in component types (since 3.18.0)

`<ClientOnly>` and `<DevOnly>` now expose typed slots, and `<NuxtTime>` exports its prop types for reuse by wrappers and extensions.

### Typed server-component fallback slots (since 3.12.0)

The `#fallback` slot exposed by server components is now typed.

### View-transition types (since 4.4.0)

Experimental view transitions now support transition types, allowing different CSS transition styles for navigation categories such as forward, backward, tab, or page navigation.

## Head state, errors, and diagnostics

### Async-context-safe head imports (since 3.16.0)

Nuxt 3.16 uses Unhead v2 with a compatibility build for Nuxt 3. Import head composables through Nuxt's auto-imports or `#app/composables/head`; direct imports from `@unhead/vue` can lose async context.

```ts
import { useHead } from '#app/composables/head'
```

### Custom and technical development error pages together (since 4.2.0)

In development, an application error now renders the custom error page together with a toggleable technical overlay, so the user-facing result and stack trace can be inspected at once.

### Error-boundary public state (since 3.17.0)

`<NuxtErrorBoundary>` now exposes `error` and `clearError` on its component instance and in the typed error slot, so callers can inspect and reset a captured error through either templates or `useTemplateRef`.

```vue
<NuxtErrorBoundary>
  <template #error="{ error, clearError }">
    <p>{{ error.message }}</p>
    <button @click="clearError">Try again</button>
  </template>
  <MyComponent />
</NuxtErrorBoundary>
```

### Explicit head targets in `useHead` (since 3.19.0)

`useHead` now honors the `head` option, allowing a call to target a specific head instance.

```ts
useHead({ title: 'Preview' }, { head })
```

### Movable development error overlay (since 4.3.0)

The development error overlay can now be dragged to a screen corner or minimized to a pill. Its position and minimized state persist across page reloads.

### New anti-pattern diagnostics (since 3.10.0)

Nuxt now throws when `setInterval` is used on the server. In development it also warns when data-fetching composables run outside a plugin or setup context, or when router integration is enabled without `<NuxtPage>`; a bare `<RouterView>` is not a supported replacement.

### Response-header and runtime-hook composables (since 3.14.0)

The new `useResponseHeader` and `useRuntimeHook` composables let application code work with a response header and register a runtime hook through composable APIs.

### Standard `Error` typing for `NuxtError` (since 4.3.0)

`NuxtError` now extends the standard `Error` type, allowing it to be used by generic error-handling code without losing standard error properties.

### Stricter usage diagnostics (since 3.17.0)

Development now warns about rootless server components, use of the reserved `runtimeConfig.app` namespace, and overrides of core auto-import presets. More than one `definePageMeta` call in a file is now an error.

## Hydration, islands, and server components

### Deep selective client islands (since 3.11.0)

With `componentIslands.selectiveClient` set to `'deep'`, `nuxt-client` can be used anywhere inside a server-component tree. Server components also emit `@error` when loading fails, and Nuxt automatically enables server-only components when a project or layer contains a server-only component or page; these APIs remain experimental.

```ts
export default defineNuxtConfig({
  experimental: {
    componentIslands: { selectiveClient: 'deep' },
  },
})
```

### Delayed component hydration (since 3.16.0)

Lazy components now support Vue's visible, idle, interaction, media-query, and timed hydration strategies through `hydrate-on-visible`, `hydrate-on-idle`, `hydrate-on-interaction`, `hydrate-on-media-query`, and `hydrate-after`. The `hydrated` event signals completion.

```vue
<LazyChart hydrate-on-visible @hydrated="onHydrated" />
<LazyMenu hydrate-on-interaction="mouseover" />
<LazyFooter :hydrate-after="2000" />
```

### Head metadata from server islands (since 3.13.0)

Server component islands can now manipulate the document head while rendering, including adding SEO metadata.

### Island payload keys containing underscores (since 4.5.2)

Island payload serialization now handles components whose keys contain underscores, preserving those keys across the server-to-client payload boundary.

### Lazy hydration for explicit component imports (since 3.18.0)

The `defineLazyHydrationComponent` macro applies Nuxt's delayed-hydration strategies to explicitly imported components, rather than only auto-imported `Lazy` components.

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

### Lazy-hydration macros without auto-imports (since 3.19.0)

Lazy-hydration macro transformation no longer depends on Nuxt auto-imports being enabled, which matters for projects that disable or customize auto-imports.

### Object-only island props (since 4.5.2)

Nitro now rejects non-object island props. Island payloads and direct island requests must provide props as an object.

### Options API in looped islands (since 4.5.2)

The islands transform now supports Options API components rendered with `v-for`; this pattern no longer requires rewriting the component to the Composition API.

### Pre-hydration browser hook (since 3.12.0)

The new `onPrehydrate` hook runs browser code during the hydration cycle before Nuxt hydrates the page.

```ts
onPrehydrate(() => {
  // runs before hydration
})
```

### Server components on static hosting (since 4.0-platform-guide)

Nuxt prerenders server components used by crawled pages by default, so they can run on fully static hosting when they are not first loaded only in the browser and their props do not change at runtime. With payload extraction enabled, their payloads can also be prefetched for client-side navigation.

### Server- and client-only pages (since 3.11.0)

Page files ending in `.client.vue` skip SSR for the entire page. Files ending in `.server.vue` produce server-rendered HTML that still works with client-side navigation and link prefetching.

### Server-island props travel in the URL (release-catalogs)

Props passed to server components and islands are serialized into the island request's query string, so they should not contain secrets and remain subject to URL serialization and size constraints.

### Server-island runtime context (since 4.0-platform-guide)

Server components can use shared state and the current route, can nest like ordinary components, and run all application plugins while rendering. A `<NuxtLink>` rendered inside one does not itself provide interactive client-side routing at this guide's snapshot; handle its clicks in a client parent with `navigateTo` when SPA navigation is required.
