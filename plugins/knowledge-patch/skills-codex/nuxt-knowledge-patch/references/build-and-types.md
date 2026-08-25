# Build systems, tooling, and types

Select builders, diagnose builds, and account for TypeScript, CSS, HMR, source-map, and bundle behavior.

## Builders, plugins, and CSS

### Disabling built-in PostCSS plugins (since 3.19.0)

The default `autoprefixer` and `cssnano` plugins can now be disabled explicitly in PostCSS configuration.

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

### Experimental Rolldown-backed Vite (since 3.19.0)

Nuxt's Vite integration has experimental support for `rolldown-vite`, so projects can evaluate Rolldown while retaining Nuxt's Vite builder integration.

### Experimental Rspack builder (since 3.14.0)

Nuxt now has a first-class experimental Rspack builder. Install `@nuxt/rspack-builder` and select it by its short builder name.

```ts
export default defineNuxtConfig({
  builder: 'rspack',
})
```

### Inline styles with webpack and Rspack (since 3.21.0)

Nuxt's `inlineStyles` feature now works with the webpack and Rspack builders as well as Vite.

### Narrower style inlining under v4 defaults (since 3.15.0)

With the v4 defaults enabled, Nuxt now limits default style inlining to styles from Vue components.

### Opt-in Vite Environment API (since 4.2.0)

Nuxt can experimentally run its Vite environments through the Vite Environment API. The integration may still change and must be enabled explicitly.

```ts
export default defineNuxtConfig({ experimental: { viteEnvironmentApi: true } })
```

### Server files in builder watch events (since 4.3.0)

Changes under `server/` now reach the `builder:watch` hook, so modules listening to that hook can respond to server-file edits.

## Bundles, source maps, HMR, and development

### Build profiling (since 4.4.0)

`nuxt build --profile` records duration, RSS, and heap changes for build phases, modules, and bundler plugins, writing `.nuxt/perf-trace.json`, `.nuxt/perf-report.json`, and `nuxt-build.cpuprofile`. Use `--profile=verbose` to also print detailed timings.

```sh
nuxt build --profile
```

### Client-side Node.js built-ins (since 3.10.0)

Client code can experimentally import Node built-ins through `node:` specifiers, but Nuxt does not install them as globals because doing so would increase every client bundle. Import only what is needed, or assign imports to `globalThis` in a client plugin when a dependency requires globals.

```ts
import { Buffer } from 'node:buffer'
import process from 'node:process'
```

### Experimental decorator support (since 3.16.0)

Enable the new experimental decorator support before using decorators in application code.

```ts
export default defineNuxtConfig({
  experimental: { decorators: true },
})
```

### Hashed-only client chunk names (since 3.11.0)

Client chunks now default to `_nuxt/[hash].js` instead of `_nuxt/[name].[hash].js` to avoid name-based ad-blocker matches. Restore named chunks through the client Vite output configuration when stable readable names are required.

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

### HMR for virtual files and page metadata (since 3.15.0)

Hot module replacement now covers Nuxt virtual files such as routes, plugins, and generated files, as well as content inside `definePageMeta`. Route and page-metadata changes can therefore take effect during development without a page reload.

### Lightweight project initializer (since 3.16.0)

`create-nuxt` is a new single-file, streamlined alternative to `nuxi init`.

```sh
npm create nuxt
```

### Newly ignored directories (since 4.3.0)

Nuxt 4.3.1 adds direnv and `vendor` directories to its default ignore set, avoiding unnecessary processing of environment and vendored files.

### Original-source server maps (since 3.13.0)

After the Nitro build, server source maps now point back to the original source files instead of Vite's intermediate output when Node runs with `--enable-source-maps`. Disable unused server maps to reduce build work.

```ts
export default defineNuxtConfig({
  sourcemap: { server: false, client: true },
})
```

### Server-side test flag (since 4.5.2)

Server code now has `import.meta.test` defined, allowing test-only server branches to use the same build-time flag directly.

```ts
if (import.meta.test) {
  // server-side test setup
}
```

### Stable entry chunks through import maps (since 4.1.0)

Vite builds now inject an import map for `#entry` by default, preventing an entry-file hash change from cascading into otherwise unchanged chunks. Nuxt disables this when `vite.build.target` includes browsers without native import-map support; it can also be disabled explicitly.

```ts
export default defineNuxtConfig({
  experimental: {
    entryImportMap: false,
  },
})
```

## Diagnostics and profiling

### Development warning changes (since 3.13.0)

Data-fetching composables used in middleware no longer trigger a development warning, while user component names beginning with `Lazy` now do.

### Editable sources from Chrome DevTools (since 3.18.0)

Chrome DevTools workspace integration lets edits made to Nuxt sources in DevTools update the actual project files.

### Nuxt DevTools v2 configuration tracing (since 3.16.0)

Nuxt DevTools v2 can inspect resolved configuration and trace how modules changed it; it also supports custom editor selection and restores the schema generator.

### Nuxt hook timings in Chromium profiles (since 3.15.0)

In development, Nuxt now publishes hook timings through the Chrome DevTools extensibility API, making them visible in the Performance panel of Chromium-based browsers.

### Request-scoped SSR logs in the browser (since 3.11.0)

During development, server-side `console.log` output associated with a request is forwarded to the browser console. The `dev:ssr-logs` hook can handle these logs on either server or client; set `features.devLogs` to `false` to disable the feature or `'silent'` to keep the hook without printing in the browser.

```ts
export default defineNuxtConfig({
  features: { devLogs: 'silent' },
})
```

### Selective debug categories (since 3.16.0)

`debug` can now be an object selecting `templates`, `modules`, `watchers`, client or server `hooks`, `nitro`, `router`, and `hydration` logs; `debug: true` still enables everything.

```ts
export default defineNuxtConfig({
  debug: { modules: true, hooks: { server: true } },
})
```

## TypeScript and generated declarations

### Context-specific TypeScript overrides (release-catalogs)

Nuxt 4 exposes `typescript.nodeTsConfig` and `typescript.sharedTsConfig` for customizing the generated Node and shared-code TypeScript projects independently.

```ts
export default defineNuxtConfig({
  typescript: {
    nodeTsConfig: { compilerOptions: { noUncheckedIndexedAccess: true } },
    sharedTsConfig: { compilerOptions: { noUncheckedIndexedAccess: true } },
  },
})
```

### Experimental Nuxt TypeScript plugins (since 4.2.0)

`experimental.typescriptPlugin` automatically installs and configures `@dxup/nuxt` plugins for component renames, definitions for dynamic imports and Nitro routes, runtime-config navigation, and auto-import navigation. VS Code must use the workspace TypeScript version.

```ts
export default defineNuxtConfig({ experimental: { typescriptPlugin: true } })
```

### Generated TypeScript defaults (since 3.21.0)

Generated TypeScript configuration now enables `allowArbitraryExtensions`, and the Nitro server configuration enables `noUncheckedIndexedAccess`, which can reveal new server type errors. The latter can be explicitly disabled when necessary.

```ts
export default defineNuxtConfig({
  nitro: {
    typescript: { tsConfig: { compilerOptions: { noUncheckedIndexedAccess: false } } },
  },
})
```

### TypeScript 5.4 module preservation (since 3.12.0)

When TypeScript 5.4 is installed locally, Nuxt's generated `tsconfig.json` now sets `module` to `preserve`.

### TypeScript bundler resolution by default (since 3.10.0)

Nuxt now opts into TypeScript's `bundler` module resolution so subpath imports match Nuxt's actual resolver more closely. Packages with incomplete `package.json` entries can require a temporary opt-out.

```ts
export default defineNuxtConfig({
  future: { typescriptBundlerResolution: false },
})
```

### Vue type-augmentation compatibility (since 3.13.0)

Nuxt now follows Vue's recommended `vue` augmentation target instead of `@vue/runtime-core`. Libraries that still augment the old target can break merged types; until they update, bridge the Vue interfaces from a root `declarations.d.ts`:

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
