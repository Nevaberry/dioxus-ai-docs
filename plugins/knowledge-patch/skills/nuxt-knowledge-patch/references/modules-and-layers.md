# Modules and layers

Use this reference for layer discovery and precedence, Nuxt Kit utilities, module lifecycle and dependencies, generated templates and types, aliases, imports, and build-time configuration.

## Contents

- [Layer discovery, naming, and precedence](#layer-discovery-naming-and-precedence)
- [Shared and protected source aliases](#shared-and-protected-source-aliases)
- [Module definitions and dependencies](#module-definitions-and-dependencies)
- [Runtime configuration and schema setup](#runtime-configuration-and-schema-setup)
- [Generated files, imports, components, and types](#generated-files-imports-components-and-types)
- [File and module resolution](#file-and-module-resolution)
- [Builder integration and watch hooks](#builder-integration-and-watch-hooks)

## Layer discovery, naming, and precedence

### Auto-register local layers (3.12.0)

Directories under `~/layers` are registered automatically, just as files under `~/modules` are auto-registered. Do not duplicate local layers in `extends` unless a non-default arrangement requires it.

### Use named layer aliases (3.16.0)

An auto-scanned `~~/layers/test` layer receives `#layers/test`. Other layers can declare `$meta.name` to create `#layers/<name>`.

```ts
export default defineNuxtConfig({
  $meta: { name: 'example-layer' },
})
```

### Resolve named layer aliases in stylesheets (release-catalogs)

Named aliases work in CSS as well as JavaScript and TypeScript imports.

```css
@import "#layers/theme/assets/styles.css";
```

### Configure remote layers and authentication (4.0-platform-guide)

An `extends` entry may point to a local directory, npm package, or `github:` repository. Supply private-repository authentication and an optional `meta.name` alias as per-layer options. If no Git branch is specified, the branch defaults to `main`; pin a branch or tag when reproducibility matters.

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

### Apply layer override order correctly (4.0-platform-guide)

Project files have highest priority, followed by auto-scanned `~~/layers`, then explicit `extends` entries. Auto-scanned layers sort alphabetically with Z overriding A. Earlier `extends` entries override later entries. Use numeric directory prefixes to make local ordering explicit.

### Resolve public layer directories through Kit (4.1.0)

Use `getLayerDirectories(nuxt)` rather than private layer internals to resolve paths such as `app`, `appPages`, `server`, and `public`.

```ts
import { getLayerDirectories } from '@nuxt/kit'

export default defineNuxtModule({
  async setup(_options, nuxt) {
    const directories = await getLayerDirectories(nuxt)
    console.log(directories.appPages)
  },
})
```

### Disable an inherited layer module (3.21.0)

Set a module's options to `false` in the extending project.

```ts
export default defineNuxtConfig({
  extends: ['../shared-layer'],
  image: false,
})
```

## Shared and protected source aliases

### Put cross-context utilities in `shared/` (3.14.0)

The top-level `shared/` directory holds types and utilities usable by both the Vue application and Nitro server. Do not import Vue-app-specific or Nitro-specific code from shared files. With compatibility version 4, shared exports are auto-imported; `#shared` provides an explicit alias.

```ts
// shared/format-id.ts
export const formatId = (id: number) => `item-${id}`

// server/api/item.ts
import { formatId } from '#shared/format-id'
```

Keep `shared/` beside `server/`, not under `app/`.

### Protect server-only imports with `#server` (3.21.0)

Server code can import from the server directory through `#server`; client and shared contexts are prevented from using the alias.

```ts
import { helper } from '#server/utils/helper'
```

### Resolve aliases in auto-import directories (3.19.0)

Aliases in `imports.dirs` are resolved before scanning:

```ts
export default defineNuxtConfig({
  imports: {
    dirs: ['#shared/composables'],
  },
})
```

## Module definitions and dependencies

### Type module installation and builder compatibility (3.12.0)

`installModule` accepts typed module options. Module options can also declare compatibility with Vite or webpack builders; report accurate requirements instead of assuming every builder is supported.

### Compose typed module options with `.with()` (3.13.0)

Use `defineNuxtModule().with()` for improved inference when composing and merging module options.

### Run installation and upgrade lifecycle hooks (3.19.0)

Module definitions can provide `onInstall` and `onUpgrade` for work specific to first installation or an existing installation's upgrade.

### Declare module dependencies (3.19.0)

Put dependencies on other modules in the module definition so consumers and Nuxt can reason about installation order and requirements.

### Match dependencies by metadata name (4.2.0)

As of 4.2.2, `moduleDependencies` entries are typed and matched against the dependency module's metadata name. `installModule` respects those declarations. Do not match on package display names or incidental import specifiers.

### Compute module dependencies asynchronously (3.21.0)

A module may expose `moduleDependencies` as an async function when the dependency set requires asynchronous discovery.

## Runtime configuration and schema setup

### Read and update runtime configuration during module setup (3.12.0)

Module authors can call build-time `useRuntimeConfig` and `updateRuntimeConfig` to inspect and modify the resolved runtime configuration during setup.

### Resolve schema after environment loading (4.4.0)

Nuxt Kit loads `.env` before resolving the Nuxt schema. Environment-dependent schema logic can read those values without a separate early dotenv load.

## Generated files, imports, components, and types

### Add Nitro runtime templates (3.14.0)

Use `addServerTemplate` to generate a virtual file that is importable from Nitro runtime routes.

### Augment Nitro types from a module (3.16.0)

Pass `{ nitro: true }` to `addTypeTemplate` so declarations join Nitro's type context.

```ts
addTypeTemplate({
  filename: 'types/my-module.d.ts',
  getContents: () => `declare module 'nitropack' {
    interface NitroRouteConfig { myCustomOption?: boolean }
  }`,
}, { nitro: true })
```

### Register components from named exports (3.17.0)

Use `addComponentExports` to register every component exposed as a named export from a file.

### Add a single server import directly (3.18.0)

`addServerImports` accepts one import object; an array is unnecessary for a single entry.

```ts
addServerImports({ from: 'my-package', name: 'myUtility' })
```

### Control generated TypeScript hoisting (3.18.0)

Modules can append dependencies to `typescript.hoist`, controlling which packages participate in Nuxt's generated TypeScript configuration and declarations.

### Set a component declaration path (4.2.0)

An individual `addComponent` entry accepts `declarationPath` for its generated declaration. The option does not apply to component-directory entries.

## File and module resolution

### Exclude files during pattern resolution (3.19.0)

Pass `ignore` to Nuxt Kit's `resolveFiles` to omit selected paths while resolving file patterns.

### Resolve additional module extensions (4.2.0)

Pass `extensions` to `resolveModule` for non-default file extensions.

```ts
await resolveModule('my-module', { extensions: ['.ts', '.mjs'] })
```

## Builder integration and watch hooks

### Load builder plugins asynchronously (3.21.0)

Pass factories to `addVitePlugin` and `addWebpackPlugin` so Nuxt loads and constructs a plugin only for the builder in use.

```ts
addVitePlugin(() => import('my-plugin').then(m => m.default()))
addWebpackPlugin(() => import('my-plugin/webpack').then(m => m.default()))
```

### Observe server changes through `builder:watch` (4.3.0)

Changes under `server/` reach the `builder:watch` hook, allowing modules to respond to server-file edits as well as application-file edits.
