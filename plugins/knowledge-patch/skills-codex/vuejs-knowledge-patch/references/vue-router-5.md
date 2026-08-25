# Vue Router 5

## Package and build-tool migration

### Move file-based routing into Vue Router (since 5.0.0)

Vue Router 5 incorporates `unplugin-vue-router`. Applications that never used
the old plugin generally need no source changes, except for the IIFE dependency
change described below. Plugin users should remove `unplugin-vue-router`, import
the Vite adapter from `vue-router/vite`, and import the other adapters,
integration utilities, and types from `vue-router/unplugin`. `resolveOptions`
is also publicly available there.

```ts
import VueRouter from 'vue-router/vite'
import type { EditableTreeNode, Options } from 'vue-router/unplugin'
```

Remove any `unplugin-vue-router/client` type reference. Generate declarations
under `src` when possible so ordinary TypeScript includes discover them:

```ts
VueRouter({ dts: 'src/routes.d.ts' })
```

### Configure bundled Volar plugins (since 5.0.0)

For file-based routes, enable the bundled SFC typed-router and route-block
plugins. The typed-router plugin infers a page route from its file location, so
no-argument `useRoute()` and template `$route` receive its parameter types.
Set `compilerOptions.rootDir` when the project root must be explicit.

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

### Use the route-definition schema (since 5.0.0)

Vue Router includes a JSON schema for route definitions. Point schema-aware
editors and validators at it to validate route data and provide completions.

### Respect distribution constraints

The experimental entry point is ESM-only (since 5.1.0); CommonJS consumers
cannot load it directly. Vite is an optional peer dependency, so non-Vite
installations need not install Vite (since 5.1.0).

The IIFE build no longer includes `@vue/devtools-api` because Devtools v8 does
not ship an IIFE build (since 5.0.0). Add Devtools separately when an IIFE
workflow needs it.

## Route parameters and generated types

### Validate parsers and declarations (since 5.0.0)

File-based routing throws at runtime when a referenced parameter parser is
missing. Parser types are emitted automatically in generated declarations,
including when the declaration file is outside the project root.

### Use stronger page and parser typing (since 5.1.0)

`definePage()` checks `params.path` and strictly types parameter defaults, so
incompatible paths and default values fail type checking. File-based parameters
support raw parsers; raw-parser types are forced to arrays, and a string can be
provided as a parser for convenience.

The global `Router` type is configurable. Enabling the experimental types
configuration applies that override to the type returned by `useRouter()`.

### Handle optional validated query parameters

Experimental typed query parameters are optional by default (since 5.0.0).
Since 5.1.0, invalid query formats issue a runtime warning and invalid values
are filtered rather than causing route matching to fail. Values may be
`undefined`; consumers must check declared query keys before use.

### Match repeatable subsegment parameters (since 5.1.0)

Experimental matching supports repeatable parameters embedded within a path
subsegment. Test both parsing and generated types for routes that use them.

### Reject malformed character escapes (since 5.2.0)

The file-based routing unplugin rejects `[x+hh]` filename character codes whose
digits are not hexadecimal. Rename routes that relied on malformed codes.

```text
valid:   [x+2F]
invalid: [x+2G]
```

## Data loaders

### Install the loader plugin before the router (batch 5.0-migration)

Data loaders run outside component setup and are collected and awaited during
navigation. They support parallel deduplicated fetching, loading and error
state, SSR, and prefetching. Basic loaders always rerun; the Colada loader uses
`@pinia/colada`.

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

### Export loaders from page components (batch 5.0-migration)

Define a loader with `defineBasicLoader()` and export it from the page so the
router can discover it. If its implementation lives in another module,
re-export it from the page. A route change reruns the loader and delays
navigation until it resolves. Other callers of the returned composable share
the same fetching instance and receive `data`, `isLoading`, `error`, and
`reload`.

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

## Navigation behavior

### Run guards on KeepAlive reactivation (since 5.0.0)

When a kept-alive component is reactivated for a different route, its
navigation guards run. Cached route components must not assume reactivation
skips guards.

### Ignore stale scroll results (since 5.2.0)

If navigations overlap, Vue Router ignores a result returned by an older
asynchronous `scrollBehavior` after a newer navigation has taken over. Test
overlap behavior rather than letting stale work reposition the page.

## Pinia interoperability

Vue Router 5.2.0 accepts Pinia 4, removing the earlier compatibility
restriction for applications that use both packages.
