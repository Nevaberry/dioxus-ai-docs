# Routing and navigation

## Router integration and page discovery

When router integration is enabled, render `<NuxtPage>`; a bare `<RouterView>` is not a supported substitute and triggers a development diagnostic (3.10.0).

Restrict page discovery with `pages.pattern` when only selected files should become routes (3.16.0):

```ts
export default defineNuxtConfig({
  pages: { pattern: ['**/*.vue'] },
})
```

Modules can inject `router.options` files through `pages:routerOptions`, including custom scroll behavior and runtime route augmentation (3.10.0). Route parameters introduced through `definePageMeta` participate in generated route types, so typed locations recognize them (4.5.2).

## Pathless route groups

Parenthesized directories organize pages without adding a URL segment: `pages/(marketing)/about.vue` maps to `/about` (3.13.0). Group names are exposed through `route.meta.groups`, so middleware can detect a route such as `pages/(protected)/account.vue` using `to.meta.groups` (3.21.0).

Route rules match case-insensitively. Request paths are decoded before matching, so percent-encoded paths are evaluated in decoded form (3.21.0, 4.5.2).

## Build-time page metadata

`scanPageMeta` exposes `definePageMeta` values to modules and build hooks and is enabled by default. Use one `definePageMeta` call per file (3.10.0, 3.12.0).

To scan after `pages:extend`, set `experimental.scanPageMeta: 'after-resolve'`; `pages:resolved` then receives extended pages with metadata attached (3.14.0). Add custom extracted keys through `experimental.extraPageMetaExtractionKeys` (3.15.0). Metadata may reference locally declared functions, including route validators (3.15.0).

Rules from `defineRouteRules` are exposed on the resolved page object's `rules` property for build-time consumers (3.19.0). Page-meta and virtual route changes update through HMR.

## Middleware and layouts through route rules

Attach named application middleware to route families using `appMiddleware`. A more-specific rule can disable inherited middleware by setting its name to `false` (3.11.0).

```ts
export default defineNuxtConfig({
  routeRules: {
    '/admin/**': { appMiddleware: ['auth'], appLayout: 'admin' },
    '/admin/login': { appMiddleware: { auth: false } },
  },
})
```

`appLayout` selects a layout for a route family without repeated page metadata (3.21.0). For runtime selection, `setPageLayout(name, props)` accepts props as its second argument and preserves them across same-path navigation (3.21.0).

Page metadata can instead use a checked layout object. Props are validated against the layout component's `defineProps` declaration (4.4.0):

```ts
definePageMeta({
  layout: { name: 'panel', props: { sidebar: true, title: 'Dashboard' } },
})
```

## `NuxtLink` prefetch and destination formatting

Configure prefetch by visibility, interaction, or both with `prefetch-on`; set defaults under `experimental.defaults.nuxtLink` and override them per link (3.13.0).

```vue
<NuxtLink prefetch-on="interaction" to="/about">About</NuxtLink>
<NuxtLink
  :prefetch-on="{ visibility: true, interaction: true }"
  to="/contact"
>
  Contact
</NuxtLink>
```

`trailingSlash` formats a single link destination with a trailing slash (3.17.0). Both `to` and `href` accept object route locations (4.2.0). `NuxtLink.useLink` accepts refs as inputs, so reactive destinations need no manual unwrapping (4.4.0).

Links rendered inside server islands use client-side navigation as of 4.5.2. At the earlier 4.0-platform-guide snapshot, those links needed a client parent calling `navigateTo` to avoid a full-page request. Check the installed patch level before keeping or removing that wrapper.

## Navigation safety and redirects

`NuxtLink` and the `navigateTo` open option reject script-capable protocols. `navigateTo` blocks path-normalization open redirects, and `reloadNuxtApp` rejects cross-origin paths (3.21.0). Preserve these checks when wrapping navigation helpers.

Route-rule redirects retain incoming URL fragments (3.20.0).

## View transitions and loading state

After enabling experimental view transitions, page metadata can opt pages in or out. Nuxt skips transitions for `prefers-reduced-motion: reduce` unless a page explicitly uses `viewTransition: 'always'` (3.10.0).

```ts
export default defineNuxtConfig({
  experimental: { viewTransition: true },
})

definePageMeta({ viewTransition: false })
```

`page:view-transition:start` runs when a View Transition begins (3.11.0). Transition types can distinguish forward, backward, tab, and page navigation for different CSS treatment (4.4.0).

`<NuxtLoadingIndicator>` accepts `hideDelay` and `resetDelay`; its composable supports custom hide timing and forced `finish()` (3.11.0, 3.17.0).

## Scrolling, focus, and announcements

`scrollBehaviorType` applies smooth scrolling only to hash changes, not ordinary route navigation (3.18.0). After hash navigation, Nuxt moves focus once navigation completes for keyboard and screen-reader users (4.3.0).

The built-in application includes `<NuxtRouteAnnouncer>`, but a custom `app.vue` must mount it explicitly so client route changes are announced (3.18.0).

For status changes that do not move focus, mount `<NuxtAnnouncer>` once and call `useAnnouncer().polite()` or `.assertive()`. Keep `useRouteAnnouncer` for route changes (4.4.0).

```ts
const { polite } = useAnnouncer()
polite('Message sent successfully')
```

## Page component diagnostics and imports

`experimental.normalizeComponentNames` makes page component names match route names for consistent diagnostics and DevTools output. Page composables have a supported direct import path at `#app/composables/pages` when auto-imports are disabled (4.4.0).
