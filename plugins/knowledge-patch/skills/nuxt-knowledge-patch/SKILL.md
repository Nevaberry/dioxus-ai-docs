---
name: nuxt-knowledge-patch
description: Nuxt
license: MIT
version: 4.4.0
metadata:
  author: Nevaberry
---

# Nuxt Knowledge Patch

Use this skill to choose current Nuxt APIs, defaults, migration paths, and ecosystem patterns. Read the topic reference that matches the task before changing code; several defaults differ by compatibility mode, builder, deployment preset, or package major.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading.md](references/upgrading.md) | Major migrations, compatibility settings, removed options, dependency changes, and upgrade commands |
| [data-fetching-and-state.md](references/data-fetching-and-state.md) | `useAsyncData`, `useFetch`, payloads, caching, cookies, `callOnce`, and state reset behavior |
| [routing-and-navigation.md](references/routing-and-navigation.md) | Pages, route rules, middleware, layouts, links, transitions, scrolling, and announcements |
| [rendering-and-components.md](references/rendering-and-components.md) | Hydration, server components, islands, head APIs, built-ins, errors, and app runtime hooks |
| [modules-and-layers.md](references/modules-and-layers.md) | Nuxt Kit, module dependencies, layers, aliases, templates, imports, and build-time configuration |
| [build-and-types.md](references/build-and-types.md) | Builders, TypeScript projects, source maps, debugging, profiling, HMR, CSS, and client bundles |
| [nitro-and-deployment.md](references/nitro-and-deployment.md) | Nitro runtime, prerelease migration, routing, assets, caching, security, tasks, and deployment presets |
| [ecosystem-modules.md](references/ecosystem-modules.md) | Nuxt Scripts, Icon, Content, UI, and Image package majors |

## Start with the compatibility boundary

1. Inspect `package.json`, the lockfile, `nuxt.config`, and generated type configuration.
2. Identify the Nuxt major, compatibility version, builder, Nitro major, and relevant module majors independently.
3. Keep a Nuxt 3 application on its release channel when upgrading; use the deduplicating upgrade command from [upgrading.md](references/upgrading.md).
4. Treat Nuxt 5 compatibility as an experimental preview, not a bounded migration target.
5. Treat Nitro 3 as an explicitly pinned prerelease unless the project already opts into it; do not infer Nitro's major from Nuxt's major.
6. Re-run type checking after changing source layout, compatibility defaults, modules, or builders.

## Breaking-change quick reference

### Source layout and context boundaries

- Expect application code under `app/` in new Nuxt 4 projects; keep `server/`, `shared/`, `content/`, `public/`, and configuration at the project root.
- Preserve a detected Nuxt 3 layout unless the task explicitly includes migration.
- Respect separate application, server, shared, and builder TypeScript projects. Do not import `#server` from client or shared code.
- Keep `shared/` utilities context-independent; import them through `#shared` when an explicit path is useful.
- Account for path-prefixed component names under v4 defaults, especially in name-based `<KeepAlive>` filters.

### Removed and changed APIs

- Remove obsolete experimental configuration instead of retaining inert flags.
- Import `mergeModels` explicitly; it is no longer auto-imported.
- Prefer `status` and `statusText` over deprecated `statusCode` and `statusMessage` in new error code.
- Import head composables from Nuxt auto-imports or `#app/composables/head`, not directly from `@unhead/vue`, to preserve async context.
- Augment Vue through `vue`; bridge legacy `@vue/runtime-core` augmentation only as a temporary compatibility measure.
- Replace deprecated Vite extension hooks in module and builder integrations.
- Check ESM-only dependency majors before relying on transitive Nuxt packages from CommonJS module code.

### Nitro prerelease migration

- Expect production dependencies to be bundled by default; trace only native or incompatible exceptions.
- Remove `nodeModulesDirs`, `nitro/deps/*`, custom `moduleSideEffects`, and the temporary TypeScript-paths option.
- Import configuration, runtime, and HTTP utilities from the root `nitro` package; import `ServerRequest` from `nitro/types`.
- Opt into filesystem routing with `serverDir`, and configure routes, renderer behavior, entries, and builders explicitly where needed.
- Review Cloudflare binding access and bundling defaults before deployment.
- Upgrade past the proxy and redirect security fixes when using those route rules.

### Ecosystem package majors

- Define Nuxt Content collections in `content.config.ts`; migrate queries to collection utilities and replace removed document-driven and `ContentSlot` APIs.
- Define Nuxt Image custom providers with a default-exported `defineProvider`; remove retired providers and update operation formatting.
- Account for Nuxt UI's Reka UI and Tailwind CSS integration before applying old Headless UI or styling assumptions.
- Use the unified Nuxt UI package for formerly separate Pro components.

## Data-fetching quick reference

### Key identity and shared state

- Give each explicit async-data key one stable meaning.
- Expect callers with the same key to share refs, refreshes, cache access, and in-flight work.
- Allow reactive keys when data identity follows a ref, computed ref, or getter; expect old data to remain while a changed key loads.
- Keep handlers side-effect-safe because prerendering, payload reuse, preview mode, refresh, and deduplication can change when they run.
- Narrow absent data as `undefined`, not `null`.

### Cancellation and cache lifetime

- Accept the handler abort signal and pass it to downstream fetches.
- Pass a caller-owned signal to `refresh()` or `execute()` when the caller controls cancellation.
- Expect `clear()` and cancel-deduplicated refreshes to abort pending work.
- Expect cached data to be purged after its consumers unmount unless compatibility behavior is explicitly retained.
- Use payload extraction for cacheable routes when client navigation should consume `_payload.json` rather than refetch.
- Use client-mode payload extraction only after evaluating its opt-in compatibility behavior.

### State helpers

- Expect a failed `callOnce` callback to be retryable; use navigation mode for once-per-navigation work.
- Expect `clearNuxtState` to restore the initializer value.
- Set `useCookie({ refresh: true })` when assigning the same value should renew expiration.
- Disable Cookie Store synchronization explicitly if the browser integration is unwanted.

## Routing and rendering quick reference

### Pages, middleware, and layouts

- Use parenthesized directories for pathless route groups and inspect `route.meta.groups` in middleware.
- Attach named page middleware and layouts through `routeRules` when the behavior applies to a route family.
- Use a layout object in page metadata for type-checked layout props; pass runtime props as the second argument to `setPageLayout`.
- Render `<NuxtPage>` when router integration is enabled; do not substitute a bare `<RouterView>`.
- Keep one `definePageMeta` call per file.

### Navigation behavior

- Configure `NuxtLink` prefetch triggers for visibility, interaction, or both.
- Use per-link trailing-slash formatting and object route locations through either `to` or `href` as appropriate.
- Rely on navigation APIs to reject script-capable protocols and unsafe open redirects; do not bypass their checks.
- Include `<NuxtRouteAnnouncer>` in a custom `app.vue` and mount `<NuxtAnnouncer>` for non-navigation status messages.
- Apply smooth-scroll configuration to hash scrolling and preserve focus behavior after hash navigation.

### Hydration and islands

- Choose lazy hydration by visibility, idle time, interaction, media query, or delay; use `defineLazyHydrationComponent` for explicit imports.
- Use `onPrehydrate` only for browser work that must run immediately before hydration.
- Treat server-island props as URL data: keep them non-secret, serializable, and small.
- Check whether a server component is available during prerender or only first appears after client navigation before promising static-host support.
- Add client navigation behavior around links rendered by server components when interactive routing is required.

## Module and layer quick reference

- Let Nuxt auto-register local `layers/` and `modules/` directories.
- Resolve layer paths with `getLayerDirectories`; use named `#layers/<name>` aliases in imports and stylesheets.
- Apply precedence deliberately: project files override layers, local layers use reverse alphabetical priority, and earlier `extends` entries override later ones.
- Authenticate private remote layers through per-layer options and pin their branch or tag.
- Declare module dependencies and compatibility in module metadata; support async dependency calculation only when necessary.
- Use install and upgrade hooks for lifecycle-specific module work.
- Use `addServerTemplate`, Nitro type templates, server imports, and async builder-plugin factories instead of private internals.
- Read `.env`-dependent schema values with the expectation that environment loading occurs before schema resolution.

## Build and diagnostics quick reference

- Verify plugins against the selected Vite, webpack, Rspack, or Rolldown-backed builder rather than assuming Vite-only behavior.
- Keep Node built-ins in client code as explicit `node:` imports; install globals only in a client plugin when a dependency truly requires them.
- Expect hashed-only client chunk names unless readable names are configured intentionally.
- Use selective debug categories for focused diagnostics and build profiling for timing, RSS, heap, and plugin costs.
- Expect virtual files and page metadata to update through HMR.
- Use generated source maps and the development error overlay before adding custom error instrumentation.
- Recheck generated TypeScript defaults, module resolution, arbitrary extensions, and server indexed access after upgrades.

## Task routing

| If the task involves... | Read first |
| --- | --- |
| An upgrade, new warning, removed option, or compatibility flag | [upgrading.md](references/upgrading.md) |
| A stale request, duplicate fetch, cache miss, or payload issue | [data-fetching-and-state.md](references/data-fetching-and-state.md) |
| Page discovery, middleware, layouts, links, or navigation accessibility | [routing-and-navigation.md](references/routing-and-navigation.md) |
| Hydration, islands, server components, head state, or built-in components | [rendering-and-components.md](references/rendering-and-components.md) |
| A Nuxt module, layer, auto-import, generated template, or hook | [modules-and-layers.md](references/modules-and-layers.md) |
| Builder behavior, typing, source maps, HMR, CSS, or performance | [build-and-types.md](references/build-and-types.md) |
| Server runtime, route handlers, deployment, caching, tasks, or Nitro | [nitro-and-deployment.md](references/nitro-and-deployment.md) |
| Scripts, Content, UI, Icon, or Image | [ecosystem-modules.md](references/ecosystem-modules.md) |

## Verification

1. Run the project's formatter, type checker, and focused tests.
2. Regenerate Nuxt types after changing modules, layers, aliases, source layout, or TypeScript configuration.
3. Exercise both initial SSR and client navigation for routing, payload, hydration, island, or head changes.
4. Exercise the actual deployment preset for Nitro, asset, cache, WebSocket, queue, or scheduled-task changes.
5. Reinspect generated output when changing builders, chunk naming, source maps, payload extraction, or dependency tracing.
