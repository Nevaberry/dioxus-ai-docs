# Routing and navigation

Configure pages, route rules, middleware, layouts, links, scrolling, and navigation accessibility.

## Links, navigation, and accessibility

### Client-side navigation inside islands (since 4.5.2)

Links rendered inside islands now use client-side navigation. A client wrapper is no longer required solely to prevent those links from causing full-page navigation.

### Configurable NuxtLink prefetch triggers (since 3.13.0)

`NuxtLink` can prefetch on interaction (hover or focus), visibility, or both through `prefetch-on`. Defaults can be set globally under `experimental.defaults.nuxtLink` and overridden per link.

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

### Focus after hash navigation (since 4.3.0)

Hash-link navigation now moves focus after the navigation completes, improving keyboard and screen-reader behavior.

### Hash-only smooth scrolling (since 3.18.0)

`scrollBehaviorType` now applies only to hash scrolling rather than ordinary route scrolling as well.

### In-page screen-reader announcements (since 4.4.0)

Mount `<NuxtAnnouncer>` once, then use `useAnnouncer().polite()` or `.assertive()` for dynamic changes that do not move focus; `useRouteAnnouncer` remains the navigation-specific API.

```ts
const { polite, assertive } = useAnnouncer()
polite('Message sent successfully')
```

### Object route locations through `NuxtLink` `href` (since 4.2.0)

The `href` prop now accepts object-format route locations, rather than requiring object destinations to be passed through `to`.

```vue
<NuxtLink :href="{ name: 'users-id', params: { id } }">Profile</NuxtLink>
```

### Per-link trailing slashes (since 3.17.0)

`<NuxtLink>` accepts a `trailingSlash` prop to format an individual destination with a trailing slash.

```vue
<NuxtLink to="/about" trailing-slash>About</NuxtLink>
```

### Reactive `NuxtLink.useLink` inputs (since 4.4.0)

`NuxtLink.useLink` now accepts refs as inputs, so a link's destination and other reactive options can be passed without manually unwrapping them.

### Route announcements in the built-in app (since 3.18.0)

Nuxt's built-in `app.vue` now includes `<NuxtRouteAnnouncer>`, so client-side page changes are announced to screen readers. Projects with their own `app.vue` do not receive this automatically and should include `<NuxtRouteAnnouncer />` themselves.

### Route-rule redirects preserve fragments (since 3.20.0)

Redirects configured through `routeRules` now retain the incoming URL hash instead of dropping it.

### Safer navigation destinations (since 3.21.0)

`<NuxtLink>` and the `navigateTo` open option reject script-capable protocols, `navigateTo` blocks path-normalization open redirects, and `reloadNuxtApp` rejects cross-origin paths.

## Page discovery and route rules

### Configurable page scanning (since 3.16.0)

The `pages` option now accepts a `pattern` array to restrict which files and directories Nuxt scans as pages.

```ts
export default defineNuxtConfig({
  pages: { pattern: ['**/*.vue'] },
})
```

### Decoded route-rule matching (since 4.5.2)

Nuxt now decodes request paths before matching route rules, so percent-encoded paths are evaluated against their decoded form.

### Explicit page-composable imports (since 4.4.0)

Page composables are now exported from `#app/composables/pages`, providing a supported direct-import path when auto-imports are unavailable or undesirable.

### Local functions in `definePageMeta` (since 3.15.0)

Page metadata can now reference locally declared functions, including functions used for route validation.

```ts
function validateIdParam(route) {
  return !!(route.params.id && !isNaN(Number(route.params.id)))
}

definePageMeta({
  validate: validateIdParam,
})
```

### Module-provided router options (since 3.10.0)

Modules can use the new `pages:routerOptions` hook to inject `router.options` files, including custom scroll behavior or runtime route augmentation.

## Page metadata, middleware, and layouts

### Additional build-time page metadata (since 3.15.0)

Module authors can list extra page-meta keys in `experimental.extraPageMetaExtractionKeys`; Nuxt extracts those keys for build-time use in the `pages:resolved` hook.

### Build-time page metadata (since 3.10.0)

Enable `scanPageMeta` to expose values from `definePageMeta` to modules and hooks at build time, where they can be inspected or changed.

```ts
export default defineNuxtConfig({
  experimental: { scanPageMeta: true },
})
```

### Layouts from route rules (since 3.21.0)

`routeRules` accepts `appLayout`, allowing a route family to select a layout without repeating `definePageMeta`. Route-rule matching is case-insensitive, in line with `vue-router`.

```ts
export default defineNuxtConfig({
  routeRules: { '/admin/**': { appLayout: 'admin' } },
})
```

### Middleware for page islands (since 3.21.0)

Page-island rendering now runs Nuxt middleware rather than bypassing it.

### Page metadata after route extension (since 3.14.0)

Opting into `experimental.scanPageMeta: 'after-resolve'` moves metadata scanning until after `pages:extend`. The new `pages:resolved` hook then runs with all extended pages augmented by their metadata.

```ts
export default defineNuxtConfig({
  experimental: {
    scanPageMeta: 'after-resolve',
  },
})
```

### Page middleware in route rules (since 3.11.0)

`routeRules` can attach named Vue application middleware to page paths with `appMiddleware`; a more specific rule can disable inherited middleware by setting its name to `false`.

```ts
export default defineNuxtConfig({
  routeRules: {
    '/admin/**': { appMiddleware: ['auth'] },
    '/admin/login': { appMiddleware: { auth: false } },
  },
})
```

### Pathless route groups (since 3.13.0)

Parenthesized directories under `pages/` organize routes without contributing a URL segment. For example, `pages/(marketing)/about.vue` produces `/about`, not `/marketing/about`.

### Route groups in page metadata (since 3.21.0)

Parenthesized page directories are exposed as `route.meta.groups`. For example, `pages/(protected)/account.vue` gives middleware a `to.meta.groups` array containing `'protected'`.

### Route rules in resolved page metadata (since 3.19.0)

Rules declared with `defineRouteRules` are extracted to the corresponding page object's `rules` property, making them available to build-time page consumers.

### Route-parameter types from page metadata (since 4.5.2)

Route parameters defined with `definePageMeta` are now included in generated types, so typed route locations recognize parameters introduced through page metadata.

### Runtime layout props (since 3.21.0)

`setPageLayout` accepts layout props as its second argument, and later 3.21 patches preserve them across same-path navigation.

```ts
setPageLayout('admin', { sidebar: true, theme: 'dark' })
```

### Typed layout props in page metadata (since 4.4.0)

`definePageMeta` accepts a layout object containing `name` and `props`; those props are checked against the layout component's `defineProps` declaration.

```ts
definePageMeta({
  layout: { name: 'panel', props: { sidebar: true, title: 'Dashboard' } },
})
```
