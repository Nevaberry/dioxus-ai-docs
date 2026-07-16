# Routing and navigation

Use this reference for page discovery and metadata, route rules, application middleware, layouts, links, transitions, scrolling, loading feedback, and accessibility announcements.

## Contents

- [Page discovery and route metadata](#page-discovery-and-route-metadata)
- [Router options and route rules](#router-options-and-route-rules)
- [Layout selection and props](#layout-selection-and-props)
- [NuxtLink behavior](#nuxtlink-behavior)
- [View transitions and loading feedback](#view-transitions-and-loading-feedback)
- [Scrolling, focus, and announcements](#scrolling-focus-and-announcements)

## Page discovery and route metadata

### Organize pages with pathless route groups (3.13.0)

Parenthesized directories under `pages/` group routes without adding a URL segment. `pages/(marketing)/about.vue` resolves to `/about`, not `/marketing/about`.

### Read route groups from page metadata (3.21.0)

Parenthesized page directories are also exposed through `route.meta.groups`. For example, `pages/(protected)/account.vue` adds `'protected'` to `to.meta.groups` for middleware and navigation logic.

### Restrict page scanning with patterns (3.16.0)

The `pages` option accepts a `pattern` array:

```ts
export default defineNuxtConfig({
  pages: { pattern: ['**/*.vue'] },
})
```

### Expose page metadata at build time (3.10.0)

Enable `scanPageMeta` when modules or hooks must inspect or modify values extracted from `definePageMeta`:

```ts
export default defineNuxtConfig({
  experimental: { scanPageMeta: true },
})
```

The option is enabled by default in later releases.

### Scan metadata after route extension (3.14.0)

Use `experimental.scanPageMeta: 'after-resolve'` to run scanning after `pages:extend`. The `pages:resolved` hook then receives extended pages augmented with their metadata.

```ts
export default defineNuxtConfig({
  experimental: { scanPageMeta: 'after-resolve' },
})
```

### Extract custom page-meta fields (3.15.0)

Add module-specific fields to `experimental.extraPageMetaExtractionKeys`; those values become available to the `pages:resolved` hook.

### Reference local functions in page metadata (3.15.0)

`definePageMeta` accepts locally declared functions, including route validators.

```ts
function validateIdParam(route) {
  return !!(route.params.id && !isNaN(Number(route.params.id)))
}

definePageMeta({ validate: validateIdParam })
```

### Read route rules from resolved pages (3.19.0)

Rules declared with `defineRouteRules` are extracted into the corresponding page object's `rules` property for build-time page consumers.

### Normalize page component names experimentally (4.4.0)

Enable `experimental.normalizeComponentNames` to make page component names match route names in debugging and DevTools output.

```ts
export default defineNuxtConfig({
  experimental: { normalizeComponentNames: true },
})
```

### Import page composables explicitly (4.4.0)

When auto-imports are disabled or undesirable, import supported page composables from `#app/composables/pages`.

## Router options and route rules

### Inject router options from modules (3.10.0)

Use the `pages:routerOptions` hook to add `router.options` files from a module. These files can define custom scroll behavior or augment routes at runtime.

### Attach page middleware through route rules (3.11.0)

Use `appMiddleware` to attach named Vue application middleware to route families. A more specific rule can disable inherited middleware by mapping its name to `false`.

```ts
export default defineNuxtConfig({
  routeRules: {
    '/admin/**': { appMiddleware: ['auth'] },
    '/admin/login': { appMiddleware: { auth: false } },
  },
})
```

### Preserve URL fragments in route-rule redirects (3.20.0)

Redirects configured through `routeRules` retain the incoming URL hash rather than dropping it.

### Run middleware for page islands (3.21.0)

Page-island rendering executes Nuxt middleware; do not assume islands bypass route guards or other middleware effects.

## Layout selection and props

### Select layouts through route rules (3.21.0)

Use `appLayout` for a route family rather than repeating `definePageMeta`. Route-rule matching is case-insensitive, matching Vue Router behavior.

```ts
export default defineNuxtConfig({
  routeRules: { '/admin/**': { appLayout: 'admin' } },
})
```

### Pass props when changing layouts at runtime (3.21.0)

`setPageLayout` accepts layout props as its second argument, and patched releases preserve them across same-path navigation.

```ts
setPageLayout('admin', { sidebar: true, theme: 'dark' })
```

### Type layout props in page metadata (4.4.0)

Pass a layout object with `name` and `props` to `definePageMeta`. Nuxt checks the props against the layout component's `defineProps` declaration.

```ts
definePageMeta({
  layout: { name: 'panel', props: { sidebar: true, title: 'Dashboard' } },
})
```

## NuxtLink behavior

### Choose prefetch triggers (3.13.0)

Configure `NuxtLink` to prefetch on visibility, interaction through hover/focus, or both. Set project defaults under `experimental.defaults.nuxtLink`, then override individual links.

```vue
<NuxtLink prefetch-on="interaction" to="/about">About</NuxtLink>
<NuxtLink
  :prefetch-on="{ visibility: true, interaction: true }"
  to="/contact"
>
  Contact
</NuxtLink>
```

```ts
export default defineNuxtConfig({
  experimental: {
    defaults: {
      nuxtLink: {
        prefetch: true,
        prefetchOn: { visibility: false, interaction: true },
      },
    },
  },
})
```

### Format a link with a trailing slash (3.17.0)

Use the `trailingSlash` prop for an individual destination:

```vue
<NuxtLink to="/about" trailing-slash>About</NuxtLink>
```

### Pass object destinations through `href` (4.2.0)

The `href` prop accepts object-format route locations as well as strings, so object destinations no longer have to use `to`.

```vue
<NuxtLink :href="{ name: 'users-id', params: { id } }">Profile</NuxtLink>
```

### Pass reactive inputs to `NuxtLink.useLink` (4.4.0)

`NuxtLink.useLink` accepts refs for destinations and other options without manual unwrapping.

### Keep navigation protocol protections intact (3.21.0)

`NuxtLink` and the `navigateTo` open option reject script-capable protocols. `navigateTo` also blocks path-normalization open redirects, and `reloadNuxtApp` rejects cross-origin paths. Do not pre-normalize or bypass these safety checks.

## View transitions and loading feedback

### Control view transitions per page (3.10.0)

Enable experimental view transitions globally, then opt a page in or out through `definePageMeta`. Nuxt skips transitions when `prefers-reduced-motion: reduce` is active unless the page explicitly uses `viewTransition: 'always'`.

```ts
export default defineNuxtConfig({
  experimental: { viewTransition: true },
})

definePageMeta({ viewTransition: false })
```

### Observe transition starts and force loading completion (3.11.0)

Use the `page:view-transition:start` hook when an experimental View Transition begins. The loading indicator also supports custom hide timing and a forced `finish()`.

### Configure loading-indicator delays as props (3.17.0)

`<NuxtLoadingIndicator>` accepts `hideDelay` and `resetDelay` directly.

```vue
<NuxtLoadingIndicator :hide-delay="500" :reset-delay="300" />
```

### Select view-transition types (4.4.0)

Experimental view transitions support types for distinct forward, backward, tab, or page-navigation CSS transitions.

## Scrolling, focus, and announcements

### Limit smooth-scroll configuration to hashes (3.18.0)

`scrollBehaviorType` applies to hash scrolling, not ordinary route scrolling.

### Announce routes in a custom root app (3.18.0)

Nuxt's built-in `app.vue` includes `<NuxtRouteAnnouncer>`. A project with its own `app.vue` must mount `<NuxtRouteAnnouncer />` explicitly so client-side page changes are announced to screen readers.

### Move focus after hash navigation (4.3.0)

Hash-link navigation moves focus after navigation completes, improving keyboard and screen-reader behavior. Avoid custom focus code that fights this behavior.

### Announce in-page status changes (4.4.0)

Mount `<NuxtAnnouncer>` once, then call `useAnnouncer().polite()` or `.assertive()` for dynamic changes that do not move focus. Keep `useRouteAnnouncer` for navigation announcements.

```ts
const { polite, assertive } = useAnnouncer()
polite('Message sent successfully')
```
