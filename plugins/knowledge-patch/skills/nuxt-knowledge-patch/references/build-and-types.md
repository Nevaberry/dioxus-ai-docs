# Build systems, tooling, and types

Use this reference for builder selection, client bundling, TypeScript generation, CSS processing, source maps, development diagnostics, HMR, DevTools, and build profiling.

## Contents

- [Builders and client bundling](#builders-and-client-bundling)
- [TypeScript resolution and generated projects](#typescript-resolution-and-generated-projects)
- [CSS and asset compilation](#css-and-asset-compilation)
- [Source maps, HMR, and editing](#source-maps-hmr-and-editing)
- [Development diagnostics and tooling](#development-diagnostics-and-tooling)
- [Initialization and profiling](#initialization-and-profiling)

## Builders and client bundling

### Import client-side Node built-ins explicitly (3.10.0)

Client code can experimentally import Node built-ins with `node:` specifiers. Nuxt does not install them as globals because globals would increase every client bundle. Import only what is used, or assign imports to `globalThis` in a client plugin when a dependency requires globals.

```ts
import { Buffer } from 'node:buffer'
import process from 'node:process'
```

### Restore readable chunk names only when required (3.11.0)

Client chunks default to `_nuxt/[hash].js`, avoiding name-based ad-blocker matches. Configure Vite's client output to restore named chunks when stable readable filenames are operationally important.

```ts
export default defineNuxtConfig({
  vite: {
    $client: {
      build: {
        rollupOptions: {
          output: {
            chunkFileNames: '_nuxt/[name].[hash].js',
            entryFileNames: '_nuxt/[name].[hash].js',
          },
        },
      },
    },
  },
})
```

### Try the first-class Rspack builder explicitly (3.14.0)

Install `@nuxt/rspack-builder` and select the experimental builder by its short name.

```ts
export default defineNuxtConfig({
  builder: 'rspack',
})
```

### Evaluate Rolldown through Nuxt's Vite integration (3.19.0)

Nuxt supports experimental `rolldown-vite`, allowing a project to test Rolldown while retaining the Nuxt Vite-builder integration.

### Stabilize entry references with import maps (4.1.0)

Vite builds inject an import map for `#entry` by default, preventing an entry-file hash change from cascading to otherwise unchanged chunks. Nuxt disables this when `vite.build.target` contains browsers without native import-map support. Disable it manually only when necessary.

```ts
export default defineNuxtConfig({
  experimental: { entryImportMap: false },
})
```

### Test the Vite Environment API behind its flag (4.2.0)

Enable the experimental Vite Environment API integration explicitly and expect its integration surface to change.

```ts
export default defineNuxtConfig({
  experimental: { viteEnvironmentApi: true },
})
```

### Inline styles with every supported builder (3.21.0)

Nuxt's `inlineStyles` feature works with webpack and Rspack as well as Vite. Avoid builder-specific fallbacks that assume only Vite supports it.

## TypeScript resolution and generated projects

### Use bundler module resolution by default (3.10.0)

Nuxt opts into TypeScript's `bundler` module resolution so subpath imports follow Nuxt's resolver. A package with incomplete `package.json` exports can require a temporary opt-out.

```ts
export default defineNuxtConfig({
  future: { typescriptBundlerResolution: false },
})
```

### Preserve modules with local TypeScript 5.4 (3.12.0)

When TypeScript 5.4 is installed locally, Nuxt's generated `tsconfig.json` sets `module` to `preserve`.

### Augment the recommended Vue module (3.13.0)

Nuxt follows Vue's `vue` augmentation target rather than `@vue/runtime-core`. Libraries that still augment the old target can break merged types. Until the dependency updates, bridge the interfaces in a root `declarations.d.ts`.

```ts
import type {
  ComponentCustomOptions as _ComponentCustomOptions,
  ComponentCustomProperties as _ComponentCustomProperties,
} from 'vue'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties extends _ComponentCustomProperties {}
  interface ComponentCustomOptions extends _ComponentCustomOptions {}
}
```

### Test editor navigation with Nuxt TypeScript plugins (4.2.0)

`experimental.typescriptPlugin` installs and configures `@dxup/nuxt` plugins for component renames, dynamic-import and Nitro-route definitions, runtime-config navigation, and auto-import navigation. Configure VS Code to use the workspace TypeScript version.

```ts
export default defineNuxtConfig({
  experimental: { typescriptPlugin: true },
})
```

### Account for stricter generated defaults (3.21.0)

Generated TypeScript configuration enables `allowArbitraryExtensions`. The Nitro server project enables `noUncheckedIndexedAccess`, potentially revealing new server errors. Disable the server setting only after evaluating the lost safety.

```ts
export default defineNuxtConfig({
  nitro: {
    typescript: {
      tsConfig: { compilerOptions: { noUncheckedIndexedAccess: false } },
    },
  },
})
```

### Override Node and shared TypeScript projects separately (release-catalogs)

Nuxt 4 exposes `typescript.nodeTsConfig` and `typescript.sharedTsConfig` for context-specific generated configuration.

```ts
export default defineNuxtConfig({
  typescript: {
    nodeTsConfig: {
      compilerOptions: { noUncheckedIndexedAccess: true },
    },
    sharedTsConfig: {
      compilerOptions: { noUncheckedIndexedAccess: true },
    },
  },
})
```

## CSS and asset compilation

### Disable built-in PostCSS plugins explicitly (3.19.0)

Turn off Nuxt's default `autoprefixer` or `cssnano` plugins by setting their entries to `false`.

```ts
export default defineNuxtConfig({
  postcss: {
    plugins: {
      autoprefixer: false,
      cssnano: false,
    },
  },
})
```

## Source maps, HMR, and editing

### Map server output to original sources (3.13.0)

Post-build server source maps point back to original sources instead of Vite's intermediate output when Node runs with `--enable-source-maps`. Disable unused server maps to reduce build work.

```ts
export default defineNuxtConfig({
  sourcemap: { server: false, client: true },
})
```

### Hot-update virtual files and page metadata (3.15.0)

HMR covers routes, plugins, generated virtual files, and content inside `definePageMeta`, so these development changes can apply without a full page reload.

### Edit source files from Chrome DevTools (3.18.0)

Chrome DevTools workspace integration can write edits made in DevTools back to the actual Nuxt project files.

## Development diagnostics and tooling

### Honor new anti-pattern diagnostics (3.10.0)

Nuxt throws when `setInterval` is used on the server. Development also warns when data-fetching composables run outside a plugin or setup context, and when router integration is enabled without `<NuxtPage>`; a bare `<RouterView>` is not a supported substitute.

### Route request-scoped SSR logs to the browser (3.11.0)

During development, server `console.log` output associated with a request appears in the browser console. Handle it on server or client through `dev:ssr-logs`. Set `features.devLogs` to `false` to disable forwarding, or `'silent'` to keep the hook without printing.

```ts
export default defineNuxtConfig({
  features: { devLogs: 'silent' },
})
```

### Apply updated warning behavior (3.13.0)

Data-fetching composables in middleware no longer produce the outside-context development warning. User component names beginning with `Lazy` now warn because the prefix has hydration semantics.

### Fix stricter usage diagnostics (3.17.0)

Development warns about rootless server components, use of the reserved `runtimeConfig.app` namespace, and overrides of core auto-import presets. More than one `definePageMeta` call in a file is an error.

### Inspect hook timings in Chromium profiles (3.15.0)

In development, Nuxt publishes hook timings through the Chrome DevTools extensibility API. Inspect them in the Performance panel of Chromium-based browsers.

### Trace resolved configuration in Nuxt DevTools v2 (3.16.0)

Nuxt DevTools v2 shows resolved configuration and how modules changed it, supports custom editor selection, and restores the schema generator.

### Select debug categories (3.16.0)

Use an object to enable only relevant `templates`, `modules`, `watchers`, client/server `hooks`, `nitro`, `router`, or `hydration` logs. `debug: true` still enables all categories.

```ts
export default defineNuxtConfig({
  debug: { modules: true, hooks: { server: true } },
})
```

### Enable decorators explicitly (3.16.0)

Turn on experimental decorator support before using decorators in application code.

```ts
export default defineNuxtConfig({
  experimental: { decorators: true },
})
```

### Inspect custom and technical error pages together (4.2.0)

In development, an application error renders the project's custom error page together with a toggleable technical overlay, allowing simultaneous inspection of user-facing output and the stack trace.

### Reposition the development error overlay (4.3.0)

Drag the overlay to a screen corner or minimize it to a pill. Nuxt persists its position and minimized state across reloads.

### Ignore environment and vendored directories (4.3.0)

Nuxt 4.3.1 adds direnv and `vendor` directories to the default ignore set, avoiding unnecessary scanning and rebuilds.

## Initialization and profiling

### Use the lightweight project initializer (3.16.0)

`create-nuxt` is a streamlined single-file alternative to `nuxi init`.

```sh
npm create nuxt
```

### Profile the build (4.4.0)

`nuxt build --profile` records duration, RSS, and heap changes for build phases, modules, and bundler plugins. It writes `.nuxt/perf-trace.json`, `.nuxt/perf-report.json`, and `nuxt-build.cpuprofile`; use `--profile=verbose` to print detailed timings too.

```sh
nuxt build --profile
```
