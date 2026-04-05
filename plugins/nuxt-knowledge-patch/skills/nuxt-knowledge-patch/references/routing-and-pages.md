# Routing and Pages

## Middleware via `routeRules` (3.11)

Assign app-level middleware to page paths in config using `appMiddleware`, instead of defining middleware per-page with `definePageMeta`:

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/admin/**': {
      appMiddleware: ['auth']
    },
    '/admin/login': {
      appMiddleware: { auth: false } // disable for specific routes
    },
  },
})
```

- Uses glob patterns for route matching
- Pass an array to apply multiple middleware
- Pass an object with `false` values to disable specific middleware on sub-routes

## Server- and Client-Only Pages (3.11)

Pages can use `.server.vue` or `.client.vue` suffixes to control rendering:

- **`pages/heavy-dashboard.client.vue`** — skips SSR entirely (equivalent to wrapping in `<ClientOnly>`)
- **`pages/landing.server.vue`** — fully server-rendered HTML, prefetched on link visibility for instant navigation

This is a file-convention alternative to runtime rendering control, useful when an entire page should be restricted to one rendering mode.

## Auto-Registered Layers (3.12)

Layers placed in `~/layers/` are now auto-registered, matching the existing behavior of `~/modules/`. No need to declare them in `nuxt.config.ts`:

```
app/
  layers/
    admin/        # auto-registered
    marketing/    # auto-registered
  modules/
    analytics/    # already auto-registered (existing behavior)
```
