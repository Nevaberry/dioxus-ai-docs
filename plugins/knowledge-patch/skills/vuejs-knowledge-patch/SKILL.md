---
name: vuejs-knowledge-patch
description: Vue.js 3.6.0-beta compatibility. Use for Vue.js work.
license: MIT
version: 3.6.0-beta
metadata:
  author: Nevaberry
---

# Vue.js Knowledge Patch

Use this patch when changing Vue applications or ecosystem tooling, especially
projects using Vue Router, Pinia, Pinia Colada, Nuxt, or Vite integrations.

## Reference index

| Reference | Topics |
| --- | --- |
| [`references/vue-router-5.md`](references/vue-router-5.md) | Router package migration, file-based routes, typed routes, parameter parsing, data loaders, guards, and distribution changes |
| [`references/pinia-3.md`](references/pinia-3.md) | Pinia package requirements, ESM/CJS metadata, and IIFE Devtools behavior |
| [`references/pinia-colada-queries.md`](references/pinia-colada-queries.md) | Query state, keys, cache operations, pagination, infinite queries, callbacks, and query plugins |
| [`references/pinia-colada-mutations-and-integration.md`](references/pinia-colada-mutations-and-integration.md) | Mutations, optimistic updates, shared definitions, persistence, SSR, testing, migrations, and extension API |
| [`references/vue-core-and-vapor.md`](references/vue-core-and-vapor.md) | Typed template refs and Vue release-channel conventions |
| [`references/ecosystem-tooling.md`](references/ecosystem-tooling.md) | Nuxt custom fetchers, Vite's Rolldown transition, and Vite+ |

## Breaking changes and migrations

### Move file-based routing imports into Vue Router

Vue Router 5 includes the former `unplugin-vue-router` functionality. Remove
that dependency and update imports:

```ts
import VueRouter from 'vue-router/vite'
import type {
  EditableTreeNode,
  Options,
} from 'vue-router/unplugin'
```

Other build adapters and utilities, including `resolveOptions`, are also
exported from `vue-router/unplugin`.

Applications that did not use the old plugin generally need no source changes.
The IIFE distribution is the exception: Devtools is no longer bundled.

Remove the old `unplugin-vue-router/client` type reference. Emit generated
declarations under `src` so ordinary TypeScript includes find them:

```ts
VueRouter({ dts: 'src/routes.d.ts' })
```

For route-aware SFC typing, use the bundled Volar plugins:

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

The typed-router plugin infers a page's route from its file location, including
the types returned by no-argument `useRoute()` and template `$route`.

### Treat the experimental router entry as ESM-only

Do not load `vue-router/experimental` from CommonJS. Vite itself is only an
optional peer dependency, so non-Vite installations do not need to install it.

Typed query parameters are optional. Invalid query formats warn and are
filtered instead of failing route matching; a query value may be `undefined`.
Do not assume a declared query key is present.

### Account for Pinia package metadata

Pinia 3 requires TypeScript 4.5 or newer because its declarations use the
native `Awaited` type. Its package declares `"type": "module"` while still
shipping CommonJS distribution files. The standalone IIFE build no longer
contains Vue Devtools, so add Devtools separately when that distribution needs
it.

### Apply Pinia Colada API migrations

Current `useQuery()` accepts one options object. Older two-argument
`useQuery`/`useQueryState` forms are removed, and global query defaults belong
under `queryOptions`. The package includes ast-grep migration rules; commit
work first, then run the matching rule from the installed package against
source files.

```sh
pnpm --package=@ast-grep/cli dlx ast-grep scan \
  -r node_modules/@pinia/colada/codemods/rules/migration-0-21-to-1-0.yaml \
  -i src
```

## Router data loaders

Install `DataLoaderPlugin` before the router so it participates in initial
navigation:

```ts
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from 'vue-router/auto-routes'
import { DataLoaderPlugin } from 'vue-router/experimental'

const router = createRouter({ history: createWebHistory(), routes })
const app = createApp({})
app.use(DataLoaderPlugin, { router })
app.use(router)
```

Loaders execute outside component setup, are collected and awaited during
navigation, and support parallel deduplicated fetching, loading/error state,
SSR, and prefetching. Basic loaders always rerun; the Colada implementation
uses `@pinia/colada`.

Export a loader from its page component. If it lives elsewhere, re-export it
from the page so the router can discover it:

```vue
<script lang="ts">
import { defineBasicLoader } from 'vue-router/experimental'

export const useUserData = defineBasicLoader('/users/[id]', (route) =>
  getUserById(route.params.id),
)
</script>

<script setup lang="ts">
const { data, isLoading, error, reload } = useUserData()
</script>
```

Navigation waits for the loader. Other callers share its fetching instance.

## Pinia Colada essentials

Register Pinia first, then Pinia Colada. Plugin factories run in array order:

```ts
app.use(createPinia())
app.use(PiniaColada, {
  queryOptions: { staleTime: 5_000, gcTime: 300_000 },
  mutationOptions: {},
  plugins: [],
})
```

The default query freshness is 5 seconds and garbage-collection time is 5
minutes. A query needs a serializable array `key` and a `query` function:

```ts
const query = useQuery({
  key: () => ['products', id.value],
  query: () => getProduct(id.value),
  enabled: () => Boolean(id.value),
})
```

Every reactive query input must occur in the reactive key. Array order matters;
object-property order does not, and `undefined` object properties are removed.
Disable long-lived queries when their route inputs are unavailable.

Read the two state axes independently:

| Field | Values | Meaning |
| --- | --- | --- |
| `status` | `pending`, `success`, `error` | Data state |
| `asyncStatus` | `idle`, `loading` | Request activity |

`refresh()` deduplicates and respects freshness. `refetch()` forces a request.
Both resolve to state by default; pass `true` to rethrow an error.

Use `defineQueryOptions()` for reusable, parameterized, type-tagged keys. Use
`defineQuery()` only for once-instantiated globally shared composables; extra
state it returns is not serialized for SSR. A query placed in a long-lived
Pinia store is effectively immortal.

## Cache and mutation safety

`invalidateQueries()` marks matching entries stale and refetches active entries
by default. Pass `'all'` as its second argument to include inactive matches.
Use `ensure()` before seeding when the cache entry must preserve query options
and freshness behavior.

`mutate()` catches failures and returns nothing; `mutateAsync()` returns a
rejecting promise. Awaited mutation hooks keep loading active, and the value
returned by `onMutate` becomes the context for later hooks.

For an optimistic update:

1. Snapshot and replace cached data in `onMutate`.
2. Call `cancelQueries()` so stale results are discarded without refetching.
3. Return the old and optimistic values as rollback context.
4. Roll back only if the cache still holds this mutation's optimistic value.
5. Invalidate the affected query on settlement.

Queries intentionally have no local success/error/settled callbacks. Watch
state for component effects or install `PiniaColadaQueryHooksPlugin` for global
fetch hooks. Query `meta` is fixed when the entry is created and must be
serializable for SSR.

## Typed template refs

Use Vue's exported `TemplateRef` when a template ref needs an explicit type:

```ts
import { useTemplateRef, type TemplateRef } from 'vue'

const input: TemplateRef<HTMLInputElement> =
  useTemplateRef<HTMLInputElement>('input')
```

## Verification checklist

- Exercise kept-alive route reactivation: guards now run when the route changes.
- Validate generated routes and parameter parsers; missing parsers throw.
- Test query loading separately from data status, including preserved data after refetch errors.
- Use real `createPinia()` in Pinia Colada component tests, then flush promises.
- Await cache restoration before mounting when using asynchronous persistence.
