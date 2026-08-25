---
name: vuejs-knowledge-patch
description: Vue.js
version: 3.6.0-beta
license: MIT
metadata:
  author: Nevaberry
---


# Vue.js Knowledge Patch

Use this patch when changing Vue applications or ecosystem tooling, especially
projects using Vue Router, Pinia, Pinia Colada, Nuxt, or Vite integrations.
Check the installed package versions before applying version-specific migration
advice.

## Reference index

| Reference | Topics |
| --- | --- |
| [`references/vue-router-5.md`](references/vue-router-5.md) | Router package migration, file-based routes, typed routes, parameters, loaders, guards, scrolling, and distribution changes |
| [`references/pinia-3.md`](references/pinia-3.md) | Pinia package requirements, ESM migration, Devtools, hydration, public APIs, and Nuxt compatibility |
| [`references/pinia-colada-queries.md`](references/pinia-colada-queries.md) | Query setup, state, keys, cache operations, pagination, infinite queries, callbacks, and query plugins |
| [`references/pinia-colada-mutations-and-integration.md`](references/pinia-colada-mutations-and-integration.md) | Mutations, optimistic updates, shared definitions, persistence, SSR, testing, migrations, and extension APIs |
| [`references/vue-core-and-vapor.md`](references/vue-core-and-vapor.md) | Typed template refs, hydration and rendering fixes, custom elements, transitions, model typing, and release channels |
| [`references/ecosystem-tooling.md`](references/ecosystem-tooling.md) | Nuxt custom fetchers, Vite's Rolldown transition, and Vite+ |

## Breaking changes and upgrade gates

### Move Pinia 4 consumers to ESM

Pinia 4 is ESM-only and requires `@vue/devtools-api` v8 as a separate
dependency. Move CommonJS-only tooling to an ESM-capable path before upgrading:

```sh
pnpm add pinia@^4 @vue/devtools-api@^8
```

Pinia 3 remains usable from CommonJS distribution files despite declaring
`"type": "module"`, but its declarations require TypeScript 4.5 or newer. The
standalone IIFE builds in both Pinia 3 and Vue Router 5 no longer bundle their
Devtools dependency.

### Move file-based routing imports into Vue Router

Vue Router 5 incorporates the former `unplugin-vue-router` functionality.
Remove that package, import the Vite plugin from `vue-router/vite`, and import
other adapters, utilities, and types from `vue-router/unplugin`:

```ts
import VueRouter from 'vue-router/vite'
import type { EditableTreeNode, Options } from 'vue-router/unplugin'
```

Remove the old `unplugin-vue-router/client` type reference. Prefer generating
declarations inside `src` so normal TypeScript includes find them:

```ts
VueRouter({ dts: 'src/routes.d.ts' })
```

Applications that did not use the old plugin generally need no source changes.

### Treat the experimental router entry as ESM-only

Do not load `vue-router/experimental` from CommonJS. Vite is an optional peer,
so projects that do not use the Vite integration need not install it.

Typed query parameters are optional. Invalid query formats warn and are
filtered rather than failing route matching, and a query value may be
`undefined`; do not assume a declared query key is present.

### Apply Pinia Colada API migrations

Current `useQuery()` accepts one options object. The old two-argument
`useQuery` and `useQueryState` forms are removed, and global query defaults
belong under `queryOptions`. Commit current work, then run the appropriate
ast-grep rule shipped by the installed package against the source tree:

```sh
pnpm --package=@ast-grep/cli dlx ast-grep scan \
  -r node_modules/@pinia/colada/codemods/rules/migration-0-21-to-1-0.yaml \
  -i src
```

## Router data loaders

Install `DataLoaderPlugin` before the router so it participates in the initial
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

Loaders run outside component setup, are collected and awaited during
navigation, and support parallel deduplicated fetching, loading and error
state, SSR, and prefetching. Basic loaders always rerun; the Colada
implementation uses `@pinia/colada`.

Export a loader from its page component. If it is defined elsewhere, re-export
it from the page so the router can discover it:

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

## Typed file-based routing

Use the bundled Volar plugins to infer a page's route from its file location,
including the types returned by no-argument `useRoute()` and template `$route`:

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

Validate generated routes and parameter parsers. Missing parsers throw, raw
parser types are arrays, and malformed `[x+hh]` filename escapes are rejected.
`definePage()` also checks `params.path` and parameter defaults.

## Pinia Colada essentials

Register Pinia before Pinia Colada. Plugin factories run in array order:

```ts
app.use(createPinia())
app.use(PiniaColada, {
  queryOptions: { staleTime: 5_000, gcTime: 300_000 },
  mutationOptions: {},
  plugins: [],
})
```

A query needs a serializable array `key` and a `query` function. Every reactive
input used by the query must also occur in a reactive key. Array order matters,
object-property order does not, and `undefined` object properties are removed.
Disable long-lived queries when route inputs are unavailable.

Read the two state axes independently:

| Field | Values | Meaning |
| --- | --- | --- |
| `status` | `pending`, `success`, `error` | Data state |
| `asyncStatus` | `idle`, `loading` | Request activity |

`refresh()` deduplicates and respects freshness. `refetch()` forces a request.
Both resolve to state by default; pass `true` to rethrow an error. A refetch
error preserves prior data, and `fetch()` must explicitly throw for non-2xx
responses to become query errors.

Use `defineQueryOptions()` for reusable parameterized, type-tagged keys. Use
`defineQuery()` only for once-instantiated shared composables; its extra state
is not serialized for SSR. A query held by a long-lived Pinia store is
effectively immortal.

## Cache and mutation safety

`invalidateQueries()` marks matches stale and refetches active entries by
default. Pass `'all'` as its second argument to include inactive matches. Use
`ensure()` before seeding when the cache entry must retain query options and
freshness behavior.

`mutate()` catches failures and returns nothing; `mutateAsync()` returns a
rejecting promise. Awaited hooks keep loading active, and the value returned by
`onMutate` becomes the context for later hooks.

For an optimistic update:

1. Snapshot and replace cached data in `onMutate`.
2. Call `cancelQueries()` so stale results are discarded without refetching.
3. Return the old and optimistic values as rollback context.
4. Roll back only if the cache still contains this mutation's optimistic value.
5. Invalidate the affected query on settlement.

Queries intentionally have no local success, error, or settled callbacks.
Watch state for component effects or install `PiniaColadaQueryHooksPlugin` for
global fetch hooks. Query `meta` is fixed when its entry is created and must be
serializable for SSR.

## Core typing and runtime checks

Use Vue's exported `TemplateRef` when a template ref needs an explicit type:

```ts
import { useTemplateRef, type TemplateRef } from 'vue'

const input: TemplateRef<HTMLInputElement> =
  useTemplateRef<HTMLInputElement>('input')
```

When upgrading Vue core, regression-test hydration of namespaced elements,
pre-hydration text input, current-type changes in `<select v-model>`, SSR
comments, Teleports inside Transitions, nullish slot-prop objects, custom
elements with native-property collisions, and `defineModel()` factory defaults.

## Verification checklist

- Exercise kept-alive route reactivation; guards run when the route changes.
- Test overlapping navigations so stale asynchronous scroll results are ignored.
- Validate query loading separately from data status, including retained data after refetch errors.
- Use real `createPinia()` in Pinia Colada component tests, then flush promises.
- Await asynchronous cache restoration before mounting the application.
- Verify Pinia hydration for skipped non-plain objects and reactive `Set` or `Map` state.
