# Build systems, tooling, and types

## Select and verify the builder

Nuxt supports Vite, webpack, and an experimental first-class Rspack builder. Install `@nuxt/rspack-builder` and set `builder: 'rspack'` to evaluate Rspack (3.14.0). Nuxt 3.15 upgraded the Vite dependency to Vite 6, so verify plugins that constrain a Vite major (3.15.0).

Experimental `rolldown-vite` support keeps Nuxt's Vite integration while replacing its bundling engine (3.19.0). The opt-in Vite Environment API can run Nuxt's Vite environments through that API, but its integration may change (4.2.0).

```ts
export default defineNuxtConfig({
  experimental: { viteEnvironmentApi: true },
})
```

Inline styles work with webpack and Rspack as well as Vite (3.21.0). Test builder-facing modules and plugins on the builder actually selected by the application.

## Client bundles and Node built-ins

Client code may import Node built-ins through explicit `node:` specifiers. Nuxt does not install them as globals because that would enlarge every bundle; add globals in a client plugin only when a dependency requires them (3.10.0).

```ts
import { Buffer } from 'node:buffer'
import process from 'node:process'
```

Client chunks default to hashed-only paths such as `_nuxt/[hash].js`, avoiding name-based ad-blocker matches. Configure client Vite output only when readable stable names are required (3.11.0).

Vite builds inject an import map for `#entry`, preventing entry hash changes from cascading to unchanged chunks. Nuxt disables this when the browser target lacks import-map support; set `experimental.entryImportMap: false` to turn it off explicitly (4.1.0).

The experimental handler extractor places async-data handlers in dynamic chunks so payload-backed prerendered routes can omit those handlers from the client bundle (4.2.0).

## TypeScript generation

Nuxt defaults to TypeScript `bundler` module resolution (3.10.0). With local TypeScript 5.4, generated configuration uses `module: preserve` (3.12.0). Nuxt 4 splits application, server, shared, and builder contexts into separate generated projects (4.0.0).

Generated configuration enables `allowArbitraryExtensions`; the Nitro server project enables `noUncheckedIndexedAccess`, which can reveal server errors. Override the latter only when necessary (3.21.0).

```ts
export default defineNuxtConfig({
  nitro: {
    typescript: {
      tsConfig: {
        compilerOptions: { noUncheckedIndexedAccess: false },
      },
    },
  },
})
```

Nuxt 4 exposes `typescript.nodeTsConfig` and `typescript.sharedTsConfig` for context-specific overrides (release-catalogs). Regenerate types after changing modules, layers, aliases, source directories, or TypeScript settings.

Experimental Nuxt TypeScript plugins install and configure `@dxup/nuxt` support for component renames, dynamic-import and Nitro-route definitions, runtime-config navigation, and auto-import navigation. VS Code must use the workspace TypeScript version (4.2.0).

## Source maps and error diagnostics

Server source maps can point from built Nitro output to original source files when Node uses `--enable-source-maps`; disable unused server maps to avoid build work (3.13.0). Newer Nuxt/Nitro integration applies source maps automatically for errors and sets security headers on rendered error pages (3.16.0).

In development, custom error pages appear with a technical overlay (4.2.0). The overlay can be dragged or minimized and persists its state across reloads (4.3.0).

## Development logging and profiling

Request-scoped server `console.log` output is forwarded to the browser during development. Handle it on either side with `dev:ssr-logs`; set `features.devLogs: false` to disable, or `'silent'` to retain the hook without browser printing (3.11.0).

```ts
export default defineNuxtConfig({
  features: { devLogs: 'silent' },
})
```

`debug` accepts categories for templates, modules, watchers, client/server hooks, Nitro, router, and hydration; `debug: true` enables all categories (3.16.0). Nuxt DevTools v2 traces resolved configuration and module changes, supports editor selection, and includes the schema generator (3.16.0).

Nuxt publishes hook timings to the Chrome DevTools extensibility API for Chromium Performance profiles (3.15.0). `nuxt build --profile` records duration, RSS, and heap deltas for phases, modules, and bundler plugins in `.nuxt/perf-trace.json`, `.nuxt/perf-report.json`, and `nuxt-build.cpuprofile`; `--profile=verbose` also prints details (4.4.0).

```sh
nuxt build --profile
```

Chrome DevTools workspace integration can write source edits back to project files (3.18.0).

## HMR and watch behavior

HMR covers virtual routes, plugins, generated files, and `definePageMeta` content (3.15.0). Changes under `server/` reach `builder:watch`, allowing modules to react to server edits (4.3.0).

Nuxt 4.3.1 ignores direnv and `vendor/` directories by default, avoiding environment and vendored-file processing (4.3.0).

## CSS and syntax configuration

Default PostCSS `autoprefixer` and `cssnano` plugins can be disabled explicitly (3.19.0):

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

Enable `experimental.decorators` before using decorators in application code (3.16.0). Under v4 defaults, automatic style inlining is limited to Vue component styles (3.15.0).

## Development diagnostics and testing

Nuxt throws when server code uses `setInterval`. Development warns when data-fetching composables run outside plugin or setup context and when routing lacks `<NuxtPage>`; middleware usage is exempt. Component names beginning with `Lazy` also warn because the prefix has hydration semantics (3.10.0, 3.13.0).

Server code has the build-time `import.meta.test` flag for test-only branches (4.5.2):

```ts
if (import.meta.test) {
  // server-side test setup
}
```
