# Modules and layers

## Local and remote layer registration

Directories under `~/layers` are auto-registered like entries under `~/modules`; local layers do not need explicit `extends` entries (3.12.0).

An `extends` entry may reference a local directory, npm package, or Git repository through `github:`. Remote entries accept per-layer authentication and a `meta.name`; an omitted branch defaults to `main`, so pin a branch or tag for reproducibility (4.0-platform-guide).

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

## Layer priority and disabling inherited modules

Project files have highest priority, followed by auto-scanned local layers, then explicit `extends`. Local layers sort alphabetically with Z overriding A; earlier `extends` entries override later ones. Numeric directory prefixes make local order obvious (4.0-platform-guide).

A project can disable a module inherited from a layer by setting that module's options to `false` (3.21.0):

```ts
export default defineNuxtConfig({
  extends: ['../shared-layer'],
  image: false,
})
```

## Public layer directories and aliases

Use `getLayerDirectories(nuxt)` instead of private directory internals. It resolves public paths such as `app`, `appPages`, `server`, and `public` (4.1.0).

```ts
import { getLayerDirectories } from '@nuxt/kit'

export default defineNuxtModule({
  async setup(_options, nuxt) {
    const directories = await getLayerDirectories(nuxt)
    console.log(directories.appPages)
  },
})
```

Auto-scanned layers receive `#layers/<directory-name>`. Other layers can set `$meta.name` to create a named alias (3.16.0). Named aliases resolve in module imports, `imports.dirs`, and stylesheets (3.19.0, release-catalogs):

```css
@import "#layers/theme/assets/styles.css";
```

Use the top-level `shared/` directory for context-independent types and utilities consumed by both the Vue app and Nitro. Under compatibility version 4 its exports are auto-imported; `#shared` addresses it explicitly. Do not import application- or server-only context into shared code (3.14.0).

Server code can import its own directory through `#server`; client and shared contexts are blocked from doing so (3.21.0).

## Module definitions and typed options

`installModule` accepts typed options, and a module can declare builder compatibility for Vite or webpack (3.12.0). `defineNuxtModule().with()` improves inference when composing merged module options (3.13.0).

Declare dependencies on other modules in the module definition (3.19.0). Dependency entries are typed and matched using the dependency module's metadata name, and `installModule` respects them (4.2.0). Supply `moduleDependencies` as an async function only when requirements genuinely need runtime calculation (3.21.0).

Consumers can enforce declared module compatibility; this is the Nuxt 4 default (3.17.0). Module definitions also support `onInstall` and `onUpgrade` for lifecycle-specific work (3.19.0).

## Build-time configuration and page metadata

During setup, modules can use the build-time `useRuntimeConfig` and `updateRuntimeConfig` utilities to read or change resolved runtime configuration (3.12.0). `.env` files are loaded before schema resolution, so environment-dependent schema values are available then (4.4.0).

Use `experimental.scanPageMeta: 'after-resolve'` when metadata must reflect `pages:extend`; consume the result in `pages:resolved` (3.14.0). Register additional extracted fields through `experimental.extraPageMetaExtractionKeys` (3.15.0). Route rules from `defineRouteRules` appear on each resolved page's `rules` property (3.19.0).

## Templates, imports, and component declarations

Use `addServerTemplate` to create a virtual file accessible from Nitro runtime routes (3.14.0). Pass `{ nitro: true }` to `addTypeTemplate` to augment Nitro's type context (3.16.0).

```ts
addTypeTemplate({
  filename: 'types/my-module.d.ts',
  getContents: () => `declare module 'nitropack' {
    interface NitroRouteConfig { myCustomOption?: boolean }
  }`,
}, { nitro: true })
```

`addServerImports` accepts one import object directly; an array is unnecessary for a single entry. Modules can add dependencies to `typescript.hoist` when generated types must see them (3.18.0).

Use `addComponentExports` to register every named component export from a file (3.17.0). A single `addComponent` entry may set `declarationPath` for its generated declaration; this is not a component-directory option (4.2.0).

`resolveFiles` accepts `ignore` to exclude paths from a glob result (3.19.0). `resolveModule` accepts `extensions` for non-default suffixes (4.2.0).

## Builder plugins

`addVitePlugin` and `addWebpackPlugin` accept async factories, allowing a module to load only the plugin for the selected builder (3.21.0):

```ts
addVitePlugin(() => import('my-plugin').then(m => m.default()))
addWebpackPlugin(() => import('my-plugin/webpack').then(m => m.default()))
```

Nuxt Kit's Vite wrapper honors a nested plugin's `apply`, `applyToEnvironment`, and `enforce`. `prepend` also prepends the environment wrapper, preserving requested activation and order (4.5.2).
