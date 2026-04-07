---
name: nuxt-knowledge-patch
description: "Nuxt changes since training cutoff (latest: 3.12) — routeRules middleware, server/client-only pages, Nuxt 4 compatibility mode, auto-registered layers. Load before working with Nuxt 3.11+."
license: MIT
metadata:
  author: Nevaberry
  version: "3.12"
---

# Nuxt 3.11+ Knowledge Patch

Claude's baseline knowledge covers Nuxt 3 through 3.9. This skill provides features from 3.11 (March 2024) onwards through 3.12 (June 2024).

## Quick Reference

### Version Timeline

| Version | Date | Key Change |
|---------|------|------------|
| 3.11 | 2024-03-16 | Middleware via `routeRules`, server/client-only pages |
| 3.12 | 2024-06-10 | Nuxt 4 compatibility mode, auto-registered layers |

### New Features at a Glance

| Feature | Version | Detail |
|---------|---------|--------|
| `appMiddleware` in `routeRules` | 3.11 | Assign middleware to routes in config instead of page-level `definePageMeta` |
| `.server.vue` / `.client.vue` pages | 3.11 | Server-only and client-only page rendering via file suffix |
| `future.compatibilityVersion: 4` | 3.12 | Opt into Nuxt 4 breaking changes incrementally while on v3 |
| Auto-registered layers | 3.12 | `~/layers/` auto-registered like `~/modules/`, no config needed |

## Middleware via `routeRules` (3.11)

Assign app-level middleware to page paths in config using `appMiddleware`:

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

See `references/routing-and-pages.md` for server/client-only pages.

## Nuxt 4 Compatibility Mode (3.12)

Opt into Nuxt 4 breaking changes incrementally:

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  future: {
    compatibilityVersion: 4,
  },
})
```

Enables v4 behavior changes (e.g., shallow reactive asyncData payloads) while still on v3, allowing gradual migration.

See `references/nuxt-4-migration.md` for details.

## Reference Files

| File | Contents |
|------|----------|
| `routing-and-pages.md` | `routeRules` middleware, server/client-only pages, auto-registered layers |
| `nuxt-4-migration.md` | Nuxt 4 compatibility mode and migration strategy |
