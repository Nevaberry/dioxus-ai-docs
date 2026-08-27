---
name: nuxt-knowledge-patch
description: Nuxt
version: "4.4.0"
license: MIT
metadata:
  author: Nevaberry
---


# Nuxt Knowledge Patch

Use this skill when choosing current Nuxt APIs, defaults, migration paths, or ecosystem patterns. Read the topic reference that matches the task before changing code; behavior can depend on the Nuxt compatibility setting, builder, deployment preset, Nitro line, and module major.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading.md](references/upgrading.md) | Upgrade commands, compatibility settings, removed options, dependency shifts, and source layout |
| [data-fetching-and-state.md](references/data-fetching-and-state.md) | Async data, payloads, caching, preview mode, cookies, `callOnce`, and state reset behavior |
| [routing-and-navigation.md](references/routing-and-navigation.md) | Pages, route rules, middleware, layouts, links, transitions, scrolling, and announcements |
| [rendering-and-components.md](references/rendering-and-components.md) | Hydration, islands, server components, head APIs, built-ins, and errors |
| [modules-and-layers.md](references/modules-and-layers.md) | Nuxt Kit, dependencies, layers, aliases, templates, imports, and build-time configuration |
| [build-and-types.md](references/build-and-types.md) | Builders, TypeScript projects, source maps, debugging, HMR, CSS, and client bundles |
| [nitro-and-deployment.md](references/nitro-and-deployment.md) | Nitro runtime, routing, bundling, assets, caching, security, tasks, and deployment presets |
| [ecosystem-modules.md](references/ecosystem-modules.md) | Nuxt Scripts, Icon, Content, UI, and Image package majors |

## Start at the compatibility boundary

1. Inspect `package.json`, the lockfile, `nuxt.config`, and generated type configuration.
2. Identify the Nuxt major, compatibility version, builder, Nitro major, and relevant module majors independently.
3. Preserve a detected Nuxt 3 source layout unless migration is part of the task.
4. Keep Nuxt 3 upgrades on the v3 channel; do not let an upgrade silently cross majors.
5. Treat compatibility version 5 as an experimental preview, not a bounded migration target.
6. Treat Nitro 3 as an explicitly pinned beta unless the project already opts into it.
7. Re-run type checking after changing source layout, compatibility defaults, modules, or builders.

## Breaking changes and deprecations

### Source layout and context boundaries

- New Nuxt 4 projects place application code under `app/`; keep `server/`, `shared/`, `content/`, `public/`, and configuration at the project root.
- Respect separate application, server, shared, and builder TypeScript projects.
- Do not import through `#server` from client or shared code.
- Keep `shared/` utilities independent of Vue-app and Nitro runtime context; use `#shared` for explicit paths.
- Account for path-prefixed component names under v4 defaults, especially in name-based `<KeepAlive>` filters.

### Removed and changed APIs

- Remove obsolete experimental configuration instead of keeping inert flags.
- Import `mergeModels` explicitly; Nuxt no longer auto-imports it.
- Prefer `status` and `statusText` over deprecated `statusCode` and `statusMessage` in new error code.
- Import head composables from Nuxt auto-imports or `#app/composables/head`, not directly from `@unhead/vue`, so async context is retained.
- Augment Vue through `vue`; use a temporary `@vue/runtime-core` bridge only for libraries that have not migrated.
- Replace deprecated Vite `extend`, `extendConfig`, and `configResolved` hooks in module or builder integrations.
- Check ESM-only dependency majors before using transitive Nuxt packages from CommonJS module code.
- Nuxt Kit no longer supports Nuxt 2.

### Nitro 3 beta migration

- Pin the beta deliberately; do not infer Nitro's major from Nuxt's major.
- Expect production dependencies to be bundled by default and trace only native or incompatible exceptions.
- Remove `nodeModulesDirs`, `nitro/deps/*`, custom `moduleSideEffects`, and the temporary TypeScript-paths option.
- Import configuration, runtime, and HTTP utilities from `nitro`; import `ServerRequest` from `nitro/types`.
- Opt into filesystem routing with `serverDir`, and configure routes, renderer behavior, entries, and builders explicitly.
- Review Cloudflare bindings and bundling defaults before deployment.
- Upgrade beyond the proxy and redirect security fixes when using those route rules.

### Ecosystem package majors

- Define Nuxt Content collections in `content.config.ts`; use collection query utilities and replace document-driven mode and `ContentSlot`.
- Define Nuxt Image custom providers with a default-exported `defineProvider`; remove retired providers and migrate operation formatting.
- Account for Nuxt UI's Reka UI and Tailwind CSS integration before applying older Headless UI or styling assumptions.
- Use the unified Nuxt UI package for components formerly shipped separately as Pro.

## Data fetching and state

### Key identity and shared state

- Give each explicit async-data key one stable meaning.
- Callers with the same key share refs, refreshes, cache access, and in-flight work.
- Reactive keys may be refs, computed refs, or getters; old data remains while a changed key loads.
- Keep handlers side-effect-safe because prerendering, payload reuse, preview mode, refresh, and deduplication affect execution.
- Narrow absent data as `undefined`, not `null`.

### Cancellation and cache lifetime

- Accept the handler abort signal and pass it to downstream requests.
- Pass a caller-owned signal to `refresh()` or `execute()` when the caller controls cancellation.
- Expect `clear()` and cancel-deduplicated refreshes to abort pending work.
- Expect cached data to be purged after its consumers unmount unless compatibility behavior is retained explicitly.
- Use payload extraction for cacheable routes when navigation should consume `_payload.json` rather than refetch.
- Evaluate the opt-in compatibility behavior before enabling client-mode payload extraction.

### State helpers

- A failed `callOnce` callback is retryable; use navigation mode for once-per-navigation work.
- `clearNuxtState` restores the initializer value.
- Use `useCookie({ refresh: true })` when assigning the same value should renew expiration.
- Disable Cookie Store synchronization explicitly if the browser integration is unwanted.

## Routing and rendering

### Pages, middleware, and layouts

- Use parenthesized directories for pathless route groups and inspect `route.meta.groups` in middleware.
- Attach named page middleware and layouts through `routeRules` when behavior applies to a route family.
- Use a layout object in page metadata for checked layout props; pass runtime props as the second argument to `setPageLayout`.
- Render `<NuxtPage>` when router integration is enabled; a bare `<RouterView>` is not a supported replacement.
- Keep one `definePageMeta` call per file.
- Route-rule matching uses decoded paths and is case-insensitive.

### Navigation behavior

- Configure `NuxtLink` prefetch for visibility, interaction, or both.
- Use per-link trailing-slash formatting and object route locations through either `to` or `href`.
- Rely on navigation APIs to reject script-capable protocols and unsafe open redirects; do not bypass their checks.
- Include `<NuxtRouteAnnouncer>` in a custom `app.vue` and mount `<NuxtAnnouncer>` for in-page status messages.
- Apply smooth scrolling only to hash navigation and preserve focus movement after hash changes.
- Links rendered inside islands use client navigation on patched releases; older Nuxt 4 applications may still need a client wrapper.

### Hydration and islands

- Choose lazy hydration by visibility, idle time, interaction, media query, or delay.
- Use `defineLazyHydrationComponent` for explicit component imports.
- Use `onPrehydrate` only for browser work that must run immediately before hydration.
- Treat server-island props as URL data: non-secret, object-shaped, serializable, and small.
- Verify that a server component is prerendered before promising fully static hosting support.
- Exercise SSR and subsequent client navigation when changing island or payload behavior.

## Modules and layers

- Let Nuxt auto-register local `layers/` and `modules/` directories.
- Resolve public layer paths with `getLayerDirectories`; use named `#layers/<name>` aliases in imports and stylesheets.
- Apply precedence deliberately: project files override layers, local layers use reverse alphabetical priority, and earlier `extends` entries override later ones.
- Authenticate private remote layers through per-layer options and pin a branch or tag.
- Declare module dependencies and compatibility in module metadata; compute dependencies asynchronously only when necessary.
- Use install and upgrade hooks for lifecycle-specific work.
- Use `addServerTemplate`, Nitro type templates, server imports, and async builder-plugin factories instead of private internals.
- Expect `.env` loading before schema resolution when schema values depend on the environment.

## Build and diagnostics

- Verify plugins against the selected Vite, webpack, Rspack, or Rolldown-backed builder.
- Keep Node built-ins in client code as explicit `node:` imports; install globals only in a client plugin when required.
- Expect hashed-only client chunk names unless readable names are configured intentionally.
- Use selective debug categories for focused diagnostics and build profiling for timing, RSS, heap, and plugin costs.
- Expect virtual files, page metadata, and server watch events to update through development tooling.
- Use generated source maps and the development error overlay before adding custom error instrumentation.
- Recheck generated TypeScript defaults, arbitrary extensions, module resolution, and server indexed access after upgrades.

## Task routing

| If the task involves... | Read first |
| --- | --- |
| An upgrade, warning, removed option, dependency shift, or compatibility flag | [upgrading.md](references/upgrading.md) |
| A stale request, duplicate fetch, cache miss, payload, cookie, or state issue | [data-fetching-and-state.md](references/data-fetching-and-state.md) |
| Page discovery, middleware, layouts, links, transitions, or navigation accessibility | [routing-and-navigation.md](references/routing-and-navigation.md) |
| Hydration, islands, server components, head state, or built-in components | [rendering-and-components.md](references/rendering-and-components.md) |
| A Nuxt module, layer, auto-import, generated template, or hook | [modules-and-layers.md](references/modules-and-layers.md) |
| Builder behavior, typing, source maps, HMR, CSS, tests, or performance | [build-and-types.md](references/build-and-types.md) |
| Server runtime, route handlers, deployment, caching, tasks, or Nitro | [nitro-and-deployment.md](references/nitro-and-deployment.md) |
| Scripts, Content, UI, Icon, or Image | [ecosystem-modules.md](references/ecosystem-modules.md) |

## Verification

1. Run the project's formatter, type checker, and focused tests.
2. Regenerate Nuxt types after changing modules, layers, aliases, source layout, or TypeScript configuration.
3. Exercise initial SSR and client navigation for routing, payload, hydration, island, or head changes.
4. Exercise the actual deployment preset for Nitro, assets, caching, WebSockets, queues, or scheduled tasks.
5. Reinspect generated output after changing builders, chunk naming, source maps, payload extraction, or dependency tracing.
