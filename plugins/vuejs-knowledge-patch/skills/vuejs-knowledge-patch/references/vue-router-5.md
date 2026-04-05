# Vue Router 5

## Overview

Released January 2026 (v5.0.0, latest v5.0.4 as of March 2026). This is a **transition release** that merges `unplugin-vue-router` (file-based routing) into the core `vue-router` package.

**For Vue Router 4 users without `unplugin-vue-router`:** No breaking changes — just update the dependency.

**Vue Router 6** will be ESM-only and remove deprecated APIs. v5 gives you time to prepare.

## Migration from unplugin-vue-router

### Checklist

1. Remove `unplugin-vue-router` dependency
2. Update `vue-router` to v5
3. Change plugin import: `unplugin-vue-router/vite` -> `vue-router/vite`
4. Change data loader imports: `unplugin-vue-router/data-loaders/*` -> `vue-router/experimental`
5. Change utility imports: `unplugin-vue-router` -> `vue-router/unplugin`
6. Change Volar plugins: `unplugin-vue-router/volar/*` -> `vue-router/volar/*`
7. Remove `unplugin-vue-router/client` from tsconfig / `env.d.ts`

### Import Changes

**Vite plugin:**

```ts
// Before
import VueRouter from 'unplugin-vue-router/vite'
// After
import VueRouter from 'vue-router/vite'
```

**Other build tools:**

```ts
import VueRouter from 'vue-router/unplugin'

VueRouter.webpack({ /* ... */ })
VueRouter.rollup({ /* ... */ })
```

**Data loaders:**

```ts
// Before
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic'
import { defineColadaLoader } from 'unplugin-vue-router/data-loaders/pinia-colada'
import { DataLoaderPlugin } from 'unplugin-vue-router/data-loaders'

// After
import { defineBasicLoader, DataLoaderPlugin } from 'vue-router/experimental'
import { defineColadaLoader } from 'vue-router/experimental/pinia-colada'
```

**Volar plugins** (tsconfig.json):

```jsonc
{
  "vueCompilerOptions": {
    "plugins": [
      "vue-router/volar/sfc-typed-router",
      "vue-router/volar/sfc-route-blocks"
    ]
  }
}
```

### Vite Config

Move generated types file inside `src/` and rename to `route-map.d.ts`:

```ts
// vite.config.ts
export default defineConfig({
  plugins: [
    VueRouter({
      dts: 'src/route-map.d.ts',
    }),
    Vue(),
  ],
})
```

Remove old client types reference from `env.d.ts`:

```ts
// Remove this line:
/// <reference types="unplugin-vue-router/client" />
```

## New Features (v5.0.3+)

### `_parent` Route Folders

Non-matchable layout routes using `_parent` prefix in nested folders. These create route nesting without adding a URL segment.

### `reroute()` Function

Replaces the deprecated `NavigationResult`:

```ts
import { reroute } from 'vue-router'

router.beforeEach((to) => {
  if (!isAuthenticated && to.meta.requiresAuth) {
    return reroute('/login')
  }
})
```

### `miss()` Returns `never`

`miss()` now throws internally and its return type is `never`.

### `next()` Callback Deprecated

Navigation guards using the `next()` callback pattern now emit deprecation warnings. Prepare for Vue Router 6 which will remove it entirely:

```ts
// Deprecated pattern
router.beforeEach((to, from, next) => {
  if (isAuthenticated) next()
  else next('/login')
})

// Recommended pattern (already works in v4+)
router.beforeEach((to) => {
  if (!isAuthenticated) return '/login'
})
```

### Other Changes

- `selectNavigationResult` removed (was experimental)
- Alias extraction from `definePage`
- Published as `type: module` package format
- IIFE build no longer includes `@vue/devtools-api` (upgraded to v8)

## Exports Reference

| Export | Purpose |
|---|---|
| `vue-router` | Main API (unchanged) |
| `vue-router/vite` | Vite plugin for file-based routing |
| `vue-router/auto-routes` | Generated routes |
| `vue-router/unplugin` | Webpack/Rollup/esbuild + utilities |
| `vue-router/experimental` | Data loaders |
| `vue-router/experimental/pinia-colada` | Pinia Colada loader |

## Troubleshooting

- **Types not recognized:** Restart TypeScript server and check that `src/route-map.d.ts` is included in tsconfig
- **Routes not generating:** Verify `routesFolder` path and file extensions
- **Route name errors:** Use generated names or add `definePage({ name: 'custom-name' })` to components
