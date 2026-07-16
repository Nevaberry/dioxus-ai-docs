# Vue Router 5

## Package and build migration

### File-based routing is part of Vue Router

Vue Router 5 folds `unplugin-vue-router` into the core package (5.0.0).
Applications that did not use the plugin can generally move from Vue Router 4
without code changes, apart from the IIFE distribution behavior described
below. Plugin users should remove `unplugin-vue-router` and change imports:

```ts
import VueRouter from 'vue-router/vite'
import type {
  EditableTreeNode,
  Options,
} from 'vue-router/unplugin'
```

The Vite plugin comes from `vue-router/vite`. Other build adapters, integration
utilities, and types come from `vue-router/unplugin`; the newly exposed
`resolveOptions` also comes from that entry point.

Remove the obsolete `unplugin-vue-router/client` type reference. Prefer writing
the generated declaration under `src`, where normal TypeScript includes will
find it:

```ts
VueRouter({ dts: 'src/routes.d.ts' })
```

### Bundled Volar integrations

Use Vue Router's own Volar plugins for file-based route typing:

```json
{
  "compilerOptions": { "rootDir": "." },
  "vueCompilerOptions": {
    "plugins": [
      "vue-router/volar/sfc-typed-router",
      "vue-router/volar/sfc-route-blocks"
    ]
  }
}
```

`vue-router/volar/sfc-typed-router` infers the current page route from its file
location. Consequently, no-argument `useRoute()` and template `$route` receive
that page's parameter types. Set `compilerOptions.rootDir` when tooling cannot
infer the intended project root.

### Distribution constraints

The experimental entry point is ESM-only (5.1.0); CommonJS consumers cannot
load it directly. Vite is an optional peer dependency, so installing Vue Router
without Vite is supported when the Vite integration is unused.

The IIFE build no longer bundles `@vue/devtools-api` (5.0.0), because Devtools
v8 has no IIFE build. Supply Devtools separately when an IIFE-based workflow
needs it.

## Experimental data loaders

The data-loader integration is experimental (5.0-migration). A loader runs
outside component setup and is collected and awaited as part of navigation.
The system supports parallel fetching with deduplication, loading and error
state, SSR, and prefetching. Basic loaders always rerun; the Colada
implementation uses `@pinia/colada`.

Install `DataLoaderPlugin` before the router so it can participate in the
initial navigation:

```ts
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from 'vue-router/auto-routes'
import { DataLoaderPlugin } from 'vue-router/experimental'

const router = createRouter({ history: createWebHistory(), routes })
const app = createApp({})
app.use(DataLoaderPlugin, { router })
app.use(router)
app.mount('#app')
```

Define a loader with `defineBasicLoader()` and export it from the page component
so the router discovers it. When the implementation lives in another module,
the page must still re-export it:

```vue
<script lang="ts">
import { defineBasicLoader } from 'vue-router/experimental'
import { getUserById } from '../api'

export const useUserData = defineBasicLoader('/users/[id]', (route) =>
  getUserById(route.params.id),
)
</script>

<script setup lang="ts">
const { data: user, isLoading, error, reload } = useUserData()
</script>
```

Route changes rerun the basic loader and delay navigation until it resolves.
Calling its returned composable elsewhere shares the same fetching instance and
exposes `data`, `isLoading`, `error`, and `reload`.

## Typed route definitions and matching

### Query parameters

Experimental typed routing treats query parameters as optional by default
(5.0.0). Code that reads a declared query key must handle absence.

Invalid query-parameter formats produce a runtime warning and the invalid
values are filtered instead of causing route matching to fail (5.1.0). Query
parameter values may also be `undefined`.

### Page and parameter typing

`definePage()` type-checks `params.path` and strictly types parameter defaults
(5.1.0). Type errors now expose path configurations or defaults that do not
match the declared parameter.

File-based parameters support raw parameter parsers. Raw parser types are
forced to arrays, and a string can be supplied as a parser for convenience.
Repeatable parameters may also be embedded within a subsegment.

At runtime, file-based routing throws when a referenced parameter parser is
missing (5.0.0). Parser types are inserted automatically into generated
declarations, even when the declaration file is outside the project root.

Vue Router includes a JSON schema for route definitions, allowing schema-aware
editors and tools to validate route data and provide completion.

### Configurable router type

The global `Router` type can be overridden (5.1.0). When the experimental types
configuration is enabled, `useRouter()` also returns the configured override
rather than the default global router type.

## Navigation lifecycle

When a kept-alive component is reactivated for a different route, its
navigation guards run (5.0.0). Cached route components must not assume that
reactivation skips route guards.
