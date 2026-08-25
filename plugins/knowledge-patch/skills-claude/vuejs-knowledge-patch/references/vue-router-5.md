# Vue Router 5

## Package and file-based routing migration

### Move the unplugin into Vue Router

Vue Router 5 merges `unplugin-vue-router` into the router package (since
5.0.0). Remove the separate dependency. Import the Vite plugin from
`vue-router/vite`; other build adapters, integration utilities, and types are
under `vue-router/unplugin`. That entry also exposes `resolveOptions`.

```ts
import VueRouter from 'vue-router/vite'
import type { Options, EditableTreeNode } from 'vue-router/unplugin'
```

Except for the IIFE distribution change below, applications that did not use
the old plugin can generally upgrade from Vue Router 4 without source changes.

### Generate route declarations where TypeScript includes them

Remove the `unplugin-vue-router/client` type reference. Prefer generating the
declaration under `src` so normal TypeScript include patterns discover it:

```ts
VueRouter({ dts: 'src/routes.d.ts' })
```

### Configure bundled Volar route typing

The router bundles `vue-router/volar/sfc-typed-router` and
`vue-router/volar/sfc-route-blocks` (since 5.0.0). The typed-router plugin
infers a page route from its file location, which types no-argument
`useRoute()` and template `$route`. Set `compilerOptions.rootDir` when the
project root must be explicit.

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

### Use route definition schema support

Vue Router 5 includes a JSON schema for route definitions, so schema-aware
editors and tools can validate route data and offer completions.

## Data loaders

The experimental data-loader integration described by the 5.0-migration
batch runs outside component setup. Loaders are collected and awaited during
navigation and support parallel deduplicated fetching, loading and error
state, SSR, and prefetching. Basic loaders rerun on every relevant navigation;
the Colada implementation uses `@pinia/colada`.

### Install the plugin before the router

Plugin order matters for initial navigation:

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

### Export loaders from their pages

Define a loader with `defineBasicLoader()` and export it from the page so the
router can discover it. When its implementation lives elsewhere, re-export it
from the page. A route change reruns it and delays navigation until it resolves.
Other callers of the composable share the fetching instance and receive
`data`, `isLoading`, `error`, and `reload`.

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

## Typed routes, parameters, and query values

### Validate parsers and generated declarations

File-based routing throws at runtime when a referenced parameter parser is
missing (since 5.0.0). Parser types are included in generated declarations,
even when the declaration file sits outside the project root.

### Treat query values as optional and validated

Experimental typed query parameters are optional by default (since 5.0.0).
Since 5.1.0, invalid query formats warn at runtime and invalid values are
filtered rather than causing route matching to fail. Values may be
`undefined`, so readers must handle absent declared keys.

### Use stronger page parameter types

`definePage()` type-checks `params.path` and strictly types parameter defaults
(since 5.1.0). Incompatible paths and default values should be fixed at type
checking time.

### Use raw and repeatable parameter support correctly

File-based parameters support raw parsers (since 5.1.0). Raw parser types are
forced to arrays; a string may be supplied as a convenience parser.
Experimental matching also supports repeatable parameters embedded in a
subsegment.

The file-based unplugin rejects malformed `[x+hh]` character codes (since
5.2.0). Both digits must be hexadecimal:

```text
valid:   [x+2F]
invalid: [x+2G]
```

## Router types and installation boundaries

The global `Router` type is configurable (since 5.1.0). When experimental
types are enabled, the override also controls the return type of `useRouter()`.

`vue-router/experimental` is ESM-only (since 5.1.0); CommonJS consumers cannot
load it directly. Vite is an optional peer dependency, so installations that
do not use the Vite integration do not need Vite.

Vue Router permits Pinia 4 starting with 5.2.0.

## Runtime and distribution behavior

### Run guards for kept-alive route changes

When a cached component is reactivated for a different route, its navigation
guards run (since 5.0.0). Do not assume a KeepAlive transition skips guards.

### Ignore obsolete asynchronous scroll results

When navigations overlap, the router ignores a result from an older async
`scrollBehavior` after a newer navigation takes over (since 5.2.0). Tests for
custom scrolling should cover overlapping navigations rather than expecting
stale work to move the page.

### Supply Devtools for IIFE builds

The IIFE build no longer bundles `@vue/devtools-api` (since 5.0.0), because
Devtools v8 has no IIFE build. Include Devtools separately if this distribution
needs it.
