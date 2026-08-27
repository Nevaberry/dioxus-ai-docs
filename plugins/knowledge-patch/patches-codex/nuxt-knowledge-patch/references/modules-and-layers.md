# Modules and layers

Build Nuxt Kit modules, compose layers, register imports and templates, and resolve generated configuration.

## Layers, aliases, and context boundaries

### Automatic local layer registration (since 3.12.0)

Directories placed under `~/layers` are now registered as Nuxt layers automatically, just as files under `~/modules` are registered as modules. Explicit `extends` entries are no longer needed for these local layers.

### Disabling modules inherited from layers (since 3.21.0)

A project extending a layer can disable one of the layer's modules by setting that module's options to `false`.

```ts
export default defineNuxtConfig({
  extends: ['../shared-layer'],
  image: false,
})
```

### Layer aliases in stylesheets (release-catalogs)

Named layer aliases such as `#layers/theme` now resolve from CSS files as well as module imports.

```css
@import "#layers/theme/assets/styles.css";
```

### Layer override order (since 4.0-platform-guide)

Project files have the highest priority, followed by auto-scanned `~~/layers` entries and then explicitly configured `extends` entries. Auto-scanned layers sort alphabetically with Z overriding A, while earlier `extends` entries override later ones; numeric directory prefixes provide an explicit local ordering convention.

### Named layer aliases (since 3.16.0)

An auto-scanned `~~/layers/test` layer now receives the `#layers/test` alias automatically. Other layers can declare `$meta.name` in their configuration to create a corresponding `#layers/<name>` alias.

```ts
export default defineNuxtConfig({
  $meta: { name: 'example-layer' },
})
```

### Protected `#server` alias (since 3.21.0)

Server code can import from the server directory through `#server`, while client and shared contexts are prevented from importing through the alias.

```ts
import { helper } from '#server/utils/helper'
```

### Remote layer configuration (since 4.0-platform-guide)

An `extends` entry can target a local directory, npm package, or a Git repository through a `github:` specifier. Remote entries accept per-layer options for private-repository authentication and a `meta.name` alias; an omitted Git branch defaults to `main`.

```ts
export default defineNuxtConfig({
  extends: [
    ['github:my-themes/private-awesome#v1', {
      auth: process.env.GITHUB_TOKEN,
      meta: { name: 'private-theme' },
    }],
  ],
})
```

### Resolved layer directories for modules (since 4.1.0)

Module authors can use `getLayerDirectories(nuxt)` from `@nuxt/kit` to resolve public layer paths such as `app`, `appPages`, `server`, and `public` without relying on private APIs.

```ts
import { getLayerDirectories } from '@nuxt/kit'

export default defineNuxtModule({
  async setup(_options, nuxt) {
    const directories = await getLayerDirectories(nuxt)
    console.log(directories.appPages)
  },
})
```

### Shared code for the Vue app and Nitro server (since 3.14.0)

The new top-level `shared/` directory holds context-independent types and utilities that both the Vue app and Nitro server can consume; its files must not import Vue-app or Nitro-specific code. With `compatibilityVersion: 4` its exports are auto-imported, and `#shared` provides an explicit alias to the directory, which sits alongside `server/` rather than inside `app/`.

```ts
// shared/format-id.ts
export const formatId = (id: number) => `item-${id}`

// server/api/item.ts
import { formatId } from '#shared/format-id'
```

## Nuxt Kit modules and dependencies

### Async build-plugin factories (since 3.21.0)

Module authors can give `addVitePlugin` and `addWebpackPlugin` factories that load and construct plugins asynchronously, avoiding loading the plugin for an unused builder.

```ts
addVitePlugin(() => import('my-plugin').then(m => m.default()))
addWebpackPlugin(() => import('my-plugin/webpack').then(m => m.default()))
```

### Async module dependencies (since 3.21.0)

Module definitions can provide `moduleDependencies` as an async function when dependencies must be computed dynamically.

### Declarative module dependencies (since 3.19.0)

Modules can now specify dependencies on other modules, making those requirements part of the module definition.

### Enforced module compatibility (since 3.17.0)

Module consumers can opt into an error when Nuxt loads a module that declares incompatible requirements; this check becomes the default in Nuxt 4.

```ts
export default defineNuxtConfig({
  experimental: { enforceModuleCompatibility: true },
})
```

### File exclusions in `resolveFiles` (since 3.19.0)

Nuxt Kit's `resolveFiles` accepts an `ignore` option, so module code can exclude selected paths while resolving file patterns.

### Module dependencies use metadata names (since 4.2.0)

As of 4.2.2, `moduleDependencies` entries are typed and matched against a dependency module's metadata name, and `installModule` respects those declarations.

### Module install and upgrade hooks (since 3.19.0)

Module definitions can provide `onInstall` and `onUpgrade` hooks for installation- and upgrade-specific work.

### Module resolution extensions (since 4.2.0)

Nuxt Kit's `resolveModule` accepts an `extensions` option for resolving non-default file extensions.

```ts
await resolveModule('my-module', { extensions: ['.ts', '.mjs'] })
```

### Module-controlled TypeScript hoisting (since 3.18.0)

Modules can now add entries to `typescript.hoist`, giving them control over which dependencies participate in Nuxt's generated TypeScript configuration and types.

### Nested Vite plugin controls (since 4.5.2)

Nuxt Kit's Vite wrapper now honors nested plugins' `apply`, `applyToEnvironment`, and `enforce` controls. Registering a plugin with `prepend` also prepends its environment wrapper, preserving the requested activation and ordering.

### Nitro type augmentation from modules (since 3.16.0)

Module authors can pass `{ nitro: true }` to `addTypeTemplate` to add declarations to Nitro's type context.

```ts
addTypeTemplate({
  filename: 'types/my-module.d.ts',
  getContents: () => `declare module 'nitropack' {
    interface NitroRouteConfig { myCustomOption?: boolean }
  }`,
}, { nitro: true })
```

### Typed module installation and builder compatibility (since 3.12.0)

`installModule` now supports typed module options, and module options can declare compatibility with Vite or webpack builders.

### Typed module-option composition (since 3.13.0)

Module authors can use `defineNuxtModule().with()` to get better inferred types for merged module options.

## Templates, imports, and generated configuration

### Aliased auto-import directories (since 3.19.0)

Aliases in `imports.dirs` are now resolved, so aliased directories can supply auto-imports.

```ts
export default defineNuxtConfig({
  imports: {
    dirs: ['#shared/composables'],
  },
})
```

### Build-time runtime configuration (since 3.12.0)

Module authors can use the new build-time `useRuntimeConfig` and `updateRuntimeConfig` utilities to read and update resolved runtime configuration during module setup.

### Component declaration paths (since 4.2.0)

`addComponent` entries can specify a custom `declarationPath` for generated component declarations. This option applies to individual components, not component-directory entries.

### Components from named exports (since 3.17.0)

Module authors can use `addComponentExports` to register every component exposed as a named export from a file automatically.

### Environment loading precedes schema resolution (since 4.4.0)

Nuxt Kit now reads `.env` before resolving the Nuxt schema, making those environment values available to environment-dependent schema resolution.

### Server runtime templates from modules (since 3.14.0)

Module authors can use `addServerTemplate` to add a virtual file that is available inside Nitro runtime routes.

### Single server imports in Nuxt Kit (since 3.18.0)

Module authors can pass one import directly to `addServerImports`; an array is no longer required for a single entry.

```ts
addServerImports({ from: 'my-package', name: 'myUtility' })
```
